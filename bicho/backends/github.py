# -*- coding: utf-8 -*-
# Copyright (C) 2012 GSyC/LibreSoft, Universidad Rey Juan Carlos
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Authors: Luis Cañas Díaz <lcanas@libresoft.es>

import sys
import time
import urllib2
import base64
import json

from bicho.backends import Backend
from bicho.config import Config
from bicho.utils import printerr, printdbg, printout
from bicho.common import Tracker, People, Issue, Comment, Change, \
    TempRelationship, Attachment
from bicho.db.database import DBIssue, DBTracker, DBBackend, get_database

from storm.locals import DateTime, Int, Reference, Unicode, Desc
from datetime import datetime
from dateutil.parser import parse  # used to convert str time to datetime

from lazr.restfulclient.errors import HTTPError


CLOSED_STATE = "closed"
OPEN_STATE = "open"
ALL_STATES = "all"


class DBGithubIssueExt(object):
    """
    """
    __storm_table__ = 'issues_ext_github'

    id = Int(primary=True)
    status = Unicode()
    issue_id = Int()
    web_link = Unicode()
    closed_at = DateTime()
    updated_at = DateTime()
    #FIXME a new table for this would be better
    milestone_name = Unicode()
    milestone_summary = Unicode()
    milestone_title = Unicode()
    milestone_web_link = Unicode()
    labels = Unicode()
    title = Unicode()

    issue = Reference(issue_id, DBIssue.id)

    def __init__(self, issue_id):
        self.issue_id = issue_id


class DBGithubIssueExtMySQL(DBGithubIssueExt):
    """
    MySQL subclass of L{DBGithubIssueExt}
    """

    __sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_ext_github (\
                     id INTEGER NOT NULL AUTO_INCREMENT, \
                     status VARCHAR(32) default NULL, \
                     issue_id INTEGER NOT NULL, \
                     web_link VARCHAR(255) default NULL, \
                     closed_at DATETIME default NULL, \
                     updated_at DATETIME default NULL, \
                     milestone_name VARCHAR(32) default NULL, \
                     milestone_summary VARCHAR(255) default NULL, \
                     milestone_title VARCHAR(255) default NULL, \
                     milestone_web_link VARCHAR(255) default NULL, \
                     labels VARCHAR(255) default NULL, \
                     title VARCHAR(255) default NULL, \
                     PRIMARY KEY(id), \
                     UNIQUE KEY(issue_id), \
                     INDEX ext_issue_idx(issue_id), \
                     FOREIGN KEY(issue_id) \
                       REFERENCES issues(id) \
                         ON DELETE CASCADE \
                         ON UPDATE CASCADE \
                     ) ENGINE=MYISAM; '


class DBGithubBackend(DBBackend):
    """
    Adapter for GitHub backend.
    """
    def __init__(self):
        self.MYSQL_EXT = [DBGithubIssueExtMySQL]

    def get_last_modification_date(self, store, tracker_id):
        # get last modification date stored in the database for a given status
        # select date_last_updated as date from issues_ext_github order by date
        # desc limit 1;
        # get latest modified since ..:
        # https://api.github.com/repos/composer/composer/issues?page=1&
        #state=closed&per_page=100&sort=updated&direction=asc&
        #since=2012-05-28T21:11:28Z

        result = store.find(DBGithubIssueExt,
                            DBGithubIssueExt.issue_id == DBIssue.id,
                            DBIssue.tracker_id == DBTracker.id,
                            DBTracker.id == tracker_id)
        #printdbg (str(Tracker(url, "github", "v3")))
        aux = result.order_by(Desc(DBGithubIssueExt.updated_at))[:1]

        for entry in aux:
            return entry.updated_at

        return None

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

        newIssue = False

        try:
            db_issue_ext = store.find(DBGithubIssueExt,
                                      DBGithubIssueExt.issue_id
                                      ==
                                      issue_id).one()
            if not db_issue_ext:
                newIssue = True
                db_issue_ext = DBGithubIssueExt(issue_id)

            db_issue_ext.status = self.__return_unicode(issue.status)
            db_issue_ext.description = self.__return_unicode(issue.description)
            db_issue_ext.web_link = self.__return_unicode(issue.web_link)
            db_issue_ext.closed_at = issue.closed_at
            db_issue_ext.updated_at = issue.updated_at
            db_issue_ext.milestone_name = self.__return_unicode(
                issue.milestone_name)
            db_issue_ext.milestone_summary = self.__return_unicode(
                issue.milestone_summary)
            db_issue_ext.milestone_title = self.__return_unicode(
                issue.milestone_title)
            db_issue_ext.milestone_web_link = self.__return_unicode(
                issue.milestone_web_link)
            db_issue_ext.labels = self.__return_unicode(issue.labels)
            db_issue_ext.title = self.__return_unicode(issue.title)

            if newIssue is True:
                store.add(db_issue_ext)

            store.flush()
            return db_issue_ext
        except:
            store.rollback()
            raise

    def __return_int(self, str):
        """
        Decodes into int, and pays attention to empty ones
        """
        if str is None:
            return str
        else:
            return int(str)

    def __return_unicode(self, str):
        """
        Decodes string and pays attention to empty ones
        """
        if str:
            return unicode(str)
        else:
            return None

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

    def insert_temp_rel(self, store, temp_relationship, trel_id, tracker_id):
        """
        Does nothing
        """
        pass


class GithubIssue(Issue):
    """
    Ad-hoc Issue extension for GitHub's issue
    """
    def __init__(self, issue, type, summary, desc, submitted_by, submitted_on):
        Issue.__init__(self, issue, type, summary, desc, submitted_by,
                       submitted_on)

        self.status = None
        self.description = None
        self.web_link = None

        # dates
        self.closed_at = None
        self.updated_at = None

        #self.importance  # mapped to type

        self.milestone_name = None  # E.g, "0.1.7" (from .milestone.name)
        self.milestone_summary = None
        # summary of the milestone (from .milestone.summary)
        self.milestone_title = None
        # project name + name + code_name (from .milestone.title)
        self.milestone_web_link = None  # (from .milestone.web_link)

        self.labels = None  # tags of the bug
        self.title = None  # title of the bug (from .bug.title)

    def set_status(self, status):
        """
        Set the status of the issue

        @param alias: status of the issue
        @type alias: C{str}
        """
        self.status = status

    def set_description(self, description):
        """
        Set the description of the issue

        @param alias: description of the issue
        @type alias: C{str}
        """
        self.description = description

    def set_web_link(self, web_link):
        """
        Set the web_link of the issue

        @param alias: web_link of the issue
        @type alias: C{str}
        """
        self.web_link = web_link

    def set_closed_at(self, closed_at):
        """
        Set the closed_at of the issue

        @param closed_at: of the issue
        @type closed_at: L{datetime.datetime}
        """
        if not isinstance(closed_at, datetime):
            raise ValueError('Parameter "closed_at" should be a %s '
                             'instance. %s given.' %
                             ('datetime', input.__class__.__name__))

        self.closed_at = closed_at

    def set_updated_at(self, updated_at):
        """
        Set the set_updated_at of the issue

        @param set_updated_at: of the issue
        @type set_updated_at: L{datetime.datetime}
        """
        if not isinstance(updated_at, datetime):
            raise ValueError('Parameter "updated_at" should be a %s '
                             'instance. %s given.' %
                             ('datetime', input.__class__.__name__))

        self.updated_at = updated_at

    def set_milestone_name(self, milestone_name):
        """
        Set the milestone_name of the issue

        @param alias: milestone_name of the issue
        @type alias: C{str}
        """
        self.milestone_name = milestone_name

    def set_milestone_summary(self, milestone_summary):
        """
        Set the milestone_summary of the issue

        @param alias: milestone_summary of the issue
        @type alias: C{str}
        """
        self.milestone_summary = milestone_summary

    def set_milestone_title(self, milestone_title):
        """
        Set the milestone_title of the issue

        @param alias: milestone_title of the issue
        @type alias: C{str}
        """
        self.milestone_title = milestone_title

    def set_milestone_web_link(self, milestone_web_link):
        """
        Set the milestone_web_link of the issue

        @param alias: milestone_web_link of the issue
        @type alias: C{str}
        """
        self.milestone_web_link = milestone_web_link

    def set_labels(self, labels):
        """
        Set the tags of the issue

        @param alias: tags of the issue
        @type alias: C{str}
        """
        self.labels = labels

    def set_title(self, title):
        """
        Set the title of the issue

        @param alias: title of the issue
        @type alias: C{str}
        """
        self.title = title


class GitHubRateLimitReached(Exception):
    pass


class GithubBackend(Backend):

    def __init__(self):
        self.url = Config.url
        self.delay = Config.delay
        self.backend_token = None
        self.backend_user = None
        self.backend_password = None
        self.users = {}

        if hasattr(Config, 'backend_token'):
            self.backend_token = Config.backend_token
        elif hasattr(Config, 'backend_user') and hasattr(Config, 'backend_password'):
            self.backend_user = Config.backend_user
            self.backend_password = Config.backend_password
        else:
            msg = "\n--backend-user and --backend-password or --backend-token" + \
                  " are mandatory to download bugs from Github\n"
            printerr(msg)
            sys.exit(1)

        self.newest_first = Config.newest_first
        self.remaining_ratelimit = 0

    def get_domain(self, url):
        strings = url.split('/')
        return strings[0] + "//" + strings[2] + "/"

    def analyze_bug(self, bug):
        #Retrieving main bug information

        printdbg(bug['url'] + " " + bug['state'] + " updated_at " +
                 bug['updated_at'] + ' (ratelimit = ' +
                 str(self.remaining_ratelimit) + ")")

        issue = bug['id']
        if bug['labels']:
            bug_type = bug['labels'][0]['name']   # FIXME
        else:
            bug_type = unicode('')
        summary = bug['title']
        desc = bug['body']
        submitted_by = self.__get_user(bug['user']['login'])

        submitted_on = self.__to_datetime(bug['created_at'])

        if bug['assignee']:
            assignee = self.__get_user(bug['assignee']['login'])
        else:
            assignee = People(unicode("nobody"))

        issue = GithubIssue(issue, bug_type, summary, desc, submitted_by,
                            submitted_on)
        issue.set_assigned(assignee)

        issue.set_status(bug['state'])
        issue.set_description(bug['body'])
        issue.set_web_link(bug['html_url'])

        try:
            if bug['closed_at']:
                issue.set_closed_at(self.__to_datetime(bug['closed_at']))
        except AttributeError:
            pass

        # updated_at offers ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ
        # MySQL doesn't support timezone, we remove it
        issue.set_updated_at(self.__to_datetime(bug['updated_at']))

        if bug['milestone']:
            issue.set_milestone_name(bug['milestone']['id'])
            issue.set_milestone_summary(bug['milestone']['description'])
            issue.set_milestone_title(bug['milestone']['title'])
            issue.set_milestone_web_link(bug['milestone']['url'])

        comments = self.__get_batch_comments(bug['number'])
        for c in comments:
            by = self.__get_user(c['user']['login'])
            date = self.__to_datetime(c['created_at'])
            com = Comment(c['body'], by, date)
            issue.add_comment(com)

        # activity
        entries = self.__get_batch_activities(bug['number'])
        for e in entries:
            field = e['event']
            added = e['commit_id']
            removed = unicode('')
            if e['actor']:
                by = self.__get_user(e['actor']['login'])
            else:
                by = People(u"nobody")
            ## by.setname() FIXME - to be done
            date = self.__to_datetime(e['created_at'])
            change = Change(field, removed, added, by, date)
            issue.add_change(change)

        return issue

    def __to_datetime(self, str):
        # converts str time to datetime
        # MySQL doesn't support timezone, we remove it

        return parse(str[:-1])

    def __set_request_auth(self, request):
        if self.backend_token:
            auth = "token %s" % self.backend_token
        else:
            base64string = base64.encodestring(
                '%s:%s' % (self.backend_user,
                           self.backend_password)).replace('\n', '')
            auth = "Basic %s" % base64string

        request.add_header("Authorization", auth)

    def __get_project_from_url(self):

        project_name = None
        url = self.url

        if url[-1] == '/':
            url = url[:-1]

        aux2 = url.rfind('/issues')
        aux1 = len('https://api.github.com/repos/')
        project_name = url[aux1:aux2]

        return project_name

    def __get_tracker_url_from_bug(self, bug):
        return bug['url'][:bug['url'].rfind('/')]

    def __fetch_data(self, url):
        request = urllib2.Request(url)
        self.__set_request_auth(request)

        try:
            result = urllib2.urlopen(request)
            content = result.read()
        except urllib2.HTTPError, e:
            if e.code == 403:
                raise GitHubRateLimitReached()
            printdbg("Error raised on %s" % url)
            raise e

        self.remaining_ratelimit = result.info()['x-ratelimit-remaining']

        return json.loads(content)

    def __get_user(self, username):
        if username in self.users:
            return self.users[username]

        url = "https://api.github.com/users/" + username
        raw_user = self.__fetch_data(url)

        user = People(username)

        if 'name' in raw_user:
            user.name = raw_user['name']
        if 'email' in raw_user:
            user.email = raw_user['email']

        self.users[username] = user

        return user

    def __get_batch_activities(self, bug_number):
        url = self.url + "/" + str(bug_number) + "/events"

        events = self.__fetch_data(url)

        return events

    def __get_batch_comments(self, bug_number):
        url = self.url + "/" + str(bug_number) + "/comments"

        comments = self.__fetch_data(url)

        return comments

    def __get_batch_bugs_state(self, state=ALL_STATES, since=None, direction='asc'):
        url = self.url + "?state=" + state + "&page=" + str(self.pagecont) \
            + "&per_page=100&sort=updated&direction=" + direction

        if since:
            url = url + "&since=" + str(since)

        printdbg(url)

        bugs = self.__fetch_data(url)

        return bugs

    def __get_batch_bugs(self):
        direction = 'asc'

        if self.newest_first:
            direction = 'desc'

        bugs = self.__get_batch_bugs_state(state=ALL_STATES,
                                           since=self.mod_date,
                                           direction=direction)
        return bugs

    def run(self):
        print("Running Bicho with delay of %s seconds" % (str(self.delay)))

        bugsdb = get_database(DBGithubBackend())

        url = self.url
        pname = None
        pname = self.__get_project_from_url()

        printdbg(url)

        bugsdb.insert_supported_traker("github", "v3")
        trk = Tracker(url, "github", "v3")
        dbtrk = bugsdb.insert_tracker(trk)

        self.bugs_state = ALL_STATES
        self.pagecont = 1
        self.mod_date = None

        aux_date = bugsdb.get_last_modification_date(tracker_id=dbtrk.id)

        if aux_date:
            self.mod_date = aux_date.isoformat()
            printdbg("Last issue already cached: %s" % self.mod_date)

        try:
            bugs = self.__get_batch_bugs()
        except GitHubRateLimitReached:
            printout("GitHub rate limit reached. To resume, wait some minutes.")
            sys.exit(0)

        nbugs = len(bugs)

        if len(bugs) == 0:
            if aux_date:
                printout("Bicho database up to date")
            else:
                printout("No bugs found. Did you provide the correct url?")
            sys.exit(0)

        auxcont = 0
        while len(bugs) > 0:

            for bug in bugs:
                try:
                    issue_data = self.analyze_bug(bug)
                except GitHubRateLimitReached:
                    printout("GitHub rate limit reached. To resume, wait some minutes.")
                    sys.exit(0)
                except Exception:
                    #FIXME it does not handle the e
                    msg = "Error in function analyzeBug with URL: %s and bug: %s" % (url, bug)
                    printerr(msg)
                    raise

                try:
                    # we can have meta-trackers but we want to have the
                    # original tracker name
                    tr_url = self.__get_tracker_url_from_bug(bug)
                    if (tr_url != url):
                        aux_trk = Tracker(tr_url, "github", "v3")
                        dbtrk = bugsdb.insert_tracker(aux_trk)
                    bugsdb.insert_issue(issue_data, dbtrk.id)
                except UnicodeEncodeError:
                    printerr(
                        "UnicodeEncodeError: the issue %s couldn't be stored"
                        % (issue_data.issue))
                except Exception, e:
                    printerr("ERROR: ")
                    print e

                printdbg ("Getting ticket number " + str(bug["number"]))
                time.sleep(self.delay)

            self.pagecont += 1

            try:
                bugs = self.__get_batch_bugs()
            except GitHubRateLimitReached:
                printout("GitHub rate limit reached. To resume, wait some minutes.")
                sys.exit(0)

            nbugs = nbugs + len(bugs)

        #end while

        printout("Done. %s bugs analyzed" % (nbugs))

Backend.register_backend("github", GithubBackend)
