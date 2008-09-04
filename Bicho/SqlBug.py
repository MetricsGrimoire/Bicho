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

from utils import *
from storm.locals import *
#from storm import database
#database.DEBUG = True
from storm.exceptions import *





#Pattern simple factory.
#This factory will create the concrete object depending on the
#type of database used

def getDatabase ():
    options = OptionsStore()

    if options.db_driver_out == "mysql":
        return DBMySQL()
    elif options.db_driver_out == "postgres":
        return DBPostGreSQL()
    elif options.db_driver_out == "sqlite":
        return SQLite()


class DBDatabaseException (Exception):
    '''Generic DBDatabase Exception'''
    
    def __init__ (self, message = None):
        Exception.__init__ (self)

        self.message = message

class DBDatabaseDriverNotAvailable (DBDatabaseException):
    '''Database driver is not available'''
class DBDatabaseDriverNotSupported (DBDatabaseException):
    '''Database driver is not supported'''
class DBDatabaseNotFound (DBDatabaseException):
    '''Selected database doesn't exist'''
class DBAccessDenied (DBDatabaseException):
    '''Access denied to databse''' 
class DBTableAlreadyExists (DBDatabaseException):
    '''Table alredy exists in database'''



class DBDatabase:

    def __init__(self):
        self.database = ""
        self.store = ""

    def insert_general_info(self, dbGeneralInfo):
        self.store.add(dbGeneralInfo)
        self.store.flush()

    def insert_bug(self, dbBug):
        self.store.add(dbBug)
        self.store.flush()

    def insert_comment(self, dbComment):
        self.store.add(dbComment)
        self.store.flush()

    def insert_attachment(self, dbAttach):
        self.store.add(dbAttach)
        self.store.flush()

    def insert_change(self, dbChange):
        self.store.add(dbChange)
        self.store.flush()

class DBMySQL(DBDatabase):

    def __init__ (self):
        options = OptionsStore()
         
        try:
            print options.db_driver_out
            self.database = create_database(options.db_driver_out +"://"+ 
            options.db_user_out +":"+ options.db_password_out  +"@"+ 
            options.db_hostname_out+":"+ options.db_port_out+"/"+ options.db_database_out)
        except DatabaseModuleError, e:
            raise DBDatabaseDriverNotAvailable (str (e))
        except ImportError:
            raise DBDatabaseDriverNotSupported
        except:
            raise


        self.store = Store(self.database)

        self.store.execute("CREATE TABLE IF NOT EXISTS GeneralInfo(" +
                           "id int auto_increment primary key," +
                           "Project varchar(256), " +
                           "Url varchar(256), " +
                           "Tracker varchar(256), " +
                           "Date varchar(128))")

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

        self.store.execute("CREATE TABLE IF NOT EXISTS Comments (" + 
                           "id int auto_increment primary key," +  
                           "idBug varchar(128)," +
                           "DateSubmitted varchar(128),"+
                           "SubmittedBy varchar(128), " + 
                           "Comment text)")

        self.store.execute("CREATE TABLE IF NOT EXISTS Attachments (" +
                           "id int auto_increment primary key," +
                           "idBug varchar(128)," +
                           "Name varchar(256), " +
                           "Description text, " + 
                           "Url varchar(256))")

        self.store.execute("CREATE TABLE IF NOT EXISTS Changes (" +
                           "id int auto_increment primary key," +
                           "idBug varchar(128)," +
                           "Field varchar(256), " +
                           "OldValue varchar(256), " +
                           "Date varchar(256), " +
                           "SubmittedBy varchar(256))")


class DBPostGreSQL(DBDatabase):
    def __init__ (self):
        options = OptionsStore()

        self.database = create_database(options.db_driver_out +"://"+
        options.db_user_out +":"+ options.db_password_out  +"@"+
        options.db_hostname_out+":"+ options.db_port_out+"/"+ options.db_database_out)

        self.store = Store(self.database)

        self.store.execute("CREATE TABLE IF NOT EXISTS GeneralInfo(" +
                           "id serial primary key," +
                           "Project varchar(256), " +
                           "Url varchar(256), " +
                           "Tracker varchar(256), " +
                           "Date varchar(128))")


        self.store.execute("CREATE TABLE Bugs (" + 
                           "id serial primary key," + 
                           "idBug varchar(128)," + 
                           "Summary text, " + 
                           "Description text," + 
                           "Datesubmitted varchar(128),"+
                           "Status varchar(64),"+
                           "Priority varchar(64),"+
                           "Category varchar(128),"+
                           "Igroup varchar(128),"+
                           "Assignedto varchar(128),"+
                           "Submittedby varchar(128))")

        self.store.execute("CREATE TABLE Comments (" + 
                           "id serial primary key," + 
                           "idBug varchar(128)," + 
                           "DateSubmitted varchar(128),"+
                           "SubmittedBy varchar(128), " +
                           "Comment text)")

        self.store.execute("CREATE TABLE Attachments (" +
                           "id serial primary key," +
                           "idBug varchar(128)," +
                           "Name varchar(256), " +
                           "Description text, " +
                           "Url varchar(256))")

        self.store.execute("CREATE TABLE IF NOT EXISTS Changes (" +
                           "id serial primary key," +
                           "idBug varchar(128)," +
                           "Field varchar(256), " +
                           "OldValue varchar(256), " +
                           "Date varchar(256), " +
                           "SubmittedBy varchar(256))")



class SQLite(DBDatabase):
    def __init__ (self):
        
        options = OptionsStore()

        self.database = create_database(options.db_driver_out + ':' + options.db_database_out + '.db')

        self.store = Store(self.database)

        self.store.execute("CREATE TABLE IF NOT EXISTS GeneralInfo(" +
                           "id integer primary key," +
                           "Project varchar(256), " +
                           "Url varchar(256), " +
                           "Tracker varchar(256), " +
                           "Date varchar(128))")

        self.store.execute("CREATE TABLE Bugs (" +
                           "id integer primary key," +
                           "idBug varchar," +
                           "summary varchar, " +
                           "description text," +
                           "datesubmitted varchar,"+
                           "status varchar,"+
                           "priority varchar,"+
                           "category varchar,"+
                           "igroup varchar,"+
                           "assignedto varchar,"+
                           "submittedby varchar)")

        self.store.execute("CREATE TABLE Comments (" +
                           "id integer primary key," +
                           "idBug varchar(128)," +
                           "DateSubmitted varchar(128),"+
                           "SubmittedBy varchar(128), " +
                           "Comment text)")

        self.store.execute("CREATE TABLE Attachments (" +
                           "id integer primary key," +
                           "idBug varchar(128)," +
                           "Name varchar(256), " +
                           "Description text, " +
                           "Url varchar(256))")

        self.store.execute("CREATE TABLE IF NOT EXISTS Changes (" +
                           "id integer primary key," +
                           "idBug varchar(128)," +
                           "Field varchar(256), " +
                           "OldValue varchar(256), " +
                           "Date varchar(256), " +
                           "SubmittedBy varchar(256))")


class DBGeneralInfo(object):
    __storm_table__ = "GeneralInfo"

    id = Int (primary = True)
    Project = Unicode()
    Url = Unicode()
    Tracker = Unicode()
    Date = Unicode()

    def __init__ (self, project, url, tracker, date):

        try:
            self.Project = unicode(project)
        except:
            pass

        try:
            self.Url = unicode(url)
        except:
            pass

        try:
            self.Tracker = unicode(tracker)
        except:
            pass

        try:
            self.Date = unicode(date)
        except:
            pass



class DBAttachment(object):
    __storm_table__ = "Attachments"

    id = Int (primary = True)
    IdBug = Unicode()
    Name = Unicode()
    Description = Unicode()
    Url = Unicode()

    def __init__ (self, attachment):

        try: 
            self.IdBug = unicode(attachment.IdBug)
        except:
            pass

        try: 
            self.IdBug = unicode(attachment.IdBug)
        except:
            pass

        try:
            self.Name = unicode(attachment.Name)
        except:
            pass

        try:
            self.Description = unicode(attachment.Description)
        except:
            pass

        try:
            self.Url = unicode(attachment.Url)
        except:
            pass


class DBComment (object):
    __storm_table__ = "Comments"

    id = Int (primary = True)
    IdBug = Unicode()
    DateSubmitted = Unicode()
    SubmittedBy = Unicode()
    Comment = Unicode()

    def __init__ (self, comment):

        try:
            self.IdBug = unicode(comment.IdBug)
        except:
            pass

        try:
            self.DateSubmitted = unicode(comment.DateSubmitted)
        except:
            pass
 
        try:
            self.SubmittedBy = unicode(comment.SubmittedBy)
        except:
            pass

        try:
            self.Comment = unicode(comment.Comment)
        except:
            pass
    

class DBChange (object):
    __storm_table__ = "Changes"

    id = Int (primary = True)
    IdBug = Unicode()
    Field = Unicode()
    OldValue = Unicode()
    Date = Unicode()
    SubmittedBy = Unicode()

    def __init__ (self, change):

        try:
            self.IdBug = unicode(change.IdBug)
        except:
            pass

        try:
            self.Field = unicode(change.Field)
        except:
            pass

        try:
            self.OldValue = unicode(change.OldValue)
        except:
            pass
    
        try:
            self.Date = unicode(change.Date)
        except:
            pass

        try:
            self.SubmittedBy = unicode(change.SubmittedBy)
        except:
            pass





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


