# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Bitergia
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
# Authors:  Santiago Dueñas <sduenas@bitergia.com>
#

import datetime
import json
import sys

import dateutil.parser
import requests

from storm.locals import DateTime, Int, Float, Reference, Unicode, Desc

from bicho.backends import Backend
from bicho.common import Tracker, People, Issue, Comment, Change
from bicho.config import Config
from bicho.utils import printout, printdbg, printerr
from bicho.db.database import DBIssue, DBTracker, DBBackend, get_database


class DBTracIssueExt(object):
    __storm_table__ = 'issues_ext_trac'

    id = Int(primary=True)
    issue_id = Int()
    milestone = Unicode()
    component = Unicode()
    keywords = Unicode()
    version = Unicode
    rhbz = Float()
    uri = Unicode()
    updated_on = DateTime()

    issue = Reference(issue_id, DBIssue.id)

    def __init__(self, issue_id):
        self.issue_id = issue_id


class DBTracIssueExtMySQL(DBTracIssueExt):
    """
    MySQL subclass of L{DBTracIssueExt}
    """

    __sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_ext_trac (\
                     id INTEGER NOT NULL AUTO_INCREMENT, \
                     issue_id INTEGER NOT NULL, \
                     milestone VARCHAR(64) default NULL, \
                     component VARCHAR(64) default NULL, \
                     version VARCHAR(64) default NULL, \
                     keywords TEXT default NULL, \
                     rhbz FLOAT default NULL, \
                     uri VARCHAR(255) default NULL, \
                     updated_on DATETIME default NULL, \
                     PRIMARY KEY(id), \
                     UNIQUE KEY(issue_id), \
                     INDEX ext_issue_idx(issue_id), \
                     FOREIGN KEY(issue_id) \
                       REFERENCES issues(id) \
                         ON DELETE CASCADE \
                         ON UPDATE CASCADE \
                     ) ENGINE=MYISAM; '

class DBTracBackend(DBBackend):
    """
    Adapter for Trac backend.
    """
    def __init__(self):
        self.MYSQL_EXT = [DBTracIssueExtMySQL]

    def get_last_modification_date(self, store, tracker_id):
        result = store.find(DBTracIssueExt,
                            DBTracIssueExt.issue_id == DBIssue.id,
                            DBIssue.tracker_id == DBTracker.id,
                            DBTracker.id == tracker_id)

        if result.is_empty():
            return None

        db_issue_ext = result.order_by(Desc(DBTracIssueExt.updated_on))[0]
        updated_on = db_issue_ext.updated_on

        return updated_on

    def insert_issue_ext(self, store, issue, issue_id):
        is_new = False

        try:
            db_issue_ext = store.find(DBTracIssueExt,
                                      DBTracIssueExt.issue_id == issue_id).one()
            if not db_issue_ext:
                is_new = True
                db_issue_ext = DBTracIssueExt(issue_id)

                db_issue_ext.milestone = self.__to_unicode(issue.milestone)
                db_issue_ext.component = self.__to_unicode(issue.component)
                db_issue_ext.keywords = self.__to_unicode(issue.keywords)
                db_issue_ext.version = self.__to_unicode(issue.version)
                db_issue_ext.rhbz = issue.rhbz
                db_issue_ext.uri = self.__to_unicode(issue.uri)
                db_issue_ext.updated_on = issue.updated_on

            if is_new:
                store.add(db_issue_ext)

            store.flush()
        except:
            store.rollback()
            raise

    def insert_comment_ext(self, store, comment, comment_id):
        pass

    def insert_attachment_ext(self, store, attch, attch_id):
        pass

    def insert_change_ext(self, store, change, change_id):
        pass

    def insert_temp_rel(self, store, temp_relationship, trel_id, tracker_id):
        pass

    def __to_unicode(self, s):
        if s:
            return unicode(s)
        else:
            return None


class TracIssue(Issue):
    """
    Ad-hoc Issue extension for Maniphest's issue
    """
    def __init__(self, issue, type, summary, desc, submitted_by, submitted_on):
        Issue.__init__(self, issue, type, summary, desc, submitted_by,
                       submitted_on)

        self.milestone = None
        self.component = None
        self.keywords = None
        self.version = None
        self.rhbz = None
        self.uri = None
        self.updated_on = None

    def set_milestone(self, milestone):
        """
        Set the milestone of the issue

        @param milestone: milestone of the issue
        @type milestone: C{str}
        """
        self.milestone = milestone if milestone else None

    def set_component(self, component):
        """
        Set the component of the issue

        @param component: component of the issue
        @type component: C{str}
        """
        self.component = component if component else None

    def set_keywords(self, keywords):
        """
        Set the keywords of the issue

        @param keywords: keywords of the issue
        @type keywords: C{str}
        """
        self.keywords = keywords if keywords else None

    def set_version(self, version):
        """
        Set the version of the issue

        @param version: version of the issue
        @type version: C{str}
        """
        self.version = version if version else None

    def set_rhbz(self, rhbz):
        """
        Set rhbz of the issue

        @param rhbz: rhbz
        @type rhbz: C{str}
        """
        try:
            self.rhbz = float(rhbz)
        except ValueError:
            self.rhbz = None

    def set_uri(self, uri):
        """
        Set the uri of the issue

        @param uri: uri of the issue
        @type uri: C{str}
        """
        self.uri = uri

    def set_updated_on(self, updated_on):
        """
        Set the updated_on of the issue

        @param updated_on: date when the issue was updated
        @type updated_on: L{datetime.datetime}
        """
        if not isinstance(updated_on, datetime.datetime):
            raise ValueError('Parameter "updated_on" should be a %s '
                             'instance. %s given.' %
                             ('datetime', input.__class__.__name__))
        self.updated_on = updated_on


class TracRPCError(Exception):
    """Raised when an error occurs with Trac JSON RPC Client"""

    def __init__(self, code, error):
        self.code = code
        self.error = error

    def __str__(self):
        return "%s - %s" % (self.code, self.error)


class TracRPC(object):
    """Trac JSON RPC"""

    HEADERS = {
               'User-Agent' : 'bicho',
               'Content-Type' : 'application/json'
               }

    def __init__(self, url):
        self.url = url

    def tickets(self, since=None):
        """Returns a list of IDs of tickets that have changed since timestamp."""

        method = 'ticket.getRecentChanges'
        params = [{}]

        if since:
            params[0]['__jsonclass__'] = ['datetime', since.isoformat()]

        result = self.call(method, params)
        return result

    def ticket(self, ticket_id):
        """Fetch a ticket. Returns [id, time_created, time_changed, attributes]."""

        method = 'ticket.get'
        params = [ticket_id]

        result = self.call(method, params)
        return result

    def changes(self, ticket_id):
        """Return the changelog as a list of tuples of the form
         (time, author, field, oldvalue, newvalue, permanent)."""

        method = 'ticket.changeLog'
        params = [ticket_id]

        result = self.call(method, params)
        return result

    def call(self, method, params):
        # POST parameters
        data = {'method': method, 'params': params}
        data = json.dumps(data)

        res = requests.post('%s/jsonrpc' % self.url,
                            headers=self.HEADERS,
                            data=data)
        printdbg("Trac RPC %s method called: %s" % (method, res.url))

        # Raise HTTP errors, if any
        res.raise_for_status()

        # Check for possible Conduit API errors
        result = res.json()

        if result['error']:
            raise TracRPCError(result['error']['code'],
                               result['error']['message'])

        return result['result']


class Trac(Backend):

    def __init__(self):
        self.url = Config.url

        if self.url.endswith('/'):
            self.url = Config.url[0:-1]

        self.delay = Config.delay
        self.identities = {}

        self.db = get_database(DBTracBackend())

        self.trac_rpc = TracRPC(self.url)

    def insert_tracker(self, url):
        self.db.insert_supported_traker('trac', None)

        trk = Tracker(url, 'trac', None)
        dbtrk = self.db.insert_tracker(trk)

        return dbtrk

    def get_datetime_from_json_obj(self, obj):
        dt = obj['__jsonclass__'][1]
        return dateutil.parser.parse(dt)

    def get_uri(self, ticket_id):
        return self.url + '/ticket/' + str(ticket_id)

    def get_identity(self, username):
        identity = self.identities.get(username, None)

        if identity:
            return identity

        identity = People(username)
        self.identities[username] = identity

        return identity

    def get_issue_from_ticket(self, ticket):
        printdbg("Parsing ticket %s" % (ticket[0]))

        # Parse dates
        submitted_on = self.get_datetime_from_json_obj(ticket[1])
        updated_on = self.get_datetime_from_json_obj(ticket[2])

        # Parse ticket attribs
        attrs = ticket[3]

        issue_id = ticket[0]
        task_type = attrs['type']
        summary = attrs['summary']
        description = attrs['description']
        status = attrs['status']
        
        resolution = attrs['resolution']

        component = attrs['component']
        keywords = attrs['keywords']
        version = attrs['version']

        # Authors
        submitted_by = self.get_identity(attrs['reporter'])
        assigned_to = self.get_identity(attrs['owner'])

        # Create issue object
        issue = TracIssue(issue_id, task_type, summary, description,
                          submitted_by, submitted_on)
        issue.set_status(status)
        
        issue.set_resolution(resolution)

        issue.set_updated_on(updated_on)
        issue.set_uri(self.get_uri(issue_id))
        issue.set_component(component)
        issue.set_keywords(keywords)
        issue.set_version(version)

        if assigned_to:
            issue.set_assigned(assigned_to)

        if 'priority' in attrs:
            issue.set_priority(attrs['priority'])

        if 'milestone' in attrs:
            issue.set_milestone(attrs['milestone'])
            
        if 'rhbz' in attrs:
            issue.set_rhbz(attrs['rhbz'])

        # Retrieve CCs
        subscribers = attrs['cc']

        for subscriber in subscribers:
            identity = self.get_identity(subscriber)
            issue.add_watcher(identity)

        # Retrieve comments and changes
        ticket_changes = self.trac_rpc.changes(ticket[0])
        comments, changes = self.get_events_from_changes(ticket_changes)

        for comment in comments:
            issue.add_comment(comment)
        for change in changes:
            issue.add_change(change)

        printdbg("Ticket %s parsed" % (ticket[0]))

        return issue

    def get_events_from_changes(self, ticket_changes):
        comments = []
        changes = []

        # time, author, field, oldvalue, newvalue, permanent
        for ch in ticket_changes:
            dt = self.get_datetime_from_json_obj(ch[0])
            author = self.get_identity(ch[1])
            field = ch[2]
            old_value = unicode(ch[3]) if ch[3] else None
            new_value = unicode(ch[4]) if ch[4] else None

            if field == 'comment' and new_value:
                comment = Comment(new_value, author, dt)
                comments.append(comment)
            else:
                change = Change(field, old_value, new_value, author, dt)
                changes.append(change)

        return comments, changes

    def fetch_and_store_tickets(self):
        printdbg("Fetching tickets")

        nbugs = 0

        # Insert tracker information
        dbtrk = self.insert_tracker(self.url)

        last_mod_date = self.db.get_last_modification_date(tracker_id=dbtrk.id)

        if last_mod_date:
            printdbg("Last modification date stored: %s" % last_mod_date)

        trac_tickets = self.trac_rpc.tickets(last_mod_date)

        for ticket_id in trac_tickets:
            printdbg("Fetching ticket %s" % str(ticket_id))
            ticket = self.trac_rpc.ticket(ticket_id)

            issue = self.get_issue_from_ticket(ticket)

            # Insert issue
            self.db.insert_issue(issue, dbtrk.id)

            nbugs += 1

        printout("Done. %s bugs analyzed from %s" % (nbugs, len(trac_tickets)))

    def run(self):
        printout("Running Bicho - %s" % self.url)

        try:
            self.fetch_and_store_tickets()
        except (requests.exceptions.HTTPError, TracRPCError), e:
            printerr("Error: %s" % e)
            sys.exit(1)


Backend.register_backend('trac', Trac)
