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
from Bicho.Config import Config
from Bicho.utils import printerr, printdbg, printout
from Bicho.common import Tracker, People, Issue, Comment, Change
from Bicho.db.database import DBIssue, DBBackend, get_database, DBTracker,\
     DBPeople
from storm.locals import DateTime, Int, Reference, Unicode, Desc, Store, \
     create_database
from storm.exceptions import NotOneError
import xml.sax.handler

from dateutil.parser import parse
from datetime import datetime

from Bicho.Config import Config


class DBIssuesLog(object):
    """
    Object shared by all the different issue log tables
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

def get_issue_logger(backend):
    if backend == 'jira':
        from issues_log_jira import JiraIssuesLog
        return JiraIssuesLog()
    elif backend == 'bg':
        from issues_log_bugzilla import BugzillaIssuesLog
        return BugzillaIssuesLog()

class IssuesLog():

    def __init__(self):
        self._connect()
        # it is not incremental so we first drop the table
        self._drop_db()
        self._create_db()

    def _connect(self):
        opts = Config()

        self.database = create_database('mysql://' + opts.db_user_out + ':'
                                        + opts.db_password_out + '@'
                                        + opts.db_hostname_out + ':'
                                        + opts.db_port_out + '/'
                                        + opts.db_database_out)
        self.store = Store(self.database)

    def _create_db(self):
        self.store.execute(self._get_sql_create())

    def _drop_db(self):
        self.store.execute(self._get_sql_drop())

    def _get_people_id(self, email, tracker_id):
        """
        Gets the id of an user
        """
        try:
            p = self.store.find(DBPeople, DBPeople.email == email,
                                DBPeople.tracker_id == tracker_id).one()
            return p.id
        except (AttributeError, NotOneError):
            p = self.store.find(DBPeople, DBPeople.user_id == email,
                                DBPeople.tracker_id == tracker_id).one()
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

    def _get_sql_drop(self):
        """
        Abstract method for inserting extra data related to a change
        """
        raise NotImplementedError

    def _get_sql_create(self):
        """
        Abstract method for inserting extra data related to a change
        """
        raise NotImplementedError

    def _get_tracker_id(self, issue_id):
        """
        Returns tracker id from issues
        """
        result = self.store.find(DBIssue.tracker_id,
                                 DBIssue.id == issue_id).one()
        return result

    def _copy_issue_ext(self, aux, db_ilog):
        """
        Abstract method for inserting extra data related to a change
        """
        raise NotImplementedError

    def _copy_issue(self, db_ilog):
        """
        This method returns a copy of the DB*Log object
        """
        aux = self._get_dbissues_object(db_ilog.issue, db_ilog.tracker_id)
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
        aux = self._copy_issue_ext(aux, db_ilog)
        return aux

    def _assign_values(self, db_ilog, field, value):
        """
        Abstract method for inserting extra data related to a change
        """
        raise NotImplementedError

    def _build_initial_state(self, db_ilog):
        """
        This method gets the first changes of every field in
        order to get the initial state of the bug
        """
        fields = self.store.execute("SELECT DISTINCT(field) FROM changes " +
                                    "WHERE issue_id=%s" % (db_ilog.issue_id))

        for f in fields:
            values = self.store.execute(
                "SELECT old_value FROM changes WHERE issue_id=%s AND \
                field=\"%s\" ORDER BY changed_on LIMIT 1"
                % (db_ilog.issue_id, f[0]))
            for v in values:
                db_ilog = self._assign_values(db_ilog, f[0], v[0])
        return db_ilog

    def _get_dbissues_object(self, issue_name, tracker_id):
        """
        Abstract method for inserting extra data related to a change
        """
        raise NotImplementedError

    def _copy_standard_values(self, issue, issue_log):
        """
        Copy the standard values from the issue object to the issue_log object
        """
        issue_log.issue_id = issue.id
        issue_log.type = issue.type
        issue_log.summary = issue.summary
        issue_log.description = issue.description
        issue_log.status = issue.status
        issue_log.resolution = issue.resolution
        issue_log.priority = issue.priority
        issue_log.submitted_by = issue.submitted_by
        issue_log.date = issue.submitted_on
        issue_log.assigned_to = issue.assigned_to
        return issue_log

    def _print_final_msg(self):
        """
        Abstract method for inserting extra data related to a change
        """
        raise NotImplementedError

    def _get_changes(self, issue_id):
        aux = self.store.execute("SELECT field, new_value, changed_by, \
        changed_on FROM changes where issue_id=%s" % (issue_id))
        return aux  

    def run(self):
        issues = self.store.find(DBIssue)
        for i in issues:
            db_ilog = self._get_dbissues_object(i.issue, i.tracker_id)
            db_ilog = self._copy_standard_values(i, db_ilog)

            db_ilog = self._build_initial_state(db_ilog)

            self.store.add(db_ilog)
            self.store.flush()

            # the code below gets all the changes and insert a row per change
            changes = self._get_changes(db_ilog.issue_id)
            
            for ch in changes:
                field = ch[0]
                new_value = ch[1]
                changed_by = ch[2]
                date = ch[3]
                # we need a new object to be inserted in the database
                db_ilog = self._copy_issue(db_ilog)
                db_ilog.date = date
                db_ilog = self._assign_values(db_ilog, field, new_value)

                try:
                    self.store.add(db_ilog)
                    self.store.flush()
                except:
                    # self.store.rollback() # is this useful in this context?
                    traceback.print_exc()
            self.store.commit()
        self._print_final_msg()
