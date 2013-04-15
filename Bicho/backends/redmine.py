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

from BeautifulSoup import BeautifulSoup, Comment as BFComment

from dateutil.parser import parse
from datetime import datetime

import errno, json, os, random, time, traceback, urllib, urllib2, feedparser, base64, sys
import pprint 
import re

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
            #db_issue_ext.due_date = issue.due_date
            #db_issue_ext.estimated_hours = issue.estimated_hours
            db_issue_ext.fixed_version_id = issue.fixed_version_id
            #db_issue_ext.lft = issue.lft
            #db_issue_ext.rgt = issue.rgt
            #db_issue_ext.lock_version = issue.lock_version
            #db_issue_ext.parent_id = issue.parent_id
            db_issue_ext.project_id = issue.project_id
            #db_issue_ext.root_id = issue.root_id
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
        try:
            self.backend_password = Config.backend_password
            self.backend_user = Config.backend_user
        except AttributeError:
            printout("No account provided.")
            self.backend_password = None
            self.backend_user = None
        
    def _convert_to_datetime(self,str_date):
        """
        Returns datetime object from string
        """
        return parse(str_date).replace(tzinfo=None)

    # def analyze_bug(self, issue_redmine):
    #     issue =  self.parse_bug(issue_redmine)
    #     #        changes = self.analyze_bug_changes(bug_url)
    #     #        for c in changes:
    #     #            issue.add_change(c)                 
    #     return issue

    def _get_redmine_root(self, url):
        return url[:url.find('projects/')]
        
    def _get_author_email(self, author_id):
        root = self._get_redmine_root(Config.url)
        author_url = root + "users/" + str(author_id) + ".json"
        #print author_url
        res = None
        try:
            f = urllib2.urlopen(author_url)         
            person = json.loads(f.read())
            res = person['user']['mail']
        except (urllib2.HTTPError, KeyError):
            printdbg("User with id %s has no account information" % author_id)
            res = author_id
        return res
            
        #return author_id
        
    def analyze_bug(self, issue_redmine):
        #print(issue_redmine)
        #print("*** %s " % issue_redmine["author"]["id"])
        try:
            people = People(self._get_author_email(issue_redmine["author"]["id"]))
            people.set_name(issue_redmine["author"]["name"])
        except KeyError:
            people = People("None")

        try:
            desc = issue_redmine["description"]
        except KeyError:
            desc = ""
                
        issue = RedmineIssue(issue_redmine["id"],
                            "ticket",
                            issue_redmine["subject"],
                            desc,
                            people,
                            self._convert_to_datetime(issue_redmine["created_on"]))        
        try:
                #print("<<< %s " % issue_redmine["assigned_to"]["id"])
                people =  People(self._get_author_email(issue_redmine["assigned_to"]["id"]))
                people.set_name(issue_redmine["assigned_to"]["name"])
                issue.assigned_to = people
        except KeyError:
                people = People("None")
                issue.assigned_to = people
        issue.status = issue_redmine["status"]["name"]
        issue.priority = issue_redmine["priority"]["id"]
        # No information from Redmine for this field. Included in Status
        issue.resolution = None
                
        # Extended attributes
        try:
            issue.category_id = issue_redmine["category"]["id"]
        except KeyError:
            issue.category_id = None
        issue.done_ratio = issue_redmine["done_ratio"]
                
        # if issue_redmine["due_date"] is None:
        #     issue.due_date = None
        # else:
        #     issue.due_date = self._convert_to_datetime(issue_redmine["due_date"])
        
        #issue.estimated_hours = issue_redmine["estimated_hours"]
        try:
            issue.fixed_version_id = issue_redmine["fixed_version"]["id"]
        except KeyError:
            issue.fixed_version_id = None
        #issue.lft = issue_redmine["lft"]
        #issue.rgt = issue_redmine["rgt"]
        #issue.lock_version = issue_redmine["lock_version"]
        #issue.parent_id = issue_redmine["parent_id"]
        issue.project_id = issue_redmine["project"]["id"]
        #issue.root_id = issue_redmine["root_id"]
        # if issue_redmine["start_date"] is None:
        #     issue.start_date = None
        # else:
        #     issue.start_date = self._convert_to_datetime(issue_redmine["start_date"])
        try:
            issue.start_date = self._convert_to_datetime(issue_redmine["start_date"])
        except:
            issue.start_date = None
        issue.tracker_id = issue_redmine["tracker"]["id"]
        # if issue_redmine["updated_on"] is None:
        #     issue.updated_on = None
        # else:
        #     issue.updated_on = self._convert_to_datetime(issue_redmine["updated_on"])
        try:
            issue.updated_on = self._convert_to_datetime(issue_redmine["updated_on"])
        except KeyError:
            issue.updated_on = None

        # get changeset
        changes = self._get_issue_changeset(issue_redmine["id"])
        for c in changes:
            issue.add_change(c)

        print("Issue #%s updated on %s" % (issue_redmine["id"], issue.updated_on))

        return issue
                    
        
    # Not yet implemented: journals in Redmine 1.1
    def _get_issue_changeset(self, bug_id):
        aux = Config.url.rfind('/')
        bug_url = Config.url[:aux + 1]
        bug_url = bug_url + "issues/" + unicode(bug_id) + ".atom"
        
        # changes_url = bug_url.replace("rest/","")+"/feed.atom"
        printdbg("Analyzing issue changes " + bug_url)
        d = feedparser.parse(bug_url)
        changes = self.parse_changes(d)
        
        return changes

    def _parse_html_change(self, html):

        # several changes can be done at the same time
        html_changes = html.split('<li>')
        fields = []
        for hc in html_changes:        
            dirchange = {}
            dirchange["what"] = None
            dirchange["old_value"] = None
            dirchange["new_value"] = None
            soup = BeautifulSoup(hc)
            txt = soup.text
            if txt.find('set to') > 0:            
                mo = re.match(r'(.*)set to(.*)',txt)
                (dirchange["what"], dirchange["new_value"]) = mo.groups()
                fields.append(dirchange)
            elif txt.find('changed from') > 0:
                mo = re.match(r'(.*)changed from(.*)to(.*)', txt)
                (dirchange["what"], dirchange["old_value"], dirchange["new_value"]) = mo.groups()
                fields.append(dirchange)
        return fields
        
    def parse_changes (self, activity):
        changesList = []
        for entry in activity['entries']:
            try:
                by = People(entry['author_detail']['email'])
            except KeyError:
                by = People(entry['author_detail']['name'])
            date = parse(entry['updated'])
            fields = self._parse_html_change(entry['summary'])
            for f in fields:
                change = Change(f["what"], f["old_value"], f["new_value"], by, date)
                changesList.append(change)            
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

        if Config.url.find('?') > 0:
            self.url_issues = Config.url+"&status_id=*&sort=updated_on&page=" + str(last_page)
        else:
            self.url_issues = Config.url+"?status_id=*&sort=updated_on&page=" + str(last_page)
        request = urllib2.Request(self.url_issues)
        if self.backend_user:
            base64string = base64.encodestring('%s:%s' % (Config.backend_user, Config.backend_password)).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)   
        f = urllib2.urlopen(request)         
        tickets = json.loads(f.read())
        for ticket in tickets["issues"]:
            issue = self.analyze_bug(ticket)
            bugsdb.insert_issue(issue, dbtrk.id)
        
        last_ticket=tickets["issues"][0]['id']
        
        while True:  
            last_page += 1
            if Config.url.find('?') > 0:
                self.url_issues = Config.url+"&status_id=*&sort=updated_on&page="+str(last_page) 
            else:
                self.url_issues = Config.url+"?status_id=*&sort=updated_on&page="+str(last_page) 
            request = urllib2.Request(self.url_issues)
            #base64string = base64.encodestring('%s:%s' % (Config.backend_user, Config.backend_password)).replace('\n', '')
            #request.add_header("Authorization", "Basic %s" % base64string)   
            f = urllib2.urlopen(request)         
            tickets = json.loads(f.read())
            
            pprint.pprint("Tickets read: " + str(tickets["issues"][0]['id']) + " " + str(tickets["issues"][-1]['id']))
            
            if tickets["issues"][0]['id'] == last_ticket:
                break
            
            for ticket in tickets["issues"]:
                issue = self.analyze_bug(ticket)
                bugsdb.insert_issue(issue, dbtrk.id)
                                
        pprint.pprint("Total pages: " + str(last_page))
        
        printout("Done. Bugs analyzed:" + str(last_page * tickets_page))
        
Backend.register_backend('redmine', Redmine)
