# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Bitergia
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
# Authors: Santiago Dueñas <sduenas@bitergia.com>
#

from bicho.post_processing import IssueLogger
from issues_log import *


__sql_drop__ = 'DROP TABLE IF EXISTS issues_log_trac;'

__sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_log_trac ( \
                     id INTEGER NOT NULL AUTO_INCREMENT, \
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
                         ON UPDATE CASCADE, \
                     FOREIGN KEY(change_id) \
                       REFERENCES changes(id) \
                         ON DELETE CASCADE \
                         ON UPDATE CASCADE \
                     ) ENGINE=MYISAM;'

#
# This dictionary contains the text that appears in the
# journals object in Trac and its equivalent in the database.
#
__trac_issues_links__ = {
                         'summary' : 'summary',
                         'description' : 'description',
                         'status' : 'status',
                         'priority' : 'priority',
                         'resolution' : 'resolution'
                         }


class DBTracIssuesLog(DBIssuesLog):
    """
    """
    __storm_table__ = 'issues_log_trac'


class TracIssuesLog(IssuesLog):

    def _assign_values(self, db_ilog, field, value):
        """
        Assign the value to the attribute field of the db_ilog object
        """
        if field in __trac_issues_links__:
            table_field = __trac_issues_links__[field]
            if table_field == 'summary':
                db_ilog.summary = value
            elif table_field == 'description':
                db_ilog.description = value
            elif table_field == 'status':
                db_ilog.status = value
            elif table_field == 'priority':
                db_ilog.priority = value
            elif table_field == 'resolution':
                db_ilog.resolution = value

        return db_ilog

    def _copy_issue_ext(self, aux, db_ilog):
        """
        This method copies extended values of DBTracIssuesLog object
        """
        return aux

    def _get_dbissues_object(self, issue_name, tracker_id):
        return DBTracIssuesLog(issue_name, tracker_id)

    def _get_sql_create(self):
        return __sql_table__

    def _get_sql_drop(self):
        return __sql_drop__

    def _print_final_msg(self):
        printout("Table issues_log_trac populated")


IssueLogger.register_logger("trac", TracIssuesLog)
