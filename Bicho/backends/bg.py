# Copyright (C) 2008  GSyC/LibreSoft
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
# Authors: Daniel Izquierdo Cortazar <dizquierdo@gsyc.es>
#



from Bicho.backends import Backend, register_backend
import urllib
import time
#libraries for sql access
import Bicho.Bug as Bug
from Bicho.SqlBug import *
from storm.locals import *
#XML parser
import xml.sax.handler
from xml.sax._exceptions import SAXParseException
#HTML parser
from HTMLParser import HTMLParser
from Bicho.utils import *


#######################################################
#Parsing HTML from each change
#######################################################
class ParserBGChanges(HTMLParser):

    (INIT_ST, ST_2, ST_3, ST_4, ST_5, ST_6) = range(6)

    def __init__(self, bugURL):
        HTMLParser.__init__(self)
        self.data = ""
        self.state = ParserBFChanges.INIT_ST

        self.dataChanges = {"Who"  :  "",
                            "When" :  "",
                            "What" :  "",
                            "Removed" : "",
                            "Added":  ""}

    def handle_starttag (self, tag, attrs):
        if tag == "td":
            self.statesMachine("", "<td>")

    def handle_data (self, data):
        self.statesMachine(data, "")

    def handle_endtag(self, tag):
        if tag == "td":
            self.statesMachine("", "</td>")

    def error (self, msg):
        printerr ("Parsing Error \"%s\", trying to recover..." % (msg))
        pass

    def getDataBug(self):
        bug = Bug.Bug()
        #code ...
        return bug


#######################################################
#Parsing XML from each bug
#######################################################
class BGComment:
    def __init__(self):
        #Common fields in every Bugzilla BTS
        self.bug_id
        self.who = None
        self.bug_when = None
        self.thetext = None


class BGChanges:
    def __init__(self):
        #Common fields in every Bugzilla BTS
        self.bug_id
        self.who
        self.what
        self.when
        self.removed
        self.added

class BugsHandler(xml.sax.handler.ContentHandler):

    def __init__ (self):
        #Common fields in every Bugzilla BTS
        #Commented fields are those which are ignored
        self.bug_id = None
        self.creation_ts = None
        self.short_desc = None
#        self.delta_ts = None
#        self.reporter_accessible = None
#        self.cclist_accessible = None
#        self.classification_id = None
#        self.classification = None
#        self.product = None
#        self.component = None
#        self.version = None
#        self.rep_platform = None
#        self.op_sys = None
        self.bug_status = None
        self.priority = None
#        self.bug_severity = None
#        self.target_milestone = None
        self.reporter = None
        self.assigned_to = None
#        self.cc = []
        self.long_desc = []

        self.is_bug_id = False
        self.is_creation_ts = False
        self.is_short_desc = False
        self.is_bug_status = False
        self.is_priority = False
        self.is_reporter = False
        self.is_assigned_to = False
        self.is_description = False
        


    def startElement(self, name, attrs): 
        if name == 'bug_id':
            self.is_bug_id = True
        elif name == 'creation_ts':
            self.is_creation_ts = True
        elif name == 'short_desc':
            self.is_short_desc = True
        elif name == 'bug_status':
            self.is_bug_status = True
        elif name == 'priority':
            self.is_priority = True
        elif name == 'reporter':
            self.is_reporter = True
        elif name == 'assigned_to':
            self.is_assigned_to = True
             
          

    def characters (self, ch): 
        if self.is_bug_id:
            self.bug_id =  str(ch)

        elif self.is_creation_ts:
            self.creation_ts = str(ch)

        elif self.is_short_desc:
            self.short_desc = str(ch)

        elif self.is_bug_status:
            self.bug_status = str(ch)

        elif self.is_priority:
            self.priority = str(ch)

        elif self.is_reporter:
            self.reporter = str(ch)

        elif self.is_assigned_to:
            self.assigned_to = str(ch)
            
    def endElement(self, name):
        if name == 'bug_id':
            self.is_bug_id = False
        elif name == 'creation_ts':
            self.is_creation_ts = False
        elif name == 'short_desc':
            self.is_short_desc = False
        elif name == 'bug_status':
            self.is_bug_status = False
        elif name == 'priority':
            self.is_priority = False
        elif name == 'reporter':
            self.is_reporter = False
        elif name == 'assigned_to':
            self.is_assigned_to = False

    def printDataBug(self):
        print ""
        print "ID: " +  self.bug_id
        print "Creation date: " + self.creation_ts
        print "Short description: " + self.short_desc
        print "Status: " + self.bug_status
        print "Priority: " + self.priority
        print "Reporter: " + self.reporter
        print "Assigned To: " + self.assigned_to
        print ""


    def getDataBug(self):

        bug = Bug.Bug()
        bug.Id = self.bug_id
        bug.Summary = self.short_desc
        bug.Description = ""
        bug.DateSubmitted = self.creation_ts
        bug.Status = self.bug_status
        bug.Priority = self.priority
        bug.Category = ""
        bug.Group = ""
        bug.AssignedTo = self.assigned_to
        bug.SubmittedBy = self.reporter

        #for comment in comments ...
            #c = Bug.Comment()

        #for change in changes ...
            #ch = Bug.Change()

        return bug



#######################################################
#Bugzilla backend
#######################################################
class BGBackend (Backend):

    def __init__ (self):
        Backend.__init__ (self)
        options = OptionsStore()
        self.url = options.url

    def getDomain(self, url):
        
        strings = url.split('/')
        return strings[0] + "//" + strings[2] + "/"
        



    def analyzeBug(self, bug_url):

        print bug_url

        handler = BugsHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)

        f = urllib.urlopen(bug_url)

        try:
            parser.feed(f.read())
        except Exception, e:
            print "Error parsing URL: " + bug_url
            raise
        
        f.close()
        parser.close()
        
        #handler.printDataBug()

        dataBug = handler.getDataBug()
    
        return dataBug


    def run (self):
        
        debug ("Running Bicho")

        #retrieving data in csv format
        url = self.url + "&ctype=csv"

        f = urllib.urlopen(url)

        #Problems using csv library, not all the fields are delimited by
        # '"' character. Easier using split.
        bugList_csv = f.read().split('\n')
        bugs = []
        #Ignoring first row
        for bug_csv in bugList_csv[1:]:
            #First field is the id field, necessary to later create the url
            #to retrieve bug information
            bugs.append(bug_csv.split(',')[0])
        
        url = self.url
        url = self.getDomain(url)

        for bug in bugs:
            #The URL from bugzilla (so far KDE and GNOME) are like:
            #http://<domain>/show_bug.cgi?id=<bugid>&ctype=xml 
            bug_url = url + "show_bug.cgi?id=" + bug + "&ctype=xml"
            try:
                dataBug = self.analyzeBug(bug_url)
            except:
                continue
            
            
            
            db = getDatabase()
            dbBug = DBBug(dataBug)
            db.insert_bug(dbBug)
          
            #work in progress
#            print ("Adding comments")
#            for comment in dataBug.Comments:
#                dbComment = DBComment(comment)
#                db.insert_comment(dbComment)

#            print "Adding changes"
#            for change in dataBug.Changes:
#                dbChange = DBChange(change)
#                db.insert_change(dbChange)
        

            time.sleep(10)

register_backend ("bg", BGBackend)   
