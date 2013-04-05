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


class DBGerritIssueExt(object):

    __storm_table__ = 'issues_ext_gerrit'

    id = Int(primary=True)
    branch = Unicode()
    url = Unicode()
    change_id = Unicode()
    related_artifacts = Unicode()
    project = Unicode()
    mod_date = DateTime()        
    issue_id = Int()
    open = Unicode()
            
    issue = Reference(issue_id, DBIssue.id)
    
    def __init__(self, issue_id):
        self.issue_id = issue_id


class DBGerritIssueExtMySQL(DBGerritIssueExt):
    """
    MySQL subclass of L{DBGerritIssueExt}
    """

    # If the table is changed you need to remove old from database
    __sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_ext_gerrit ( \
                    id INTEGER NOT NULL AUTO_INCREMENT, \
                    branch TEXT, \
                    url TEXT,  \
                    change_id TEXT, \
                    related_artifacts TEXT, \
                    project TEXT, \
                    mod_date DATETIME, \
                    issue_id INTEGER NOT NULL, \
                    open TEXT, \
                    PRIMARY KEY(id), \
                    FOREIGN KEY(issue_id) \
                    REFERENCES issues (id) \
                    ON DELETE CASCADE \
                    ON UPDATE CASCADE \
                     ) ENGINE=MYISAM;'

class DBGerritBackend(DBBackend):
    """
    Adapter for Gerrit backend.
    """
    def __init__(self):
        self.MYSQL_EXT = [DBGerritIssueExtMySQL]
        
    def insert_issue_ext(self, store, issue, issue_id):
        """
        Insert the given extra parameters of issue with id X{issue_id}.
        
        @param store: database connection
        @type store: L{storm.locals.Store}
        @param issue: issue to insert
        @type issue: L{GerritIssue}
        @param issue_id: identifier of the issue
        @type issue_id: C{int}
        
        @return: the inserted extra parameters issue
        @rtype: L{DBGerritIssueExt}
        """
        
        newIssue = False;
        
        try:
            db_issue_ext = store.find(DBGerritIssueExt,
                                      DBGerritIssueExt.issue_id == issue_id).one()
            if not db_issue_ext:
                newIssue = True
                db_issue_ext = DBGerritIssueExt(issue_id)
                #db_issue_ext = DBSourceForgeIssueExt(issue.category, issue.group, issue_id)
        
            db_issue_ext.branch = issue.branch 
            db_issue_ext.url = issue.url
            db_issue_ext.change_id = issue.change_id
            db_issue_ext.related_artifacts = issue.related_artifacts
            db_issue_ext.project = issue.project
            db_issue_ext.mod_date = issue.mod_date
            db_issue_ext.open = unicode(issue.open)
        
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
        # select date_last_updated as date from issues_ext_gerrit order by date
        result = store.find(DBGerritIssueExt)
        aux = result.order_by(Desc(DBGerritIssueExt.mod_date))[:1]

        for entry in aux:
            return entry.mod_date.strftime('%Y-%m-%d %H:%M:%S')

        return None

class GerritIssue(Issue):
    """
    Ad-hoc Issue extension for gerrit's issue
    """
    def __init__(self, issue, type, summary, desc, submitted_by, submitted_on):
        Issue.__init__(self, issue, type, summary, desc, submitted_by,
                       submitted_on)
        
    
class Gerrit():
    
    project_test_file = None
    safe_delay = 5
    
    def __init__(self):
        self.delay = Config.delay
        
    def _convert_to_datetime(self, date):
        """
        Returns datetime object from string
        """
        import time
        return parse(time.strftime('%Y %m %d %H:%M:%S', time.localtime(date)))
        # return parse(str(str_date)).replace(tzinfo=None)

    def analyze_review(self, review):
        try:
            issue =  self.parse_review(review)
            changes = self.analyze_review_changes(review)
            for c in changes:
                issue.add_change(c)
            return issue

        except Exception, e:
            print "Problems with Review format: " + review['number']
            pprint.pprint(review)           
            print e
            return None
    
        
    def parse_review(self, review):
        if "username" in review["owner"].keys():
            people = People(review['owner']['username'])
        elif "email" in review["owner"].keys():
            people = People(review['owner']['email'])
        elif "name" in review["owner"].keys():
            people = People(review['owner']['name'])
        else:
            people = People(unicode(''))
    
        if "name" in review["owner"].keys():
            people.set_name(review["owner"]["name"])
        if "email" in review["owner"].keys():
            people.set_email(review["owner"]["email"])

        description = ""
        issue = GerritIssue(review["number"],
                            "review",
                            review["subject"],
                            description,
                            people,
                            self._convert_to_datetime(review["createdOn"])
                            )     
#        people =  People(review["assigned_to_id"])
#        people.set_name(review["assigned_to"])
#        issue.assigned_to = people
        issue.status = review["status"]
        # No information from Gerrit for this fields
        issue.assigned_to = None
        issue.resolution = None
        issue.priority = None
                

        issue.branch = review["branch"]
        issue.url = review["url"]
        issue.change_id = review["id"]
        if "topic" in review.keys():
            issue.related_artifacts = review["topic"]
        else:
            issue.related_artifacts = None  
        issue.project = review["project"]
        issue.mod_date = self._convert_to_datetime(review["lastUpdated"])
        issue.open = review["open"]

        return issue
                    
        
    def analyze_review_changes (self, review):        
        changes = self.parse_changes(review)        
        return changes

    # We support now just one patchSets
    def parse_changes (self, review):
        changesList = []
        patchSets = review['patchSets']
        
        for activity in patchSets: 
        
            # activity = patchSets[len(patchSets)-1]
        
#            if len(patchSets)>1:
#                printdbg(str(len(patchSets)) + " patchSets: "+review['url'])
    
            if "approvals" not in activity.keys():
                return changesList
            
            patchSetNumber = activity['number']
                
            for entry in activity['approvals']:
                # print "changed_by:" + entry['author']
                if "username" in entry["by"].keys():
                    by = People(entry['by']['username'])
                elif "email" in entry["by"].keys():
                    by = People(entry['by']['email'])
                elif "name" in entry["by"].keys():
                    by = People(entry['by']['name'])
                else:
                    by = People(unicode(''))
                
                if "name" in entry["by"].keys():
                    by.set_name(entry["by"]["name"])
                if "email" in entry["by"].keys():
                    by.set_email(entry["by"]["email"])
                # print "changed_on:" + entry['updated']
                field = entry['type'] 
                new_value = entry['value']
                old_value = patchSetNumber
                update = self._convert_to_datetime(entry["grantedOn"])
                change = Change(field, old_value, new_value, by, update)
                changesList.append(change)
                
        return changesList
    
    def getReviews (self, limit, start):
                
        args_gerrit ="gerrit query "
        args_gerrit += "project:" + Config.gerrit_project
        args_gerrit += " limit:" + str(limit) 
        if (start != ""): 
            args_gerrit += " resume_sortkey:"+start
                        
        args_gerrit += " --all-approvals --format=JSON"
        
        printdbg("Gerrit cmd: " + args_gerrit)
                
        cmd = ["ssh", "-p 29418", Config.url, args_gerrit]
        import subprocess 
        tickets_raw = subprocess.check_output(cmd)
        tickets_raw = "["+tickets_raw.replace("\n",",")+"]"
        tickets_raw = tickets_raw.replace(",]","]")
        tickets = json.loads(tickets_raw)
        
#        tickets_test = '[{"project":"openstack/nova","branch":"master","topic":"bug/857209","id":"I660532ee5758c7595138d4dcf5a2825ddf898c65","number":"637","subject":"contrib/nova.sh: Updated to latest \\u0027upstream\\u0027 commit:6a8433a resolves bug 857209","owner":{"name":"Dave Walker","email":"Dave.Walker@canonical.com","username":"davewalker"},"url":"https://review.openstack.org/637","createdOn":1316815511,"lastUpdated":1316815646,"sortKey":"0017e78f0000027d","open":false,"status":"ABANDONED","patchSets":[{"number":"1","revision":"95d8d0f75c188f7eabf00ecf6bd5b397852e67b9","ref":"refs/changes/37/637/1","uploader":{"name":"Dave Walker","email":"Dave.Walker@canonical.com","username":"davewalker"},"createdOn":1316815511}]},'
#        tickets_test += '{"project":"openstack/nova","branch":"master","id":"I812e95fb0744ad84abd7ea2ad7d11123667abbc8","number":"635","subject":"Made jenkins email pruning more resilient.","owner":{"name":"Monty Taylor","email":"mordred@inaugust.com","username":"mordred"},"url":"https://review.openstack.org/635","createdOn":1316813897,"lastUpdated":1316814951,"sortKey":"0017e7830000027b","open":false,"status":"MERGED","patchSets":[{"number":"1","revision":"c586e4ed23846420177802c164f594e021cceea8","ref":"refs/changes/35/635/1","uploader":{"name":"Monty Taylor","email":"mordred@inaugust.com","username":"mordred"},"createdOn":1316813897,"approvals":[{"type":"SUBM","value":"1","grantedOn":1316814951,"by":{"name":"Jenkins","username":"jenkins"}},{"type":"VRIF","description":"Verified","value":"1","grantedOn":1316814948,"by":{"name":"Jenkins","username":"jenkins"}},{"type":"CRVW","description":"Code Review","value":"2","grantedOn":1316814192,"by":{"name":"Brian Waldon","email":"bcwaldon@gmail.com","username":"bcwaldon"}}]}]},'
#        tickets_test += '{"project":"openstack/nova","branch":"master","id":"I495363b44d9da96d66f85c2a621393329830aeb3","number":"630","subject":"Fixing bug 857712","owner":{"name":"Brian Waldon","email":"bcwaldon@gmail.com","username":"bcwaldon"},"url":"https://review.openstack.org/630","createdOn":1316810421,"lastUpdated":1316813692,"sortKey":"0017e76e00000276","open":false,"status":"MERGED","patchSets":[{"number":"1","revision":"ddb6945e8fbb8a00d5b67a6a6b8a069b7642022d","ref":"refs/changes/30/630/1","uploader":{"name":"Brian Waldon","email":"bcwaldon@gmail.com","username":"bcwaldon"},"createdOn":1316810421,"approvals":[{"type":"SUBM","value":"1","grantedOn":1316813692,"by":{"name":"Jenkins","username":"jenkins"}},{"type":"VRIF","description":"Verified","value":"1","grantedOn":1316813689,"by":{"name":"Jenkins","username":"jenkins"}},{"type":"CRVW","description":"Code Review","value":"1","grantedOn":1316811221,"by":{"name":"Josh Kearney","email":"josh@jk0.org","username":"jk0"}},{"type":"CRVW","description":"Code Review","value":"2","grantedOn":1316812789,"by":{"name":"Brian Lamar","email":"brian.lamar@gmail.com","username":"blamar"}},{"type":"CRVW","description":"Code Review","value":"1","grantedOn":1316810744,"by":{"name":"Mark McLoughlin","email":"markmc@redhat.com","username":"markmc"}}]}]},'
#        tickets_test += '{"type":"stats","rowCount":67,"runTimeMilliseconds":365}]'        
#        tickets = json.loads(tickets_test)

        
        return tickets


    def run(self):
        """
        """
        printout("Running Bicho with delay of %s seconds" % (str(self.delay)))
        
        bugs = [];
        bugsdb = get_database (DBGerritBackend())
                
        # still useless in gerrit
        bugsdb.insert_supported_traker("gerrit", "beta")
        trk = Tracker (Config.url+"_"+Config.gerrit_project, "gerrit", "beta")
        dbtrk = bugsdb.insert_tracker(trk)
        
        last_mod_time = 0        
        last_mod_date = bugsdb.get_last_modification_date()                
        if last_mod_date:
            printdbg("Last reviews analyzed were modified on date: %s" 
                     % last_mod_date)
            last_mod_time = time.mktime(time.strptime
                                        (last_mod_date, '%Y-%m-%d %H:%M:%S'))
            
        limit = 500 # gerrit default 500
        last_item = "";
        # last_item = "001f672c00002f80";
        number_results = limit
        total_reviews = 0
        
        while (number_results == limit):
            # ordered by lastUpdated        
            tickets = self.getReviews(limit, last_item)
            number_results = 0
                
            reviews = []
            for entry in tickets:
                if 'project' in entry.keys():
                    if (entry['lastUpdated']<last_mod_time):
                        break
                    reviews.append(entry["number"])
                    review_data = self.analyze_review(entry)
                    last_item = entry['sortKey']
                    bugsdb.insert_issue(review_data, dbtrk.id)
                    number_results = number_results+1
                elif 'rowCount' in entry.keys():
                    pprint.pprint(entry)
                    printdbg("CONTINUE FROM: " + last_item)
            total_reviews = total_reviews + int(number_results)

        print("Done. Number of reviews: " + str(total_reviews))
        
Backend.register_backend('gerrit', Gerrit)