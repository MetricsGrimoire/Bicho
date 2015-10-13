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
import sys
import time
import urlparse

import dateutil.parser
import requests

from storm.locals import Int, DateTime, Reference, Unicode, Desc

from bicho.backends import Backend
from bicho.common import Tracker, People, Issue, Comment, Change
from bicho.config import Config
from bicho.utils import printout, printdbg, printerr

from bicho.db.database import DBIssue, DBTracker, DBBackend, get_database


STATUS_FIELD = unicode('status')
UPLOAD_FIELD = unicode('Upload')
CODE_REV_FIELD = unicode('Code-Review')

NEW_STATUS = unicode('NEW')
UPLOADED_STATUS = unicode('UPLOADED')
MERGED_STATUS = unicode('MERGED')
ABANDONED_STATUS = unicode('ABANDONED')


class DBReviewBoardIssueExt(object):
    __storm_table__ = 'issues_ext_reviewboard'

    id = Int(primary=True)
    issue_id = Int()
    updated_on = DateTime()
    branch = Unicode()
    uri = Unicode()

    issue = Reference(issue_id, DBIssue.id)

    def __init__(self, issue_id):
        self.issue_id = issue_id


class DBReviewBoardIssueExtMySQL(DBReviewBoardIssueExt):
    """
    MySQL subclass of L{DBReviewBoardIssueExt}
    """

    __sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_ext_reviewboard (\
                     id INTEGER NOT NULL AUTO_INCREMENT, \
                     issue_id INTEGER NOT NULL, \
                     updated_on DATETIME default NULL, \
                     branch TEXT, \
                     uri TEXT, \
                     PRIMARY KEY(id), \
                     UNIQUE KEY(issue_id), \
                     INDEX ext_issue_idx(issue_id), \
                     FOREIGN KEY(issue_id) \
                       REFERENCES issues(id) \
                         ON DELETE CASCADE \
                         ON UPDATE CASCADE \
                     ) ENGINE=MYISAM; '


class DBReviewBoardBackend(DBBackend):
    """
    Adapter for Trac backend.
    """
    def __init__(self):
        self.MYSQL_EXT = [DBReviewBoardIssueExtMySQL]

    def get_last_modification_date(self, store, tracker_id):
        result = store.find(DBReviewBoardIssueExt,
                            DBReviewBoardIssueExt.issue_id == DBIssue.id,
                            DBIssue.tracker_id == DBTracker.id,
                            DBTracker.id == tracker_id)

        if result.is_empty():
            return None

        db_issue_ext = result.order_by(Desc(DBReviewBoardIssueExt.updated_on))[0]
        updated_on = db_issue_ext.updated_on

        return updated_on

    def insert_issue_ext(self, store, issue, issue_id):
        is_new = False

        try:
            db_issue_ext = store.find(DBReviewBoardIssueExt,
                                      DBReviewBoardIssueExt.issue_id == issue_id).one()
            if not db_issue_ext:
                is_new = True
                db_issue_ext = DBReviewBoardIssueExt(issue_id)

                db_issue_ext.updated_on = issue.updated_on
                db_issue_ext.branch = issue.branch
                db_issue_ext.uri = issue.uri

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


class ReviewBoardIssue(Issue):
    """
    Ad-hoc Issue extension for ReviewBoard's issue
    """
    def __init__(self, issue, type, summary, desc, submitted_by, submitted_on):
        Issue.__init__(self, issue, type, summary, desc, submitted_by,
                       submitted_on)

        self.updated_on = None

    def set_branch(self, branch):
        """
        Set branch of the issue

        @param branch: branch
        @type branch: C{str}
        """
        self.branch = branch


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


class ReviewBoardAPIError(Exception):
    """Raised when an error occurs with ReviewBoard API Client"""

    def __init__(self, code, error):
        self.code = code
        self.error = error

    def __str__(self):
        return "%s - %s" % (self.code, self.error)


class ReviewBoardAPIClient(object):
    """Review Board API client"""

    URL = "%(base)s/api/%(method)s"
    HEADERS = {
               'User-Agent': 'bicho',
               'Content-Type' : 'application/json'
               }

    def __init__(self, url):
        self.url = url

    def review_requests(self, offset=None, limit=None, group=None, last_date=None):
        method = 'review-requests/'
        params = {'status' : 'all'}

        if offset:
            params['start'] = offset
        if limit:
            params['max-results'] = limit
        if group:
            params['to-groups'] = group
        if last_date:
            params['last-updated-from'] = last_date.isoformat()

        # Call REST API method
        result = self.call(method, params)

        return result

    def review_request_reviews(self, review_req_id):
        method = 'review-requests/%(review_req_id)s/reviews/'
        params = {}

        # Call REST API method
        resource = method % {'review_req_id' : review_req_id}
        result = self.call(resource, params)

        return result

    def review_request_changes(self, review_req_id):
        method = 'review-requests/%(review_req_id)s/changes/'
        params = {}

        # Call REST API method
        resource = method % {'review_req_id' : review_req_id}
        result = self.call(resource, params)

        return result

    def user(self, username):
        method = 'users/%(username)s/'
        params = {}

        # Call REST API method
        resource = method % {'username' : username}
        result = self.call(resource, params)

        return result

    def call(self, method, params):
        url = self.URL % {'base' : self.url, 'method' : method}

        req = requests.get(url, params=params,
                           headers=self.HEADERS)

        printdbg("Review Board %s method called: %s" % (method, req.url))

        # Raise HTTP errors, if any
        req.raise_for_status()

        result = req.json()

        # Check for possible API errors
        if 'err' in result:
            raise ReviewBoardAPIError(result['err']['code'],
                                      result['message'])

        return result


class ReviewBoard(Backend):

    def __init__(self):
        parts = urlparse.urlsplit(Config.url)

        self.url = Config.url
        self.base_url = parts.scheme + '://' + parts.netloc
        self.group = None
        self.max_issues = Config.nissues

        if parts.path and parts.path.startswith('/groups/'):
            group = parts.path.replace('/groups/', '')

            if group.endswith('/'):
                group = group[:-1]

            self.group = group

        self.delay = Config.delay
        self.identities = {}

        self.db = get_database(DBReviewBoardBackend())

        self.api_client = ReviewBoardAPIClient(self.base_url)

    def insert_tracker(self, url, group=None):
        self.db.insert_supported_traker('reviewboard', None)

        if group:
            url = url + '/groups/' + group

        trk = Tracker(url, 'reviewboard', None)
        dbtrk = self.db.insert_tracker(trk)

        return dbtrk

    def get_identity(self, username):
        if not username:
            return None

        if username in self.identities:
            return self.identities[username]

        result = self.api_client.user(username)
        raw_user = result['user']

        identity = People(username)

        if 'user' in result:
            if 'fullname' in raw_user:
                identity.name = raw_user['fullname']
            elif 'first_name' in raw_user:
                identity.name = '%s %s' % (raw_user['first_name'], raw_user['last_name'])

            if 'email' in raw_user:
                identity.email = raw_user['email']

        self.identities[username] = identity

        return identity

    def get_review_request(self, raw_rq):
        printdbg("Parsing review request %s - date: %s" \
                 % (raw_rq['id'], raw_rq['last_updated']))

        # Parse review request
        rq_id = unicode(raw_rq['id'])
        rq_type = 'review request'
        summary = raw_rq['summary']
        desc = raw_rq['description']
        status = raw_rq['status']
        branch = raw_rq['branch']
        url = raw_rq['absolute_url']

        submitted_on = self.str_to_datetime(raw_rq['time_added'])
        updated_on = self.str_to_datetime(raw_rq['last_updated'])

        # Retrieve submitter information
        submitted_by = self.get_identity(raw_rq['links']['submitter']['title'])

        # Create issue object
        rq = ReviewBoardIssue(rq_id, rq_type, summary, desc,
                              submitted_by, submitted_on)
        rq.set_status(status)
        rq.set_updated_on(updated_on)
        rq.set_branch(branch)
        rq.set_uri(url)

        # Get changes
        printdbg("Fetching review request changes from %s" % (rq_id))
        changes = self.fetch_review_changes(rq)

        # Get reviews
        printdbg("Fetching review request reviews from %s" % (rq_id))
        reviews = self.fetch_reviews(rq)

        # Complete review request activity
        activity = self.process_review_request_activity(changes, reviews)

        for a in activity:
            rq.add_change(a)

        printdbg("Review request %s parsed" % (raw_rq['id']))

        return rq

    def process_review_request_activity(self, changes, reviews):
        activity = [] + changes + reviews
        activity.sort(key=lambda x: x.changed_on)

        last_rev = unicode(1)

        for a in activity:
            if a.field == CODE_REV_FIELD:
                a.old_value = last_rev
            elif a.new_value != NEW_STATUS:
                last_rev = a.old_value
            else:
                continue
        return activity

    def fetch_reviews(self, rq):
        result = self.api_client.review_request_reviews(rq.issue)
        raw_reviews = result['reviews']

        reviews = []

        for raw_rv in reversed(raw_reviews):
            ts = raw_rv['timestamp']
            dt = self.str_to_datetime(ts)

            if raw_rv['ship_it'] == True:
                value = unicode(2)
            else:
                value = unicode(-1)

            # Retrieve reviewer information
            author = self.get_identity(raw_rv['links']['user']['title'])

            # Old value will be updated later
            code_rev_ch = Change(CODE_REV_FIELD, None, value, author, dt)

            reviews.append(code_rev_ch)

        return reviews

    def fetch_review_changes(self, rq):
        result = self.api_client.review_request_changes(rq.issue)
        raw_changes = result['changes']

        last_rev = unicode(1)
        author = rq.submitted_by

        # Create first two changes
        upload_ch = Change(UPLOAD_FIELD, last_rev, None, author, rq.submitted_on)
        status_ch = Change(STATUS_FIELD, None, NEW_STATUS, author, rq.submitted_on)

        changes = [upload_ch, status_ch]

        for raw_ch in reversed(raw_changes):
            ch_fields = raw_ch['fields_changed']

            # New patch
            if 'diff' in ch_fields:
                revision = unicode(ch_fields['diff']['added']['revision'])

                ts = ch_fields['diff']['added']['timestamp']
                dt = self.str_to_datetime(ts)

                # Two entries per patch (upload and status)
                upload_ch = Change(UPLOAD_FIELD, revision, None, author, dt)
                status_ch = Change(STATUS_FIELD, revision, UPLOADED_STATUS, author, dt)

                changes.append(upload_ch)
                changes.append(status_ch)

                # Update last revision
                last_rev = revision
            elif 'status' in ch_fields:
                value = ch_fields['status']['new']
                ts = raw_ch['timestamp']
                dt = self.str_to_datetime(ts)

                if value == 'S':
                    status = MERGED_STATUS
                elif value == 'D':
                    status = ABANDONED_STATUS
                elif value == 'P':
                    status = UPLOADED_STATUS
                else:
                    raise Exception("Invalid status %s" % value)

                if status == UPLOADED_STATUS:
                    revision = unicode(int(last_rev) + 1)
                    status_ch = Change(STATUS_FIELD, revision, status, author, dt)
                else:
                    status_ch = Change(STATUS_FIELD, last_rev, status, None, dt)

                changes.append(status_ch)
            else:
                continue

        return changes

    def str_to_datetime(self, s):
        return dateutil.parser.parse(s, ignoretz=True)

    def fetch_and_store(self):
        printdbg("Fetching reviews from")

        total_rqs = 0
        nrqs = 0
        offset = 0

        # Insert tracker information
        dbtrk = self.insert_tracker(self.base_url, self.group)

        last_mod_date = self.db.get_last_modification_date(tracker_id=dbtrk.id)

        if last_mod_date:
            printdbg("Last modification date stored: %s" % last_mod_date)

        printout("Fetching reviews requests from %s to %s" % (offset, offset + self.max_issues))

        result = self.api_client.review_requests(offset=offset,
                                                 limit=self.max_issues,
                                                 group=self.group,
                                                 last_date=last_mod_date)
        raw_rqs = result['review_requests']

        while raw_rqs:
            total_rqs += len(raw_rqs)

            for raw_rq in raw_rqs:
                rq = self.get_review_request(raw_rq)

                # Insert review request
                self.db.insert_issue(rq, dbtrk.id)
                nrqs += 1

            time.sleep(self.delay)

            offset += self.max_issues
            printout("Fetching reviews requests from %s to %s" % (offset, offset + self.max_issues))

            result = self.api_client.review_requests(offset=offset,
                                                     limit=self.max_issues,
                                                     group=self.group,
                                                     last_date=last_mod_date)
            raw_rqs = result['review_requests']

        printout("Done. %s review requests analyzed from %s" % (nrqs, total_rqs))

    def run(self):
        printout("Running Bicho - url: %s" % self.url)

        try:
            self.fetch_and_store()
        except (requests.exceptions.HTTPError, ReviewBoardAPIError), e:
            printerr("Error: %s" % e)
            sys.exit(1)

Backend.register_backend('reviewboard', ReviewBoard)
