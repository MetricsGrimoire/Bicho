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
import time

import requests

from storm.locals import DateTime, Int, Float, Reference, Unicode, Desc

from bicho.config import Config
from bicho.utils import printout, printdbg, printerr
from bicho.backends import Backend
from bicho.common import Tracker, People, Issue, Comment, Change
from bicho.db.database import DBIssue, DBTracker, DBBackend, NotFoundError, get_database


def unix_to_datetime(timestamp):
    return datetime.datetime.fromtimestamp(float(timestamp))

def datetime_to_unix(dt):
    return time.mktime(dt.timetuple())


class DBManiphestIssueExt(object):
    __storm_table__ = 'issues_ext_maniphest'

    id = Int(primary=True)
    issue_id = Int()
    phid = Unicode()
    object_name = Unicode()
    status_name = Unicode()
    priority_color = Unicode()
    points = Float()
    uri = Unicode()
    updated_on = DateTime()

    issue = Reference(issue_id, DBIssue.id)

    def __init__(self, issue_id):
        self.issue_id = issue_id


class DBManiphestProject(object):
    __storm_table__ = 'projects_maniphest'

    id = Int(primary=True)
    name = Unicode()
    phid = Unicode()

    def __init__(self, name, phid):
        self.name = name
        self.phid = phid


class DBManiphestIssueProject(object):
    __storm_table__ = 'issues_projects_maniphest'

    id = Int(primary=True)
    issue_id = Int()
    project_id = Int()

    issue = Reference(issue_id, DBIssue.id)
    relationship = Reference(project_id, DBManiphestProject.id)

    def __init__(self, issue_id, project_id):
        self.issue_id = issue_id
        self.project_id = project_id


class DBManiphestIssueExtMySQL(DBManiphestIssueExt):
    """
    MySQL subclass of L{DBManiphestIssueExt}
    """

    __sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_ext_maniphest (\
                     id INTEGER NOT NULL AUTO_INCREMENT, \
                     issue_id INTEGER NOT NULL, \
                     phid VARCHAR(64) default NULL, \
                     status_name VARCHAR(64) default NULL, \
                     object_name VARCHAR(32) default NULL, \
                     priority_color VARCHAR(32) default NULL, \
                     points FLOAT default NULL, \
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


class DBManiphestProjectMySQL(DBManiphestProject):
    """
    MySQL subclass of L{DBManiphestProject}
    """

    __sql_table__ = 'CREATE TABLE IF NOT EXISTS projects_maniphest (\
                     id INTEGER NOT NULL AUTO_INCREMENT, \
                     name VARCHAR(64) NOT NULL, \
                     phid VARCHAR(64) NOT NULL, \
                     PRIMARY KEY(id), \
                     UNIQUE KEY(phid), \
                     INDEX ph_project_idx(phid) \
                     ) ENGINE=MYISAM; '


class DBManiphestIssuesProjectstMySQL(DBManiphestIssueProject):
    """
    MySQL subclass of L{DBManiphestIssueProject}
    """

    __sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_projects_maniphest (\
                     id INTEGER NOT NULL AUTO_INCREMENT, \
                     issue_id INTEGER NOT NULL, \
                     project_id INTEGER NOT NULL, \
                     PRIMARY KEY(id), \
                     UNIQUE KEY(issue_id, project_id), \
                     INDEX ph_issue_idx(issue_id), \
                     INDEX ph_project_idx(project_id), \
                     FOREIGN KEY(issue_id) \
                       REFERENCES issues(id) \
                         ON DELETE CASCADE \
                         ON UPDATE CASCADE, \
                     FOREIGN KEY(project_id) \
                       REFERENCES projects_maniphest(id) \
                         ON DELETE CASCADE \
                         ON UPDATE CASCADE \
                     ) ENGINE=MYISAM; '



class DBManiphestBackend(DBBackend):
    """
    Adapter for Maniphest backend.
    """
    def __init__(self):
        self.MYSQL_EXT = [DBManiphestIssueExtMySQL, DBManiphestProjectMySQL,
                          DBManiphestIssuesProjectstMySQL]

    def get_last_modification_date(self, store, tracker_id):
        result = store.find(DBManiphestIssueExt,
                            DBManiphestIssueExt.issue_id == DBIssue.id,
                            DBIssue.tracker_id == DBTracker.id,
                            DBTracker.id == tracker_id)

        if result.is_empty():
            return None

        db_issue_ext = result.order_by(Desc(DBManiphestIssueExt.updated_on))[0]
        updated_on = db_issue_ext.updated_on

        return updated_on

    def insert_issue_ext(self, store, issue, issue_id):
        is_new = False

        try:
            db_issue_ext = store.find(DBManiphestIssueExt,
                                      DBManiphestIssueExt.issue_id == issue_id).one()
            if not db_issue_ext:
                is_new = True
                db_issue_ext = DBManiphestIssueExt(issue_id)

            db_issue_ext.phid = self.__to_unicode(issue.phid)
            db_issue_ext.object_name = self.__to_unicode(issue.object_name)
            db_issue_ext.status_name = self.__to_unicode(issue.status_name)
            db_issue_ext.priority_color = self.__to_unicode(issue.priority_color)
            db_issue_ext.points = issue.points
            db_issue_ext.uri = self.__to_unicode(issue.uri)
            db_issue_ext.updated_on = issue.updated_on

            if is_new:
                store.add(db_issue_ext)

            store.flush()
        except:
            store.rollback()
            raise

        # Remove all relationships
        self.remove_issues_projects(store, issue_id)

        # Insert projects relationships
        for project in issue.projects:
            # Update relationships
            db_project = self.insert_project(store, project)
            self.insert_issue_project(store, issue_id, db_project.id)

        return db_issue_ext

    def insert_project(self, store, project):
        try:
            db_project = DBManiphestProject(unicode(project.name),
                                            unicode(project.phid))
            store.add(db_project)
            store.commit()
        except:
            db_project = self._get_db_project(store, project.phid)
            db_project.name = project.name
            store.commit()
        return db_project

    def insert_issue_project(self, store, issue_id, project_id):
        try:
            db_rel = DBManiphestIssueProject(issue_id, project_id)
            store.add(db_rel)
            store.commit()
        except:
            pass

    def remove_issues_projects(self, store, issue_id):
        result = self._get_db_issues_projects(store, issue_id)

        for r in result:
            store.remove(r)
        store.commit()

    def insert_comment_ext(self, store, comment, comment_id):
        pass

    def insert_attachment_ext(self, store, attch, attch_id):
        pass

    def insert_change_ext(self, store, change, change_id):
        pass

    def insert_temp_rel(self, store, temp_relationship, trel_id, tracker_id):
        pass

    def _get_db_project(self, store, phid):
        db_project = store.find(DBManiphestProject,
                                DBManiphestProject.phid == unicode(phid)).one()
        if not db_project:
            raise NotFoundError('Maniphest project %s not found' % phid)
        return db_project

    def _get_db_issues_projects(self, store, issue_id):
        result = store.find(DBManiphestIssueProject,
                            DBManiphestIssueProject.issue_id == issue_id)
        return result

    def __to_unicode(self, s):
        if s:
            return unicode(s)
        else:
            return None


class ManiphestProject(object):
    """
    Project class for Maniphest backend
    """
    def __init__(self, name, phid):
        self.name = name
        self.phid = phid


class ManiphestIssue(Issue):
    """
    Ad-hoc Issue extension for Maniphest's issue
    """
    def __init__(self, issue, type, summary, desc, submitted_by, submitted_on):
        Issue.__init__(self, issue, type, summary, desc, submitted_by,
                       submitted_on)

        self.phid = None
        self.object_name = None
        self.status_name = None
        self.priority_color = None
        self.points = None
        self.uri = None
        self.updated_on = None
        self.projects = []

    def set_phid(self, phid):
        """
        Set the phid of the issue

        @param phid: phid of the issue
        @type phid: C{str}
        """
        self.phid = phid

    def set_object_name(self, object_name):
        """
        Set the object name of the issue

        @param object_name: object name of the issue
        @type object_name: C{str}
        """
        self.object_name = object_name

    def set_status_name(self, status_name):
        """
        Set the status name of the issue

        @param status_name: status of the issue
        @type status_name: C{str}
        """
        self.status_name = status_name

    def set_priority_color(self, priority_color):
        """
        Set the priority color of the issue

        @param priority_color: priority color of the issue
        @type priority_color: C{str}
        """
        self.priority_color = priority_color

    def set_points(self, points):
        """
        Set the points of the issue

        @param priority_color: priority color of the issue
        @type priority_color: C{str}
        """
        self.points = float(points)

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

    def add_project(self, project):
        """
        Add a project to the issue.

        @param project: project where this issue is assigned
        @type project: L{ManiphestProject}

        @raise ValueError: raised if the type of X{project} is not valid.
        """
        if not isinstance(project, ManiphestProject):
            raise ValueError('Parameter "project" should be a %s instance. %s given.' %
                             ('ManiphestProject', project.__class__.__name__,))
        self.projects.append(project)


class ConduitError(Exception):
    """Raised when an error occurs with Conduit Client"""

    def __init__(self, code, error):
        self.code = code
        self.error = error

    def __str__(self):
        return "%s - %s" % (self.code, self.error)


class Conduit(object):
    """Conduit Client"""

    HEADERS = {'User-Agent': 'bicho'}

    def __init__(self, url, token):
        self.url = url
        self.token = token

    def whoami(self):
        method = 'user.whoami'
        params = {}

        result = self.call(method, params)
        return result

    def users(self, phids):
        method = 'user.query'
        params = {'phids' : phids,
                  'limit' : len(phids)}

        result = self.call(method, params)
        return result

    def projects(self, phids):
        if not phids:
            return []

        method = 'project.query'
        params = {'phids' : phids}

        result = self.call(method, params)

        prjs = [p for p in result['data'].values()]

        return prjs

    def tasks(self, offset=None, limit=None):
        method = 'maniphest.query'
        params = {'order' : 'order-modified'}

        if offset:
            params['offset'] = offset
        if limit:
            params['limit'] = limit

        result = self.call(method, params)

        ph_tasks = sorted(result.items(),
                          key=lambda x : x[1]['dateModified'],
                          reverse=True)

        ph_tasks = [pht[1] for pht in ph_tasks]

        return ph_tasks

    def info(self, task_id):
        method = 'maniphest.info'
        params = {'task_id' : task_id}

        result = self.call(method, params)
        return result

    def transactions(self, task_id):
        method = 'maniphest.gettasktransactions'
        params = {'ids' : [task_id]}

        result = self.call(method, params)

        ph_trans = result[task_id]
        ph_trans.sort(key=lambda x : x['dateCreated'])

        return ph_trans

    def call(self, method, params):
        # Conduit parameters
        params['__conduit__'] = {'token' : self.token}

        # POST parameters
        data = {'params' : json.dumps(params),
                'output' : 'json',
                '__conduit__' : True}

        req = requests.post('%s/api/%s' % (self.url, method),
                            headers=self.HEADERS,
                            data=data)
        printdbg("Conduit %s method called: %s" % (method, req.url))

        # Raise HTTP errors, if any
        req.raise_for_status()

        # Check for possible Conduit API errors
        result = req.json()

        if result['error_code']:
            raise ConduitError(result['error_code'],
                               result['error_info'])

        return result['result']


class Maniphest(Backend):

    def __init__(self):
        self.url = Config.url
        self.delay = Config.delay
        self.max_issues = Config.nissues
        self.db = get_database(DBManiphestBackend())

        self.identities = {}
        self.projects = {}

        try:
            self.backend_token = Config.backend_token
            self.conduit = Conduit(self.url, self.backend_token)
        except AttributeError:
            printerr("Error: --backend-token is mandatory to download issues from Maniphest\n")
            sys.exit(1)

    def up_to_date(self, last_mod_date, pht):
        # If the next issue to parse is older than the issue
        # we had stored at the beginning, that "means" we already
        # have updated the set
        if not last_mod_date:
            return False

        updated_on = unix_to_datetime(pht['dateModified'])
        return last_mod_date > updated_on

    def insert_tracker(self, url):
        self.db.insert_supported_traker('maniphest', None)

        trk = Tracker(url, 'maniphest', None)
        dbtrk = self.db.insert_tracker(trk)

        return dbtrk

    def check_auth(self):
        # Check conduit credentials
        try:
            printdbg("Checking conduit credentials")
            self.conduit.whoami()
            printdbg("Credentials checked")

            return True
        except (requests.exceptions.HTTPError, ConduitError), e:
            printerr("Error: %s" % e)
            return False

    def get_issue_from_task(self, pht):
        printdbg("Parsing task %s (%s) - date: %s" \
                 % (pht['objectName'], pht['phid'], pht['dateModified']))

        # Parse task
        issue_id = pht['id']
        summary = pht['title']
        description = pht['description']
        submitted_on = unix_to_datetime(pht['dateCreated'])
        updated_on = unix_to_datetime(pht['dateModified'])
        status = pht['status']
        priority = pht['priority']
        resolution = 'closed' if pht['isClosed'] else None
        phid = pht['phid']
        object_name = pht['objectName']
        status_name = pht['statusName']
        priority_color = pht['priorityColor']
        uri = pht['uri']

        # Retrieve author and owner information
        submitted_by = self.get_identity(pht['authorPHID'])
        assigned_to = self.get_identity(pht['ownerPHID'])

        # Create issue object
        issue = ManiphestIssue(issue_id, 'task', summary, description,
                               submitted_by, submitted_on)
        issue.set_updated_on(updated_on)
        issue.set_status(status)
        issue.set_status_name(status_name)
        issue.set_resolution(resolution)
        issue.set_priority(priority)
        issue.set_priority_color(priority_color)

        if assigned_to:
            issue.set_assigned(assigned_to)

        issue.set_object_name(object_name)
        issue.set_phid(phid)
        issue.set_uri(uri)

        # Retrieve points
        points = pht['auxiliary']['isdc:sprint:storypoints']
        if points:
            issue.set_points(points)

        # Retrieve project information
        if pht['projectPHIDs']:
            projects = self.get_projects(pht['projectPHIDs'])

            for project in projects:
                issue.add_project(project)

        # Retrieve comments and changes
        phtrans = self.conduit.transactions(pht['id'])
        comments, changes = self.get_events_from_transactions(phtrans)

        for comment in comments:
            issue.add_comment(comment)
        for change in changes:
            issue.add_change(change)

        printdbg("Task %s (%s) parsed" % (pht['objectName'], pht['phid']))

        return issue

    def get_events_from_transactions(self, phtrans):
        comments = []
        changes = []

        for phtr in phtrans:
            printdbg("Parsing transaction %s - date: %s" \
                     % (phtr['transactionPHID'], phtr['dateCreated']))

            field = phtr['transactionType']
            dt = unix_to_datetime(phtr['dateCreated'])
            author = self.get_identity(phtr['authorPHID'])
            ov = phtr['oldValue']
            nv = phtr['newValue']
            text = phtr['comments']

            if field == 'core:comment':
                comment = Comment(text, author, dt)
                comments.append(comment)
            else:
                old_value = unicode(ov) if ov is not None else None
                new_value = unicode(nv) if nv is not None else None
                change = Change(field, old_value, new_value, author, dt)
                changes.append(change)

        return comments, changes

    def get_identity(self, ph_id):
        if not ph_id:
            return None

        if ph_id in self.identities:
            return self.identities[ph_id]

        result = self.conduit.users([ph_id])

        if result:
            raw_data = result[0]
            identity = People(raw_data['userName'])
            identity.name = raw_data['realName']
        else:
            identity = People(ph_id)

        self.identities[ph_id] = identity

        return identity

    def get_projects(self, phids):
        prjs = []
        request = []

        for phid in phids:
            if phid in self.projects:
                prjs.append(self.projects[phid])
            else:
                request.append(phid)

        # Request non-cached projects
        result = self.conduit.projects(request)

        for r in result:
            project = ManiphestProject(r['name'], r['phid'])
            prjs.append(project)
            self.projects[project.phid] = project
        return prjs

    def run(self):
        nbugs = 0

        printout("Running Bicho with delay of %s seconds" % (str(self.delay)))

        if not self.check_auth():
            sys.exit(1)

        # Insert tracker information
        dbtrk = self.insert_tracker(self.url)

        last_mod_date = self.db.get_last_modification_date(tracker_id=dbtrk.id)

        if last_mod_date:
            printdbg("Last modification date stored: %s" % last_mod_date)

        try:
            printdbg("Fetching tasks")

            count = 0
            stop = False

            ph_tasks = self.conduit.tasks(offset=count,
                                          limit=self.max_issues)
            printdbg("Tasks fetched from %s to %s" % (count, count + self.max_issues))

            while ph_tasks:
                for pht in ph_tasks:
                    if self.up_to_date(last_mod_date, pht):
                        printout("Up to date")
                        stop = True
                        break

                    issue = self.get_issue_from_task(pht)

                    # Insert issue
                    self.db.insert_issue(issue, dbtrk.id)

                    nbugs += 1

                if stop:
                    break

                count = count + self.max_issues

                ph_tasks = self.conduit.tasks(offset=count,
                                              limit=self.max_issues)
                printdbg("Tasks fetched from %s to %s" % (count, count + self.max_issues))

                if not ph_tasks:
                    printdbg("No more tasks fetched")
                    printout("Up to date")
        except (requests.exceptions.HTTPError, ConduitError), e:
            printerr("Error: %s" % e)
            sys.exit(1)

        printout("Done. %s bugs analyzed" % (nbugs))


Backend.register_backend('maniphest', Maniphest)
