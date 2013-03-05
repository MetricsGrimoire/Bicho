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

from Bicho.Config import Config

from Bicho.backends import Backend
from Bicho.utils import create_dir, printdbg, printout, printerr
from Bicho.db.database import DBIssue, DBBackend, get_database
from Bicho.common import Tracker, Issue, People, Change

from dateutil.parser import parse
from datetime import datetime

import errno, json, os, random, time, traceback, urllib, urllib2, feedparser, base64, sys
import pprint 

from storm.locals import DateTime, Desc, Int, Reference, Unicode, Bool


class DBRedmineIssueExt(object):
        
    __storm_table__ = 'issues_ext_redmine'

    id = Int(primary=True)
    category_id = Int()
    done_ratio = Int()
    due_date  = DateTime()
    estimated_hours = Int()        
    fixed_version_id = Int()
    lft = Int()
    rgt = Int()
    lock_version = Int()
    parent_id = Int()
    project_id = Int()
    root_id = Int()
    start_date = DateTime()
    tracker_id = Int()        
    updated_on = DateTime()
    issue_id = Int()
                    
    issue = Reference(issue_id, DBIssue.id)
    
    def __init__(self, issue_id):
        self.issue_id = issue_id


class DBRedmineIssueExtMySQL(DBRedmineIssueExt):
    """
    MySQL subclass of L{DBRedmineIssueExt}
    """

    # If the table is changed you need to remove old from database
    __sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_ext_redmine ( \
                    id INTEGER NOT NULL AUTO_INCREMENT, \
                    category_id INTEGER, \
                    done_ratio INTEGER, \
                    due_date DATETIME, \
                    estimated_hours INTEGER, \
                    fixed_version_id INTEGER, \
                    lft INTEGER, \
                    rgt INTEGER, \
                    lock_version INTEGER, \
                    parent_id INTEGER, \
                    project_id INTEGER, \
                    root_id INTEGER, \
                    start_date DATETIME, \
                    tracker_id INTEGER, \
                    updated_on DATETIME, \
                    issue_id INTEGER, \
                    PRIMARY KEY(id), \
                    FOREIGN KEY(issue_id) \
                    REFERENCES issues (id) \
                    ON DELETE CASCADE \
                    ON UPDATE CASCADE \
                     ) ENGINE=MYISAM;'

class DBRedmineBackend(DBBackend):
    """
    Adapter for Redmine backend.
    """
    def __init__(self):
        self.MYSQL_EXT = [DBRedmineIssueExtMySQL]
        
    def insert_issue_ext(self, store, issue, issue_id):
        
        newIssue = False;
        
        try:
            db_issue_ext = store.find(DBRedmineIssueExt,
                                      DBRedmineIssueExt.issue_id == issue_id).one()
            if not db_issue_ext:
                newIssue = True
                db_issue_ext = DBRedmineIssueExt(issue_id)
                #db_issue_ext = DBSourceForgeIssueExt(issue.category, issue.group, issue_id)

            db_issue_ext.category_id = issue.category_id
            db_issue_ext.done_ratio = issue.done_ratio
            db_issue_ext.due_date = issue.due_date
            db_issue_ext.estimated_hours = issue.estimated_hours
            db_issue_ext.fixed_version_id = issue.fixed_version_id
            db_issue_ext.lft = issue.lft
            db_issue_ext.rgt = issue.rgt
            db_issue_ext.lock_version = issue.lock_version
            db_issue_ext.parent_id = issue.parent_id
            db_issue_ext.project_id = issue.project_id
            db_issue_ext.root_id = issue.root_id
            db_issue_ext.start_date = issue.start_date
            db_issue_ext.tracker_id = issue.tracker_id        
            db_issue_ext.updated_on = issue.updated_on
        
            if newIssue == True:
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

    def get_last_modification_date(self, store):
        # get last modification date (day) stored in the database
        # select date_last_updated as date from issues_ext_redmine order by date
#        result = store.find(DBRedmineIssueExt)
#        aux = result.order_by(Desc(DBRedmineIssueExt.mod_date))[:1]
#
#        for entry in aux:
#            return entry.mod_date.strftime('%Y-%m-%dT%H:%M:%SZ')

        return None


class RedmineIssue(Issue):
    """
    Ad-hoc Issue extension for redmine's issue
    """
    def __init__(self, issue, type, summary, desc, submitted_by, submitted_on):
        Issue.__init__(self, issue, type, summary, desc, submitted_by,
                       submitted_on)
    
class Redmine():
    
    project_test_file = None
    safe_delay = 5
    
    def __init__(self):
        self.delay = Config.delay
        
    def _convert_to_datetime(self,str_date):
        """
        Returns datetime object from string
        """
        return parse(str_date).replace(tzinfo=None)

    def analyze_bug(self, issue_redmine):
        issue =  self.parse_bug(issue_redmine)
#        changes = self.analyze_bug_changes(bug_url)
#        for c in changes:
#            issue.add_change(c)                 
        return issue

        
    def parse_bug(self, issue_redmine):
        
        people = People(issue_redmine["author_id"])            
        # people.set_name(issue_redmine["reported_by"])
                
        issue = RedmineIssue(issue_redmine["id"],
                            "ticket",
                            issue_redmine["subject"],
                            issue_redmine["description"],
                            people,
                            self._convert_to_datetime(issue_redmine["created_on"]))        
        people =  People(issue_redmine["assigned_to_id"])
        # people.set_name(issue_redmine["assigned_to"])
        issue.assigned_to = people
        issue.status = issue_redmine["status_id"]
        issue.priority = issue_redmine["priority_id"]
        # No information from Redmine for this field. Included in Status
        issue.resolution = None
                
        # Extended attributes
        issue.category_id = issue_redmine["category_id"]
        issue.done_ratio = issue_redmine["done_ratio"]
                
        if issue_redmine["due_date"] is None:
            issue.due_date = None
        else:
            issue.due_date = self._convert_to_datetime(issue_redmine["due_date"])
        
        issue.estimated_hours = issue_redmine["estimated_hours"]
        issue.fixed_version_id = issue_redmine["fixed_version_id"]
        issue.lft = issue_redmine["lft"]
        issue.rgt = issue_redmine["rgt"]
        issue.lock_version = issue_redmine["lock_version"]
        issue.parent_id = issue_redmine["parent_id"]
        issue.project_id = issue_redmine["project_id"]
        issue.root_id = issue_redmine["root_id"]
        if issue_redmine["start_date"] is None:
            issue.start_date = None
        else:
            issue.start_date = self._convert_to_datetime(issue_redmine["start_date"])
        issue.tracker_id = issue_redmine["tracker_id"]
        if issue_redmine["updated_on"] is None:
            issue.updated_on = None
        else:
            issue.updated_on = self._convert_to_datetime(issue_redmine["updated_on"])

        return issue
                    
        
    # Not yet implemented: journals in Redmine 1.1
    def analyze_bug_changes (self, bug_url):
        bug_number = bug_url.split('/')[-1]
        changes_url = bug_url.replace("rest/","")+"/feed.atom"

        printdbg("Analyzing issue changes" + changes_url)

        d = feedparser.parse(changes_url)
        changes = self.parse_changes(d)
        
        return changes

    def parse_changes (self, activity):
        changesList = []
        for entry in activity['entries']:
            # print "changed_by:" + entry['author']
            by = People(entry['author'])
            # print "changed_on:" + entry['updated']
            description = entry['description'].split('updated:')
            changes = description.pop(0)
            field = changes.rpartition('\n')[2].strip()
            while description:                
                changes = description.pop(0).split('\n')
                values = changes[0].split('=>')                
                if (len(values) != 2):
                    printdbg(field + " not supported in changes analysis")
                    old_value = new_value = ""                    
                else:
                    # u'in-progress' => u'closed'
                    values = changes[0].split('=>')
                    old_value = self.remove_unicode(values[0].strip())
                    if old_value == "''": old_value =""
                    new_value = self.remove_unicode(values[1].strip())
                    if new_value == "''": new_value =""
                update = parse(entry['updated'])
                change = Change(unicode(field), unicode(old_value), unicode(new_value), by, update)
                changesList.append(change)
                if (len(changes)>1):
                    field = changes[1].strip()
        return changesList

    def remove_unicode(self, str):
        """
        Cleanup u'' chars indicating a unicode string
        """
        if (str.startswith('u\'') and str.endswith('\'')):
            str = str[2:len(str)-1]
        return str


    def run(self):
        """
        """
        printout("Running Bicho with delay of %s seconds" % (str(self.delay)))
        
        # redmine 1.0 support
        last_page=1
        tickets_page = 25 # fixed redmine


        bugs = [];
        bugsdb = get_database (DBRedmineBackend())
                
        # still useless in redmine
        bugsdb.insert_supported_traker("redmine", "beta")
        trk = Tracker (Config.url, "redmine", "beta")
        dbtrk = bugsdb.insert_tracker(trk)
        
        self.url_issues = Config.url+"?status_id=*&page=" + str(last_page)
        request = urllib2.Request(self.url_issues)
        base64string = base64.encodestring('%s:%s' % (Config.backend_user, Config.backend_password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)   
        f = urllib2.urlopen(request)         
        tickets = json.loads(f.read())
        for ticket in tickets:
            issue = self.analyze_bug(ticket)
            bugsdb.insert_issue(issue, dbtrk.id)
        
        last_ticket=tickets[0]['id']
        
        while True:  
            last_page += 1
            self.url_issues = Config.url+"?status_id=*&page="+str(last_page) 
            request = urllib2.Request(self.url_issues)
            base64string = base64.encodestring('%s:%s' % (Config.backend_user, Config.backend_password)).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)   
            f = urllib2.urlopen(request)         
            tickets = json.loads(f.read())
            
            pprint.pprint("Tickets read: " + str(tickets[0]['id']) + " " + str(tickets[-1]['id']))
            
            if tickets[0]['id'] == last_ticket:
                break
            
            for ticket in tickets:
                issue = self.analyze_bug(ticket)
                bugsdb.insert_issue(issue, dbtrk.id)
                                
        pprint.pprint("Total pages: " + str(last_page))
        
        printout("Done. Bugs analyzed:" + str(last_page * tickets_page))
        
Backend.register_backend('redmine', Redmine)
