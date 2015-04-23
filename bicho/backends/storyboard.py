# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Bitergia
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
# Authors:  Alvaro del Castillo <acs@bitergia.com>
#

from bicho.config import Config

from bicho.backends import Backend
from bicho.utils import create_dir, printdbg, printout, printerr
from bicho.db.database import DBIssue, DBChange, DBPeople, DBBackend, get_database
from bicho.common import Tracker, Issue, People, Change

from dateutil.parser import parse
from datetime import datetime

import errno
import feedparser
import json
import logging
import os
import pprint
import random
import sys
import time
import traceback
import urllib


from storm.locals import DateTime, Desc, Int, Reference, Unicode, Bool


class DBStoryBoardStory(object):
    __storm_table__ = 'stories'

    story_id = Int(primary=True)
    created_at = DateTime()
    updated_at = DateTime()
    status = Unicode()
    description = Unicode()
    title = Unicode()
    tags = Unicode()
    creator_id = Int()
    is_bug = Bool()

    def __init__(self, story_id):
        self.story_id = story_id

class DBStoryBoardStoryMySQL(DBStoryBoardStory):
    """
    MySQL subclass of L{DBStoryBoardIssueExt}
    """

    # If the table is changed you need to remove old from database
    __sql_table__ = 'CREATE TABLE IF NOT EXISTS stories ( \
                    story_id INTEGER NOT NULL, \
                    created_at DATETIME, \
                    updated_at DATETIME, \
                    status VARCHAR(255), \
                    creator_id INTEGER NOT NULL, \
                    is_bug BOOLEAN, \
                    title TEXT, \
                    description TEXT, \
                    tags TEXT, \
                    PRIMARY KEY(story_id) \
                     ) ENGINE=MYISAM;'

class DBStoryBoardIssueExt(object):
    __storm_table__ = 'issues_ext_storyboard'

    id = Int(primary=True)
    project_id = Int()
    story_id = Int()
    mod_date = DateTime()
    issue_id = Int()

    issue = Reference(issue_id, DBIssue.id)

    def __init__(self, issue_id):
        self.issue_id = issue_id


class DBStoryBoardIssueExtMySQL(DBStoryBoardIssueExt):
    """
    MySQL subclass of L{DBStoryBoardIssueExt}
    """

    # If the table is changed you need to remove old from database
    __sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_ext_storyboard ( \
                    id INTEGER NOT NULL AUTO_INCREMENT, \
                    project_id INTEGER, \
                    story_id INTEGER NOT NULL, \
                    mod_date DATETIME, \
                    issue_id INTEGER NOT NULL, \
                    PRIMARY KEY(id), \
                    FOREIGN KEY(issue_id) \
                    REFERENCES tasks (id) \
                    ON DELETE CASCADE \
                    ON UPDATE CASCADE \
                     ) ENGINE=MYISAM;'

class DBStoryBoardBackend(DBBackend):
    """
    Adapter for StoryBoard backend.
    """
    def __init__(self):
        self.MYSQL_EXT = [DBStoryBoardIssueExtMySQL,DBStoryBoardStoryMySQL]

    def insert_story(self, store, story):
        newStory = False
        try:
            db_story = store.find(DBStoryBoardStory,
                                  DBStoryBoardStory.story_id == story['id']).one()
            if not db_story:
                newStory = True
                db_story = DBStoryBoardStory(story['id'])

            db_story.updated_at = StoryBoard.convert_to_datetime(story['updated_at'])
            db_story.created_at = StoryBoard.convert_to_datetime(story['created_at'])
            db_story.status = story['status']
            if story['creator_id']:
                db_story.creator_id = story['creator_id']
            else:
                db_story.creator_id = -1
            db_story.is_bug = story['is_bug']
            db_story.description = story['description']
            db_story.title = story['title']
            db_story.tags = unicode(";".join(story['tags']))

            if newStory is True:
                store.add(db_story)

            store.flush()
            return db_story
        except:
            store.rollback()
            raise

    def insert_issue_ext(self, store, issue, issue_id):
        """
        Insert the given extra parameters of issue with id X{issue_id}.

        @param store: database connection
        @type store: L{storm.locals.Store}
        @param issue: issue to insert
        @type issue: L{StoryBoardIssue}
        @param issue_id: identifier of the issue
        @type issue_id: C{int}

        @return: the inserted extra parameters issue
        @rtype: L{DBStoryBoardIssueExt}
        """

        newIssue = False

        try:
            db_issue_ext = store.find(DBStoryBoardIssueExt,
                                      DBStoryBoardIssueExt.issue_id == issue_id).one()
            if not db_issue_ext:
                newIssue = True
                db_issue_ext = DBStoryBoardIssueExt(issue_id)
                #db_issue_ext = DBSourceForgeIssueExt(issue.category, issue.group, issue_id)


            self.project_id = None
            self.story_id = None
            self.mod_date = None

            db_issue_ext.project_id = issue.project_id
            db_issue_ext.story_id = issue.story_id
            db_issue_ext.mod_date = issue.mod_date

            if newIssue is True:
                store.add(db_issue_ext)

            store.flush()
            return db_issue_ext
        except:
            store.rollback()
            raise

    def insert_change_ext(self, store, change, change_id):
        """
        Does nothing
        """
        pass

    def get_last_modification_date(self, store, tracker_id = None):
        # get last modification date (day) stored in the database
        # select date_last_updated as date from issues_ext_storyboard order by date
        result = store.find(DBStoryBoardIssueExt)
        aux = result.order_by(Desc(DBStoryBoardIssueExt.mod_date))[:1]

        for entry in aux:
            return entry.mod_date.strftime('%Y-%m-%dT%H:%M:%SZ')

        return None


class StoryBoardIssue(Issue):
    """
    Ad-hoc Issue extension for storyboard's issue
    """
    def __init__(self, issue, type, summary, desc, submitted_by, submitted_on):
        Issue.__init__(self, issue, type, summary, desc, submitted_by,
                       submitted_on)
        self.project_id = None
        self.story_id = None
        self.mod_date = None

class StoryBoard():
    """
    StoryBoard backend
    """

    project_test_file = None
    safe_delay = 5

    def __init__(self):
        self.delay = Config.delay

    @staticmethod
    def convert_to_datetime(str_date):
        """
        Returns datetime object from string
        """
        return parse(str_date).replace(tzinfo=None)

    def analyze_task(self, task):
        issue = self.parse_task(task)
        return issue

    def parse_task(self, task):
        # [u'status', u'assignee_id', u'title', u'story_id', u'created_at', u'updated_at', u'priority', u'creator_id', u'project_id', u'id']
        people = People(task["creator_id"])
        people.set_email(self.get_email(task["creator_id"]))
        people.set_name(self.get_fullname(task["creator_id"]))

        description = None
        created_at = None
        if task["created_at"] is not None:
            created_at = StoryBoard.convert_to_datetime(task["created_at"])

        issue = StoryBoardIssue(task["id"],
                            "task",
                            task["title"],
                            description,
                            people,
                            created_at)
        people = People(task["assignee_id"])
        people.set_email(self.get_email(task["assignee_id"]))
        people.set_name(self.get_fullname(task["assignee_id"]))

        issue.assigned_to = people
        issue.status = task["status"]
        # No information from StoryBoard for this fields
        issue.resolution = None
        issue.priority = task["priority"]

        # Extended attributes
        if task["project_id"] is not None:
            issue.project_id = task["project_id"]
        issue.story_id = task["story_id"]
        if task["updated_at"] is not None:
            issue.mod_date = StoryBoard.convert_to_datetime(task["updated_at"])

        return issue

    def parse_change(self, change):
        # print "changed_by:" + entry['author']
        field = change['event_type']
        by = People(change['author_id'])
        by.set_email(self.get_email(change['author_id']))
        by.set_name(self.get_fullname(change['author_id']))

        old_value = new_value = None
        if field == "task_created":
            new_value = change['event_info']['task_title']
        elif field == "task_priority_changed":
            old_value = change['event_info']['old_priority']
            new_value = change['event_info']['new_priority']
        elif field == "task_status_changed":
            old_value = change['event_info']['old_status']
            new_value = change['event_info']['new_status']
        elif field == "task_assignee_changed":
            old_value = change['event_info']['old_assignee_id']
            new_value = change['event_info']['new_assignee_id']
        elif field == "task_details_changed":
            # No data about the old and new details provided in API REST JSON
            pass
        elif field == "task_deleted":
            pass
        else:
            logging.error(field + " not supported yet in changes.")
            logging.info(change)

        update = parse(change['created_at'])
        change = Change(field, unicode(old_value), unicode(new_value), by, update)
        return change

    def remove_unicode(self, str):
        """
        Cleanup u'' chars indicating a unicode string
        """
        if (str.startswith('u\'') and str.endswith('\'')):
            str = str[2:len(str) - 1]
        return str

    def analyze_tasks(self):
        self.url_tasks = Config.url + "/api/v1/tasks"
        # self.url_tasks += "?sort_field=updated_at&sort_dir=asc&limit="+str(tasks_per_query)
        self.url_tasks_total = self.url_tasks + "?limit=1"
        self.url_tasks += "?limit="+str(self.items_per_query)

        logging.debug("URL for getting tasks " + self.url_tasks)

        f = urllib.urlopen(self.url_tasks_total)
        total_tasks = int(f.info()['x-total'])
        limit_tasks = int(f.info()['x-limit'])
        f.close()

        logging.info("Number of tasks: " + str(total_tasks))

        if total_tasks == 0:
            logging.info("No tasks found. Did you provide the correct url? " + Config.url)
            sys.exit(0)
        remaining = total_tasks

        start_page = 0
        total_pages = total_tasks / self.items_per_query
        marker = None # The resource id where the page should begin

        while start_page <= total_pages:
            if marker:
                self.url_tasks_page = self.url_tasks + "&marker="+str(marker)
            else:
                self.url_tasks_page = self.url_tasks

            logging.info("URL for next tasks " + self.url_tasks_page)

            f = urllib.urlopen(self.url_tasks_page)
            taskList = json.loads(f.read())

            for task in taskList:
                try:
                    issue_data = self.analyze_task(task)
                    marker = task['id']
                    if issue_data is None:
                        continue
                    self.bugsdb.insert_issue(issue_data, self.dbtrk.id)
                    remaining -= 1
                except Exception, e:
                    logging.error("Error in function analyze_task ")
                    logging.error(task)
                    traceback.print_exc(file=sys.stdout)
                    sys.exit()
                except UnicodeEncodeError:
                    logging.error("UnicodeEncodeError: the task couldn't be stored")
                    logging.error(task)
            start_page += 1
            logging.info("Remaining issues: %i" % (remaining))

        logging.info("Done. Tasks analyzed:" + str(total_tasks - remaining))


    def check_tasks_events (self):
        """ Add event/invalid changes if don't exists and task in this status """
        by = People('bicho_tool')
        # TODO: at some point this should be NULL
        by.set_name('Unknown')

        issues = self.bugsdb.store.find(DBIssue)
        people_none = self.bugsdb.store.find(DBPeople, DBPeople.user_id == unicode("None")).one()
        for task in issues:
            if task.status in ['merged','invalid']:
                # Closed condition that needs and event for it
                changes = self.bugsdb.store.find(DBChange, DBChange.issue_id == task.id)
                found_change = False
                for change in changes:
                    if change.new_value == task.status:
                        found_change = True
                        break
                if not found_change:
                    task_ext = self.bugsdb.store.find(DBStoryBoardIssueExt,
                                                      DBStoryBoardIssueExt.issue_id == task.id).one()
                    field = "task_status_changed"
                    old_value = None
                    if task_ext.mod_date == None:
                        # Can't generate the event without date
                        continue
                    # logging.info("Adding to " + task.summary + " " + task.status + " event")
                    change = Change(field, old_value, task.status, by, task_ext.mod_date)
                    self.bugsdb._insert_change(change, task.id, self.dbtrk.id)

    def analyze_stories_and_events(self):
        # The changes in tasks is in stories events
        # Get all stories updated after last analysis store them
        # and review their changes
        self.url_stories = Config.url + "/api/v1/stories"
        self.url_stories += "?sort_field=updated_at&sort_dir=desc"
        self.url_stories_total = self.url_stories + "&limit=1"
        self.url_stories += "&limit="+str(self.items_per_query)

        f = urllib.urlopen(self.url_stories_total)
        total_stories = int(f.info()['x-total'])
        f.close()

        logging.info("Number of stories: " + str(total_stories))

        if total_stories == 0:
            logging.info("No stories found. Did you provide the correct url? " + Config.url)
            sys.exit(0)
        remaining = total_stories

        start_page = 0
        total_pages = total_stories / self.items_per_query
        marker = None # The resource id where the page should begin
        storiesUpdated = [] # stories with updated info
        updated_stories = True # control if we have more updated stories

        while start_page <= total_pages and updated_stories:
            if marker:
                self.url_stories_page = self.url_stories + "&marker="+str(marker)
            else:
                self.url_stories_page = self.url_stories

            logging.info("URL for next stories " + self.url_stories_page)

            f = urllib.urlopen(self.url_stories_page)
            storiesList = json.loads(f.read())
            logging.info("Stories gathered: " + str(len(storiesList)))

            for story in storiesList:
                # print story['updated_at'],story['title']
                story_date = parse(story['updated_at']).replace(tzinfo=None)
                if self.last_mod_date:
                    last_date_shown = parse(self.last_mod_date).replace(tzinfo=None)
                    if story_date > last_date_shown:
                        storiesUpdated.append(story['id'])
                        self.backend.insert_story(self.bugsdb.store, story)
                    else:
                        logging.info("First story updated before " + self.last_mod_date)
                        logging.info("No updates from " + story['updated_at']+" "+story['title'])
                        updated_stories = False
                        break
                else:
                    storiesUpdated.append(story['id'])
                    self.backend.insert_story(self.bugsdb.store, story)
                marker = story['id']
                remaining -= 1

            start_page += 1
            logging.info("Remaining stories: %i" % (remaining))
            if (self.debug): break

        logging.info("Done. Stories analyzed (updated):" + str(total_stories - remaining))

        if remaining != 0 and self.last_mod_date is None:
            logging.error("Not all stories downloaded. Pending: " + str(remaining))

        # Time to analyze tasks changes for updated stories
        logging.info("Total stories to analyze changes " + str(len(storiesUpdated)))

        remaining = len(storiesUpdated)
        for story_id in storiesUpdated:
            url_events = Config.url + "/api/v1/stories/" + str(story_id) + "/events"
            f = urllib.urlopen(url_events)
            data = f.read()
            events = json.loads(data)

            for event in events:
                if event['event_info'] is None: continue
                # Hack: event_info not provided in API as a JSON object. Convert it to JSON.
                event['event_info'] = json.loads(event['event_info'])
                if 'task_id' in event['event_info'].keys():
                    task_id = event['event_info']['task_id']
                    issue = self.bugsdb.store.find(DBIssue, DBIssue.issue == unicode(task_id)).one()
                    if issue is None:
                        logging.error("Task " + str(task_id) + " found in event but does not exists")
                        logging.info(event)
                        continue
                    change = self.parse_change(event)
                    db_change = self.bugsdb._get_db_change(change, issue.id, self.dbtrk.id)
                    if db_change == -1:
                        self.bugsdb._insert_change(change, issue.id, self.dbtrk.id)


            remaining -= 1
            if remaining % 100 == 0: logging.info("Remaining: " + str(remaining))
            f.close()
            time.sleep(0.2)

    def get_user_field(self, user_id, field):
        for user in self.all_users:
            if user['id'] == user_id:
                if field in user:
                    return user[field]

    def get_username(self, user_id):
        return self.get_user_field(user_id, "username")
    def get_fullname(self, user_id):
        return self.get_user_field(user_id, "full_name")
    def get_email(self, user_id):
        return self.get_user_field(user_id, "email")

    def analyze_users(self):
        """ Users is not big data so just gather all and store the info in memory """
        self.all_users = []
        self.url_users = Config.url + "/api/v1/users"
        self.url_users_total = self.url_users + "?limit=1"
        self.url_users += "?limit="+str(self.items_per_query)

        f = urllib.urlopen(self.url_users_total)
        total_users = int(f.info()['x-total'])
        f.close()

        start_page = 0
        total_pages = total_users / self.items_per_query
        marker = None # The resource id where the page should begin

        while start_page <= total_pages:
            if marker:
                self.url_users_page = self.url_users + "&marker="+str(marker)
            else:
                self.url_users_page = self.url_users

            logging.info("URL for next users " + self.url_users_page)

            f = urllib.urlopen(self.url_users_page)
            userList = json.loads(f.read())
            marker = userList[-1]['id']
            start_page += 1

            self.all_users += userList


        logging.info("Done user gathering")


    def run(self):
        self.debug = False
        logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s')

        logging.info("Running StoryBoard bicho backend")

        self.items_per_query = 500 # max limit by default in https://storyboard.openstack.org/api/v1/
        if (self.debug): self.items_per_query = 10 # debug

        self.backend = DBStoryBoardBackend()
        self.bugsdb = get_database(self.backend)

        self.bugsdb.insert_supported_traker("storyboard", "beta")
        trk = Tracker(Config.url, "storyboard", "beta")
        self.dbtrk = self.bugsdb.insert_tracker(trk)

        self.last_mod_date = self.bugsdb.get_last_modification_date()

        if self.last_mod_date:
            logging.info("Last bugs analyzed were modified on: %s" % self.last_mod_date)

        self.analyze_users()
        self.analyze_tasks()
        self.analyze_stories_and_events()
        self.check_tasks_events()

Backend.register_backend('storyboard', StoryBoard)
