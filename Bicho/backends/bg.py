# -*- coding: utf-8 -*-
# Copyright (C) 2007-2011 GSyC/LibreSoft, Universidad Rey Juan Carlos
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
# Authors: Daniel Izquierdo Cortazar <dizquierdo@gsyc.es>
#          Juan Francisco Gato Luis <jfcogato@libresoft.es>
#          Luis Cañas Díaz <lcanas@libresoft.es>
#          Santiago Dueñas <sduenas@libresoft.es>

import urllib
import string
import sys
import time

import urllib2
import cookielib

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import Comment as BFComment
from Bicho.backends import Backend
from Bicho.Config import Config
from Bicho.utils import printerr, printdbg, printout
from Bicho.common import Tracker, People, Issue, Comment, Change
from Bicho.db.database import DBIssue, DBBackend, get_database

from storm.locals import DateTime, Int, Reference, Unicode, Desc
import xml.sax.handler
#from xml.sax._exceptions import SAXParseException
from dateutil.parser import parse
from datetime import datetime

class DBBugzillaIssueExt(object):
    """
    """
    __storm_table__ = 'issues_ext_bugzilla'

    id = Int(primary=True)
    alias = Unicode()
    delta_ts = DateTime()
    reporter_accessible = Unicode()
    cclist_accessible = Unicode()
    classification_id = Unicode()
    classification = Unicode()
    product = Unicode()
    component = Unicode()
    version = Unicode()
    rep_platform = Unicode()
    op_sys = Unicode()
    dup_id = Int()
    bug_file_loc = Unicode()
    status_whiteboard = Unicode()
    target_milestone = Unicode()
    votes = Int()
    everconfirmed = Unicode()
    qa_contact = Unicode()
    estimated_time = Unicode()
    remaining_time = Unicode()
    actual_time = DateTime()
    deadline = DateTime()
    keywords = Unicode()
    cc = Unicode()
    group_bugzilla = Unicode()
    flag = Unicode()
    issue_id = Int()

    issue = Reference(issue_id, DBIssue.id)

    def __init__(self, issue_id):
        self.issue_id = issue_id


class DBBugzillaIssueExtMySQL(DBBugzillaIssueExt):
    """
    MySQL subclass of L{DBBugzillaIssueExt}
    """

    __sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_ext_bugzilla ( \
                     id INTEGER NOT NULL AUTO_INCREMENT, \
                     alias VARCHAR(32) default NULL, \
                     delta_ts DATETIME NOT NULL, \
                     reporter_accessible VARCHAR(32) default NULL, \
                     cclist_accessible VARCHAR(32) default NULL, \
                     classification_id VARCHAR(32) default NULL, \
                     classification VARCHAR(32) default NULL, \
                     product VARCHAR(32) default NULL, \
                     component VARCHAR(32) default NULL, \
                     version VARCHAR(32) default NULL, \
                     rep_platform VARCHAR(32) default NULL, \
                     op_sys VARCHAR(32) default NULL, \
                     dup_id INTEGER UNSIGNED default NULL, \
                     bug_file_loc VARCHAR(32) default NULL, \
                     status_whiteboard VARCHAR(32) default NULL, \
                     target_milestone VARCHAR(32) default NULL, \
                     votes INTEGER UNSIGNED default NULL, \
                     everconfirmed VARCHAR(32) default NULL, \
                     qa_contact VARCHAR(32) default NULL, \
                     estimated_time VARCHAR(32) default NULL, \
                     remaining_time VARCHAR(32) default NULL, \
                     actual_time DATETIME default NULL, \
                     deadline DATETIME default NULL, \
                     keywords VARCHAR(32) default NULL, \
                     flag VARCHAR(32) default NULL, \
                     cc VARCHAR(32) default NULL, \
                     group_bugzilla VARCHAR(32) default NULL, \
                     issue_id INTEGER NOT NULL, \
                     PRIMARY KEY(id), \
                     UNIQUE KEY(issue_id), \
                     INDEX ext_issue_idx(issue_id), \
                     FOREIGN KEY(issue_id) \
                       REFERENCES issues (id) \
                         ON DELETE CASCADE \
                         ON UPDATE CASCADE \
                     ) ENGINE=MYISAM;'


class DBBugzillaBackend(DBBackend):
    """
    Adapter for Bugzilla backend.
    """
    def __init__(self):
        self.MYSQL_EXT = [DBBugzillaIssueExtMySQL]

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

        newIssue = False;

        try:
            db_issue_ext = store.find(DBBugzillaIssueExt,
                                    DBBugzillaIssueExt.issue_id == issue_id).one()
            if not db_issue_ext:
                newIssue = True
                db_issue_ext = DBBugzillaIssueExt(issue_id)

            db_issue_ext.alias = self.__return_unicode(issue.alias)
            db_issue_ext.delta_ts = issue.delta_ts
            db_issue_ext.reporter_accessible = issue.reporter_accessible
            db_issue_ext.cclist_accessible = issue.cclist_accessible
            db_issue_ext.classification_id = issue.classification_id
            db_issue_ext.classification = self.__return_unicode(issue.classification)
            db_issue_ext.product = self.__return_unicode(issue.product)
            db_issue_ext.component = self.__return_unicode(issue.component)
            db_issue_ext.version = self.__return_unicode(issue.version)
            db_issue_ext.rep_platform = self.__return_unicode(issue.rep_platform)
            db_issue_ext.op_sys = self.__return_unicode(issue.op_sys)
            db_issue_ext.dup_id = issue.dup_id
            db_issue_ext.bug_file_loc = self.__return_unicode(issue.bug_file_loc)
            db_issue_ext.status_whiteboard = self.__return_unicode(issue.status_whiteboard)
            db_issue_ext.target_milestone = self.__return_unicode(issue.target_milestone)
            db_issue_ext.votes = self.__return_int(issue.votes)
            db_issue_ext.everconfirmed = self.__return_unicode(issue.everconfirmed)
            db_issue_ext.qa_contact = self.__return_unicode(issue.qa_contact)
            db_issue_ext.estimated_time = self.__return_unicode(issue.estimated_time)
            db_issue_ext.remaining_time = self.__return_unicode(issue.remaining_time)
            db_issue_ext.actual_time = self.__return_unicode(issue.actual_time)
            db_issue_ext.deadline = self.__return_unicode(issue.deadline)
            db_issue_ext.keywords = self.__return_unicode(issue.keywords)
            db_issue_ext.group = self.__return_unicode(issue.group)
            db_issue_ext.flag = self.__return_unicode(issue.flag)

            if newIssue == True:
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

    def get_last_modification_date(self, store):
        # get last modification date (day) stored in the database
        # select date_last_updated as date from issues_ext_bugzilla order by date
        result = store.find(DBBugzillaIssueExt)
        aux = result.order_by(Desc(DBBugzillaIssueExt.delta_ts))[:1]

        for entry in aux:
            return entry.delta_ts.strftime('%Y-%m-%d') 

        return None


class SoupHtmlParser():
    """
    Parses HTML to get 5 different fields from a table
    """

    field_map = {}
    status_map = {}
    resolution_map = {}

    def __init__ (self, html, idBug):
        self.html = html
        self.idBug = idBug
        self.field_map = {'Status': u'status', 'Resolution': u'resolution',}

    def sanityze_change(self, field, old_value, new_value):
        field = self.field_map.get(field, field)
        old_value = old_value.strip()
        new_value = new_value.strip()
        if field == 'status':
            old_value = self.status_map.get(old_value, old_value)
            new_value = self.status_map.get(new_value, new_value)
        elif field == 'resolution':
            old_value = self.resolution_map.get(old_value, old_value)
            new_value = self.resolution_map.get(new_value, new_value)

        return field, old_value, new_value

    def remove_comments(self, soup):
        cmts = soup.findAll(text=lambda text:isinstance(text, BFComment))
        [comment.extract() for comment in cmts]

    def _to_datetime_with_secs(self,str_date):
        """
        Returns datetime object from string
        """
        return parse(str_date).replace(tzinfo=None)

    def parse_changes(self):
        soup = BeautifulSoup(self.html)
        self.remove_comments(soup)
        remove_tags = ['a', 'span','i']
        changes = []
        tables = soup.findAll('table')

        # We look for the first table with 5 cols
        table = None
        for table in tables:
            if len(table.tr.findAll('th')) == 5:
                try:
                    for i in table.findAll(remove_tags):
                        i.replaceWith(i.contents[0])
                except:
                    printerr("error removing HTML tags")
                break

        if table is None:
            return changes

        rows = list(table.findAll('tr'))
        for row in rows[1:]:
            cols = list(row.findAll('td'))
            if len(cols) == 5:
                person_email = cols[0].contents[0].strip()
                person_email = unicode(person_email.replace('&#64;', '@'))
                date = self._to_datetime_with_secs(cols[1].contents[0].strip())
                field = unicode(cols[2].contents[0].strip())
                removed = unicode(cols[3].contents[0].strip())
                added = unicode(cols[4].contents[0].strip())
            else:
                field = cols[0].contents[0].strip()
                removed = cols[1].contents[0].strip()
                added = cols[2].contents[0].strip()

            field, removed, added = self.sanityze_change(field, removed, added)
            by = People(person_email)
            by.set_email(person_email)
            change = Change(field, removed, added, by, date)
            changes.append(change)

        return changes


class BugzillaIssue(Issue):
    """
    Ad-hoc Issue extension for bugzilla's issue
    """
    def __init__(self, issue, type, summary, desc, submitted_by, submitted_on):
        Issue.__init__(self, issue, type, summary, desc, submitted_by,
                       submitted_on)
        self.alias = None
        self.delta_ts = None
        self.reporter_accessible = None
        self.cclist_accessible = None
        self.classification_id = None
        self.classification = None
        self.product = None
        self.component = None
        self.version = None
        self.rep_platform = None
        self.op_sys = None
        self.dup_id = None
        self.bug_file_loc = None
        self.status_whiteboard = None
        self.target_milestone = None
        self.votes = None
        self.everconfirmed = None
        self.qa_contact = None
        self.estimated_time = None
        self.remaining_time = None
        self.actual_time = None
        self.deadline = None
        self.keywords = None
        self.group = None
        self.flag = None

    def set_alias(self, alias):
        """
        Set the alias of the issue

        @param alias: alias of the issue
        @type alias: C{str}
        """
        self.alias = alias

    def set_delta_ts(self, delta_ts):
        """
        Set the delta_ts of the issue

        @param delta_ts: of the issue
        @type delta_ts: L{datetime.datetime}
        """
        if not isinstance(delta_ts, datetime):
            raise ValueError('Parameter "delta_ts" should be a %s instance. %s given.' %
                             ('datetime', input.__class__.__name__))

        self.delta_ts = delta_ts

    def set_reporter_accessible(self, reporter_accessible):
        """
        Set the reporter_accesible of the issue

        @param  : of the issue
        @type  : C{str}
        """
        self.reporter_accessible = reporter_accessible

    def set_cclist_accessible(self, cclist_accessible):
        """
        Set the cclist_accessible of the issue

        @param cclist_accessible: of the issue
        @type cclist_accessible: C{str}
        """
        self.cclist_accessible = cclist_accessible

    def set_classification_id(self, classification_id):
        """
        Set the classification_id of the issue

        @param classification_id: of the issue
        @type classification_id: C{str}
        """
        self.classification_id = classification_id

    def set_classification(self, classification):
        """
        Set the classification of the issue

        @param classification: classification of the issue
        @type classification: C{str}
        """
        self.classification = classification

    def set_product(self, product):
        """
        Set the product of the issue

        @param product: product of the issue
        @type product: C{str}
        """
        self.product = product

    def set_component(self, component):
        """
        Set the component of the issue

        @param component: component of the issue
        @type component: C{str}
        """
        self.component = component

    def set_version(self, version):
        """
        Set the version of the issue

        @param version: version of the issue
        @type version: C{str}
        """
        self.version = version

    def set_rep_platform(self, rep_platform):
        """
        Set the rep_platform of the issue

        @param rep_platform: rep_platform of the issue
        @type rep_platform: C{str}
        """
        self.rep_platform = rep_platform

    def set_op_sys(self, op_sys):
        """
        Set the op_sys of the issue

        @param op_sys: op_sys of the issue
        @type op_sys: C{str}
        """
        self.op_sys = op_sys

    def set_dup_id(self, dup_id):
        """
        Set the dup_id of the issue

        @param dup_id: of the issue
        @type dup_id: C{str}
        """
        self.dup_id = dup_id

    def set_bug_file_loc(self, bug_file_loc):
        """
        Set the bug_file_loc of the issue

        @param bug_file_loc: of the issue
        @type bug_file_loc: C{str}
        """
        self.bug_file_loc = bug_file_loc

    def set_status_whiteboard(self, status_whiteboard):
        """
        Set the status_whiteboard of the issue

        @param status_whiteboard: status_whiteboard of the issue
        @type status_whiteboard: C{str}
        """
        self.status_whiteboard = status_whiteboard

    def set_target_milestone(self, target_milestone):
        """
        Set the target_milestone of the issue

        @param target_milestone: target_milestone of the issue
        @type target_milestone: C{str}
        """
        self.target_milestone = target_milestone

    def set_votes(self, votes):
        """
        Set the votes of the issue

        @param votes: votes of the issue
        @type votes: C{str}
        """
        self.votes = votes

    def set_everconfirmed(self, everconfirmed):
        """
        Set the everconfirmed of the issue

        @param everconfirmed: everconfirmed of the issue
        @type everconfirmed: C{str}
        """
        self.everconfirmed = everconfirmed

    def set_qa_contact(self, qa_contact):
        """
        Set the qa_contact of the issue

        @param qa_contact: qa_contact of the issue
        @type qa_contact: C{str}
        """
        self.qa_contact = qa_contact

    def set_estimated_time(self, estimated_time):
        """
        Set the estimated_time of the issue

        @param estimated_time: estimated_time of the issue
        @type estimated_time: C{str}
        """
        self.estimated_time = estimated_time

    def set_remaining_time(self, remaining_time):
        """
        Set the remaining_time of the issue

        @param remaining_time: remaining_time of the issue
        @type remaining_time: C{str}
        """
        self.remaining_time =  remaining_time

    def set_actual_time(self, actual_time):
        """
        Set the actual_time of the issue

        @param actual_time: actual_time of the issue
        @type actual_time: C{str}
        """
        self.actual_time =  actual_time

    def set_deadline(self, deadline):
        """
        Set the deadline of the issue

        @param deadline: deadline of the issue
        @type deadline: C{str}
        """
        self.deadline = deadline

    def set_keywords(self, keywords):
        """
        Set the keywords of the issue

        @param keywords: keywords of the issue
        @type keywords: C{str}
        """
        self.keywords = keywords

    def set_group(self, group):
        """
        Set the group of the issue

        @param group: group of the issue
        @type group: C{str}
        """
        self.group = group

    def set_flag(self, flag):
        """
        Set the flag of the issue

        @param flag: flag of the issue
        @type flag: C{str}
        """
        self.flag = flag


class BugsHandler(xml.sax.handler.ContentHandler):
    """
    Parses XML for each bug, the XML is using
    https://bugzilla.libresoft.es/bugzilla.dtd
    """


    # TBD get the bugzilla version number

    def __init__ (self):
        """
        """
        # TBD attachments and flag, see bugzilla.dtd

        self.atags = {
            "bug_id": None,
            "alias": None,
            "creation_ts":None,
            "short_desc": None,
            "delta_ts": None,
            "reporter_accessible": None,
            "cclist_accessible": None,
            "classification_id": None,
            "classification": None,
            "product": None,
            "component": None,
            "version": None,
            "rep_platform": None,
            "op_sys": None,
            "bug_status": None,
            "resolution": None,
            "dup_id": None,
            "bug_file_loc": None,
            "status_whiteboard": None,
            "priority": None,
            "bug_severity": None,
            "target_milestone": None,
            "votes": None,
            "everconfirmed": None,
            "reporter": None,
            "reporter_name": None, #attribute
            "assigned_to": None,
            "assigned_to_name": None, #attribute
            "qa_contact": None,
            "estimated_time": None,
            "remaining_time": None,
            "actual_time": None,
            "deadline": None }

        self.btags = {
            "keywords": [],
            "dependson": [],
            "blocked": [],
            "cc": [],
            "group": [],
            "flag": []}

        self.ctags = {
            "long_desc": [],
            "attachment": []}

        self.long_desc_tags = {
            "who": None,
            "who_name": None, #attribute
            "bug_when": None,
            "work_time": None,
            "thetext": None}

        self.attachment_tags = {
            "attachid": None,
            "date": None,
            "desc": None,
            "filename": None,
            "type": None,
            "size": None,
            "data": None,
            "flag": []}

        self.interestData = []
        self.tag_name = None

    def startElement(self, name, attrs):
        """
        It is called every time a start tag is detected.
        """
        if self.atags.has_key( name ) or self.btags.has_key( name ) \
                or self.long_desc_tags.has_key( name ):
            self.tag_name = name
            self.interestData = []

        for attrName in attrs.keys():
            if self.tag_name == "reporter":
                self.atags["reporter_name"] = unicode(attrs.get(attrName))
            elif self.tag_name == "assigned_to":
                self.atags["assigned_to_name"] = unicode(attrs.get(attrName))
            elif self.tag_name == "who":
                self.long_desc_tags["who_name"] = unicode(attrs.get(attrName))

    def characters (self, chrs):
        if self.tag_name:
            self.interestData.append(chrs)

    def _init_long_desc_tags(self):
        """
        Initializes the directory long_desc_tags
        """
        for item in self.long_desc_tags:
            self.long_desc_tags[item] = None

    def _copy_long_desc_tags(self):
        """
        Returns a copy of the dictionary long_desc_tags
        """
        aux = {}
        for item in self.long_desc_tags:
            aux[item] = self.long_desc_tags[item]
        return aux

    def endElement(self, name):
        if self.atags.has_key( name ):
            aux = string.join(self.interestData)
            if not self.atags[name]:
                #delta_ts could be overwritten by delta_ts of attachment
                self.atags[name] = unicode(aux)
            self.tag_name = None
        elif self.long_desc_tags.has_key( name ):
            aux = string.join(self.interestData)
            self.long_desc_tags[name] = unicode(aux)
            self.tag_name = None
        elif self.btags.has_key( name ):
            aux = string.join(self.interestData)
            self.btags[name].append(unicode(aux))
            self.tag_name = None
        elif self.ctags.has_key( name ):
            if name == 'long_desc':
                aux = self._copy_long_desc_tags()
                self.ctags['long_desc'].append(aux)
                self._init_long_desc_tags()
            elif name == 'attachment':
                pass
            self.tag_name = None

        else:
            printdbg( "unknown tag:" + name)


    def print_debug_data(self):
        printdbg("")
        printdbg("ID: " +  self.bug_id)
        printdbg("Creation date: " + self.creation_ts)
        printdbg("Short description: " + self.short_desc)
        printdbg("Status: " + self.bug_status)
        printdbg("Priority: " + self.priority)
        printdbg("Resolution: " + self.resolution)
        printdbg("Reporter: " + self.reporter)
        printdbg("Assigned To: " + self.assigned_to)
        printdbg("Delta_ts: " + self.delta_ts)
        printdbg("")

    def _get_raw_comments(self):
        """
        Returns long description comments from 2nd to last one if the bug has
        comments. Empty list in any other case
        """
        if len(self.ctags["long_desc"]) > 1 :
            return self.ctags["long_desc"][1:]
        else:
            return []

    def _convert_to_datetime(self,str_date):
        """
        Returns datetime object from string
        """
        return parse(str_date).replace(tzinfo=None)

    def _to_datetime_with_secs(self,str_date):
        """
        Returns datetime object from string with seconds
        """
        return parse(str_date).replace(tzinfo=None)


    def get_issue(self):
        issue_id = self.atags["bug_id"]
        type  = self.atags["bug_severity"]
        summary = self.atags["short_desc"]
        desc = self.ctags["long_desc"][0]["thetext"]
        submitted_by = People(self.atags["reporter"])
        submitted_by.set_name(self.atags["reporter_name"])
        submitted_by.set_email(self.atags["reporter"])
        submitted_on = self._convert_to_datetime(self.atags["creation_ts"])

        # FIXME: I miss resolution and priority
        issue = BugzillaIssue(issue_id, type, summary, desc, submitted_by,
                              submitted_on)
        issue.set_priority(self.atags["priority"])
        issue.set_status(self.atags["bug_status"])

        assigned_to = People(self.atags["assigned_to"])
        assigned_to.set_name(self.atags["assigned_to_name"])
        assigned_to.set_email(self.atags["assigned_to"])
        issue.set_assigned(assigned_to)

        # FIXME = I miss the number of comment and the work_time (useful in
        # bugzillas)

        # date must be also a datetime
        for rc in self._get_raw_comments():
            if rc["bug_when"]:
                by = People(rc["who"])
                by.set_name(rc["who_name"])
                by.set_email(rc["who"])
                com = Comment(rc["thetext"], by, self._to_datetime_with_secs(rc["bug_when"]))
                issue.add_comment(com)
            else:
                #FIXME bug_when empty
                printdbg("ERROR - Comment")

        # FIXME TBD: Attachment is not supported so far
        ## at = Attachment
        #issue.add_attachment()

        # FIXME TBD: Relations
        # fields in btags: dependson, blocked
        # issue.add_relationship() # issue_id, type

        issue.set_resolution(self.atags["resolution"])

        issue.set_alias(self.atags["alias"])
        issue.set_delta_ts(self._to_datetime_with_secs(self.atags["delta_ts"]))
        issue.set_reporter_accessible(self.atags["reporter_accessible"])
        issue.set_cclist_accessible(self.atags["cclist_accessible"])
        issue.set_classification_id(self.atags["classification_id"])
        issue.set_classification(self.atags["classification"])
        issue.set_product(self.atags["product"])
        issue.set_component(self.atags["component"])
        issue.set_version(self.atags["version"])
        issue.set_rep_platform(self.atags["rep_platform"])
        issue.set_op_sys(self.atags["op_sys"])
        if self.atags["dup_id"]:
            issue.set_dup_id(int(self.atags["dup_id"]))
        issue.set_bug_file_loc(self.atags["bug_file_loc"])
        issue.set_status_whiteboard(self.atags["status_whiteboard"])
        issue.set_target_milestone(self.atags["target_milestone"])
        issue.set_votes(self.atags["votes"])
        issue.set_everconfirmed(self.atags["everconfirmed"])
        issue.set_qa_contact(self.atags["qa_contact"])
        issue.set_estimated_time(self.atags["estimated_time"])
        issue.set_remaining_time(self.atags["remaining_time"])
        issue.set_actual_time(self.atags["actual_time"])
        if self.atags["deadline"]:
            issue.set_deadline(self.atags["deadline"])
        issue.set_keywords(self.btags["keywords"])
        # we also store the list of watchers/CC
        for w in self.btags["cc"]:
            auxp = People(w)
            issue.add_watcher(auxp)
        issue.set_group(self.btags["group"])
        issue.set_flag(self.btags["flag"])

        return issue


class DBIssueBugzilla(object):
    """
    """
    __storm_table__ = 'issues_extra'

    id = Int(primary=True)
    alias = Unicode()
    delta_ts = DateTime()
    reporter_accessible = Unicode()
    cclist_accessible = Unicode()
    classification_id = Unicode()
    classification = Unicode()
    product = Unicode()
    component = Unicode()
    version = Unicode()
    rep_platform = Unicode()
    op_sys = Unicode()
    dup_id = Int()
    bug_file_loc = Unicode()
    status_whiteboard = Unicode()
    target_milestone = Unicode()
    votes = Int()
    everconfirmed = Unicode()
    qa_contact = Unicode()
    estimated_time = Unicode()
    remaining_time = Unicode()
    actual_time = DateTime()
    deadline = Unicode()
    keywords = Unicode()
    cc = Unicode()
    group = Unicode()
    flag = Unicode()
    issue_id = Int()

    issue = Reference(issue_id, DBIssue.id)

    def __init__(self, issue_id):
        self.issue_id = issue_id

class BGBackend (Backend):

    def __init__ (self):
        self.url = Config.url
        self.delay = Config.delay
        self.cookies = {}
        try:
            self.backend_password = Config.backend_password
            self.backend_user = Config.backend_user
        except AttributeError:
            printout("No bugzilla account provided, mail addresses won't " +\
                     "be retrieved")
            self.backend_password = None
            self.backend_user = None

    def get_domain(self, url):
        strings = url.split('/')
        return strings[0] + "//" + strings[2] + "/"

    def analyze_bug(self, bug_id, url):
        #Retrieving main bug information
        bug_url = url + "show_bug.cgi?id=" + bug_id + "&ctype=xml"
        printdbg(bug_url)

        handler = BugsHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)

        

        ## In [43]: opener = urllib2.build_opener()
        ## In [44]: opener.addheaders.append(('Cookie', 'Bugzilla_login=27'))
        ## In [45]: opener.addheaders.append(('Cookie', 'Bugzilla_logincookie=WBizdtDFtv'))
        ##
        ## In [46]: response=urllib2.urlopen('https://bugzilla.libresoft.es/show_bug.cgi?ctype=xml&id=298')

        if self.__auth_session():
            opener = urllib2.build_opener()
            for c in self.cookies:
                key = str(c)
                value = self.cookies[c]
                aux = key + '=' + value
                opener.addheaders.append(('Cookie', aux))
            f = urllib2.urlopen(bug_url)
        else:
            f = urllib.urlopen(bug_url)

        try:
            parser.feed(f.read())
        except Exception:
            printerr("Error parsing URL: %s" % (bug_url))
            raise

        f.close()
        parser.close()
        #handler.print_debug_data()
        issue = handler.get_issue()
        printdbg(" updated at " + issue.delta_ts.isoformat())

        #Retrieving changes
        bug_activity_url = url + "show_activity.cgi?id=" + bug_id
        printdbg( bug_activity_url )
        data_activity = urllib.urlopen(bug_activity_url).read()
        parser = SoupHtmlParser(data_activity, bug_id)
        try:
            changes = parser.parse_changes()
            for c in changes:
                issue.add_change(c)
        except Exception, e:
            printerr("error while parsing HTML")
        return issue

    def __auth_session(self):
        # returns True if the session is authenticated
        if len(self.cookies) > 0:
            return True
        else:
            return False

    def __login(self):

        cookie_j = cookielib.CookieJar()
        cookie_h = urllib2.HTTPCookieProcessor(cookie_j)
        
        to_aux = self.url.rfind('buglist')
        url = self.url[:to_aux] + 'index.cgi'

        values = {'Bugzilla_login': self.backend_user,
                  'Bugzilla_password': self.backend_password}
        opener = urllib2.build_opener(cookie_h)
        urllib2.install_opener(opener)
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        for n,c in enumerate(cookie_j):
            self.cookies[c.name] = c.value

        print self.cookies
        #sys.exit(1)

        ## In [43]: opener = urllib2.build_opener()
        ## In [44]: opener.addheaders.append(('Cookie', 'Bugzilla_login=27'))
        ## In [45]: opener.addheaders.append(('Cookie', 'Bugzilla_logincookie=WBizdtDFtv'))
        ##
        ## In [46]: response=urllib2.urlopen('https://bugzilla.libresoft.es/show_bug.cgi?ctype=xml&id=298')
        

    def run (self):
        print("Running Bicho with delay of %s seconds" % (str(self.delay)))
        #retrieving data in csv format

        bugsdb = get_database (DBBugzillaBackend())

        if self.backend_user and self.backend_password:
            self.__login()

        url = self.url + "&order=changeddate&ctype=csv"

        printdbg(url)

        #The url is a bug            
        if url.find("show_bug.cgi")>0:
            bugs = []
            bugs.append(self.url.split("show_bug.cgi?id=")[1])

        else:

            last_mod_date = bugsdb.get_last_modification_date()

            if last_mod_date:
                url = url + "&chfieldfrom=" + last_mod_date
                printdbg("Last bugs cached were modified on: %s" % last_mod_date)
            f = urllib.urlopen(url)

            #Problems using csv library, not all the fields are delimited by
            # '"' character. Easier using split.
            bugList_csv = f.read().split('\n')

            #&chfieldfrom=2012-06-01

            
            bugs = []
            #Ignoring first row
            for bug_csv in bugList_csv[1:]:
                #First field is the id field, necessary to later create the url
                #to retrieve bug information
                bugs.append(bug_csv.split(',')[0])

        nbugs = len(bugs)
        
        url = self.url
        url = self.get_domain(url)
        if url.find("apache")>0:
            url =  url + "bugzilla/"
            
        # still useless
        bugsdb.insert_supported_traker("bugzilla", "3.2.3")
        trk = Tracker ( url, "bugzilla", "3.2.3")

        dbtrk = bugsdb.insert_tracker(trk)

        if nbugs == 0:
            printout("No bugs found. Did you provide the correct url?")
            sys.exit(0)

        for bug in bugs:

            #The URL from bugzilla (so far KDE and GNOME) are like:
            #http://<domain>/show_bug.cgi?id=<bugid>&ctype=xml

            try:
                issue_data = self.analyze_bug(bug, url)
            except Exception:
                #FIXME it does not handle the e
                printerr("Error in function analyzeBug with URL: %s and Bug: %s"
                         % (url,bug))
                #print e
                #continue
                raise

            try:
                bugsdb.insert_issue(issue_data, dbtrk.id)
            except UnicodeEncodeError:
                printerr("UnicodeEncodeError: the issue %s couldn't be stored"
                      % (issue_data.issue))

            time.sleep(self.delay)

        printout("Done. %s bugs analyzed" % (nbugs))

Backend.register_backend ("bg", BGBackend)
