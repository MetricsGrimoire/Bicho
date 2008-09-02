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

class Attachment:
    def __init__(self):
        self.__dict__={"IdBug" : None,
                      "Name" : None,
                      "Description" : None,
                      "Url" : None}

    def __getattr__(self, attr):
        return self.__dict__[attr]


    def __setattr__(self, attr, value):
        self.__dict__[attr] = value



class Comment:
    
    def __init__(self):

        self.__dict__ = {"IdBug" : None,
                        "DateSubmitted" : None,
                        "SubmittedBy" : None,
                        "Comment" : None}

    def __getattr__(self, attr):
        return self.__dict__[attr]
    
    
    def __setattr__(self, attr, value):
        self.__dict__[attr] = value
        

    def __str__ (self):
        
        return "\n\nId: " + self.Id + "\n" + \
               "IdBug: " + self.IdBug  + "\n" + \
               "DateSubmitted: " + self.DateSubmitted  + "\n" + \
               "Comment: " + self.Comment  + "\n"

class Change:

    def __init__(self):
        self.__dict__= {"IdBug" : None,
                       "Field" : None,
                       "OldValue" : None,
                       "Date" : None,
                       "SubmittedBy" : None}

    def __getattr__(self, attr):
        return self.__dict__[attr]

    def __setattr__(self, attr, value):
        self.__dict__[attr] = value

    def __str__ (self):

        return "\n\nId: " + self.Id + "\n" + \
               "IdBug: " + self.IdBug  + "\n" + \
               "Field: " + self.Field  + "\n" + \
               "OldValue: " + self.OldValue  + "\n" + \
               "Date: " + self.Date  + "\n" + \
               "SubmittedBy: " + self.SubmittedBy  + "\n"





class Bug:

    def __init__(self):
        
 
        
        self.__dict__ = {"Id" : None,
                                "Summary" : None,
                                "Description" : None,
                                "DateSubmitted" : None,
                                "Status" : None,
                                "Priority" : None,
                                "Category" : None,
                                "Group" : None,
                                "AssignedTo" : None,
                                "SubmittedBy" : None,
                                "Comments" : [],
                                "Attachments" : [],
                                "Changes" : []}
        
    def __getattr__(self, attr):
        return self.__dict__[attr]
    
    
    def __setattr__(self, attr, value):
        self.__dict__[attr] = value

    def __str__(self):

        return "\n\n\nId: " + self.Id + "\n" + \
                    "Summary: " + self.Summary + "\n" + \
                    "Description: " + self.Description + "\n" + \
                    "DateSubmitted: " + self.DateSubmitted + "\n" + \
                    "Status: " + self.Status + "\n" + \
                    "Priority: " + self.Priority + "\n" + \
                    "Category: " + self.Category + "\n" + \
                    "Group: " + self.Group + "\n" + \
                    "AssignedTo: "+ self.AssignedTo + "\n" + \
                    "SubmittedBy: " + self.SubmittedBy + "\n\n\n" 
        
        

