# -*- coding: utf-8 -*-
# Copyright (C) 2007-2012 GSyC/LibreSoft, Universidad Rey Juan Carlos
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
# Authors: Luis Cañas Díaz <lcanas@bitergia.com>
#
#

import cookielib
import pprint
import string
import sys
import time
import urllib
import urllib2
import traceback

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import Comment as BFComment
from Bicho.backends import Backend
from Bicho.backends.bg import DBBugzillaIssueExt
from Bicho.backends.jira import DBJiraIssueExt
from Bicho.Config import Config
from Bicho.utils import printerr, printdbg, printout
from Bicho.common import Tracker, People, Issue, Comment, Change
from Bicho.db.database import DBIssue, DBBackend, get_database, DBTracker, \
     DBPeople, DBChange

from storm.locals import DateTime, Int, Reference, Unicode, Desc, Asc, Store, \
     create_database
from storm.expr import Or, And
import xml.sax.handler

from dateutil.parser import parse
from datetime import datetime

from Bicho.Config import Config

__sql_table_bugzilla__ = 'CREATE TABLE IF NOT EXISTS issues_log_bugzilla ( \
                     id INTEGER NOT NULL AUTO_INCREMENT, \
                     tracker_id INTEGER NOT NULL, \
                     issue_id INTEGER NOT NULL, \
                     issue VARCHAR(255) NOT NULL, \
                     type VARCHAR(32) NULL, \
                     summary VARCHAR(255) NOT NULL, \
                     description TEXT NOT NULL, \
                     status VARCHAR(32) NOT NULL, \
                     resolution VARCHAR(32) NULL, \
                     priority VARCHAR(32) NULL, \
                     submitted_by INTEGER UNSIGNED NOT NULL, \
                     date DATETIME NOT NULL, \
                     assigned_to INTEGER UNSIGNED NOT NULL, \
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
                     actual_time VARCHAR(32) default NULL, \
                     deadline DATETIME default NULL, \
                     keywords VARCHAR(32) default NULL, \
                     flag VARCHAR(32) default NULL, \
                     cc VARCHAR(32) default NULL, \
                     group_bugzilla VARCHAR(32) default NULL, \
                     PRIMARY KEY(id), \
                     UNIQUE KEY(id), \
                     INDEX issues_submitted_idx(submitted_by), \
                     INDEX issues_assigned_idx(assigned_to), \
                     INDEX issues_tracker_idx(tracker_id), \
                     FOREIGN KEY(submitted_by) \
                       REFERENCES people(id) \
                         ON DELETE SET NULL \
                         ON UPDATE CASCADE, \
                     FOREIGN KEY(assigned_to) \
                       REFERENCES people(id) \
                         ON DELETE SET NULL \
                         ON UPDATE CASCADE, \
                     FOREIGN KEY(tracker_id) \
                       REFERENCES trackers(id) \
                         ON DELETE CASCADE \
                         ON UPDATE CASCADE \
                     ) ENGINE=MYISAM;'

__sql_table_jira__ = 'CREATE TABLE IF NOT EXISTS issues_log_jira ( \
                     id INTEGER NOT NULL AUTO_INCREMENT, \
                     tracker_id INTEGER NOT NULL, \
                     issue_id INTEGER NOT NULL, \
                     issue VARCHAR(255) NOT NULL, \
                     type VARCHAR(32) NULL, \
                     summary VARCHAR(255) NOT NULL, \
                     description TEXT NOT NULL, \
                     status VARCHAR(32) NOT NULL, \
                     resolution VARCHAR(32) NULL, \
                     priority VARCHAR(32) NULL, \
                     submitted_by INTEGER UNSIGNED NOT NULL, \
                     date DATETIME NOT NULL, \
                     assigned_to INTEGER UNSIGNED NOT NULL, \
                     issue_key VARCHAR(32) NOT NULL, \
                     link VARCHAR(100) NOT NULL, \
                     title VARCHAR(100) NOT NULL, \
                     environment VARCHAR(35) NOT NULL, \
                     security VARCHAR(35) NOT NULL, \
                     updated DATETIME NOT NULL, \
                     version VARCHAR(35) NOT NULL, \
                     component VARCHAR(35) NOT NULL, \
                     votes INTEGER UNSIGNED, \
                     project VARCHAR(35) NOT NULL, \
                     project_id INTEGER UNSIGNED, \
                     project_key VARCHAR(35) NOT NULL, \
                     PRIMARY KEY(id), \
                     UNIQUE KEY(id), \
                     INDEX issues_submitted_idx(submitted_by), \
                     INDEX issues_assigned_idx(assigned_to), \
                     INDEX issues_tracker_idx(tracker_id), \
                     FOREIGN KEY(submitted_by) \
                       REFERENCES people(id) \
                         ON DELETE SET NULL \
                         ON UPDATE CASCADE, \
                     FOREIGN KEY(assigned_to) \
                       REFERENCES people(id) \
                         ON DELETE SET NULL \
                         ON UPDATE CASCADE, \
                     FOREIGN KEY(tracker_id) \
                       REFERENCES trackers(id) \
                         ON DELETE CASCADE \
                         ON UPDATE CASCADE \
                     ) ENGINE=MYISAM;'


#
# these dictionaries contain the text that appears in the HTML history
# table for bugzilla and its equivalent in the database
#

bg_issues_links = {
    "Summary": "summary",
    "Priority": "priority",
    "Assignee": "assigned_to",
    "status": "status",
    "resolution": "resolution",
    "Severity": "type",
    "Alias": "alias",
    "Reporter accessible": "reporter_accessible",
    "CC list accessible": "cclist_accessible",
    #"":"classification_id",
    #"":"classification",
    "Product": "product",
    "Component": "component",
    "Version": "version",
    "Hardware": "rep_platform",
    "OS": "op_sys",
    #"":"dup_id",
    "URL": "bug_file_loc",
    "Whiteboard": "status_whiteboard",
    "Target Milestone": "target_milestone",
    "Votes": "votes",
    "Ever confirmed": "everconfirmed",
    "QA Contact": "qa_contact",
    #"":"estimated_time",
    #"":"remaining_time",
    #"":"actual_time",
    #"":"deadline",
    "Keywords": "keywords",
    #"":"flag",
    #"":"group_bugzilla",
    "CC": "cc"}

jira_issues_links = {
    "Link": "link",
    "Summary": "summary",
    "Priority": "priority",
    "Resolution": "resolution",
    "Status": "status",
    "Assignee": "assigned_to",
    "Fix Version/s": "version",
    #"Comment": "",
    #"Attachment": "",
    "Environment": "environment",
    "Component/s": "component",
    "Issue Type": "type",
    "Description": "description",
    "Security": "security"}


class DBIssuesLog(object):
    """
    """
    #__storm_table__ = 'issues_log_bugzilla'
    id = Int(primary=True)
    #
    issue_id = Int()
    issue = Unicode()
    type = Unicode()
    summary = Unicode()
    description = Unicode()
    status = Unicode()
    resolution = Unicode()
    priority = Unicode()
    submitted_by = Int()
    date = DateTime()
    assigned_to = Int()
    tracker_id = Int()
    #

    tracker = Reference(tracker_id, DBTracker.id)
    submitted = Reference(submitted_by, DBPeople.id)
    assigned = Reference(assigned_to, DBPeople.id)

    def __init__(self, issue, tracker_id):
        self.issue = unicode(issue)
        self.tracker_id = tracker_id


class DBBugzillaIssuesLog(DBIssuesLog):
    """
    """
    __storm_table__ = 'issues_log_bugzilla'
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
    actual_time = Unicode()
    deadline = DateTime()
    keywords = Unicode()
    cc = Unicode()
    group_bugzilla = Unicode()
    flag = Unicode()
    issue_id = Int()


class DBJiraIssuesLog(DBIssuesLog):
    """
    """
    __storm_table__ = 'issues_log_jira'
    issue_key = Unicode()
    link = Unicode()
    environment = Unicode()
    security = Unicode()
    updated = DateTime()
    version = Unicode()
    component = Unicode()
    votes = Int()
    project = Unicode()
    project_id = Int
    project_key = Unicode()


class IssuesLog():

    def __init__(self, backend_name):
        self.backend_name = backend_name
        self.connect()
        self.create_db()

    def connect(self):
        opts = Config()

        self.database = create_database('mysql://' + opts.db_user_out + ':'
                                        + opts.db_password_out + '@'
                                        + opts.db_hostname_out + ':'
                                        + opts.db_port_out + '/'
                                        + opts.db_database_out)
        self.store = Store(self.database)

    def create_db(self):
        print("self.backend_name = %s" % (self.backend_name))
        if self.backend_is_bugzilla():
            self.store.execute(__sql_table_bugzilla__)
        elif self.backend_is_jira():
            self.store.execute(__sql_table_jira__)

    def copy_issue(self, db_ilog):
        """
        This method creates a copy of DBBugzilla/JiraIssuesLog object
        """

        if self.backend_is_bugzilla():
            aux = DBBugzillaIssuesLog(db_ilog.issue, db_ilog.tracker_id)
            aux.issue_id = db_ilog.issue_id
            aux.type = db_ilog.type
            aux.summary = db_ilog.summary
            aux.description = db_ilog.description
            aux.status = db_ilog.status
            aux.resolution = db_ilog.resolution
            aux.priority = db_ilog.priority
            aux.submitted_by = db_ilog.submitted_by
            aux.date = db_ilog.date
            aux.assigned_to = db_ilog.assigned_to

            #aux = DBBugzillaIssuesLog (db_ilog.issue_id)
            aux.alias = db_ilog.alias
            aux.delta_ts = db_ilog.delta_ts
            aux.reporter_accessible = db_ilog.reporter_accessible
            aux.cclist_accessible = db_ilog.cclist_accessible
            aux.classification_id = db_ilog.classification_id
            aux.classification = db_ilog.classification
            aux.product = db_ilog.product
            aux.component = db_ilog.component
            aux.version = db_ilog.version
            aux.rep_platform = db_ilog.rep_platform
            aux.op_sys = db_ilog.op_sys
            aux.dup_id = db_ilog.dup_id
            aux.bug_file_loc = db_ilog.bug_file_loc
            aux.status_whiteboard = db_ilog.status_whiteboard
            aux.target_milestone = db_ilog.target_milestone
            aux.votes = db_ilog.votes
            aux.everconfirmed = db_ilog.everconfirmed
            aux.qa_contact = db_ilog.qa_contact
            aux.estimated_time = db_ilog.estimated_time
            aux.remaining_time = db_ilog.remaining_time
            aux.actual_time = db_ilog.actual_time
            aux.deadline = db_ilog.deadline
            aux.keywords = db_ilog.keywords
            aux.cc = db_ilog.cc
            aux.group_bugzilla = db_ilog.group_bugzilla
            aux.flag = db_ilog.flag
            return aux

        elif self.backend_is_jira():
            aux = DBJiraIssuesLog(db_ilog.issue, db_ilog.tracker_id)
            aux.issue_id = db_ilog.issue_id
            aux.type = db_ilog.type
            aux.summary = db_ilog.summary
            aux.description = db_ilog.description
            aux.status = db_ilog.status
            aux.resolution = db_ilog.resolution
            aux.priority = db_ilog.priority
            aux.submitted_by = db_ilog.submitted_by
            aux.date = db_ilog.date
            aux.assigned_to = db_ilog.assigned_to

            aux.link = db_ilog.link
            aux.component = db_ilog.component
            aux.version = db_ilog.version
            aux.issue_key = db_ilog.issue_key
            aux.environment = db_ilog.environment
            aux.project = db_ilog.project
            aux.project_key = db_ilog.project_key
            aux.security = db_ilog.security

            return aux

    def get_people_id(self, email, tracker_id):
        """
        Gets the id of an user
        """
        p = self.store.find(DBPeople, DBPeople.email == email).one()
        ##
        ## the code below was created ad-hoc for KDE solid
        ##
        try:
            return p.id
        except AttributeError:
            p = self.store.find(DBPeople, DBPeople.user_id == email).one()
            try:
                return p.id
            except AttributeError:
                # no person was found in People with the email above, so
                # we include it
                printdbg("Person not found. Inserted with email %s " % (email))
                dp = DBPeople(email, tracker_id)
                self.store.add(dp)
                self.store.commit()
                return dp.id

    def get_last_change_date(self):
        """
        This method gets the date of the last change included in the log table
        """
        if self.backend_is_bugzilla():
            result = self.store.find(DBBugzillaIssuesLog)
            aux = result.order_by(Desc(DBBugzillaIssuesLog.date))[:1]
            for entry in aux:
                return entry.date
        elif self.backend_is_jira():
            result = self.store.find(DBJiraIssuesLog)
            aux = result.order_by(Desc(DBJiraIssuesLog.date))[:1]
            for entry in aux:
                return entry.date
        return None

    def get_issues_changed_since(self, date):
        """
        This method fetchs the issues changes since date
        """

        #SELECT DISTINCT(issues.id) FROM issues, changes
        #WHERE issues.id = changes.issue_id
        #AND (issues.submitted_on >= '2012-02-28 12:34:44'
        #    OR changes.changed_on >= '2012-02-28 12:34:44');

        result = self.store.find(DBIssue,
                                 DBChange.issue_id == DBIssue.id,
                                 Or(DBIssue.submitted_on > date,
                                    DBChange.changed_on > date )).group_by(DBIssue.id)

        return result

    def get_previous_state(self, issue_id):
        """
        This method returns a db_ilog object with the last row found in
        the log table
        """
        db_ilog = None
        if self.backend_is_jira():
            rows = self.store.find(DBJiraIssuesLog,
                                   DBJiraIssuesLog.issue_id==issue_id)
            lrow = rows.order_by(Desc(DBJiraIssuesLog.id))[:1]
            for aux in lrow:  # FIXME it only contains an element!
                db_ilog = DBJiraIssuesLog(aux.issue, aux.tracker_id)
                db_ilog.issue_id = aux.issue_id
                db_ilog.type = aux.type
                db_ilog.summary = aux.summary
                db_ilog.description = aux.description
                db_ilog.status = aux.status
                db_ilog.resolution = aux.resolution
                db_ilog.priority = aux.priority
                db_ilog.submitted_by = aux.submitted_by
                db_ilog.date = aux.date
                db_ilog.assigned_to = aux.assigned_to
                db_ilog.issue_key = aux.issue_key
                db_ilog.link = aux.link
                db_ilog.environment = aux.environment
                db_ilog.security = aux.security
                db_ilog.updated = aux.updated
                db_ilog.version = aux.version
                db_ilog.component = aux.component
                db_ilog.votes = aux.votes
                db_ilog.project = aux.project
                db_ilog.project_id = aux.project_id
                db_ilog.project_key = aux.project_key
        else:  # elif self.backend_is_bugzilla():
            rows = self.store.find(DBBugzillaIssuesLog,
                                   DBBugzillaIssuesLog.issue_id==issue_id)
            lrow = rows.order_by(Desc(DBBugzillaIssuesLog.id))[:1]
            for aux in lrow:  # FIXME it only contains an element!
                db_ilog = DBBugzillaIssuesLog(aux.issue, aux.tracker_id)
                db_ilog.issue_id = aux.issue_id
                db_ilog.type = aux.type
                db_ilog.summary = aux.summary
                db_ilog.description = aux.description
                db_ilog.status = aux.status
                db_ilog.resolution = aux.resolution
                db_ilog.priority = aux.priority
                db_ilog.submitted_by = aux.submitted_by
                db_ilog.date = aux.date
                db_ilog.assigned_to = aux.assigned_to
                db_ilog.alias = aux.alias
                db_ilog.delta_ts = aux.delta_ts
                db_ilog.reporter_accessible = aux.reporter_accessible
                db_ilog.cclist_accessible = aux.cclist_accessible
                db_ilog.classification_id = aux.classification_id
                db_ilog.classification = aux.classification
                db_ilog.product = aux.product
                db_ilog.component = aux.component
                db_ilog.version = aux.version
                db_ilog.rep_platform = aux.rep_platform
                db_ilog.op_sys = aux.op_sys
                db_ilog.dup_id = aux.dup_id
                db_ilog.bug_file_loc = aux.bug_file_loc
                db_ilog.status_whiteboard = aux.status_whiteboard
                db_ilog.target_milestone = aux.target_milestone
                db_ilog.votes = aux.votes
                db_ilog.everconfirmed = aux.everconfirmed
                db_ilog.qa_contact = aux.qa_contact
                db_ilog.estimated_time = aux.estimated_time
                db_ilog.remaining_time = aux.remaining_time
                db_ilog.actual_time = aux.actual_time
                db_ilog.deadline = aux.deadline
                db_ilog.keywords = aux.keywords
                db_ilog.cc = aux.cc
                db_ilog.group_bugzilla = aux.group_bugzilla
                db_ilog.flag = aux.flag

        return db_ilog

    def issue_is_new(self, issue_id):
        """
        This method returns True if the issue is not logged in the log table
        """
        if self.backend_is_jira():
            result = self.store.find(DBJiraIssuesLog,
                                     DBJiraIssuesLog.issue_id == issue_id)
        elif self.backend_is_bugzilla():
            result = self.store.find(DBBugzillaIssuesLog,
                                     DBBugzillaIssuesLog.issue_id == issue_id)
        return (result.count() == 0)

    def build_initial_state(self, db_ilog):
        """
        This method gets the first changes of every field in
        order to get the initial state of the bug
        """
        fields = self.store.execute("SELECT DISTINCT(field) FROM changes\
        where issue_id=%s" % (db_ilog.issue_id))

        for f in fields:
            value = self.store.execute("SELECT old_value FROM changes \
            WHERE issue_id=%s AND field=\"%s\" ORDER BY changed_on LIMIT 1"
                                  % (db_ilog.issue_id, f[0]))
            for v in value:
                if self.backend_is_bugzilla():
                    # Bugzilla section
                    #
                    if f[0] in bg_issues_links:
                        table_field = bg_issues_links[f[0]]
                        if table_field == 'summary':
                            db_ilog.summary = v[0]
                        elif table_field == 'priority':
                            db_ilog.priority = v[0]
                        elif table_field == 'type':
                            db_ilog.type = v[0]
                        elif table_field == 'assigned_to':
                            db_ilog.assigned_to = self.get_people_id(
                                v[0], self.get_tracker_id(db_ilog.issue_id))
                        elif table_field == 'status':
                            db_ilog.status = v[0]
                        elif table_field == 'resolution':
                            db_ilog.resolution = v[0]
                        elif table_field == 'alias':
                            db_ilog.alias = v[0]
                        elif table_field == 'reporter_accessible':
                            db_ilog.reporter_accessible = v[0]
                        elif table_field == 'cclist_accessible':
                            db_ilog.cclist_accessible = v[0]
                        elif table_field == 'product':
                            db_ilog.product = v[0]
                        elif table_field == 'component':
                            db_ilog.component = v[0]
                        elif table_field == 'version':
                            db_ilog.version = v[0]
                        elif table_field == 'rep_platform':
                            db_ilog.rep_platform = v[0]
                        elif table_field == 'op_sys':
                            db_ilog.op_sys = v[0]
                        elif table_field == 'bug_file_loc':
                            db_ilog.bug_file_loc = v[0]
                        elif table_field == 'status_whiteboard':
                            db_ilog.status_whiteboard = v[0]
                        elif table_field == 'target_milestone':
                            db_ilog.target_milestone = v[0]
                        elif table_field == 'votes':
                            db_ilog.votes = v[0]
                        elif table_field == 'everconfirmed':
                            db_ilog.everconfirmed = v[0]
                        elif table_field == 'qa_contact':
                            db_ilog.qa_contact = v[0]
                        elif table_field == 'keywords':
                            db_ilog.Keywords = v[0]
                        elif table_field == 'cc':
                            db_ilog.cc = v[0]
                if self.backend_is_jira():
                    # Jira section
                    #
                    if f[0] in jira_issues_links:
                        table_field = jira_issues_links[f[0]]
                        if table_field == 'summary':
                            db_ilog.summary = v[0]
                        elif table_field == 'priority':
                            db_ilog.priority = v[0]
                        elif table_field == 'type':
                            db_ilog.type = v[0]
                        elif table_field == 'assigned_to':
                            db_ilog.assigned_to = self.get_people_id(v[0])
                        elif table_field == 'status':
                            db_ilog.status = v[0]
                        elif table_field == 'resolution':
                            db_ilog.resolution = v[0]
                        elif table_field == 'link':
                            db_ilog.link = v[0]
                        elif table_field == 'environment':
                            db_ilog.environment = v[0]
                        elif table_field == 'component':
                            db_ilog.component = v[0]
                        elif table_field == 'description':
                            db_ilog.description = v[0]
                        elif table_field == 'security':
                            db_ilog.security = v[0]

        return db_ilog

    def backend_is_bugzilla(self):
        return self.backend_name == 'bg'

    def backend_is_jira(self):
        return self.backend_name == 'jira'

    def get_last_values(self, issue_row):
        i = issue_row
        db_ilog = None
        if self.backend_is_bugzilla():
            db_ilog_bugzilla = DBBugzillaIssuesLog(i.issue, i.tracker_id)
            db_ilog_bugzilla.issue_id = i.id
            db_ilog_bugzilla.type = i.type
            db_ilog_bugzilla.summary = i.summary
            db_ilog_bugzilla.description = i.description
            db_ilog_bugzilla.status = i.status
            db_ilog_bugzilla.resolution = i.resolution
            db_ilog_bugzilla.priority = i.priority
            db_ilog_bugzilla.submitted_by = i.submitted_by
            db_ilog_bugzilla.date = i.submitted_on
            db_ilog_bugzilla.assigned_to = i.assigned_to

            ib = self.store.find(DBBugzillaIssueExt, \
                                 DBBugzillaIssueExt.issue_id == db_ilog_bugzilla.issue_id).one()

            ####
            db_ilog_bugzilla.alias = ib.alias
            db_ilog_bugzilla.delta_ts = ib.delta_ts
            db_ilog_bugzilla.reporter_accessible = ib.reporter_accessible
            db_ilog_bugzilla.cclist_accessible = ib.cclist_accessible
            db_ilog_bugzilla.classification_id = ib.classification_id
            db_ilog_bugzilla.classification = ib.classification
            db_ilog_bugzilla.product = ib.product
            db_ilog_bugzilla.component = ib.component
            db_ilog_bugzilla.version = ib.version
            db_ilog_bugzilla.rep_platform = ib.rep_platform
            db_ilog_bugzilla.op_sys = ib.op_sys
            db_ilog_bugzilla.dup_id = ib.dup_id
            db_ilog_bugzilla.bug_file_loc = ib.bug_file_loc
            db_ilog_bugzilla.status_whiteboard = ib.status_whiteboard
            db_ilog_bugzilla.target_milestone = ib.target_milestone
            db_ilog_bugzilla.votes = ib.votes
            db_ilog_bugzilla.everconfirmed = ib.everconfirmed
            db_ilog_bugzilla.qa_contact = ib.qa_contact
            db_ilog_bugzilla.estimated_time = ib.estimated_time
            db_ilog_bugzilla.remaining_time = ib.remaining_time
            db_ilog_bugzilla.actual_time = ib.actual_time
            db_ilog_bugzilla.deadline = ib.deadline
            db_ilog_bugzilla.keywords = ib.keywords
            db_ilog_bugzilla.cc = ib.cc
            db_ilog_bugzilla.group_bugzilla = ib.group_bugzilla
            db_ilog_bugzilla.flag = ib.flag
            db_ilog = db_ilog_bugzilla

        elif self.backend_is_jira():
            db_ilog = DBJiraIssuesLog(i.issue, i.tracker_id)
            db_ilog.issue_id = i.id
            db_ilog.type = i.type
            db_ilog.summary = i.summary
            db_ilog.description = i.description
            db_ilog.status = i.status
            db_ilog.resolution = i.resolution
            db_ilog.priority = i.priority
            db_ilog.submitted_by = i.submitted_by
            db_ilog.date = i.submitted_on
            db_ilog.assigned_to = i.assigned_to

            ib = self.store.find(DBJiraIssueExt, \
                                 DBJiraIssueExt.issue_id == db_ilog.issue_id).one()

            db_ilog.issue_key = ib.issue_key
            db_ilog.link = ib.link
            db_ilog.environment = ib.environment
            db_ilog.security = ib.security
            db_ilog.updated = ib.updated
            db_ilog.version = ib.version
            db_ilog.component = ib.component
            db_ilog.votes = ib.votes
            db_ilog.project = ib.project
            db_ilog.project_id = ib.project_id
            db_ilog.project_key = ib.project_key

        return db_ilog

    def insert_new_bugs_created(self, date_from, date_to):
        """
        This method inserts an entry with the data of the creation time
        """
        if (not date_from) and (not date_to):
            issues = self.store.find(DBIssue)
        elif not date_from:
            issues = self.store.find(DBIssue, DBIssue.submitted_on < date_to)
        elif not date_to:
            issues = self.store.find(DBIssue, DBIssue.submitted_on > date_from)
        else:
            issues = self.store.find(DBIssue,
                                     And(DBIssue.submitted_on <= date_to,
                                         DBIssue.submitted_on > date_from))

        issues = issues.order_by(Asc(DBIssue.submitted_on))
        ## we store the initial data for each bug found
        for i in issues:
            db_ilog = self.get_last_values(i)  # from issues and change tables
            db_ilog = self.build_initial_state(db_ilog)
            self.store.add(db_ilog)
            printdbg("Issue #%s created at %s - date_from = %s - date_to = %s"
                     % (db_ilog.issue, db_ilog.date, date_from, date_to))

    def get_tracker_id(self, issue_id):
        """
        Returns tracker id from issues
        """
        result = self.store.find(DBIssue.tracker_id,
                                 DBIssue.id == issue_id).one()
        return result

    def run(self):

        last_change_date = self.get_last_change_date()
        printdbg("Last change logged at %s" % (last_change_date))

        date_from = None
        date_to = None

        if last_change_date:
            changes = self.store.find(DBChange,
                                      DBChange.changed_on > last_change_date)
            date_from = last_change_date
        else:
            changes = self.store.find(DBChange)

        changes = changes.order_by(Asc(DBChange.changed_on))

        for ch in changes:
            # insert creation if needed
            date_to = ch.changed_on
            self.insert_new_bugs_created(date_from, date_to)
            date_from = date_to

            field = ch.field
            new_value = ch.new_value
            changed_by = ch.changed_by
            date = ch.changed_on
            issue_id = ch.issue_id

            #print("field = %s, new_value = %s, changed_by = %s, date = %s"
            #      % (field, new_value, str(changed_by), str(date)))

            db_ilog = self.get_previous_state(issue_id)

            printdbg("Issue #%s modified at %s" %
                     (db_ilog.issue, date))

            if self.backend_is_bugzilla():
                # Bugzilla section
                #
                #
                if (field in bg_issues_links):
                    table_field = bg_issues_links[field]
                    db_ilog.submitted_by = changed_by
                    db_ilog.date = date

                    if table_field == 'summary':
                        db_ilog.summary = new_value
                    elif table_field == 'priority':
                        db_ilog.priority = new_value
                    elif table_field == 'type':
                        db_ilog.type = new_value
                    elif table_field == 'assigned_to':
                        db_ilog.assigned_to = self.get_people_id(
                            new_value, self.get_tracker_id(db_ilog.issue_id))
                    elif table_field == 'status':
                        db_ilog.status = new_value
                    elif table_field == 'resolution':
                        db_ilog.resolution = new_value
                    elif table_field == 'alias':
                        db_ilog.alias = new_value
                    elif table_field == 'reporter_accessible':
                        db_ilog.reporter_accessible = new_value
                    elif table_field == 'cclist_accessible':
                        db_ilog.cclist_accessible = new_value
                    elif table_field == 'product':
                        db_ilog.product = new_value
                    elif table_field == 'component':
                        db_ilog.component = new_value
                    elif table_field == 'version':
                        db_ilog.version = new_value
                    elif table_field == 'rep_platform':
                        db_ilog.rep_platform = new_value
                    elif table_field == 'op_sys':
                        db_ilog.op_sys = new_value
                    elif table_field == 'bug_file_loc':
                        db_ilog.bug_file_loc = new_value
                    elif table_field == 'status_whiteboard':
                        db_ilog.status_whiteboard = new_value
                    elif table_field == 'target_milestone':
                        db_ilog.target_milestone = new_value
                    elif table_field == 'votes':
                        db_ilog.votes = new_value
                    elif table_field == 'everconfirmed':
                        db_ilog.everconfirmed = new_value
                    elif table_field == 'qa_contact':
                        db_ilog.qa_contact = new_value
                    elif table_field == 'keywords':
                        db_ilog.Keywords = new_value
                    elif table_field == 'cc':
                        db_ilog.cc = new_value

                    try:
                        self.store.add(db_ilog)
                    except:
                        traceback.print_exc()

            elif self.backend_is_jira():
                # Jira section
                #
                #

                if (field in jira_issues_links):
                    table_field = jira_issues_links[field]
                    db_ilog.submitted_by = changed_by
                    db_ilog.date = date

                    if table_field == 'summary':
                        db_ilog.summary = new_value
                    elif table_field == 'priority':
                        db_ilog.priority = new_value
                    elif table_field == 'type':
                        db_ilog.type = new_value
                    elif table_field == 'assigned_to':
                        db_ilog.assigned_to = self.get_people_id(
                            new_value, self.get_tracker_id(db_ilog.issue_id))
                    elif table_field == 'status':
                        db_ilog.status = new_value
                    elif table_field == 'resolution':
                        db_ilog.resolution = new_value
                    elif table_field == 'description':
                        db_ilog.description = new_value
                    elif table_field == 'link':
                        db_ilog.link = new_value
                    elif table_field == 'component':
                        db_ilog.component = new_value
                    elif table_field == 'version':
                        db_ilog.version = new_value
                    elif table_field == 'security':
                        db_ilog.security = new_value
                    try:
                        self.store.add(db_ilog)
                    except:
                        traceback.print_exc()

            # if there are changes, it stores the last bugs after the last
            # change. If there are no changes, insert all the created bugs
        self.insert_new_bugs_created(date_from, None)
        self.store.commit()
