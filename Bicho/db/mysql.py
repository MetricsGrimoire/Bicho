# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2011  GSyC/LibreSoft, Universidad Rey Juan Carlos
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# Authors: Santiago Dueñas <sduenas@libresoft.es>
#

"""
MySQL database module
"""

import warnings

from storm.locals import Store, create_database

from Bicho.Config import Config
from Bicho.db.database import DBDatabase, DBTracker, DBPeople, \
    DBIssue, DBIssuesWatchers, DBIssueRelationship, DBComment, DBAttachment, \
    DBChange, DBSupportedTracker, DBIssueTempRelationship


class DBMySQL(DBDatabase):
    """
    MySQL database adapter.
    """

    def __init__(self, backend=None):
        DBDatabase.__init__(self, backend)
        opts = Config()

        self.database = create_database('mysql://' + opts.db_user_out + ':'
                                        + opts.db_password_out + '@'
                                        + opts.db_hostname_out + ':'
                                        + opts.db_port_out + '/'
                                        + opts.db_database_out)
        self.store = Store(self.database)

        clsl = [DBSupportedTracker, DBTrackerMySQL, DBPeopleMySQL,
                DBIssueMySQL, DBIssueRelationshipMySQL,
                DBCommentMySQL, DBAttachmentMySQL, DBChangeMySQL,
                DBIssuesWatchersMySQL, DBIssueTempRelationshipMySQL]

        if backend is not None:
            clsl.extend([cls for cls in backend.MYSQL_EXT])

        self.suppress_warnings()
        self.create_tables(clsl)

    def suppress_warnings(self):
        warnings.filterwarnings("ignore", message="Table .* already exists")


class DBSupportedTracker(DBSupportedTracker):
    """
    MySQL subclass of L{DBSupportedTracker}.
    """
    __sql_table__ = 'CREATE TABLE IF NOT EXISTS supported_trackers ( \
                     id INTEGER NOT NULL AUTO_INCREMENT, \
                     name VARCHAR(64) NOT NULL, \
                     version VARCHAR(64) NOT NULL, \
                     PRIMARY KEY(id), \
                     UNIQUE KEY(name, version) \
                     ) ENGINE=MYISAM;'


class DBTrackerMySQL(DBTracker):
    """
    MySQL subclass of L{DBTracker}.
    """
    __sql_table__ = 'CREATE TABLE IF NOT EXISTS trackers ( \
                     id INTEGER NOT NULL AUTO_INCREMENT, \
                     url VARCHAR(255) NOT NULL, \
                     type INTEGER NOT NULL, \
                     retrieved_on DATETIME NOT NULL, \
                     PRIMARY KEY(id), \
                     UNIQUE KEY(url), \
                     FOREIGN KEY(type) \
                       REFERENCES tracker_types (id) \
                         ON DELETE CASCADE \
                         ON UPDATE CASCADE \
                     ) ENGINE=MYISAM;'


class DBPeopleMySQL(DBPeople):
    """
    MySQL subclass of L{DBPeople}.
    """
    __sql_table__ = 'CREATE TABLE IF NOT EXISTS people ( \
                     id INTEGER NOT NULL AUTO_INCREMENT, \
                     name VARCHAR(64) NULL, \
                     email VARCHAR(64) NULL, \
                     user_id VARCHAR(255) NOT NULL, \
                     PRIMARY KEY(id), \
                     UNIQUE KEY(user_id) \
                     ) ENGINE=MYISAM;'


class DBIssueMySQL(DBIssue):
    """
    MySQL subclass of L{DBIssue}.
    """
    __sql_table__ = 'CREATE TABLE IF NOT EXISTS issues ( \
                     id INTEGER NOT NULL AUTO_INCREMENT, \
                     tracker_id INTEGER NOT NULL, \
                     issue VARCHAR(255) NOT NULL, \
                     type VARCHAR(32) NULL, \
                     summary VARCHAR(255) NOT NULL, \
                     description TEXT NOT NULL, \
                     status VARCHAR(32) NOT NULL, \
                     resolution VARCHAR(32) NULL, \
                     priority VARCHAR(32) NULL, \
                     submitted_by INTEGER UNSIGNED NOT NULL, \
                     submitted_on DATETIME NOT NULL, \
                     assigned_to INTEGER UNSIGNED NOT NULL, \
                     PRIMARY KEY(id), \
                     UNIQUE KEY(issue, tracker_id), \
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

class DBIssuesWatchersMySQL(DBIssuesWatchers):
    """
    MySQL subclass of L{DBIssuesWatchers}
    """
    __sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_watchers ( \
                     id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT, \
                     issue_id INTEGER UNSIGNED NOT NULL, \
                     person_id INTEGER UNSIGNED NOT NULL, \
                     PRIMARY KEY(id), \
                     UNIQUE KEY(issue_id, person_id), \
                     INDEX issue_person_idx1(issue_id), \
                     INDEX issue_person_idx2(person_id), \
                     FOREIGN KEY(issue_id) \
                       REFERENCES issues(id) \
                         ON DELETE CASCADE \
                         ON UPDATE CASCADE, \
                     FOREIGN KEY(person_id) \
                       REFERENCES people(id) \
                         ON DELETE CASCADE \
                         ON UPDATE CASCADE \
                     ) ENGINE=MYISAM;'

class DBIssueRelationshipMySQL(DBIssueRelationship):
    """
    MySQL subclass of L{DBIssueRelationship}.
    """
    __sql_table__ = 'CREATE TABLE IF NOT EXISTS related_to ( \
                     id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT, \
                     issue_id INTEGER UNSIGNED NOT NULL, \
                     related_to INTEGER UNSIGNED NOT NULL, \
                     type VARCHAR(64) NOT NULL, \
                     PRIMARY KEY(id), \
                     UNIQUE KEY(issue_id, related_to, type), \
                     INDEX issues_related_idx1(issue_id), \
                     INDEX issues_related_idx2(related_to), \
                     FOREIGN KEY(issue_id) \
                       REFERENCES issues(id) \
                         ON DELETE CASCADE \
                         ON UPDATE CASCADE, \
                     FOREIGN KEY(related_to) \
                       REFERENCES issues(id) \
                         ON DELETE CASCADE \
                         ON UPDATE CASCADE \
                     ) ENGINE=MYISAM;'

class DBIssueTempRelationshipMySQL(DBIssueTempRelationship):
    """
    MySQL subclass of L{DBIssueTempRelationship}.
    """
    __sql_table__ = 'CREATE TEMPORARY TABLE temp_related_to ( \
                     id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT, \
                     issue_id INTEGER UNSIGNED NOT NULL, \
                     related_to VARCHAR(64) NOT NULL, \
                     type VARCHAR(64) NOT NULL, \
                     tracker_id INTEGER UNSIGNED NOT NULL, \
                     PRIMARY KEY(id), \
                     UNIQUE KEY(issue_id, related_to, type, tracker_id), \
                     INDEX issues_related_idx1(issue_id), \
                     FOREIGN KEY(issue_id) \
                       REFERENCES issues(id) \
                         ON DELETE CASCADE \
                         ON UPDATE CASCADE \
                     ) ENGINE=MYISAM;'


class DBCommentMySQL(DBComment):
    """
    MySQL subclass of L{DBComment}.
    """
    __sql_table__ = 'CREATE TABLE IF NOT EXISTS comments ( \
                     id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT, \
                     issue_id INTEGER UNSIGNED NOT NULL, \
                     comment_id INTEGER UNSIGNED, \
                     text TEXT NOT NULL, \
                     submitted_by INTEGER UNSIGNED NOT NULL, \
                     submitted_on DATETIME NOT NULL, \
                     PRIMARY KEY(id), \
                     INDEX comments_submitted_idx(submitted_by), \
                     INDEX comments_issue_idx(issue_id), \
                     FOREIGN KEY(submitted_by) \
                       REFERENCES people(id) \
                         ON DELETE SET NULL \
                         ON UPDATE CASCADE, \
                     FOREIGN KEY(issue_id) \
                       REFERENCES issues(id) \
                         ON DELETE CASCADE \
                         ON UPDATE CASCADE \
                     ) ENGINE=MYISAM;'


class DBAttachmentMySQL(DBAttachment):
    """
    MySQL subclass of L{DBAttachment}.
    """
    __sql_table__ = 'CREATE TABLE IF NOT EXISTS attachments ( \
                     id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT, \
                     issue_id INTEGER UNSIGNED NOT NULL, \
                     name VARCHAR(64) NOT NULL, \
                     description TEXT NOT NULL, \
                     url VARCHAR(255) NOT NULL, \
                     submitted_by INTEGER UNSIGNED, \
                     submitted_on DATETIME, \
                     PRIMARY KEY(id), \
                     INDEX attachments_submitted_idx(submitted_by), \
                     INDEX attachments_issue_idx(issue_id), \
                     FOREIGN KEY(submitted_by) \
                       REFERENCES people(id) \
                         ON DELETE SET NULL \
                         ON UPDATE CASCADE, \
                     FOREIGN KEY(issue_id) \
                       REFERENCES issues(id) \
                         ON DELETE CASCADE \
                         ON UPDATE CASCADE \
                     ) ENGINE=MYISAM;'


class DBChangeMySQL(DBChange):
    """
    MySQL subclass of L{DBChange}.
    """
    __sql_table__ = 'CREATE TABLE IF NOT EXISTS changes ( \
                     id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT, \
                     issue_id INTEGER UNSIGNED NOT NULL, \
                     field VARCHAR(64) NOT NULL, \
                     old_value VARCHAR(255) NOT NULL, \
                     new_value VARCHAR(255) NOT NULL, \
                     changed_by INTEGER UNSIGNED NOT NULL, \
                     changed_on DATETIME NOT NULL, \
                     PRIMARY KEY(id), \
                     INDEX changes_issue_idx(issue_id), \
                     INDEX changes_changed_idx(changed_by), \
                     FOREIGN KEY(issue_id) \
                       REFERENCES issues(id) \
                         ON DELETE CASCADE \
                         ON UPDATE CASCADE, \
                     FOREIGN KEY(changed_by) \
                       REFERENCES people(id) \
                         ON DELETE SET NULL \
                         ON UPDATE CASCADE \
                    ) ENGINE=MYISAM;'
