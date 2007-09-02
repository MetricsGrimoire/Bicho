# Copyright (C) 2007  GSyC/LibreSoft
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
# Authors: Daniel Izquierdo Cortazar <dizquierdo@gsyc.escet.urjc.es>
#


from HTMLParser import HTMLParser
from storm.locals import *
from Bicho.utils import *
import Bicho.Bug as Bug
import urllib
import re

class ParserSFBugs(HTMLParser):
    #FIXME: The description contains the sentence "Add a comment:". It must be deleted from the
    #whole string

    (INIT_ST, ST_2, ST_3, ST_4, ST_5, ST_6, ST_7, ST_8) = range (8)

    def __init__(self, bugURL):
        HTMLParser.__init__ (self)
        self.data = ""
        self.attrs = {}
        self.tag = ""
        
        self.state = ParserSFBugs.INIT_ST
        
        self.currentKey = ""
        #dictionary key(initial td in table)-value (next td value in table)
        self.dataBugs = {"Submitted By:" : "",
                        "Date Submitted:" : "",
                        "Last Updated By:" : "",
                        "Date Last Updated:" : "",
                        "Number of Comments:" : "",
                        "Number of Attachments:" : "",
                        "Category: " : "",
                        "Group: " : "",
                        "Assigned To: " : "",
                        "Priority: " : "",
                        "Status: " : "",
                        "Resolution: " : "",
                        "Summary: " : "",
                        "Private: " : "",
                        "Description:" : "",
                        "URL:" : bugURL,
                        "IdBug:" : self.getIdBug(bugURL)}
        
    

    def getIdBug(self, bugURL):
        #FIXME: no errors control
        
        query = urllib.splitquery (bugURL)
        attrs = query[1].split('&')
        for attr in attrs:
            if re.search("aid=", attr):
                key, value = attr.split('=')
                return value
    
    def normalizeData(self, data):
        value = ""
        
        #Parsering the data (Deleting tabs and others ...)
        data = data.replace("\t", "")
        strings = data.splitlines()
        for string in strings:
            if string <>"":
                value = value.join(string)
                
        return (value)
        
        
    def statesMachine(self, data, tag):
    
        if self.state == ParserSFBugs.INIT_ST:
            #print "Step 1"
            if tag == "<td>":
                self.state = ParserSFBugs.ST_2
            
        elif self.state == ParserSFBugs.ST_2:
        
            value = self.normalizeData(data)
            #print "Step 2"
            
            
            if self.dataBugs.has_key(value):
                self.currentKey= value
            if self.dataBugs.has_key(value) and value == "Private: ":
               self.state = ParserSFBugs.ST_5
               self.data = ""
            if self.dataBugs.has_key(value) and value <> "Private: ":
               self.state = ParserSFBugs.ST_3
               self.data = ""
            
        elif self.state == ParserSFBugs.ST_3:
            #print "Step 3"
            value = self.normalizeData(data)
            if tag == "</td>":
                self.dataBugs[self.currentKey] = self.data
                self.state = ParserSFBugs.ST_4
            else:
               if value <> "(?)":
                    self.data = self.data + value
                
        elif self.state == ParserSFBugs.ST_4:
            #print "Step 4"
            if tag == "<td>":
                self.state = ParserSFBugs.ST_2

        elif self.state == ParserSFBugs.ST_5:
            #print "Step 5"
            value = self.normalizeData(data)
            if tag == "</td>":
                self.dataBugs[self.currentKey] = self.data
                self.state = ParserSFBugs.ST_6
            else:
                if value <> "(?)":
                    self.data = self.data + value
          
        elif self.state == ParserSFBugs.ST_6:
            #print "Step 6"
            if tag == "<td>":
                self.state = ParserSFBugs.ST_7
         
        elif self.state == ParserSFBugs.ST_7:
            #print "Step 7"
            value = self.normalizeData(data)
            if tag == "</td>":
                self.dataBugs["Description:"] = self.data
                self.state = ParserSFBugs.ST_8
            else:
                if value <> "(?)":
                    self.data = self.data + value
            
        elif self.state == ParserSFBugs.ST_8:
            #print "Step 8"
            return
            
 
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
        
    def getDataBug(self):
    
        bug = Bug.Bug()
        bug.Id = self.dataBugs["IdBug:"]
        bug.Summary = self.dataBugs["Summary: "]
        bug.Description = self.dataBugs["Description:"]
        bug.DateSubmitted = self.dataBugs["Date Submitted:"]
        bug.Status = self.dataBugs["Status: "]
        bug.Priority = self.dataBugs["Priority: "]
        bug.Category = self.dataBugs["Category: "]
        bug.Group = self.dataBugs["Group: "]
        bug.AssignedTo = self.dataBugs["Assigned To: "]
        bug.SubmittedBy = self.dataBugs["Submitted By:"]
    
        return bug
        
        

