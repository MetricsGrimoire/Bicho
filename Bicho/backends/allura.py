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
from Bicho.common import Tracker, Issue, People

from dateutil.parser import parse
from datetime import datetime

import errno
import json
import os
import pprint
import random
import sys
import time
import urllib

from storm.locals import DateTime, Int, Reference, Unicode, Bool


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
    MySQL subclass of L{DBBugzillaIssueExt}
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
    
    project_cache_file = None
    safe_delay = 5
    
    def __init__(self):
        self.delay = Config.delay
        self.url = Config.url
        
    def _convert_to_datetime(self,str_date):
        """
        Returns datetime object from string
        """
        return parse(str_date).replace(tzinfo=None)
                
    def analyze_bug(self, bug_url):
        #Retrieving main bug information
        printdbg(bug_url)

        try:
            if Config.cache:
                bug_number = bug_url.split('/')[-1]
                bug_cache_file = self.project_cache_file + "." + bug_number
                try:
                    f = open(bug_cache_file)
                except Exception, e:                                        
                    if e.errno == errno.ENOENT:
                        f = open(bug_cache_file,'w')
                        fr = urllib.urlopen(bug_url)
                        f.write(fr.read())
                        f.close()
                        f = open(bug_cache_file)
                    else:
                        print "ERROR", e.errno
                        raise e
            else:
                f = urllib.urlopen(bug_url)

            # f = urllib.urlopen(bug_url)
            # f = open(os.path.join(os.path.dirname(__file__),"../../test/ticket_allura.json")); 
            json_ticket = f.read()
            try:                
                issue_allura = json.loads(json_ticket)["ticket"]
            except Exception, e:
                print "Probably Allura has banned us. Use --cache and a longer delay than", Config.delay
                print e
                os.remove(bug_cache_file)
                sys.exit()
    
        except Exception, e:
            printerr("Error in bug analysis: " + bug_url);
            print(e)
            raise
        
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
                
        #Retrieving changes
#        bug_activity_url = url + "show_activity.cgi?id=" + bug_id
#        printdbg( bug_activity_url )
#        data_activity = urllib.urlopen(bug_activity_url).read()
#        parser = SoupHtmlParser(data_activity, bug_id)
#        changes = parser.parse_changes()
#        for c in changes:
#            issue.add_change(c)
        return issue


    def run(self):
        """
        """
        printout("Running Bicho with delay of %s seconds" % (str(self.delay)))
        
        bugs = [];
        bugsdb = get_database (DBAlluraBackend())
                
        # still useless
        bugsdb.insert_supported_traker("allura", "beta")
        trk = Tracker (Config.url, "allura", "beta")

        dbtrk = bugsdb.insert_tracker(trk)
        
        self.url = Config.url
        
        if Config.cache:
            printdbg("Using file cache")
            tracker_cache_dir = os.path.join(Config.get_cache_dir(), trk.name)
            if not os.path.isdir (tracker_cache_dir):
                create_dir (os.path.join(Config.get_cache_dir(), trk.name))
            project_name = self.url.split("/")[-2]
            self.project_cache_file = os.path.join(tracker_cache_dir, project_name) 
            try:
                f = open(self.project_cache_file)
            except Exception, e:
                if e.errno == errno.ENOENT:
                    f = open(self.project_cache_file,'w+')
                    fr = urllib.urlopen(self.url)
                    f.write(fr.read())
                    f.close()
                    f = open(self.project_cache_file)
        else:
            f = urllib.urlopen(self.url)
            
        ticketList = json.loads(f.read())
        for ticket in ticketList["tickets"]:
            bugs.append(ticket["ticket_num"])                    
        
        nbugs = len(bugs)
        
        if len(bugs) == 0:
            printout("No bugs found. Did you provide the correct url?")
            sys.exit(0)
        
        # test_bugs = bugs[random.randint(0,len(bugs))::100][0:100]
        
        print "Total bugs", nbugs
        print "ETA ", (nbugs*Config.delay)/(60), "m (", (nbugs*Config.delay)/(60*60), "h)" 
        
        sys.exit()
                
        for bug in bugs:
            try:
                issue_url = self.url+"/"+str(bug)
                issue_data = self.analyze_bug(issue_url)
                bugsdb.insert_issue(issue_data, dbtrk.id)
            except Exception, e:
                printerr("Error in function analyze_bug " + issue_url)
                print(e)
            except UnicodeEncodeError:
                printerr("UnicodeEncodeError: the issue %s couldn't be stored"
                      % (issue_data.issue))

            time.sleep(self.delay)
            
        printout("Done. %s bugs analyzed" % (len(bugs)))
        
Backend.register_backend('allura', Allura)