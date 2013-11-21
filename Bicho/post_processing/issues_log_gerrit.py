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

__sql_drop__ = 'DROP TABLE IF EXISTS issues_log_gerrit;'

# Extended issue fields and field column values in changes table 
__gerrit_fields__ = 'branch TEXT, \
                     url TEXT,  \
                     related_artifacts TEXT, \
                     project TEXT, \
                     mod_date DATETIME, \
                     open TEXT, \
                     verified VARCHAR(255), \
                     submit VARCHAR(255), \
                     review VARCHAR(255)'

__common_fields__ = 'id INTEGER NOT NULL AUTO_INCREMENT, \
                     change_id INTEGER NOT NULL, \
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
                     assigned_to INTEGER UNSIGNED NOT NULL'


__sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_log_gerrit ( \
                     '+__common_fields__+', \
                     '+__gerrit_fields__+', \
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
                         ON UPDATE CASCADE, \
                     FOREIGN KEY(change_id) \
                       REFERENCES changes(id) \
                         ON DELETE CASCADE \
                         ON UPDATE CASCADE \
                     ) ENGINE=MYISAM;'


# mapping between each different "field" in changes table and field in issues_log table
__gerrit_issues_links__ = {
    "Verified":"verified",
    "Code-Review":"review",
    "SUBM":"submit",
    "branch":"branch",
    "url":"url",
    "change_id":"change_id",
    "related_artifacts":"related_artifacts",
    "project":"project",
    "mod_date":"mod_date",
    "issue_id":"issue_id",
    "open":"open"
}

class DBGerritIssuesLog(DBIssuesLog):
    """
    """
    __storm_table__ = 'issues_log_gerrit'

    branch = Unicode()
    url = Unicode()
    change_id = Unicode()
    related_artifacts = Unicode()
    project = Unicode()
    mod_date = DateTime()
    issue_id = Int()
    open = Unicode()
    verified = Unicode()
    review = Unicode()
    submit = Unicode()

class GerritIssuesLog(IssuesLog):

    def _assign_values(self, db_ilog, field, value):
        """
        Assign the value to the attribute field of the db_ilog object
        """
        if field in __gerrit_issues_links__:
            table_field = __gerrit_issues_links__[field]
            if table_field == 'branch':
                db_ilog.branch = value
            elif table_field == 'url':
                db_ilog.url = value
            elif table_field == 'change_id':
                db_ilog.change_id = value
            elif table_field == 'related_artifacts':
                db_ilog.related_artifacts = value
            elif table_field == 'project':
                db_ilog.project = value
            elif table_field == 'mod_date':
                db_ilog.mod_date = value
            elif table_field == 'issue_id':
                db_ilog.issue_id = value
            elif table_field == 'component':
                db_ilog.component = value
            elif table_field == 'open':
                db_ilog.open = value
            elif table_field == 'verified':
                db_ilog.verified = value
            elif table_field == 'review':
                db_ilog.review = value
            elif table_field == 'submit':
                db_ilog.submit = value
        return db_ilog

    def _copy_issue_ext(self, aux, db_ilog):
        """
        This method copies extended values of DBGerritIssuesLog object
        """
        aux.branch = db_ilog.branch
        aux.url = db_ilog.url
        aux.change_id = db_ilog.change_id
        aux.related_artifacts = db_ilog.related_artifacts
        aux.project = db_ilog.project
        aux.mod_date = db_ilog.mod_date
        aux.issue_id = db_ilog.issue_id
        aux.open = db_ilog.open
        return aux

    def _get_dbissues_object(self, issue_name, tracker_id):
        return DBGerritIssuesLog(issue_name, tracker_id)

    def _get_sql_create(self):
        return __sql_table__

    def _get_sql_drop(self):
        return __sql_drop__

    def _print_final_msg(self):
        printout("Table issues_log_gerrit populated")

IssueLogger.register_logger("gerrit", GerritIssuesLog)
