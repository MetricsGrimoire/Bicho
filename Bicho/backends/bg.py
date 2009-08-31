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
import random


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

    (INIT_ST, ST_2, ST_3, ST_4, ST_5, ST_6, ST_7, ST_8, ST_9, ST_10) = range(10)

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
        #self.change = Change()
        self.cont = 0
        self.rowspan = 0

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
            if tag == "</table>":
                self.state = ParserBGChanges.ST_10

        elif self.state == ParserBGChanges.ST_4:
            #Field Who
            if tag == "<td>":
                self.change = Change(self.IdBug)
                self.data = ""
                self.cont = 1

            if len(attrs)>0:
                self.rowspan = int(attrs[0][1])
                self.cont = 0

            if data <> "":
                self.data = self.data + data
                
            if tag == "</td>":
                self.change.setSubmittedBy(self.data.strip())
                self.data = ""
                self.state = ParserBGChanges.ST_5

        elif self.state == ParserBGChanges.ST_5:
            #Field When
            if tag == "<td>":
                pass

            if data <> "":
                self.data = self.data + data
                
            if tag == "</td>":
                self.change.setDate(self.data.strip())
                self.data = ""
                self.state = ParserBGChanges.ST_6

        
        elif self.state == ParserBGChanges.ST_6:
            #Field What
            if tag == "<td>":
                who = self.change.getSubmittedBy()
                when = self.change.getDate()
                self.data = ""
                
                self.change = Change(self.IdBug)
                
                self.change.setSubmittedBy(who)
                self.change.setDate(when)


            if data <> "":
                self.data = self.data + data
                
            if tag == "</td>":
                self.change.setField(self.data.strip())
                self.data = ""
                self.cont = self.cont + 1
                self.state = ParserBGChanges.ST_7


        elif self.state == ParserBGChanges.ST_7:
            #Field Removed
            if tag == "<td>":
                pass

            if data <> "":
                self.data = self.data + data
                
            if tag == "</td>":
                self.change.setOldValue(self.data.strip())
                self.data = ""
                self.state = ParserBGChanges.ST_8


        elif self.state == ParserBGChanges.ST_8:
            #Field Added - so far, ignored
            if tag == "<td>":
                pass
                
            if tag == "</td>":
                self.state = ParserBGChanges.ST_9

        elif self.state == ParserBGChanges.ST_9:
            if tag =="</tr>" and not (self.cont==self.rowspan):
                #Starting another set of values because of rowspan > 1
                #Going to what field
                self.state = ParserBGChanges.ST_6
                self.changes.append(self.change)

            if tag == "</tr>" and self.cont==self.rowspan:
                self.state = ParserBGChanges.ST_4
                self.changes.append(self.change)
             

        elif self.state == ParserBGChanges.ST_10:

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
        self.bug_id = None
        self.creation_ts = None
        self.short_desc = None
        self.delta_ts = None
        self.reporter_accessible = None
        self.cclist_accessible = None
        self.classification_id = None
        self.classification = None
        self.product = None
        self.component = None
        self.version = None
        self.rep_platform = None
        self.op_sys = None
        self.bug_status = None
        self.resolution = None
        self.priority = None
        self.bug_severity = None
        self.target_milestone = None
        self.reporter = None
        self.assigned_to = None
        self.cc = []
        self.long_desc = []

        self.is_bug_id = False
        self.is_creation_ts = False
        self.is_short_desc = False
        self.is_bug_status = False
        self.is_resolution = False
        self.is_priority = False
        self.is_reporter = False
        self.is_assigned_to = False
        self.is_description = False

        self.is_delta_ts = False
        self.is_reporter_accessible = False
        self.is_cclist_accessible = False
        self.is_classification_id = False
        self.is_classification = False
        self.is_product = False
        self.is_component = False
        self.is_version = False
        self.is_rep_platform = False
        self.is_op_sys = False
        self.is_bug_severity = False
        self.is_target_milestone = False
        self.is_cc = False

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
        #Generic information found in other BTSs
        if name == 'bug_id':
            self.is_bug_id = True
        elif name == 'creation_ts':
            self.is_creation_ts = True
        elif name == 'short_desc':
            self.is_short_desc = True
        elif name == 'bug_status':
            self.is_bug_status = True
        elif name == 'resolution':
            self.is_resolution = True
        elif name == 'priority':
            self.is_priority = True
        elif name == 'reporter':
            self.is_reporter = True
        elif name == 'assigned_to':
            self.is_assigned_to = True
        
        #Specific information just found in Bugzillas
        elif name == 'delta_ts':
            self.is_delta_ts = True
        elif name == 'reporter_accessible':
            self.is_reporter_accessible = True
        elif name == 'cclist_accessible':
            self.is_cclist_accessible = True
        elif name == 'classification_id':
            self.is_classification_id = True
        elif name == 'classification':
            self.is_classification = True
        elif name == 'product':
            self.is_product = True
        elif name == 'component':
            self.is_component = True
        elif name == 'version':
            self.is_version = True
        elif name == 'rep_platform':
            self.is_rep_platform = True
        elif name == 'op_sys':
            self.is_op_sys = True
        elif name == 'bug_severity':
            self.is_bug_severity = True
        elif name == 'target_milestone':
            self.is_target_milestone = True
        elif name == 'cc':
            self.is_cc = True


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
        #Generic Information
        if self.is_bug_id:
            self.bug_id =  str(ch)
        elif self.is_creation_ts:
            self.creation_ts = str(ch)
        elif self.is_short_desc:
            self.short_desc = str(ch)
        elif self.is_bug_status:
            self.bug_status = str(ch)
        elif self.is_resolution  :
            self.resolution  = str(ch)
        elif self.is_priority:
            self.priority = str(ch)
        elif self.is_reporter:
            self.reporter = str(ch)
        elif self.is_assigned_to:
            self.assigned_to = str(ch)
        #Specific information just found in Bugzillas
        elif self.is_delta_ts  :
            self.delta_ts  = str(ch)
        elif self.is_reporter_accessible  :
            self.reporter_accessible  = str(ch)
        elif self.is_cclist_accessible  :
            self.cclist_accessible  = str(ch)
        elif self.is_classification_id  :
            self.classification_id  = str(ch)
        elif self.is_classification  :
            self.classification  = str(ch)
        elif self.is_product  :
            self.product  = str(ch)
        elif self.is_component  :
            self.component  = str(ch)
        elif self.is_version  :
            self.version  = str(ch)
        elif self.is_rep_platform  :
            self.rep_platform  = str(ch)
        elif self.is_op_sys  :
            self.op_sys  = str(ch)
        elif self.is_bug_severity  :
            self.bug_severity  = str(ch)
        elif self.is_target_milestone  :
            self.target_milestone  = str(ch)
        elif self.is_cc  :
            self.cc  = str(ch)



        #parsing comments
        elif self.is_who:
            self.who = str(ch)
        elif self.is_bug_when:
            self.bug_when = str(ch)
        elif self.is_the_text:
            self.the_text = self.the_text + str(ch.encode('utf-8'))
            
            

            
    def endElement(self, name):
        #Generic information found in all BTSs
        if name == 'bug_id':
            self.is_bug_id = False
        elif name == 'creation_ts':
            self.is_creation_ts = False
        elif name == 'short_desc':
            self.is_short_desc = False
        elif name == 'bug_status':
            self.is_bug_status = False
        elif name == 'resolution':
            self.is_resolution = False
        elif name == 'priority':
            self.is_priority = False
        elif name == 'reporter':
            self.is_reporter = False
        elif name == 'assigned_to':
            self.is_assigned_to = False

        #Specific information just found in Bugzillas
        elif name == 'delta_ts':
            self.is_delta_ts = False
        elif name == 'reporter_accessible':
            self.is_reporter_accessible = False
        elif name == 'cclist_accessible':
            self.is_cclist_accessible = False
        elif name == 'classification_id':
            self.is_classification_id = False
        elif name == 'classification':
            self.is_classification = False
        elif name == 'product':
            self.is_product = False
        elif name == 'component':
            self.is_component = False
        elif name == 'version':
            self.is_version = False
        elif name == 'rep_platform':
            self.is_rep_platform = False
        elif name == 'op_sys':
            self.is_op_sys = False
        elif name == 'bug_severity':
            self.is_bug_severity = False
        elif name == 'target_milestone':
            self.is_target_milestone = False
        elif name == 'cc':
            self.is_cc = False


        #parsing comments
        elif name == 'long_desc':
            self.is_long_desc = False
        elif name == 'who':
            self.is_who = False
        elif name == 'bug_when':
            self.is_bug_when = False
        elif name == 'thetext':
            self.comment = Comment(self.bug_id, self.who, self.bug_when, self.the_text)
            self.comments.append(self.comment)
            self.the_text = ""
            self.is_the_text = False

    def printDataBug(self):
        print ""
        print "ID: " +  self.bug_id
        print "Creation date: " + self.creation_ts
        print "Short description: " + self.short_desc
        print "Status: " + self.bug_status
        print "Priority: " + self.priority
        print "Resolution: " + self.resolution
        print "Reporter: " + self.reporter
        print "Assigned To: " + self.assigned_to
        
        print "Delta_ts: " + self.delta_ts
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
        bug.Resolution = self.resolution
        bug.Priority = self.priority
        bug.Category = ""
        bug.Group = ""
        bug.AssignedTo = self.assigned_to
        bug.SubmittedBy = self.reporter
        bug.Comments = self.comments


        bug.delta_ts = self.delta_ts
        bug.reporter_accessible  =  self.reporter_accessible
        bug.cclist_accessible  =  self.cclist_accessible
        bug.classification_id  =  self.classification_id
        bug.classification  =  self.classification
        bug.product  =  self.product
        bug.component  =  self.component
        bug.version  =  self.version
        bug.rep_platform  =  self.rep_platform
        bug.op_sys  =  self.op_sys
        bug.bug_severity  =  self.bug_severity
        bug.target_milestone  =  self.target_milestone
        bug.cc  =  self.cc

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
        #print "Getting changes"
        dataBug.Changes = parser.getDataChanges()

        return dataBug

    def insert_general_info(self, url):

                            
        db = getDatabase()
        #By default, using bugzilla, field tracker=Bugs
        dbGeneralInfo = DBGeneralInfo("", url, "Bugs", datetime.date.today())
        db.insert_general_info(dbGeneralInfo)



    def run (self):
        
        debug ("Running Bicho")
        print "Running Bicho"
        #retrieving data in csv format

        url = self.url + "&ctype=csv"

        print url

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


        if url.find("apache")>0:
            url =  url + "bugzilla/"


        random.seed()
        for bug in bugs:

            #The URL from bugzilla (so far KDE and GNOME) are like:
            #http://<domain>/show_bug.cgi?id=<bugid>&ctype=xml 
            
            try:
                dataBug = self.analyzeBug(bug, url)
            except Exception, e:
                print "ERROR detected"
                print e
                continue
            
            db = getDatabase()
            dbBug = DBBug(dataBug)
            db.insert_bug(dbBug)

            dbBugzilla_extra = DBBugzilla_extra(dataBug)
            db.insert_bugzilla_extra(dbBugzilla_extra)
          
            #print ("Adding comments")
            for comment in dataBug.Comments:
                dbComment = DBComment(comment)
                db.insert_comment(dbComment)

            #print "Adding changes"
            for change in dataBug.Changes:
                #print "Se inserta change:"
                #change.printChange()
                #print "******************"
                dbChange = DBChange(change)
                db.insert_change(dbChange)
        

            time.sleep(random.randint(0,20))

register_backend ("bg", BGBackend)   
