# -*- coding: utf-8 -*-
# Copyright (C) 2012 GSyC/LibreSoft, Universidad Rey Juan Carlos
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
# Authors: Luis Cañas Díaz <lcanas@libresoft.es>

import sys
import time

from launchpadlib.launchpad import Launchpad
from Bicho.backends import Backend, register_backend
from Bicho.Config import Config
from Bicho.utils import printerr, printdbg, printout
from Bicho.common import Tracker, People, Issue, Comment, Change
from Bicho.db.database import DBIssue, DBBackend, get_database

from storm.locals import DateTime, Int, Reference, Unicode
from datetime import datetime

from tempfile import mkdtemp


class DBLaunchpadIssueExt(object):
    """
    """
    __storm_table__ = 'issues_ext_launchpad'

    id = Int(primary=True)
    status = Unicode()
    issue_id = Int()
    description = Unicode()
    web_link = Unicode()
    bug_target_display_name = Unicode()
    bug_target_name = Unicode()
    date_assigned = DateTime()
    date_closed = DateTime()
    date_confirmed = DateTime()
    date_created = DateTime()
    date_fix_committed = DateTime()
    date_fix_released = DateTime()
    date_in_progress = DateTime()
    date_incomplete = DateTime()
    date_left_closed = DateTime()
    date_left_new = DateTime()
    date_triaged = DateTime()
    date_last_message = DateTime()
    date_last_updated = DateTime()
    #FIXME a new table for this would be better
    milestone_code_name = Unicode()
    milestone_data_targeted = Unicode()
    milestone_name = Unicode()
    milestone_summary = Unicode()
    milestone_title = Unicode()
    milestone_web_link = Unicode()
    duplicate_of = Int()
    #duplicates
    heat = Int()
    linked_branches = Unicode()
    #messages
    tags = Unicode()
    title = Unicode()
    users_affected_count = Int()
    web_link_standalone = Unicode()

    issue = Reference(issue_id, DBIssue.id)

    def __init__(self, issue_id):
        self.issue_id = issue_id


class DBLaunchpadIssueExtMySQL(DBLaunchpadIssueExt):
    """
    MySQL subclass of L{DBLaunchpadIssueExt}
    """

    __sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_ext_launchpad (\
                     id INTEGER NOT NULL AUTO_INCREMENT, \
                     status VARCHAR(32) default NULL, \
                     issue_id INTEGER NOT NULL, \
                     description TEXT default NULL, \
                     web_link VARCHAR(32) default NULL, \
                     bug_target_display_name VARCHAR(32) default NULL, \
                     bug_target_name VARCHAR(32) default NULL, \
                     date_assigned DATETIME default NULL, \
                     date_closed DATETIME default NULL, \
                     date_confirmed DATETIME default NULL, \
                     date_created DATETIME default NULL, \
                     date_fix_committed DATETIME default NULL, \
                     date_fix_released DATETIME default NULL, \
                     date_in_progress DATETIME default NULL, \
                     date_incomplete DATETIME default NULL, \
                     date_left_closed DATETIME default NULL, \
                     date_left_new DATETIME default NULL, \
                     date_triaged DATETIME default NULL, \
                     date_last_message DATETIME default NULL, \
                     date_last_updated DATETIME default NULL, \
                     milestone_code_name VARCHAR(32) default NULL, \
                     milestone_data_targeted VARCHAR(32) default NULL, \
                     milestone_name VARCHAR(32) default NULL, \
                     milestone_summary VARCHAR(32) default NULL, \
                     milestone_title VARCHAR(32) default NULL, \
                     milestone_web_link VARCHAR(32) default NULL, \
                     duplicate_of INTEGER UNSIGNED default NULL, \
                     heat INTEGER UNSIGNED default NULL, \
                     linked_branches VARCHAR(32) default NULL, \
                     tags VARCHAR(32) default NULL, \
                     title VARCHAR(32) default NULL, \
                     users_affected_count INTEGER UNSIGNED default NULL, \
                     web_link_standalone VARCHAR(32) default NULL, \
                     PRIMARY KEY(id), \
                     UNIQUE KEY(issue_id), \
                     INDEX ext_issue_idx(issue_id), \
                     FOREIGN KEY(issue_id) \
                       REFERENCES issues(id) \
                         ON DELETE CASCADE \
                         ON UPDATE CASCADE \
                     ) ENGINE=MYISAM; '


class DBLaunchpadBackend(DBBackend):
    """
    Adapter for Bugzilla backend.
    """
    def __init__(self):
        self.MYSQL_EXT = [DBLaunchpadIssueExtMySQL]

    def insert_issue_ext(self, store, issue, issue_id):
        """
        Insert the given extra parameters of issue with id X{issue_id}.

        @param store: database connection
        @type store: L{storm.locals.Store}
        @param issue: issue to insert
        @type issue: L{SourceForgeIssue}
        @param issue_id: identifier of the issue
        @type issue_id: C{int}

        @return: the inserted extra parameters issue
        @rtype: L{DBSourceForgeIssueExt}
        """

        newIssue = False

        try:
            db_issue_ext = store.find(DBLaunchpadIssueExt,
                                      DBLaunchpadIssueExt.issue_id
                                      ==
                                      issue_id).one()
            if not db_issue_ext:
                newIssue = True
                db_issue_ext = DBLaunchpadIssueExt(issue_id)

            db_issue_ext.status = self.__return_unicode(issue.status)
            db_issue_ext.description = self.__return_unicode(issue.description)
            db_issue_ext.web_link = self.__return_unicode(issue.web_link)
            db_issue_ext.target_display_name = self.__return_unicode(
                issue.target_display_name)
            db_issue_ext.target_name = self.__return_unicode(issue.target_name)
            db_issue_ext.date_assigned = issue.date_assigned
            db_issue_ext.date_closed = issue.date_closed
            db_issue_ext.date_confirmed = issue.date_confirmed
            db_issue_ext.date_created = issue.date_created
            db_issue_ext.date_fix_committed = issue.date_fix_committed
            db_issue_ext.date_fix_released = issue.date_fix_released
            db_issue_ext.date_in_progress = issue.date_in_progress
            db_issue_ext.date_incomplete = issue.date_incomplete
            db_issue_ext.date_left_closed = issue.date_left_closed
            db_issue_ext.date_left_new = issue.date_left_new
            db_issue_ext.date_triaged = issue.date_triaged
            db_issue_ext.date_last_message = issue.date_last_message
            db_issue_ext.date_last_updated = issue.date_last_updated
            db_issue_ext.milestone_code_name = self.__return_unicode(
                issue.milestone_code_name)
            db_issue_ext.milestone_data_targeted = self.__return_unicode(
                issue.milestone_data_targeted)
            db_issue_ext.milestone_name = self.__return_unicode(
                issue.milestone_name)
            db_issue_ext.milestone_summary = self.__return_unicode(
                issue.milestone_summary)
            db_issue_ext.milestone_title = self.__return_unicode(
                issue.milestone_title)
            db_issue_ext.milestone_web_link = self.__return_unicode(
                issue.milestone_web_link)
            db_issue_ext.duplicate_of = issue.duplicate_of
            #db_issue_ext.duplicates
            db_issue_ext.heat = issue.heat
            db_issue_ext.linked_branches = self.__return_unicode(
                issue.linked_branches)

        #### TO DO : create comment instances for
        ## issue.set_messages()

            db_issue_ext.tags = self.__return_unicode(issue.tags)
            db_issue_ext.title = self.__return_unicode(issue.title)
            db_issue_ext.users_affected_count = self.__return_int(
                issue.users_affected_count)
            db_issue_ext.web_link_standalone = self.__return_unicode(
                issue.web_link_standalone)

            if newIssue == True:
                store.add(db_issue_ext)

            store.flush()
            return db_issue_ext
        except:
            store.rollback()
            raise

    def __return_int(self, str):
        """
        Decodes into int, and pays attention to empty ones
        """
        if str is None:
            return str
        else:
            return int(str)

    def __return_unicode(self, str):
        """
        Decodes string and pays attention to empty ones
        """
        if str:
            return unicode(str)
        else:
            return None

    def insert_comment_ext(self, store, comment, comment_id):
        """
        Does nothing
        """
        pass

    def insert_attachment_ext(self, store, attch, attch_id):
        """
        Does nothing
        """
        pass

    def insert_change_ext(self, store, change, change_id):
        """
        Does nothing
        """
        pass


class LaunchpadIssue(Issue):
    """
    Ad-hoc Issue extension for launchpad's issue
    """
    def __init__(self, issue, type, summary, desc, submitted_by, submitted_on):
        Issue.__init__(self, issue, type, summary, desc, submitted_by,
                       submitted_on)

        self.status = None
        self.description = None
        self.web_link = None

        # the two below will be People instances
        #self.assignee = None
        #self.owner = None

        self.bug_target_display_name = None  # name of the target release
        self.bug_target_name = None  # unix name of the target release

        # dates
        self.date_assigned = None
        self.date_closed = None
        self.date_confirmed = None
        self.date_created = None
        self.date_fix_committed = None
        self.date_fix_released = None
        self.date_in_progress = None
        self.date_incomplete = None
        self.date_left_closed = None
        self.date_left_new = None
        self.date_triaged = None
        self.date_last_message = None  # .bug.date_last_message
        self.date_last_updated = None  # .bug.date_last_updated

        #self.importance  # mapped to type

        self.milestone_code_name = None
        # code name (from .milestone.code_name)
        self.milestone_data_targeted = None  # (from .milestone.data_targeted)
        self.milestone_name = None  # E.g, "0.1.7" (from .milestone.name)
        self.milestone_summary = None
        # summary of the milestone (from .milestone.summary)
        self.milestone_title = None
        # project name + name + code_name (from .milestone.title)
        self.milestone_web_link = None  # (from .milestone.web_link)

        self.duplicate_of = None
        self.duplicates = None  # list of duplicates (is it really needed??)

        self.heat = None  # heat of the issue (calculated measure)

        self.linked_branches = None  # ????

        self.messages = None  # Comment instances (from .bug.messages)

        self.tags = None  # tags of the bug
        self.title = None  # title of the bug (from .bug.title)

        self.users_affected_count = None  # users affected by the bug
        self.web_link_standalone = None
        # global URL of the bug (without project name)

    def set_status(self, status):
        """
        Set the status of the issue

        @param alias: status of the issue
        @type alias: C{str}
        """
        self.status = status

    def set_description(self, description):
        """
        Set the description of the issue

        @param alias: description of the issue
        @type alias: C{str}
        """
        self.description = description

    def set_web_link(self, web_link):
        """
        Set the web_link of the issue

        @param alias: web_link of the issue
        @type alias: C{str}
        """
        self.web_link = web_link

    def set_target_display_name(self, target_display_name):
        """
        Set the target_display_name of the issue

        @param alias: target_display_name of the issue
        @type alias: C{str}
        """
        self.target_display_name = target_display_name

    def set_target_name(self, target_name):
        """
        Set the target_name of the issue

        @param alias: target_name of the issue
        @type alias: C{str}
        """
        self.target_name = target_name

    def set_date_assigned(self, date_assigned):
        """
        Set the date_assigned of the issue

        @param date_assigned: of the issue
        @type date_assigned: L{datetime.datetime}
        """
        if not isinstance(date_assigned, datetime):
            raise ValueError('Parameter "date_assigned" should be a %s ' \
                             'instance. %s given.' %
                             ('datetime', input.__class__.__name__))

        self.date_assigned = date_assigned

    def set_date_closed(self, date_closed):
        """
        Set the date_closed of the issue

        @param date_closed: of the issue
        @type date_closed: L{datetime.datetime}
        """
        if not isinstance(date_closed, datetime):
            raise ValueError('Parameter "date_closed" should be a %s ' \
                             'instance. %s given.' %
                             ('datetime', input.__class__.__name__))

        self.date_closed = date_closed

    def set_date_confirmed(self, date_confirmed):
        """
        Set the date_confirmed of the issue

        @param date_confirmed: of the issue
        @type date_confirmed: L{datetime.datetime}
        """
        if not isinstance(date_confirmed, datetime):
            raise ValueError('Parameter "date_confirmed" should be a %s ' \
                             'instance. %s given.' %
                             ('datetime', input.__class__.__name__))

        self.date_confirmed = date_confirmed

    def set_date_created(self, date_created):
        """
        Set the date_created of the issue

        @param date_created: of the issue
        @type date_created: L{datetime.datetime}
        """
        if not isinstance(date_created, datetime):
            raise ValueError('Parameter "date_created" should be a %s ' \
                             'instance. %s given.' %
                             ('datetime', input.__class__.__name__))

        self.date_created = date_created

    def set_date_fix_committed(self, date_fix_committed):
        """
        Set the date_fix_committed of the issue

        @param date_fix_committed: of the issue
        @type date_fix_committed: L{datetime.datetime}
        """
        if not isinstance(date_fix_committed, datetime):
            raise ValueError('Parameter "date_fix_committed" should be a %s ' \
                             'instance. %s given.' %
                             ('datetime', input.__class__.__name__))

        self.date_fix_committed = date_fix_committed

    def set_date_fix_released(self, date_fix_released):
        """
        Set the date_fix_released of the issue

        @param date_fix_released: of the issue
        @type date_fix_released: L{datetime.datetime}
        """
        if not isinstance(date_fix_released, datetime):
            raise ValueError('Parameter "date_fix_released" should be a %s ' \
                             'instance. %s given.' %
                             ('datetime', input.__class__.__name__))

        self.date_fix_released = date_fix_released

    def set_date_in_progress(self, date_in_progress):
        """
        Set the date_in_progress of the issue

        @param date_in_progress: of the issue
        @type date_in_progress: L{datetime.datetime}
        """
        if not isinstance(date_in_progress, datetime):
            raise ValueError('Parameter "date_in_progress" should be a %s ' \
                             'instance. %s given.' %
                             ('datetime', input.__class__.__name__))

        self.date_in_progress = date_in_progress

    def set_date_incomplete(self, date_incomplete):
        """
        Set the date_incomplete of the issue

        @param date_incomplete: of the issue
        @type date_incomplete: L{datetime.datetime}
        """
        if not isinstance(date_incomplete, datetime):
            raise ValueError('Parameter "date_incomplete" should be a %s ' \
                             'instance. %s given.' %
                             ('datetime', input.__class__.__name__))

        self.date_incomplete = date_incomplete

    def set_date_left_closed(self, date_left_closed):
        """
        Set the date_left_closed of the issue

        @param date_left_closed: of the issue
        @type date_left_closed: L{datetime.datetime}
        """
        if not isinstance(date_left_closed, datetime):
            raise ValueError('Parameter "date_left_closed" should be a %s ' \
                             'instance. %s given.' %
                             ('datetime', input.__class__.__name__))

        self.date_left_closed = date_left_closed

    def set_date_left_new(self, date_left_new):
        """
        Set the date_left_new of the issue

        @param date_left_new: of the issue
        @type date_left_new: L{datetime.datetime}
        """
        if not isinstance(date_left_new, datetime):
            raise ValueError('Parameter "date_left_new" should be a %s ' \
                             'instance. %s given.' %
                             ('datetime', input.__class__.__name__))

        self.date_left_new = date_left_new

    def set_date_triaged(self, date_triaged):
        """
        Set the date_triaged of the issue

        @param date_triaged: of the issue
        @type date_triaged: L{datetime.datetime}
        """
        if not isinstance(date_triaged, datetime):
            raise ValueError('Parameter "date_triaged" should be a %s ' \
                             'instance. %s given.' %
                             ('datetime', input.__class__.__name__))

        self.date_triaged = date_triaged

    def set_date_last_message(self, date_last_message):
        """
        Set the date_last_message of the issue

        @param date_last_message: of the issue
        @type date_last_message: L{datetime.datetime}
        """
        if not isinstance(date_last_message, datetime):
            raise ValueError('Parameter "date_last_message" should be a %s ' \
                             'instance. %s given.' %
                             ('datetime', input.__class__.__name__))

        self.date_last_message = date_last_message

    def set_date_last_updated(self, date_last_updated):
        """
        Set the date_last_updated of the issue

        @param date_last_updated: of the issue
        @type date_last_updated: L{datetime.datetime}
        """
        if not isinstance(date_last_updated, datetime):
            raise ValueError('Parameter "date_last_updated" should be a %s ' \
                             'instance. %s given.' %
                             ('datetime', input.__class__.__name__))

        self.date_last_updated = date_last_updated

    def set_milestone_code_name(self, milestone_code_name):
        """
        Set the milestone_code_name of the issue

        @param alias: milestone_code_name of the issue
        @type alias: C{str}
        """
        self.milestone_code_name = milestone_code_name

    def set_milestone_data_targeted(self, milestone_data_targeted):
        """
        Set the milestone_data_targeted of the issue

        @param alias: milestone_data_targeted of the issue
        @type alias: C{str}
        """
        self.milestone_data_targeted = milestone_data_targeted

    def set_milestone_name(self, milestone_name):
        """
        Set the milestone_name of the issue

        @param alias: milestone_name of the issue
        @type alias: C{str}
        """
        self.milestone_name = milestone_name

    def set_milestone_summary(self, milestone_summary):
        """
        Set the milestone_summary of the issue

        @param alias: milestone_summary of the issue
        @type alias: C{str}
        """
        self.milestone_summary = milestone_summary

    def set_milestone_title(self, milestone_title):
        """
        Set the milestone_title of the issue

        @param alias: milestone_title of the issue
        @type alias: C{str}
        """
        self.milestone_title = milestone_title

    def set_milestone_web_link(self, milestone_web_link):
        """
        Set the milestone_web_link of the issue

        @param alias: milestone_web_link of the issue
        @type alias: C{str}
        """
        self.milestone_web_link = milestone_web_link

    def set_duplicate_of(self, duplicate_of):
        """
        Set the duplicate_of of the issue

        @param alias: duplicate_of of the issue
        @type alias: C{str}
        """
        self.duplicate_of = duplicate_of

    def set_duplicates(self, duplicates):
        ### FIXME is this neccesary??
        """
        Set the duplicates of the issue

        @param alias: duplicates of the issue
        @type alias: C{str}
        """
        self.duplicates = duplicates

    def set_heat(self, heat):
        """
        Set the heat of the issue

        @param alias: heat of the issue
        @type alias: C{str}
        """
        self.heat = heat

    def set_linked_branches(self, linked_branches):
        """
        Set the linked_branches of the issue

        @param alias: linked_branches of the issue
        @type alias: C{str}
        """
        self.linked_branches = linked_branches

    def set_messages(self, messages):
        """
        Set the messages of the issue

        @param alias: messages of the issue
        @type alias: C{str}
        """
        self.messages = messages

    def set_tags(self, tags):
        """
        Set the tags of the issue

        @param alias: tags of the issue
        @type alias: C{str}
        """
        self.tags = tags

    def set_title(self, title):
        """
        Set the title of the issue

        @param alias: title of the issue
        @type alias: C{str}
        """
        self.title = title

    def set_users_affected_count(self, users_affected_count):
        """
        Set the users_affected_count of the issue

        @param alias: users_affected_count of the issue
        @type alias: C{str}
        """
        self.users_affected_count = users_affected_count

    def set_web_link_standalone(self, web_link_standalone):
        """
        Set the web_link_standalone of the issue

        @param alias: web_link_standalone of the issue
        @type alias: C{str}
        """
        self.web_link_standalone = web_link_standalone


class LPBackend(Backend):

    def __init__(self):
        Backend.__init__(self)
        options = Config()
        self.url = options.url
        self.delay = options.delay

    def get_domain(self, url):
        strings = url.split('/')
        return strings[0] + "//" + strings[2] + "/"

    def analyze_bug(self, bug):
        #Retrieving main bug information

        ##
        ## all the retrieval can be improved. The method bug.lp_attributes
        ##offers a list of the available attributes for the object
        ##
        printdbg(bug.web_link)

        issue = bug.web_link[bug.web_link.rfind('/') + 1:]
        bug_type = bug.importance
        summary = bug.bug.title
        desc = bug.bug.description
        submitted_by = People(bug.owner.name)
        submitted_by.set_name(bug.owner.display_name)

        submitted_on = bug.date_created

        if bug.assignee:
            assignee = People(bug.assignee.name)
            assignee.set_name(bug.assignee.display_name)
        else:
            assignee = People("nobody")

        issue = LaunchpadIssue(issue, bug_type, summary, desc, submitted_by,
                               submitted_on)
        issue.set_assigned(assignee)

        issue.set_status(bug.status)
        issue.set_description(bug.bug.description)
        issue.set_web_link(bug.web_link)

        issue.set_target_display_name(bug.bug_target_display_name)
        issue.set_target_name(bug.bug_target_name)

        try:
            if bug.date_assigned:
                issue.set_date_assigned(bug.date_assigned)
        except AttributeError:
            pass

        try:
            if bug.date_closed:
                issue.set_date_closed(bug.date_closed)
        except AttributeError:
            pass

        try:
            if bug.date_confirmed:
                issue.set_date_confirmed(bug.date_confirmed)
        except AttributeError:
            pass

        try:
            if bug.date_created:
                issue.set_date_created(bug.date_created)
        except AttributeError:
            pass

        try:
            if bug.date_fix_committed:
                issue.set_date_fix_committed(bug.date_fix_committed)
        except AttributeError:
            pass

        try:
            if bug.date_fix_released:
                issue.set_date_fix_released(bug.date_fix_released)
        except AttributeError:
            pass

        try:
            if bug.date_in_progress:
                issue.set_date_in_progress(bug.date_in_progress)
        except AttributeError:
            pass

        try:
            if bug.date_incomplete:
                issue.set_date_incomplete(bug.date_incomplete)
        except AttributeError:
            pass

        try:
            if bug.date_left_closed:
                issue.set_date_left_closed(bug.date_left_closed)
        except AttributeError:
            pass

        try:
            if bug.date_left_new:
                issue.set_date_left_new(bug.date_left_new)
        except AttributeError:
            pass

        try:
            if bug.date_triaged:
                issue.set_date_triaged(bug.date_triaged)
        except AttributeError:
            pass

        try:
            if bug.date_last_message:
                issue.set_date_last_message(bug.date_last_message)
        except AttributeError:
            pass

        try:
            if bug.date_last_updated:
                issue.set_date_last_updated(bug.date_last_updated)
        except AttributeError:
            pass

        if bug.milestone:
            issue.set_milestone_code_name(bug.milestone.code_name)
            issue.set_milestone_data_targeted(bug.milestone.date_targeted)
            issue.set_milestone_name(bug.milestone.name)
            issue.set_milestone_summary(bug.milestone.summary)
            issue.set_milestone_title(bug.milestone.title)
            issue.set_milestone_web_link(bug.milestone.web_link)

        if bug.bug.duplicate_of:
            aux = bug.bug.duplicate_of.web_link
            dupe_of = int(aux[aux.rfind('/') + 1:])
            issue.set_duplicate_of(dupe_of)

        #issue.set_duplicates(bug.bug.duplicates)
        issue.set_heat(bug.bug.heat)
        issue.set_linked_branches(bug.bug.linked_branches)

        # storing the comments:
        # first message of the bugs contains the description
        if (bug.bug.messages and len(bug.bug.messages) > 1):
            skip = 1
            for c in bug.bug.messages:
                if (skip==1):
                    # we skip the first comment which is the description
                    skip = 0
                    continue
                by = People(c.owner.name)
                by.set_name(c.owner.display_name)
                #by.set_email()
                com = Comment(c.content, by, c.date_created)
                issue.add_comment(com)        

        issue.set_tags(bug.bug.tags)
        issue.set_title(bug.bug.title)
        issue.set_users_affected_count(bug.bug.users_affected_count)
        issue.set_web_link_standalone(bug.bug.web_link)

        return issue

    def __get_project_from_url(self):

        project_name = None
        url = self.url

        if url[-1] == '/':
            url = url[:-1]

        if (url.rfind('://bugs.launchpad.net') >= 0) or \
               (url.rfind('://launchpad.net') >= 0):
            project_name = url[url.rfind('/') + 1:]

        return project_name

    def __get_tracker_url_from_bug(self, bug):
        return bug.web_link[:bug.web_link.rfind('+bug')-1]

    def run(self, url):

        print("Running Bicho with delay of %s seconds" % (str(self.delay)))

        if not self.url:
            self.url = url

        pname = None
        pname = self.__get_project_from_url()

        bugsdb = get_database(DBLaunchpadBackend())

        printdbg(url)

        # launchpad needs a temp directory to store cached data
        cachedir = mkdtemp(suffix='launchpad')

        lp = Launchpad.login_anonymously('just testing', 'production',
                                         cachedir)
        aux_status = ["New", "Incomplete", "Opinion", "Invalid", "Won't Fix",
                      "Expired", "Confirmed", "Triaged", "In Progress",
                      "Fix Committed", "Fix Released",
                      "Incomplete (with response)",
                      "Incomplete (without response)"]
        bugs = lp.projects[pname].searchTasks(status=aux_status,
                                              omit_duplicates=False)
        nbugs = len(bugs)

        # still useless
        bugsdb.insert_supported_traker("launchpad", "x.x")
        trk = Tracker(url, "launchpad", "x.x")
        dbtrk = bugsdb.insert_tracker(trk)
        #

        if nbugs == 0:
            printout("No bugs found. Did you provide the correct url?")
            sys.exit(0)

        for bug in bugs:
            try:
                issue_data = self.analyze_bug(bug)
            except Exception:
                #FIXME it does not handle the e
                printerr("Error in function analyzeBug with URL: ' \
                '%s and Bug: %s" % (url, bug))
                #print e
                #continue
                raise
            try:
                # we can have meta-trackers but we want to have the original
                #tracker name
                tr_url = self.__get_tracker_url_from_bug(bug)
                if (tr_url != url):
                    aux_trk = Tracker(tr_url, "launchpad", "x.x")
                    dbtrk = bugsdb.insert_tracker(aux_trk)                
                bugsdb.insert_issue(issue_data, dbtrk.id)
            except UnicodeEncodeError:
                printerr("UnicodeEncodeError: the issue %s couldn't be stored"
                      % (issue_data.issue))

            time.sleep(self.delay)

        printout("Done. %s bugs analyzed" % (nbugs))

register_backend("lp", LPBackend)
