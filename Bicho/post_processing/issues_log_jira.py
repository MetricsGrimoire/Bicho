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

__sql_drop__ = 'DROP TABLE IF EXISTS issues_log_jira;'

__sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_log_jira ( \
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
                     version VARCHAR(35) default NULL, \
                     component VARCHAR(35) default NULL, \
                     votes INTEGER UNSIGNED, \
                     project VARCHAR(35) default NULL, \
                     project_id INTEGER UNSIGNED, \
                     project_key VARCHAR(35) default NULL, \
                     theme VARCHAR(35) default NULL, \
                     parent VARCHAR(35) default NULL, \
                     qa VARCHAR(35) default NULL, \
                     workflow VARCHAR(100) default NULL, \
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
__jira_issues_links__ = {
    "Link": "link",
    "Summary": "summary",
    "Priority": "priority",
    "Project": "project",
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
    "Security": "security",
    "Epic/Theme": "theme",
    "Parent": "parent",
    "QA": "qa",
    "Workflow": "workflow"}


class DBJiraIssuesLog(DBIssuesLog):
    """
    """
    __storm_table__ = 'issues_log_jira'
    issue_key = Unicode()
    link = Unicode()
    environment = Unicode()
    security = Unicode()
    #updated = DateTime()
    version = Unicode()
    component = Unicode()
    votes = Int()
    project = Unicode()
    project_id = Int
    project_key = Unicode()
    theme = Unicode()
    parent = Unicode()
    qa = Unicode()
    workflow = Unicode()


class JiraIssuesLog(IssuesLog):

    def _assign_values(self, db_ilog, field, value):
        """
        Assign the value to the attribute field of the db_ilog object
        """
        if field in __jira_issues_links__:
            table_field = __jira_issues_links__[field]
            if table_field == 'summary':
                db_ilog.summary = value
            elif table_field == 'priority':
                db_ilog.priority = value
            elif table_field == 'type':
                db_ilog.type = value
            elif table_field == 'assigned_to':
                db_ilog.assigned_to = self._get_people_id(value,
                    self._get_tracker_id(db_ilog.issue_id))
            elif table_field == 'status':
                db_ilog.status = value
            elif table_field == 'resolution':
                db_ilog.resolution = value
            elif table_field == 'link':
                db_ilog.link = value
            elif table_field == 'environment':
                db_ilog.environment = value
            elif table_field == 'component':
                db_ilog.component = value
            elif table_field == 'description':
                db_ilog.description = value
            elif table_field == 'security':
                db_ilog.security = value
            elif table_field == 'version':
                db_ilog.version = value
            elif table_field == 'theme':
                db_ilog.theme = value
            elif table_field == 'parent':
                db_ilog.parent = value
            elif table_field == 'project':
                db_ilog.project = value
            elif table_field == 'qa':
                db_ilog.qa = value
            elif table_field == 'workflow':
                db_ilog.workflow = value
        return db_ilog

    def _copy_issue_ext(self, aux, db_ilog):
        """
        This method copies extended values of DBBugzillaIssuesLog object
        """
        aux.link = db_ilog.link
        aux.component = db_ilog.component
        aux.version = db_ilog.version
        aux.issue_key = db_ilog.issue_key
        aux.environment = db_ilog.environment
        aux.project = db_ilog.project
        aux.project_key = db_ilog.project_key
        aux.security = db_ilog.security
        aux.theme = db_ilog.theme
        aux.parent = db_ilog.parent
        aux.qa = db_ilog.qa
        aux.workflow = db_ilog.workflow
        return aux

    def _get_dbissues_object(self, issue_name, tracker_id):
        return DBJiraIssuesLog(issue_name, tracker_id)

    def _get_sql_create(self):
        return __sql_table__

    def _get_sql_drop(self):
        return __sql_drop__

    def _print_final_msg(self):
        printout("Table issues_log_jira populated")

IssueLogger.register_logger("jira", JiraIssuesLog)
