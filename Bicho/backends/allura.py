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

import errno
import json
import os
import pprint
import random
import sys
import time
import traceback
import urllib
import feedparser

from storm.locals import DateTime, Desc, Int, Reference, Unicode, Bool


class DBAlluraIssueExt(object):
    # FIXME: Do we really need all this comments? DRY!!!
    """
    Maps elements from X{issues_ext_allura} table.

    @param labels: issue labels
    @type labels: C{str}
    @param private: issue private or not
    @type private: C{boolean}
    @param ticket_num: identifier of the issue
    @type ticket_num: C{int}
    @param discussion_thread_url: issue url for discussion thread
    @type discussion_thread_url: L{storm.locals.Unicode}
    @param related_artifacts: issue related artifacts
    @type related_artifacts: L{storm.locals.Unicode}
    @param custom_fields: issue custom fields
    @type custom_fields: L{storm.locals.Unicode}
    @param mod_date: issue modification date
    @type mod_date: L{storm.locals.Date}

    @param issue_id: identifier of the issue
    @type issue_id: C{int}


    @ivar __storm_table__: Name of the database table.
    @type __storm_table__: C{str}

    @ivar id: Extra issue fields identifier.
    @type id: L{storm.locals.Int}
    @ivar labels: issue labels
    @type labels: L{storm.locals.Unicode}
    @ivar private: issue private or not
    @type private: L{storm.locals.Boolean}
    @ivar ticket_num: Issue identifier.
    @type ticket_num: L{storm.locals.Int}
    @ivar discussion_thread_url: issue url for discussion thread
    @type discussion_thread_url: L{storm.locals.Unicode}
    @ivar related_artifacts: issue related artifacts
    @type related_artifacts: L{storm.locals.Unicode}
    @ivar custom_fields: issue custom fields
    @type custom_fields: L{storm.locals.Unicode}
    @ivar mod_date: issue modification date
    @type mod_date: L{storm.locals.Date}
    @ivar issue_id: Issue identifier.
    @type issue_id: L{storm.locals.Int}
    @ivar issue: Reference to L{DBIssue} object.
    @type issue: L{storm.locals.Reference}
    """
        
    __storm_table__ = 'issues_ext_allura'

    id = Int(primary=True)
    labels = Unicode()
    private = Bool()
    ticket_num = Int()
    discussion_thread_url = Unicode()
    related_artifacts = Unicode()
    custom_fields = Unicode()
    mod_date = DateTime()        
    issue_id = Int()
            
    issue = Reference(issue_id, DBIssue.id)
    
    def __init__(self, issue_id):
        self.issue_id = issue_id


class DBAlluraIssueExtMySQL(DBAlluraIssueExt):
    """
    MySQL subclass of L{DBAlluraIssueExt}
    """

    # If the table is changed you need to remove old from database
    __sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_ext_allura ( \
                    id INTEGER NOT NULL AUTO_INCREMENT, \
                    labels TEXT, \
                    private BOOLEAN, \
                    ticket_num INTEGER NOT NULL, \
                    discussion_thread_url TEXT, \
                    related_artifacts TEXT, \
                    custom_fields TEXT, \
                    mod_date DATETIME, \
                    issue_id INTEGER NOT NULL, \
                    PRIMARY KEY(id), \
                    FOREIGN KEY(issue_id) \
                    REFERENCES issues (id) \
                    ON DELETE CASCADE \
                    ON UPDATE CASCADE \
                     ) ENGINE=MYISAM;'

class DBAlluraBackend(DBBackend):
    """
    Adapter for Allura backend.
    """
    def __init__(self):
        self.MYSQL_EXT = [DBAlluraIssueExtMySQL]
        
    def insert_issue_ext(self, store, issue, issue_id):
        """
        Insert the given extra parameters of issue with id X{issue_id}.
        
        @param store: database connection
        @type store: L{storm.locals.Store}
        @param issue: issue to insert
        @type issue: L{AlluraIssue}
        @param issue_id: identifier of the issue
        @type issue_id: C{int}
        
        @return: the inserted extra parameters issue
        @rtype: L{DBAlluraIssueExt}
        """
        
        newIssue = False;
        
        try:
            db_issue_ext = store.find(DBAlluraIssueExt,
                                      DBAlluraIssueExt.issue_id == issue_id).one()
            if not db_issue_ext:
                newIssue = True
                db_issue_ext = DBAlluraIssueExt(issue_id)
                #db_issue_ext = DBSourceForgeIssueExt(issue.category, issue.group, issue_id)
        
            db_issue_ext.labels = unicode(issue.labels) 
            db_issue_ext.private = bool(issue.private)
            db_issue_ext.ticket_num = int(issue.ticket_num)
            db_issue_ext.discussion_thread_url = unicode(issue.discussion_thread_url)
            db_issue_ext.related_artifacts = unicode(issue.related_artifacts)
            db_issue_ext.custom_fields = unicode(issue.custom_fields)
            db_issue_ext.mod_date = issue.mod_date
        
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
        # select date_last_updated as date from issues_ext_allura order by date
        result = store.find(DBAlluraIssueExt)
        aux = result.order_by(Desc(DBAlluraIssueExt.mod_date))[:1]

        for entry in aux:
            return entry.mod_date.strftime('%Y-%m-%dT%H:%M:%SZ')

        return None


class AlluraIssue(Issue):
    """
    Ad-hoc Issue extension for allura's issue
    """
    def __init__(self, issue, type, summary, desc, submitted_by, submitted_on):
        Issue.__init__(self, issue, type, summary, desc, submitted_by,
                       submitted_on)
        
        if False:
            self.labels = None
            self.private = None
            self.ticket_num = None
            
            self.discussion_thread_url = None
            self.related_artifacts = None
            self.custom_fields = None
            self.mod_date = None

    
class Allura():
    
    project_test_file = None
    safe_delay = 5
    
    def __init__(self):
        self.delay = Config.delay
        
    def _convert_to_datetime(self,str_date):
        """
        Returns datetime object from string
        """
        return parse(str_date).replace(tzinfo=None)

    def analyze_bug(self, bug_url):
        #Retrieving main bug information
        printdbg(bug_url)
        bug_number = bug_url.split('/')[-1]

        try:
            f = urllib.urlopen(bug_url)

            # f = urllib.urlopen(bug_url) 
            json_ticket = f.read()
            # print json_ticket
            try:                
                issue_allura = json.loads(json_ticket)["ticket"]
                issue =  self.parse_bug(issue_allura)
                changes = self.analyze_bug_changes(bug_url)
                for c in changes:
                    issue.add_change(c)                 
                return issue

            except Exception, e:
                print "Problems with Ticket format: " + bug_number
                print e
                return None
    
        except Exception, e:
            printerr("Error in bug analysis: " + bug_url);
            print(e)
            raise
        
    def parse_bug(self, issue_allura):
        people = People(issue_allura["reported_by_id"])            
        people.set_name(issue_allura["reported_by"])
                
        issue = AlluraIssue(issue_allura["_id"],
                            "ticket",
                            issue_allura["summary"],
                            issue_allura["description"],
                            people,
                            self._convert_to_datetime(issue_allura["created_date"]))        
        people =  People(issue_allura["assigned_to_id"])
        people.set_name(issue_allura["assigned_to"])
        issue.assigned_to = people
        issue.status = issue_allura["status"]
        # No information from Allura for this fields
        issue.resolution = None
        issue.priority = None
                
        # Extended attributes
        issue.labels = str(issue_allura["labels"])
        issue.private = issue_allura["private"]
        issue.ticket_num = issue_allura["ticket_num"]
        issue.discussion_thread_url = issue_allura["discussion_thread_url"]
        issue.related_artifacts = str(issue_allura["related_artifacts"])
        issue.custom_fields = str(issue_allura["custom_fields"])
        issue.mod_date = self._convert_to_datetime(issue_allura["mod_date"])

        return issue
                    
        
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
        
        # limit=-1 is NOT recognized as 'all'.  500 is a reasonable limit. - allura code
        issues_per_query = 500
        start_page=0


        bugs = [];
        bugsdb = get_database (DBAlluraBackend())
                
        # still useless in allura
        bugsdb.insert_supported_traker("allura", "beta")
        trk = Tracker (Config.url, "allura", "beta")
        dbtrk = bugsdb.insert_tracker(trk)
        
        last_mod_date = bugsdb.get_last_modification_date()

        # Date before the first ticket
        time_window_start = "1900-01-01T00:00:00Z" 
        time_window_end = datetime.now().isoformat()+"Z"

        if last_mod_date:
            time_window_start = last_mod_date
            printdbg("Last bugs analyzed were modified on: %s" % last_mod_date)

        time_window = time_window_start + " TO  " + time_window_end
        
        self.url_issues = Config.url + "/search/?limit=1"
        self.url_issues += "&q="
        # A time range with all the tickets
        self.url_issues +=  urllib.quote("mod_date_dt:["+time_window+"]")
        printdbg("URL for getting metadata " + self.url_issues)

        f = urllib.urlopen(self.url_issues)
        ticketTotal = json.loads(f.read())
        
        total_issues = int(ticketTotal['count'])
        total_pages = total_issues/issues_per_query
        print("Number of tickets: " + str(total_issues))

        if  total_issues == 0:
            printout("No bugs found. Did you provide the correct url?")
            sys.exit(0)
        remaining = total_issues

        print "ETA ", (total_issues*Config.delay)/(60), "m (", (total_issues*Config.delay)/(60*60), "h)"
        
        while start_page <= total_pages:
            self.url_issues = Config.url + "/search/?limit="+str(issues_per_query)
            self.url_issues += "&page=" + str(start_page) + "&q="
            # A time range with all the tickets
            self.url_issues +=  urllib.quote("mod_date_dt:["+time_window+"]")
            # Order by mod_date_dt desc
            self.url_issues +=  "&sort=mod_date_dt+asc"

            printdbg("URL for next issues " + self.url_issues) 

            f = urllib.urlopen(self.url_issues)

            ticketList = json.loads(f.read())

            bugs=[]
            for ticket in ticketList["tickets"]:
                bugs.append(ticket["ticket_num"])

            for bug in bugs:
                try:
                    issue_url = Config.url+"/"+str(bug)
                    issue_data = self.analyze_bug(issue_url)
                    if issue_data is None:
                        continue
                    bugsdb.insert_issue(issue_data, dbtrk.id)
                    remaining -= 1
                    print "Remaining time: ", (remaining)*Config.delay/60, "m"
                    time.sleep(self.delay)
                except Exception, e:
                    printerr("Error in function analyze_bug " + issue_url)
                    traceback.print_exc(file=sys.stdout)
                except UnicodeEncodeError:
                    printerr("UnicodeEncodeError: the issue %s couldn't be stored"
                          % (issue_data.issue))
            start_page += 1
            
        printout("Done. Bugs analyzed:" + str(total_issues-remaining))
        
Backend.register_backend('allura', Allura)
