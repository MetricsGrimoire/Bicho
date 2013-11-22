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
# Authors: Alvaro del Castillo <acs@bitergia.com>
#
#

import pprint
from Bicho.post_processing import IssueLogger
from issues_log import *

__sql_drop__ = 'DROP TABLE IF EXISTS issues_log_gerrit;'

# Extended issue fields and field column values in changes table 
__gerrit_ext_fields__ = 'branch TEXT, \
                         url TEXT,  \
                         related_artifacts TEXT, \
                         project TEXT, \
                         mod_date DATETIME, \
                         open TEXT'

__gerrit_changes_fields__ = 'verified VARCHAR(255), \
                             submit VARCHAR(255), \
                             review VARCHAR(255)'

__common_fields__ = 'id INTEGER NOT NULL AUTO_INCREMENT, \
                     change_id INTEGER NOT NULL, \
                     changed_by INTEGER NOT NULL, \
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
                     '+__gerrit_ext_fields__+', \
                     '+__gerrit_changes_fields__+', \
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


# mapping between each different status field in changes table
# and the extended fields for gerrit  
# with the field in issues_log table
__gerrit_issues_links__ = {
    "Verified":"verified",
    "Code-Review":"review",
    "SUBM":"submit"
}

class DBGerritIssuesLog(DBIssuesLog):
    """
    """
    __storm_table__ = 'issues_log_gerrit'

    # issues_ext_gerrit fields
    branch = Unicode()
    url = Unicode()
    change_id = Int()
    changed_by = Int()
    related_artifacts = Unicode()
    project = Unicode()
    mod_date = DateTime()
    issue_id = Int()
    open = Unicode()
    # changes fields
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
            if table_field == 'verified':
                db_ilog.verified = value
            elif table_field == 'review':
                db_ilog.review = value
            elif table_field == 'submit':
                db_ilog.submit = value
        return db_ilog

    def _build_initial_state(self, db_ilog):
        # Initial status in gerrit is NEW
        db_ilog.status = unicode('NEW')
        return db_ilog

    def _copy_issue_ext(self, aux, db_ilog):
        """
        This method copies extended values of DBGerritIssuesLog object
        """
        aux.branch = db_ilog.branch
        aux.url = db_ilog.url
        aux.change_id = db_ilog.change_id
        aux.changed_by = db_ilog.changed_by
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

    def _post_history(self, db_ilog, final_status):
        if final_status == 'MERGED':
            printout("Creating MERGED entries for " + str(db_ilog.issue_id))
            # Search for the last Code-Review +2 -> data for merged and reviewer
            aux = self.store.execute ('SELECT changed_on, changed_by FROM changes \
                                       WHERE issue_id=%s AND \
                                             field="Code-Review" AND \
                                             new_value="2" \
                                             ORDER BY changed_on DESC LIMIT 1'
                                      % (db_ilog.issue_id))
            db_ilog = self._copy_issue(db_ilog)
            db_ilog.status = unicode('MERGED')
            aux = aux.get_one()
            db_ilog.date = aux[0]
            db_ilog.changed_by = aux[1]
            # This entry is not related to a row in changes
            db_ilog.change_id = 0
            self.store.add(db_ilog)
            self.store.flush()
        if final_status == 'ABANDONED':
            printout("Creating ABANDONED entries for " + str(db_ilog.issue_id))

IssueLogger.register_logger("gerrit", GerritIssuesLog)
