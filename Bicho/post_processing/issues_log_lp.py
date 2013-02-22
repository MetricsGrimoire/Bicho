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

__sql_drop__ = 'DROP TABLE IF EXISTS issues_log_launchpad;'

__sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_log_launchpad (\
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
                     issue_key VARCHAR(32) default NULL, \
                     link VARCHAR(100) default NULL, \
                     title VARCHAR(100) default NULL, \
                     environment VARCHAR(35) default NULL, \
                     security VARCHAR(35) default NULL, \
                     updated DATETIME default NULL, \
                     version VARCHAR(35) default NULL, \
                     component VARCHAR(35) default NULL, \
                     votes INTEGER UNSIGNED, \
                     project VARCHAR(35) default NULL, \
                     project_id INTEGER UNSIGNED, \
                     project_key VARCHAR(35) default NULL, \
                     affects VARCHAR(100) default NULL, \
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

"""
The fields with the comment "# project" contain the name of the project
and the semicolon before the tag. 
Example: "oslo: status"
"""
__launchpad_issues_links__ = { # the ones seen in Maria
    "affects":"affects",
    #"attachment added":"",
    #"attachment removed":"",
    "assignee": "assigned_to",  # project:
    #"branch linked":"",
    #"branch unlinked":"",
    #"bug": "",
    #"bug task added":"",
    #"bug watch added":"",
    "description": "description",
    "importance": "priority",  # project:
    #"marked as duplicate":"",
    "milestone": "version",  # project:
    #"nominated for series":"",
    #"removed duplicate marker":"",
    #"removed subscriber Cafuego":"",
    "security vulnerability": "security",
    "status": "status",  # project: status
    #"statusexplanation":"", #project:
    "summary": "summary",
    #"tags":"",
    #"visibility":""
    }


class DBLaunchpadIssuesLog(DBIssuesLog):
    """
    """
    __storm_table__ = 'issues_log_launchpad'
    affects = Unicode()
    version = Unicode()
    security = Unicode()


class LaunchpadIssuesLog(IssuesLog):

    def __init__(self):
        IssuesLog.__init__(self)
        self._project_name = None

    def _assign_values(self, db_ilog, field, value):
        """
        Assign the value to the attribute field of the db_ilog object
        """

        # first we need to confirm the change belongs to the currenct project
        # and extract the content
        if not self._project_name:
            self._project_name = self._get_project_name(db_ilog.tracker_id)
        field = self._filter_field(field, self._project_name)

        if field in __launchpad_issues_links__:
            table_field = __launchpad_issues_links__[field]
            # to be done
            if table_field == 'summary':
                db_ilog.summary = value
            elif table_field == 'priority':
                db_ilog.priority = value
            #elif table_field == 'type':
            #    db_ilog.type = value
            elif table_field == 'assigned_to':
                uid = self._get_user_id(value)
                db_ilog.assigned_to = self._get_people_id(uid,
                    self._get_tracker_id(db_ilog.issue_id))
            elif table_field == 'status':
                db_ilog.status = value
            elif table_field == 'affects':
                db_ilog.affects = value
            elif table_field == 'description':
                db_ilog.description = value
            elif table_field == 'security':
                db_ilog.security = value
            elif table_field == 'version':
                db_ilog.version = value
        return db_ilog

    def _copy_issue_ext(self, aux, db_ilog):
        """
        This method copies extended values of DBLaunchpadIssuesLog object
        """
        aux.affects = db_ilog.affects
        aux.security = db_ilog.security
        aux.version = db_ilog.version
        return aux

    def _filter_field(self, text, project_name):
        """
        Returns the field without the project name ("project: status")
        """
        if text.find(':') < 0:
            return text
        elif text.find(project_name) < 0:
            # if the text contains another project we skip it
            return None
        else:
            offset = text.find(": ") + 2
            return text[offset:]

    def _get_changes(self, issue_id):
        aux = self.store.execute("SELECT field, new_value, changed_by, \
        changed_on FROM changes \
        WHERE (changes.issue_id=%s AND field NOT LIKE '%%:%%') \
        OR (changes.issue_id=%s AND field LIKE '%%%s:%%')" %
        (issue_id, issue_id, self._project_name))
        return aux

    def _get_dbissues_object(self, issue_name, tracker_id):
        return DBLaunchpadIssuesLog(issue_name, tracker_id)

    def _get_sql_create(self):
        return __sql_table__

    def _get_sql_drop(self):
        return __sql_drop__

    def _get_user_id(self, text):
        if text == 'None':
            return text
        else:
            a = text.find('(') + 1
            b = text.find(')')
            return text[a:b]

    def _get_project_name(self, tracker_id):
        """
        Returns project name based on tracker url
        """
        result = self.store.find(DBTracker.url,
                                 DBTracker.id == tracker_id).one()
        offset = result.rfind('/') + 1
        project_name = result[offset:]
        return project_name

    def _print_final_msg(self):
        printout("Table issues_log_launchpad populated")

IssueLogger.register_logger("lp", LaunchpadIssuesLog)
