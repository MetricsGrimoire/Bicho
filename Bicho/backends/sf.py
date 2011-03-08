# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2011  GSyC/LibreSoft, Universidad Rey Juan Carlos
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# Authors:  Santiago Dueñas <sduenas@libresoft.es>
#           Ronaldo Maia <romaia@async.com.br>
#           Daniel Izquierdo Cortazar <dizquierdo@glibresoft.es>
#

import re
import urlparse
import random
import urllib2
import datetime
import os

import BeautifulSoup
from storm.locals import *

from Bicho.common import Issue, People, Tracker, Comment, Attachment, Change
from Bicho.backends import register_backend
from Bicho.db.database import *


SOURCEFORGE_DOMAIN = 'http://sourceforge.net'

# SourceForge patterns for HTML fields
NUM_ISSUES_PATTERN = re.compile('Results&nbsp;-&nbsp;Display')
ISSUE_LINK_PATTERN = re.compile('/tracker/\?func=detail')
ISSUE_ID_PATTERN = re.compile('.*Detail: ([0-9]+) -')
ISSUE_SUMMARY_PATTERN = re.compile('.*- (.+)')
ISSUE_DETAILS_PATTERN = re.compile('Details:')
ISSUE_SUBMISSION_PATTERN = re.compile('Submitted:')
ISSUE_SUBMISSION_DATE_PATTERN = re.compile('.*\- ([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} .+)')
ISSUE_PRIORITY_PATTERN = re.compile('Priority:')
ISSUE_STATUS_PATTERN = re.compile('Status:')
ISSUE_RESOLUTION_PATTERN = re.compile('Resolution:')
ISSUE_ASSIGNED_TO_PATTERN = re.compile('Assigned:')
ISSUE_CATEGORY_PATTERN = re.compile('Category:')
ISSUE_GROUP_PATTERN = re.compile('Group:')
ISSUE_VISIBILITY_PATTERN = re.compile('Visibility:')
ISSUE_COMMENT_CLASS_PATTERN = re.compile('artifact_comment')
ISSUE_COMMENT_DATE_PATTERN = re.compile('.*Date: ([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} .+)')


class NotValidURLError(Exception):
    """
    Not Valid URL
    """
    pass


class SourceForgeParserError(Exception):
    """
    Error parsing SourceForge webpages
    """
    pass


class SourceForgeIssue(Issue):
    """
    """
    def __init__(self, issue, type, summary, desc, submitted_by, submitted_on):
        """
        """
        Issue.__init__(self, issue, type, summary, desc,
                       submitted_by, submitted_on)
        self.category = None
        self.group = None
    
    def set_category(self, category):
        """
        """
        self.category = category
    
    def set_group(self, group):
        """
        """
        self.group = group


class DBSourceForgeIssueExt(object):
    """
    Maps elements from X{issues_ext_sf} table.

    @param category: category of the issue
    @type category: C{str}
    @param group: group of the issue
    @type group: C{str}
    @param issue_id: identifier of the issue
    @type issue_id: C{int}

    @ivar __storm_table__: Name of the database table.
    @type __storm_table__: C{str}

    @ivar id: Extra issue fields identifier.
    @type id: L{storm.locals.Int}
    @ivar category: Category of the issue.
    @type category: L{storm.locals.Unicode}
    @ivar group_sf: Group of the issue.
    @type group_sf: L{storm.locals.Unicode}
    @ivar issue_id: Issue identifier.
    @type issue_id: L{storm.locals.Int}
    @ivar issue: Reference to L{DBIssue} object.
    @type issue: L{storm.locals.Reference}
    """
    __storm_table__ = 'issues_ext_sf'

    id = Int(primary=True)
    category = Unicode()
    group_sf = Unicode()
    issue_id = Int()

    issue = Reference(issue_id, DBIssue.id)
    
    def __init__(self, category, group, issue_id):
        self.category = unicode(category)
        self.group_sf = unicode(group)
        self.issue_id = issue_id


class DBSourceForgeIssueExtMySQL(DBSourceForgeIssueExt):
    """
    MySQL subclass of L{DBSourceForgeIssueExt}
    """
    __sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_ext_sf ( \
                     id INTEGER NOT NULL AUTO_INCREMENT, \
                     category VARCHAR(32) NOT NULL, \
                     group_sf VARCHAR(32) NOT NULL, \
                     issue_id INTEGER UNSIGNED NOT NULL, \
                     PRIMARY KEY(id), \
                     UNIQUE KEY(issue_id), \
                     INDEX ext_issue_idx(issue_id), \
                     FOREIGN KEY(issue_id) \
                       REFERENCES issues (id) \
                         ON DELETE CASCADE \
                         ON UPDATE CASCADE \
                     )'


class DBSourceForgeBackend(DBBackend):
    """
    Adapter for SourceForge backend.
    """
    def __init__(self):
        self.MYSQL_EXT = [DBSourceForgeIssueExtMySQL]

    def insert_issue_ext(self, store, issue, issue_id):
        """
        Insert the given extra parameters of issue with id X{issue_id}.

        @param store: database connection
        @type store: L{storm.locals.Store}
        @param issue: issue to insert
        @type issue: L{SourceForgeIssue}
        @param issue_id: identifier of the issue
        @type issue_id: C{int}

        @return: the inserted extra parameters issue
        @rtype: L{DBSourceForgeIssueExt}
        """
        try:
            db_issue_ext = DBSourceForgeIssueExt(issue.category, issue.group, issue_id)
            store.add(db_issue_ext)
            store.flush()
            return db_issue_ext
        except:
            store.rollback()
            raise

    def insert_comment_ext(self, store, comment, comment_id):
        """
        Does nothing
        """
        pass
    
    def insert_attachment_ext(self, store, attch, attch_id):
        """
        Does nothing
        """
        pass
    
    def insert_change_ext(self, store, change, change_id):
        """
        Does nothing
        """
        pass


class SourceForgeParser():
    """
    """
    def parse_issues_list(self, html):
        """
        """
        soup = BeautifulSoup.BeautifulSoup(html)
        hrefs = soup.findAll(href=ISSUE_LINK_PATTERN)

        ids = []
        for href in hrefs:
            query = urlparse.urlsplit(href.get('href')).query
            ids.append(urlparse.parse_qs(query)['aid'][0])
        return ids

    def parse_issue(self, html):
        """
        """
        soup = BeautifulSoup.BeautifulSoup(html,
                                           convertEntities=BeautifulSoup.BeautifulSoup.XHTML_ENTITIES)
        self.__prepare_soup(soup)

        try:
            id = self.__parse_issue_id(soup)
            summary = self.__parse_issue_summary(soup)
            desc = self.__parse_issue_description(soup)
            submission = self.__parse_issue_submission(soup)
            priority = self.__parse_issue_priority(soup)
            status = self.__parse_issue_status(soup)
            resolution = self.__parse_issue_resolution(soup)
            asignation = self.__parse_issue_assigned_to(soup)
            category = self.__parse_issue_category(soup)
            group = self.__parse_issue_group(soup)
            visibility = self.__parse_issue_visibility(soup)
            comments = self.__parse_issue_comments(soup)
            attachments = self.__parse_issue_attachments(soup)
            changes = self.__parse_issue_changes(soup)
        except:
            raise

        submitted_by = People(submission['id'])
        submitted_by.set_name(submission['name'])
        submitted_on = submission['date']
        assigned_to = People(asignation)

        issue = SourceForgeIssue(id, 'bug', summary, desc,
                                 submitted_by, submitted_on)
        issue.set_priority(priority)
        issue.set_status(status, resolution)
        issue.set_assigned(assigned_to)
        issue.set_category(category)
        issue.set_group(group)

        for comment in comments:
            submitted_by = People(comment['by']['id'])
            submitted_by.set_name(comment['by']['name'])
            issue.add_comment(Comment(comment['desc'], submitted_by,
                                      comment['date']))

        for attachment in attachments:
            a = Attachment(attachment['url'])
            a.set_name(attachment['filename'])
            a.set_description(attachment['desc'])
            issue.add_attachment(a)

        for change in changes:
            changed_by = People(change['by']['id'])
            changed_by.set_name(change['by']['name'])
            issue.add_change(Change(change['field'], change['old_value'],
                                    'unknown', changed_by, change['date']))

        return issue

    def get_total_issues(self, html):
        """
        """
        soup = BeautifulSoup.BeautifulSoup(html)
        text = soup.find(text=NUM_ISSUES_PATTERN)

        if text is None:
            raise SourceForgeParserError('total of issues not found')

        nissues = text.split('&nbsp')[4].split(';')[1]
        return int(nissues)

    def __parse_issue_id(self, soup):
        """
        """
        try :
            m = ISSUE_ID_PATTERN.match(unicode(soup.title.string))
            return m.group(1)
        except:
            print('Error parsing issue id')

    def __parse_issue_summary(self, soup):
        """
        """
        try:
            m = ISSUE_SUMMARY_PATTERN.match(unicode(soup.title.string))
            return m.group(1)
        except:
            print('Error parsing issue summary')

    def __parse_issue_description(self, soup):
        """
        """
        try:
            # Details is a list of unicode strings, so the
            # strings are joined into a string to build the
            # description field.
            details = soup.find({'label': True},
                                text=ISSUE_DETAILS_PATTERN).findNext('p')
            desc = u''.join(details.contents)
            return desc
        except:
            print('Error parsing issue description')
    
    def __parse_issue_submission(self, soup):
        """
        """
        try:
            submission = {}

            submitted = soup.find({'label': True},
                                  text=ISSUE_SUBMISSION_PATTERN).findNext('p')

            submission['name'] = submitted.a.get('title')
            submission['id'] = submitted.a.string
            submission['date'] = self.__str_to_date(ISSUE_SUBMISSION_DATE_PATTERN.match(submitted.contents[2]).group(1))
            return submission
        except:
            print('Error parsing issue submission')

    def __parse_issue_priority(self, soup):
        """
        """
        try:
            priority = soup.find({'label': True},
                                 text=ISSUE_PRIORITY_PATTERN).findNext('p')
            return priority.contents[0]
        except:
            print('Error parsing issue priority')
    
    def __parse_issue_status(self, soup):
        """
        """
        try:
            status = soup.find({'label': True},
                               text=ISSUE_STATUS_PATTERN).findNext('p')
            return status.contents[0]
        except:
            print('Error parsing issue status')

    def __parse_issue_resolution(self, soup):
        """
        """
        try:
            resolution = soup.find({'label': True},
                                   text=ISSUE_RESOLUTION_PATTERN).findNext('p')
            return resolution.contents[0]
        except:
            print('Error parsing issue resolution')
    
    def __parse_issue_assigned_to(self, soup):
        """
        """
        try:
            assigned = soup.find({'label': True},
                                 text=ISSUE_ASSIGNED_TO_PATTERN).findNext('p')
            return assigned.contents[0]
        except:
            print('Error parsing issue assigned to')

    def __parse_issue_category(self, soup):
        """
        """
        try:
            category = soup.find({'label': True},
                                 text=ISSUE_CATEGORY_PATTERN).findNext('p')
            return category.contents[0]
        except:
            print('Error parsing issue category')
    
    def __parse_issue_group(self, soup):
        """
        """
        try:
            group = soup.find({'label': True},
                              text=ISSUE_GROUP_PATTERN).findNext('p')
            return group.contents[0]
        except:
            print('Error parsing issue group')
    
    def __parse_issue_visibility(self, soup):
        """
        """
        try:
            visibility = soup.find({'label': True},
                                   text=ISSUE_VISIBILITY_PATTERN).findNext('p')
            return visibility.contents[0]
        except:
            print('Error parsing issue visibility')
    
    def __parse_issue_comments(self, soup):
        """
        """
        try:
            comments = []

            artifacts = soup.findAll('tr', {'class': ISSUE_COMMENT_CLASS_PATTERN})
            for art in artifacts:
                comment = {}

                rawsub, rawdesc = art.findAll('p')
                # Date and sender are content on the first 'p'
                a = rawsub.find('a')
                comment['by'] = {'name' : a.get('title'), 'id' : a.string}

                # Time stamp is the first value of the 'p' contents
                d = self.__clean_str(rawsub.contents[0])
                comment['date'] = self.__str_to_date(ISSUE_COMMENT_DATE_PATTERN.match(d).group(1))

                # Description is content on the second 'p'.
                comment['desc'] = self.__clean_str(u''.join(rawdesc.contents))

                comments.append(comment)
            return comments
        except:
            print('Errror parsing issue comments')
    
    def __parse_issue_attachments(self, soup):
        """
        """
        try:
            attachments = []

            files = soup.find('h4', {'id': 'filebar'}).findNext('tbody').findAll('tr')
            for f in files:
                attch = {}
                # Each entry contains three fields (td tags) that
                # follow the next order: filename, description and URL.
                aux = f.findAll('td')
                attch['filename'] = self.__clean_str(u''.join(aux[0].contents))
                attch['desc'] = self.__clean_str(u''.join(aux[1].contents))
                attch['url'] = SOURCEFORGE_DOMAIN + aux[2].a.get('href')

                attachments.append(attch)
            return attachments
        except:
            print('Errror parsing issue attachments')

    def __parse_issue_changes(self, soup):
        """
        """
        try:
            changes = []

            entries = soup.find('h4', {'id': 'changebar'}).findNext('tbody').findAll('tr')
            for e in entries:
                change = {}
                # Each change contains four fields (td tags) that
                # follow the next order: field, old value, date, by.
                aux = e.findAll('td')
                change['field'] = self.__clean_str(aux[0].string)
                change['old_value'] = self.__clean_str(aux[1].string)
                change['date'] = self.__str_to_date(self.__clean_str(aux[2].string))
                change['by'] = {'name': self.__clean_str(aux[3].a.get('title')),
                                'id': self.__clean_str(aux[3].a.string)}

                changes.append(change)
            return changes
        except:
            print('Errror parsing issue changes')
    
    def __prepare_soup(self, soup):
        """
        """
        self.__remove_comments(soup)
        self.__remove_tag(soup, 'br')

    def __remove_comments(self, soup):
        """
        """
        cmts = soup.findAll(text=lambda text:isinstance(text,
                                                        BeautifulSoup.Comment))
        [comment.extract() for comment in cmts]

    def __remove_tag(self, soup, tag):
        """
        """
        [t.extract() for t in soup.findAll(tag)]

    def __clean_str(self, s):
        """
        """
        return s.strip(' \n\t')

    def __str_to_date(self, s):
      """
      Convert a string with the form YYYY-MM-DD HH:MM to an well-formed
      datatime type.
      """
      from datetime import datetime
      dt = datetime.strptime(s, '%Y-%m-%d %H:%M:%S UTC')
      return dt


SUPPORTED_SF_TRACKERS = ('sourceforge', 'website')

class SourceForge():
    """
    SourceForge backend
    """
    URL_REQUIRED_FIELDS = ['atid', 'group_id']

    def run(self, url):
        """
        """
        self.url = url
        self.__check_tracker_url(self.url)

        self.db = get_database(DBSourceForgeBackend())
        self.db.insert_supported_traker(SUPPORTED_SF_TRACKERS[0],
                                        SUPPORTED_SF_TRACKERS[1])
        self.__insert_tracker(self.url)

        self.parser = SourceForgeParser()
        ids = self.__get_issues_list(self.url)

        for id in ids:
            url = self.url + '&func=detail&aid=%s' % id # FIXME:urls!!!
            issue = self.__get_issue(url)
            self.__insert_issue(issue)

    def __get_issues_list(self, url):
        """
        """
        # Gets the main HTML page
        html = self.__get_html(url)
        nissues = self.parser.get_total_issues(html)

        urls = []
        for i in xrange(0, nissues, 100):
            urls.append(url + '&offset=%s&limit=100' % i)

        ids = []
        for url in urls:
            html = self.__get_html(url)
            ids.extend(self.parser.parse_issues_list(html))
        return ids

    def __get_issue(self, url):
        """
        """
        html = self.__get_html(url)
        issue = self.parser.parse_issue(html)
        return issue

    def __insert_tracker(self, url):
        """
        """
        db_trk = self.db.insert_tracker(Tracker(url, SUPPORTED_SF_TRACKERS[0],
                                                SUPPORTED_SF_TRACKERS[1]))
        self.tracker_id = db_trk.id

    def __insert_issue(self, issue):
        """
        """
        db_issue = self.db.insert_issue(issue, self.tracker_id)

    def __get_html(self, url):
        """
        """
        html = urllib2.urlopen(url).read()
        return html

    def __check_tracker_url(self, url):
        """
        """
        query = urlparse.urlsplit(url).query
        if query is not None:
            # Get query field names
            qs = urlparse.parse_qs(query).keys()

            for field in self.URL_REQUIRED_FIELDS:
                if field not in qs:
                    raise NotValidURLError('Missing field %s' % field)
        else:
            raise NotValidURLError('Missing URL query set')


register_backend('sf', SourceForge)


if __name__ == "__main__":
    import urllib2
    url = "http://sourceforge.net/tracker/?func=detail&aid=3178299&group_id=152568&atid=784665"
    html = urllib2.urlopen(url)

    parser = SourceForgeParser()
    parser.parse_issue(html)
