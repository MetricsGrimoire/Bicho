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

import cookielib, pprint, string, sys, time, urllib, urllib2
import traceback

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import Comment as BFComment
from Bicho.backends import Backend
from Bicho.backends.bg import DBBugzillaIssueExt
from Bicho.Config import Config
from Bicho.utils import printerr, printdbg, printout
from Bicho.common import Tracker, People, Issue, Comment, Change
from Bicho.db.database import DBIssue, DBBackend, get_database, DBTracker, DBPeople

from storm.locals import DateTime, Int, Reference, Unicode, Desc, Store, create_database
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


#
# these dictionaries contain the text that appears in the HTML history
# table for bugzilla and its equivalent in the database
#

bg_issues_links = {
    "Summary":"summary",
    "Priority":"priority",
    "Assignee":"assigned_to",
    "status":"status",
    "resolution":"resolution",
    "Severity":"type",
    "Alias":"alias",
    "Reporter accessible":"reporter_accessible",
    "CC list accessible":"cclist_accessible",
    #"":"classification_id",
    #"":"classification",
    "Product":"product",
    "Component":"component",
    "Version":"version",
    "Hardware":"rep_platform",
    "OS":"op_sys",
    #"":"dup_id",
    "URL":"bug_file_loc",
    "Whiteboard":"status_whiteboard",
    "Target Milestone":"target_milestone",
    "Votes":"votes",
    "Ever confirmed":"everconfirmed",
    "QA Contact":"qa_contact",
    #"":"estimated_time",
    #"":"remaining_time",
    #"":"actual_time",
    #"":"deadline",
    "Keywords":"keywords",
    #"":"flag",
    #"":"group_bugzilla",
    "CC":"cc"}



class DBBugzillaIssuesLog(object):
    """
    """
    __storm_table__ = 'issues_log_bugzilla'
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

    tracker = Reference(tracker_id, DBTracker.id)
    submitted = Reference(submitted_by, DBPeople.id)
    assigned = Reference(assigned_to, DBPeople.id)

    def __init__(self, issue, tracker_id):
        self.issue = unicode(issue)
        self.tracker_id = tracker_id


class IssuesLog():

    def __init__(self,backend_name):
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
        self.store.execute(__sql_table_bugzilla__)

    def copy_issue_ext_bugzilla(self, db_ilog_bugzilla):
        """
        This method creates a copy of DBBugzillaIssuesLog object
        """

        aux = DBBugzillaIssuesLog(db_ilog_bugzilla.issue, db_ilog_bugzilla.tracker_id)
        aux.issue_id = db_ilog_bugzilla.issue_id
        aux.type = db_ilog_bugzilla.type
        aux.summary = db_ilog_bugzilla.summary
        aux.description = db_ilog_bugzilla.description
        aux.status = db_ilog_bugzilla.status
        aux.resolution = db_ilog_bugzilla.resolution
        aux.priority = db_ilog_bugzilla.priority
        aux.submitted_by = db_ilog_bugzilla.submitted_by
        aux.date = db_ilog_bugzilla.date
        aux.assigned_to = db_ilog_bugzilla.assigned_to        
                
        #aux = DBBugzillaIssuesLog (db_ilog_bugzilla.issue_id)
        aux.alias = db_ilog_bugzilla.alias
        aux.delta_ts = db_ilog_bugzilla.delta_ts
        aux.reporter_accessible = db_ilog_bugzilla.reporter_accessible
        aux.cclist_accessible = db_ilog_bugzilla.cclist_accessible
        aux.classification_id = db_ilog_bugzilla.classification_id
        aux.classification = db_ilog_bugzilla.classification
        aux.product = db_ilog_bugzilla.product
        aux.component = db_ilog_bugzilla.component
        aux.version = db_ilog_bugzilla.version
        aux.rep_platform = db_ilog_bugzilla.rep_platform
        aux.op_sys = db_ilog_bugzilla.op_sys
        aux.dup_id = db_ilog_bugzilla.dup_id
        aux.bug_file_loc = db_ilog_bugzilla.bug_file_loc
        aux.status_whiteboard = db_ilog_bugzilla.status_whiteboard
        aux.target_milestone = db_ilog_bugzilla.target_milestone
        aux.votes = db_ilog_bugzilla.votes
        aux.everconfirmed = db_ilog_bugzilla.everconfirmed
        aux.qa_contact = db_ilog_bugzilla.qa_contact
        aux.estimated_time = db_ilog_bugzilla.estimated_time
        aux.remaining_time = db_ilog_bugzilla.remaining_time
        aux.actual_time = db_ilog_bugzilla.actual_time
        aux.deadline = db_ilog_bugzilla.deadline
        aux.keywords = db_ilog_bugzilla.keywords
        aux.cc = db_ilog_bugzilla.cc
        aux.group_bugzilla = db_ilog_bugzilla.group_bugzilla
        aux.flag = db_ilog_bugzilla.flag

        return aux

    def get_people_id(self, email):
        """
        """
        p = self.store.find(DBPeople, DBPeople.email == email).one()
        return p.id

    def build_initial_state(self, db_ilog):
        """
        This method gets the first changes of every field in
        order to get the initial state of the bug
        """
        fields = self.store.execute("SELECT DISTINCT(field) FROM changes where issue_id=%s" % (db_ilog.issue_id))

        for f in fields:
            value = self.store.execute("SELECT old_value FROM changes WHERE issue_id=%s AND field=\"%s\" ORDER BY changed_on LIMIT 1"
                                  % (db_ilog.issue_id, f[0]))
            for v in value:
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
                        db_ilog.assigned_to = self.get_people_id(v[0])
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

        return db_ilog

        
    def run(self):
        issues = self.store.find(DBIssue)
        for i in issues:
            printdbg("Writing log for issue %s" % (i.issue))
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

            ib = self.store.find(DBBugzillaIssueExt, DBBugzillaIssueExt.issue_id == db_ilog_bugzilla.issue_id).one()

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
            
            ####

            db_ilog_bugzilla = self.build_initial_state(db_ilog_bugzilla)         

            self.store.add(db_ilog_bugzilla)

            # the code below gets all the changes and insert a row per change
            changes = self.store.execute("SELECT field, new_value, changed_by, changed_on FROM changes where issue_id=%s" % (db_ilog_bugzilla.issue_id))
            
            for ch in changes:
                field = ch[0]
                new_value = ch[1]
                changed_by = ch[2]
                date = ch[3]

                db_ilog_bugzilla = self.copy_issue_ext_bugzilla(db_ilog_bugzilla)
                
                # Bugzilla section
                #
                #

                if (field in bg_issues_links):
                    table_field = bg_issues_links[field]
                    db_ilog_bugzilla.submitted_by = changed_by
                    db_ilog_bugzilla.date = date

                    if table_field == 'summary':
                        db_ilog_bugzilla.summary = new_value                    
                    elif table_field == 'priority':
                        db_ilog_bugzilla.priority = new_value
                    elif table_field == 'type':
                        db_ilog_bugzilla.type = new_value
                    elif table_field == 'assigned_to':
                        db_ilog_bugzilla.assigned_to = self.get_people_id(new_value)
                    elif table_field == 'status':
                        db_ilog_bugzilla.status = new_value
                    elif table_field == 'resolution':
                        db_ilog_bugzilla.resolution = new_value
                    elif table_field == 'alias':
                        db_ilog_bugzilla.alias = new_value
                    elif table_field == 'reporter_accessible':
                        db_ilog_bugzilla.reporter_accessible = new_value
                    elif table_field == 'cclist_accessible':
                        db_ilog_bugzilla.cclist_accessible = new_value
                    elif table_field == 'product':
                        db_ilog_bugzilla.product = new_value
                    elif table_field == 'component':
                        db_ilog_bugzilla.component = new_value
                    elif table_field == 'version':
                        db_ilog_bugzilla.version = new_value
                    elif table_field == 'rep_platform':
                        db_ilog_bugzilla.rep_platform = new_value
                    elif table_field == 'op_sys':
                        db_ilog_bugzilla.op_sys = new_value
                    elif table_field == 'bug_file_loc':
                        db_ilog_bugzilla.bug_file_loc = new_value
                    elif table_field == 'status_whiteboard':
                        db_ilog_bugzilla.status_whiteboard = new_value
                    elif table_field == 'target_milestone':
                        db_ilog_bugzilla.target_milestone = new_value
                    elif table_field == 'votes':
                        db_ilog_bugzilla.votes = new_value
                    elif table_field == 'everconfirmed':
                        db_ilog_bugzilla.everconfirmed = new_value
                    elif table_field == 'qa_contact':
                        db_ilog_bugzilla.qa_contact = new_value
                    elif table_field == 'keywords':
                        db_ilog_bugzilla.Keywords = new_value
                    elif table_field == 'cc':
                        db_ilog_bugzilla.cc = new_value

                    try:
                        self.store.add(db_ilog_bugzilla)
                    except:
                        traceback.print_exc()
            
            self.store.commit()

        
