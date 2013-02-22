# -*- coding: utf-8 -*-
# Copyright (C) 2007-2013 GSyC/LibreSoft, Universidad Rey Juan Carlos
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

from Bicho.post_processing import IssueLogger
from issues_log import *

__sql_drop__ = 'DROP TABLE IF EXISTS issues_log_bugzilla;'

__sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_log_bugzilla ( \
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
                     url VARCHAR(255) default NULL, \
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
__bg_issues_links__ = {"Summary": "summary",
                "Priority": "priority",
                "Assignee": "assigned_to",
                "status": "status",
                "resolution": "resolution",
                "Severity": "type",
                "Alias": "alias",
                "Reporter accessible": "reporter_accessible",
                "CC list accessible": "cclist_accessible",
                "Product": "product",
                "Version": "version",
                "Hardware": "rep_platform",
                "OS": "op_sys",
                "Component": "component",
                "Target Milestone": "target_milestone",
                "Ever confirmed": "everconfirmed",
                "QA Contact": "qa_contact",
                "CC": "cc",
                "Keywords": "keywords",
                "URL": "url"}


class DBBugzillaIssuesLog(DBIssuesLog):
    """
    """
    __storm_table__ = 'issues_log_bugzilla'
    alias = Unicode()
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
    url = Unicode()


class BugzillaIssuesLog(IssuesLog):

    def _assign_values(self, db_ilog, field, value):
        """
        Assign the value to the attribute field of the db_ilog object
        """
        if field in __bg_issues_links__:
            table_field = __bg_issues_links__[field]
            if table_field == 'summary':
                db_ilog.summary = value
            elif table_field == 'priority':
                db_ilog.priority = value
            elif table_field == 'assigned_to':
                db_ilog.assigned_to = self._get_people_id(
                    value, self._get_tracker_id(db_ilog.issue_id))
            elif table_field == 'status':
                db_ilog.status = value
            elif table_field == 'resolution':
                db_ilog.resolution = value
            elif table_field == 'type':
                db_ilog.type = value
            elif table_field == 'alias':
                db_ilog.alias = value
            elif table_field == 'reporter_accessible':
                db_ilog.reporter_accessible = value
            elif table_field == 'cclist_accessible':
                db_ilog.cclist_accessible = value
            elif table_field == 'product':
                db_ilog.product = value
            elif table_field == 'component':
                db_ilog.component = value
            elif table_field == 'version':
                db_ilog.version = value
            elif table_field == 'rep_platform':
                db_ilog.rep_platform = value
            elif table_field == 'op_sys':
                db_ilog.op_sys = value
            elif table_field == 'bug_file_loc':
                db_ilog.bug_file_loc = value
            elif table_field == 'status_whiteboard':
                db_ilog.status_whiteboard = value
            elif table_field == 'target_milestone':
                db_ilog.target_milestone = value
            elif table_field == 'votes':
                db_ilog.votes = value
            elif table_field == 'everconfirmed':
                db_ilog.everconfirmed = value
            elif table_field == 'qa_contact':
                db_ilog.qa_contact = value
            elif table_field == 'keywords':
                db_ilog.Keywords = value
            elif table_field == 'cc':
                db_ilog.cc = value
            elif table_field == 'url':
                db_ilog.url = value
        return db_ilog

    def _copy_issue_ext(self, aux, db_ilog):
        """
        This method copies extended values of DBBugzillaIssuesLog object
        """
        aux.alias = db_ilog.alias
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
        aux.url = db_ilog.url
        return aux

    def _get_dbissues_object(self, issue_name, tracker_id):
        return DBBugzillaIssuesLog(issue_name, tracker_id)

    def _get_sql_create(self):
        return __sql_table__

    def _get_sql_drop(self):
        return __sql_drop__

    def _print_final_msg(self):
        printout("Table issues_log_bugzilla populated")

IssueLogger.register_logger("bg", BugzillaIssuesLog)
