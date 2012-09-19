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
from Bicho.Config import Config
from Bicho.utils import printerr, printdbg, printout
from Bicho.common import Tracker, People, Issue, Comment, Change
from Bicho.db.database import DBIssue, DBBackend, get_database, DBTracker, DBPeople

from storm.locals import DateTime, Int, Reference, Unicode, Desc, Store, create_database
import xml.sax.handler

from dateutil.parser import parse
from datetime import datetime

from Bicho.Config import Config

__sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_log ( \
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
bg_issues_links = {"Summary":"summary",
                "Priority":"priority",
                "Assignee":"assigned_to",
                "status":"status",
                "resolution":"resolution"}

bg_issues_ext_links = {"Product":"product",
                "Version":"version",
                "Hardware":"rep_platform",
                "OS":"op_sys",
                "Component":"component",
                "Target Milestone":"target_milestone",
                "Ever confirmed":"everconfirmed",
                "QA Contact":"qa_contact",
                "CC":"cc"}


class DBIssuesLog(object):
    """
    """
    __storm_table__ = 'issues_log'

    id = Int(primary=True)
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
        self.store.execute(__sql_table__)

    def copy_issue(self, db_ilog):
        """
        This method is create a copy of a DBIssueLog object
        """
        aux = DBIssuesLog(db_ilog.issue, db_ilog.tracker_id)
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
        return aux
    

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
                    elif table_field == 'assignted_to':
                        db_ilog.assigned_to = v[0]
                    elif table_field == 'status':
                        db_ilog.status = v[0]
                    elif table_field == 'resolution':
                        db_ilog.resolution = v[0]
        return db_ilog

        
    def run(self):
        issues = self.store.find(DBIssue)
        for i in issues:
            db_ilog = DBIssuesLog(i.issue, i.tracker_id)
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

            db_ilog = self.build_initial_state(db_ilog)         

            self.store.add(db_ilog)

            # the code below gets all the changes and insert a row per change
            changes = self.store.execute("SELECT field, new_value, changed_by, changed_on FROM changes where issue_id=%s" % (db_ilog.issue_id))
            
            for ch in changes:
                field = ch[0]
                new_value = ch[1]
                changed_by = ch[2]
                date = ch[3]

                db_ilog = self.copy_issue(db_ilog)

                
                # Bugzilla section
                #
                if field in bg_issues_links:
                    table_field = bg_issues_links[field]
                    if table_field == 'summary':
                        db_ilog.summary = new_value                    
                    elif table_field == 'priority':
                        db_ilog.priority = new_value
                    elif table_field == 'assignted_to':
                        db_ilog.assigned_to = new_value
                    elif table_field == 'status':
                        db_ilog.status = new_value
                    elif table_field == 'resolution':
                        db_ilog.resolution = new_value
                    db_ilog.submitted_by = changed_by
                    db_ilog.date = date          

                    try:
                        self.store.add(db_ilog)
                    except:
                        traceback.print_exc()
            
            self.store.commit()

        
