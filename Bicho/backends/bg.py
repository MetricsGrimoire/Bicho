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
import datetime


#######################################################
#Parsing HTML from each change
#######################################################
class Change():
#Bugzilla provides five fields for each change:
#Who, When, What, Removed and Added.
#In order to translate that information to the standar database 
#used in Bicho:
#	Who = SubmittedBy
#	When = Date
#	What = Field
#	Removed = OldValue
#	Regarding the Added, this is one of the current data, so 
#it is not necessary to add this information.

    def __init__(self, idBug, who, when, what, removed, added):
        self.IdBug = idBug
        self.SubmittedBy = who
        self.Date = when
        self.Field = what
        self.OldValue = removed
        self.added = added #This value is stored, but not used

    def __init__(self):
        self.IdBug = ""
        self.SubmittedBy = ""
        self.Date = ""
        self.Field = ""
        self.OldValue = ""
        self.added = "" #This value is stored but not used

    def __init__ (self, idBug):
        self.IdBug = idBug
        self.SubmittedBy = ""
        self.Date = ""
        self.Field = ""
        self.OldValue = ""
        self.added = "" #This value is stored but not used


    def setIdBug(self, idBug):
        self.IdBug = idBug

    def setSubmittedBy(self, who):
        self.SubmittedBy = who

    def setDate(self, when):
        self.Date = when
  
    def setField(self, what):
        self.Field = what

    def setOldValue(self, removed):
        self.OldValue = removed

    def setAdded(self, added):
        self.added = added

    def getIdBug(self):
        return self.IdBug

    def getSubmittedBy(self):
        return self.SubmittedBy

    def getDate(self):
        return self.Date
 
    def getField(self):
        return self.Field

    def getOldValue(self):
        return self.OldValue

    def getAdded(self):
        return self.added

   
    def printChange(self):
        print "Who (SubmittedBy): " + self.SubmittedBy
        print "When (Date): " + self.Date
        print "What (Field): " + self.Field
        print "Removed (Old Value): " + self.OldValue
        print "Added: " + self.added


class Comment():

    def __init__():
        self.IdBug = ""
        self.DateSubmitted = ""
        self.SubmittedBy = ""
        self.Comment = ""

    def __init__ (self, idBug, who, when, the_text):
        self.IdBug = idBug
        self.DateSubmitted = when
        self.SubmittedBy = who
        self.Comment = the_text


class ParserBGChanges(HTMLParser):

    (INIT_ST, ST_2, ST_3, ST_4, ST_5, ST_6) = range(6)

    def __init__(self, bugURL, idBug):
        HTMLParser.__init__(self)
        self.data = ""
        self.state = ParserBGChanges.INIT_ST
        self.SubmittedBy = ""
        self.Date = ""
        self.rows = 0
        self.dataChanges = {"Who"  :  "",
                            "When" :  "",
                            "What" :  "",
                            "Removed" : "",
                            "Added":  ""}
        self.changes = []
        #self.change = Change()
        self.values = []
        self.waitingData = False
        self.data = ""
        self.IdBug = idBug

    def parserData(self, data):
        #print data
        values = data.split('\n')

        init = True
        changes = []
        firstBlank = False
        secondBlank = False
        submittedBy = ""
        date = ""

        for value in values:
            if init:
                change = Change(self.IdBug)
                init = False
                change.setSubmittedBy(value)

                continue


            if firstBlank and secondBlank:
                self.changes.append(change)
                change = Change(self.IdBug)
                change.setSubmittedBy(value)
                firstBlank = False
                secondBlank = False
                continue

            if len(value.strip())==0 and not firstBlank:
                firstBlank = True
                continue

            if len(value.strip())==0 and firstBlank:
                secondBlank = True
                continue

            if value <> "" and firstBlank and change.getField()<>"":
                #change.printChange()
                self.changes.append(change)

                submittedBy = change.getSubmittedBy()
                date = change.getDate()

                change = Change(self.IdBug)
                change.setSubmittedBy(submittedBy)
                change.setDate(date)
                change.setField(value)
                
                firstBlank = False
                continue

            if value <> "" and firstBlank and change.getField()== "":
                firstBlank = False

                
            if change.getSubmittedBy() == "":
                change.setSubmittedBy(value)
            elif change.getDate() == "":
                change.setDate(value)
            elif change.getField() == "":
                change.setField(value)
            elif change.getOldValue() == "":
                change.setOldValue(value)

            #Data is stored but not used
            elif change.getAdded() == "":
                change.setAdded(value)
                   
 

    def statesMachine(self, data, tag, attrs):

        if self.state == ParserBGChanges.INIT_ST:
           
            if tag == "<table>":
                self.state = ParserBGChanges.ST_2

        elif self.state == ParserBGChanges.ST_2:
            if data=="Who":
                self.state = ParserBGChanges.ST_3

        elif self.state == ParserBGChanges.ST_3:
            if tag == "<tr>":
                self.state = ParserBGChanges.ST_4

        elif self.state == ParserBGChanges.ST_4:
            if (data == "\n        " or data == "\n            ") and not self.waitingData:
               
                self.waitingData = True
                return

            if tag == "</table>":
                self.state = ParserBGChanges.ST_5
                self.parserData(self.data)
                return


            if data <> "":
                self.values.append(data)
                self.data = self.data + data

            if len(attrs) > 0:
                self.values.append(attrs[0][1])
                self.data = self.data + data
                #if attrs[0][1] = n, then this the field who or when will
                #remain the same during the next n iterations

            self.waitingData = False
                

        elif self.state == ParserBGChanges.ST_5:
            return


    def handle_starttag (self, tag, attrs):
        if tag == "table":
            self.statesMachine("", "<table>", "")

        elif tag == "tr":
            self.statesMachine("", "<tr>", "")

        elif tag == "td":
            self.statesMachine("", "<td>", attrs)

        elif tag == "th":
            self.statesMachine("", "<th>", "")

    def handle_data (self, data):
        self.statesMachine(data, "", "")
      
    def handle_endtag(self, tag):
        if tag == "table":
            self.statesMachine("", "</table>", "")
        elif tag == "tr":
            self.statesMachine("", "</tr>", "")
        elif tag == "td":
            self.statesMachine("", "</td>", "")
        elif tag == "th":
            self.statesMachine("", "</th>", "")

    def error (self, msg):
        printerr ("Parsing Error \"%s\", trying to recover..." % (msg))
        pass

    def getDataChanges(self):
        
        return self.changes


#######################################################
#Parsing XML from each bug
#######################################################



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

        #Comments
        self.comments = []
        self.comment = Comment("","","","")
        self.is_long_desc = False
        self.is_who = False
        self.is_bug_when = False
        self.is_the_text = False

        self.who = ""
        self.bug_when = ""
        self.the_text = ""
        


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

        #parsing comments
        elif name == 'long_desc':
            self.is_long_desc = True
        elif name == 'who':
            self.is_who = True
        elif name == 'bug_when':
            self.is_bug_when = True
        elif name == 'thetext':
            self.is_the_text = True


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

        #parsing comments
        elif self.is_who:
            self.who = str(ch)
        elif self.is_bug_when:
            self.bug_when = str(ch)
        elif self.is_the_text:
            self.the_text = str(ch.encode('utf-8'))
            self.comment = Comment(self.bug_id, self.who, self.bug_when, self.the_text)
            self.comments.append(self.comment)

            
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

        #parsing comments
        elif name == 'long_desc':
            self.is_long_desc = False
        elif name == 'who':
            self.is_who = False
        elif name == 'bug_when':
            self.is_bug_when = False
        elif name == 'thetext':
            self.is_the_text = False

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

    def getIdBug(self):
        return self.bug_id

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
        bug.Comments = self.comments

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
        



    def analyzeBug(self, bug_id, url):

        #Retrieving main bug information
        bug_url = url + "show_bug.cgi?id=" + bug_id + "&ctype=xml"

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
    
        #Retrieving changes
        bug_activity_url = url + "show_activity.cgi?id=" + bug_id
        
        print bug_activity_url

        parser = ParserBGChanges(bug_activity_url, bug_id)
        data_activity = urllib.urlopen(bug_activity_url).read()
        parser.feed(data_activity)
        parser.close()
        print "Getting changes"
        dataBug.Changes = parser.getDataChanges()

        return dataBug

    def insert_general_info(self, url):

                            
        db = getDatabase()
        #By default, using bugzilla, field tracker=Bugs
        dbGeneralInfo = DBGeneralInfo("", url, "Bugs", datetime.date.today())
        db.insert_general_info(dbGeneralInfo)



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

        self.insert_general_info(url)

        url = self.getDomain(url)

        

        for bug in bugs:
            #The URL from bugzilla (so far KDE and GNOME) are like:
            #http://<domain>/show_bug.cgi?id=<bugid>&ctype=xml 
            
            try:
                dataBug = self.analyzeBug(bug, url)
            except:
                print "ERROR detected"
                continue
            
                        
            db = getDatabase()
            dbBug = DBBug(dataBug)
            db.insert_bug(dbBug)
          
            print ("Adding comments")
            for comment in dataBug.Comments:
                dbComment = DBComment(comment)
                db.insert_comment(dbComment)

            print "Adding changes"
            for change in dataBug.Changes:

                dbChange = DBChange(change)
                db.insert_change(dbChange)
        

            time.sleep(10)

register_backend ("bg", BGBackend)   
