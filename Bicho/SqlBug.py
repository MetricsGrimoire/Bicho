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

from storm.locals import *
from storm import database
database.DEBUG = True






#Pattern simple factory.
#This factory will create the concrete object depending on the
#type of database used

def getDatabase (type):
    if type == "mysql":
        return DBMySQL()
    elif type == "postgresql":
        return DBPostGreSQL()
    elif type == "sqlite":
        return SQLite()



#Abstract class
class DBDatabase:

    def __init__(self):
        self.database = ""
        self.store = ""


    def insert(self, dbBug):
        self.store.add(dbBug)
        self.store.flush()



class DBMySQL(DBDatabase):

    def __init__ (self):
        self.database = create_database("mysql://root:root@localhost:3306/Prueba_Storm")
        self.store = Store(self.database)
        self.store.execute ("CREATE TABLE  IF NOT EXISTS Bugs (" +
                           "id int auto_increment primary key," +
                           "idBug varchar(128)," +
                           "Summary text," +
                           "Description text,"+
                           "DateSubmitted varchar(128),"+
                           "Status varchar(64),"+
                           "Priority varchar(64),"+
                           "Category varchar(128),"+
                           "IGroup varchar(128),"+
                           "AssignedTo varchar(128),"+
                           "SubmittedBy varchar(128)) DEFAULT CHARSET=utf8")


class DBPostGreSQL(DBDatabase):
    def __init__ (self):
        print "Access to PostGreSQL not implemented"



class SQLite(DBDatabase):
    def __init__ (self):
        print "Access to SQLite not implemented"




#Class necessary to talk to Storm
class DBBug (object):
    __storm_table__ = "Bugs"

    id = Int (primary = True)
    idBug = Unicode ()
    Summary = Unicode ()
    Description = Unicode()
    DateSubmitted = Unicode()
    Status = Unicode ()
    Priority = Unicode ()
    Category = Unicode ()
    IGroup = Unicode ()
    AssignedTo = Unicode ()
    SubmittedBy = Unicode ()

    def __init__ (self, bug):
        #TODO: If there is an error, that field is ignored. There must
        #be an encoding option to solve this problem
   
        #Each field could contain that error and we are interested in 
        #getting as much data as we can, thus it is necessary to have
        #a try-except statement for each field in order to obtain 
        #data from the others

        self.idBug = unicode(bug.Id)
        try:
            self.Summary = unicode(bug.Summary)
        except:
            pass

        try:
            self.Description = unicode(bug.Description)
        except:
            pass
        
        try:
            self.DateSubmitted = unicode(bug.DateSubmitted)
        except:
            pass

        try:
            self.Status = unicode(bug.Status)
        except:
            pass

        try:
            self.Priority = unicode(bug.Priority)
        except:
            pass

        try:
            self.Category = unicode(bug.Category)
        except:
            pass

        try:
            self.IGroup = unicode(bug.Group)
        except:
            pass

        try:
            self.AssignedTo = unicode(bug.AssignedTo)
        except:
            pass
        
        try:
            self.SubmittedBy = unicode(bug.SubmittedBy)
        except:
            pass



