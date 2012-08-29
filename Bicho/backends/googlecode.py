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

from storm.locals import DateTime, Int, Reference, Unicode, Bool


class DBGoogleCodeIssueExt(object):        
    __storm_table__ = 'issues_ext_googlecode'

    id = Int(primary=True)
    ticket_num = Int()
    closed_date = DateTime()
    mod_date = DateTime()
    issue_id = Int()
            
    issue = Reference(issue_id, DBIssue.id)
    
    def __init__(self, issue_id):
        self.issue_id = issue_id


class DBGoogleCodeIssueExtMySQL(DBGoogleCodeIssueExt):
    """
    MySQL subclass of L{DBGoogleCodeIssueExt}
    """

    # If the table is changed you need to remove old from database
    __sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_ext_googlecode ( \
                    id INTEGER NOT NULL AUTO_INCREMENT, \
                    star TEXT, \
                    ticket_num INTEGER NOT NULL, \
                    mod_date DATETIME, \
                    closed_date DATETIME, \
                    issue_id INTEGER NOT NULL, \
                    PRIMARY KEY(id), \
                    FOREIGN KEY(issue_id) \
                    REFERENCES issues (id) \
                    ON DELETE CASCADE \
                    ON UPDATE CASCADE \
                     ) ENGINE=MYISAM;'

class DBGoogleCodeBackend(DBBackend):
    """
    Adapter for GoogleCode backend.
    """
    def __init__(self):
        self.MYSQL_EXT = [DBGoogleCodeIssueExtMySQL]
        
    def insert_issue_ext(self, store, issue, issue_id):
        
        newIssue = False;
        
        try:
            db_issue_ext = store.find(DBGoogleCodeIssueExt,
                                      DBGoogleCodeIssueExt.issue_id == issue_id).one()
            if not db_issue_ext:
                newIssue = True
                db_issue_ext = DBGoogleCodeIssueExt(issue_id)
            
            db_issue_ext.star = unicode(issue.star)
            db_issue_ext.ticket_num = int(issue.ticket_num) 
            db_issue_ext.mod_date = issue.mod_date             
            db_issue_ext.closed_date = issue.closed_date
            
            if newIssue == True:
                store.add(db_issue_ext)
            
            store.flush()
            return db_issue_ext
        except:
            store.rollback()
            raise

    def insert_change_ext(self, store, change, change_id):
        pass

class GoogleCodeIssue(Issue):
    """
    Ad-hoc Issue extension for googlecode's issue
    """
    def __init__(self, issue, type, summary, desc, submitted_by, submitted_on):
        Issue.__init__(self, issue, type, summary, desc, submitted_by,
                       submitted_on)        
        if False:
            self.star = None
            self.ticket_num = None            
            self.closed_date = None
            self.mod_date = None

    
class GoogleCode():
            
    def __init__(self):
        self.delay = Config.delay
        self.url = Config.url
        
    def _convert_to_datetime(self,str_date):
        return parse(str_date).replace(tzinfo=None)
                
    def analyze_bug(self, entry):        
        people = People(entry['author_detail']['href'])                        
        people.set_name(entry['author_detail']['name'])
            
        issue = GoogleCodeIssue(entry['id'],
                        'issue',
                        entry['title'],
                        entry['content'],
                        people,
                        self._convert_to_datetime(entry['published']))

        # Strange how the parser rename this fields
        if 'issues_uri' in entry.keys():
            people =  People(entry['issues_uri'])
            people.set_name(entry['issues_username'])
            issue.assigned_to = people
        issue.status = entry['issues_status']
        issue.resolution = entry['issues_state'] 
        issue.priority = entry['issues_label']
            
        # Extended attributes
        # issue.labels = str(issue_googlecode["labels"])
        issue.star = entry['issues_stars']
        issue.ticket_num = entry['issues_id']
        issue.mod_date = self._convert_to_datetime(entry['updated'])
        issue.closed_date = None
        if 'issues_closeddate' in entry.keys():
            issue.closed_date = self._convert_to_datetime(entry['issues_closeddate'])
                
        changes_url = Config.url + "/issues/" + issue.ticket_num + "/comments/full"
        printdbg("Analyzing issue " + changes_url)

        d = feedparser.parse(changes_url)
        changes = self.parse_changes(d, issue.ticket_num)

        for c in changes:
            issue.add_change(c)
                                                    
        return issue

    def parse_changes (self, activity, bug_id):
        changesList = []
        for entry in activity['entries']:
            if not 'issues_status' in entry.keys():
                continue
            by = People(entry['author_detail']['href'])                        
            update = parse(entry['updated'])
            field =  'Status'
            old_value = ''
            new_value = entry['issues_status']
            change = Change(unicode(field), unicode(old_value), unicode(new_value), by, update)
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
        
        issues_per_query = 250
        start_issue=1

        bugs = [];
        bugsdb = get_database (DBGoogleCodeBackend())
                
        # still useless
        bugsdb.insert_supported_traker("googlecode", "beta")
        trk = Tracker (Config.url, "googlecode", "beta")

        dbtrk = bugsdb.insert_tracker(trk)
        
        self.url = Config.url
        
        
       #  https://code.google.com/feeds/issues/p/mobile-time-care
        self.url_issues = Config.url + "/issues/full?max-results=1" 
        printdbg("URL for getting metadata " + self.url_issues)        
                            
        d = feedparser.parse(self.url_issues)
                
        total_issues = int(d['feed']['opensearch_totalresults'])
        print "Total bugs: ", total_issues
        if  total_issues == 0:
            printout("No bugs found. Did you provide the correct url?")
            sys.exit(0)
        remaining = total_issues                

        print "ETA ", (total_issues*Config.delay)/(60), "m (", (total_issues*Config.delay)/(60*60), "h)"

        while start_issue < total_issues:            
            self.url_issues = Config.url + "/issues/full?max-results=" + str(issues_per_query) 
            self.url_issues += "&start-index=" + str(start_issue)
            
            printdbg("URL for next issues " + self.url_issues) 
                                                            
            d = feedparser.parse(self.url_issues)
                                    
            for entry in d['entries']:
                try:
                    issue = self.analyze_bug(entry)
                    if issue is None:
                        continue
                    bugsdb.insert_issue(issue, dbtrk.id)
                    remaining -= 1
                    print "Remaining time: ", (remaining)*Config.delay/60, "m", " issues ", str(remaining) 
                    time.sleep(Config.delay)
                except Exception, e:
                    printerr("Error in function analyze_bug ")
                    pprint.pprint(entry)
                    traceback.print_exc(file=sys.stdout)
                except UnicodeEncodeError:
                    printerr("UnicodeEncodeError: the issue %s couldn't be stored"
                          % (issue.issue))
            
            start_issue += issues_per_query

                                            
        printout("Done. %s bugs analyzed" % (total_issues-remaining))
        
Backend.register_backend('googlecode', GoogleCode)