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

import getopt
import sys
from utils import *
import ConfigParser


def usage ():
    print "Usage: bicho [options] [URL]"
    print """
It extracts data from bug tracking systems from a project given

Options:

   -h, --help		Print this usage message.
   -t, --type           Type of bug tracking system (sf|bg) SourceForge or Bugzilla
   -p, --path		Path where downloaded URLs will be stored (/tmp/bicho/)

Database input specific options:
   --db-driver_in	Input database driver [sqlite|mysql|postgres] (None)
   --db-user_in		Database user name (None)
   --db-password_in	Database user password (None)
   --db-database_in	Database name (None)
   --db-hostname_in	Name of the host where database server is running (None)
   --db-port_in		Port where the database server is running (None)

Database output specific options:

  --db-driver_out	Output database driver [sqlite|mysql|postgres] (mysql)
  --db-user_out		Database user name (None)
  --db-password_out	Database user password (None)
  --db-database_out	Database name (None)
  --db-hostname_out	Name of the host where database server is running (localhost)
  --db-port_out		Port where the database is (3306)


Values found in config file 'bicho.conf' are used as default values
If config file is not found all parameters are required except:

    if url is given:
        Database input parameters are not required
    else:
        Database input parameteres are required.
"""
  


def getOptsFromFile ():
    import os.path

    #from utils.py
    options = OptionsStore()

    config = ConfigParser.ConfigParser()

    try:
        config.read([os.path.join('/etc', 'bicho'), 
                     os.path.expanduser('~/.bicho')])
    except:
        printerr("Config file not found")
        return options
    
    if config.has_section('General'):
        for opt,value in config.items('General'):
            if opt == "type":
                options.type = value
            if opt == "url":
                options.url = value
            if opt == "path":
                options.path = value

    if config.has_section('DatabaseIn'):
        for opt,value in config.items('DatabaseIn'):
            if opt == "db-driver_in":
                options.db_driver_in = value
            if opt == "db-user_in":
                options.db_user_in = value
            if opt == "db-password_in":
                options.db_password_in = value
            if opt == "db-database_in":
                options.db_database_in = value
            if opt == "db-hostname_in":
                options.db_hostname_in = value
            if opt == "db-port_in":
                options.db_port_in = value
    
    if config.has_section('DatabaseOut'): 
        for opt,value in config.items('DatabaseOut'):
            if opt == "db-driver_out":
                options.db_driver_out = value
            if opt == "db-user_out":
                options.db_user_out = value
            if opt == "db-password_out":
                options.db_password_out = value
            if opt == "db-database_out":
                options.db_database_out = value
            if opt == "db-hostname_out":
                options.db_hostname_out = value
            if opt == "db-port_out":
                options.db_port_out = value

    return options

def areDBOutCorrect(options):
    #Return True if parameters are not None    

    correct = True

    if options.db_driver_out is None:
        printerr ("Required parameter 'db-driver_out' is missing")
        correct = False
    elif options.db_user_out is None:
        printerr ("Required parameter 'db-user_out' is missing")
        correct = False
    elif options.db_password_out is None:
        printerr ("Required parameter 'db-password_out' is missing")
        correct = False
    elif options.db_database_out is None:
        printerr ("Required parameter 'db-database_out' is missing")
        correct = False
    elif options.db_hostname_out is None:
        printerr ("Required parameter 'db-hostname_out' is missing")
        correct = False
    elif options.db_port_out is None:
        printerr ("Required parameter 'db-port_out' is missing")
        correct = False

    return correct

def areDBInCorrect(options):

    #Return True if parameters are not None
    correct = True

    if options.db_driver_in is None:
        printerr ("Required parameter (if URL not given) 'db-driver_in' is missing")
        correct = False
    elif options.db_user_in is None:
        printerr ("Required parameter (if URL not given) 'db-user_in' is missing")
        correct = False
    elif options.db_password_in is None:
        printerr ("Required parameter (if URL not given) 'db-password_in' is missing")
        correct = False
    elif options.db_database_in is None:
        printerr ("Required parameter (if URL not given) 'db-database_in' is missing")
        correct = False
    elif options.db_hostname_in is None:
        printerr ("Required parameter (if URL not given) 'db-hostname_in' is missing")
        correct = False
    elif options.db_port_in is None:
        printerr ("Required parameter (if URL not given) 'db-port_in' is missing")
        correct = False

    return correct



def areOptionsCorrect(options):
    #return False if an error is encountered
    correct = True

    if options.type is None:
        printerr ("Required parameter 'type' is missing")
        correct = False
    elif options.url is None:
        if not areDBInCorrect(options):
            correct = False
        debug ("URL was not provided")
    elif not areDBOutCorrect(options):
        correct = False

    return correct

def areDBCorrect(options):
    #return False if some of the connections to DB fail.
    #FIXME: Not implemented 
    return True


def main (argv):
    import Bicho

    #Shared object
    options = getOptsFromFile()

    short_opts = "ht:p:"
    long_opts = ["help", "type=", "path=", "db-driver_in=", "db-user_in=", "db-password_in=",
                 "db-database_in=", "db-hostname_in=", "db-port_in=",
                 "db-driver_out=", "db-user_out=", "db-password_out=",
                 "db-database_out=", "db-hostname_out=", "db-port_out="]

    
    try:
        opts, args = getopt.getopt (argv, short_opts, long_opts)
    except getopt.GetoptError, e:
        print e
        return 1

    for opt, value in opts:
        if opt in ("-h", "--help"):
            usage ()
            return 0
        elif opt in ("-t", "--type"):
            options.type = value
        elif opt in ("-p", "--path"):
            options.path = value
        elif opt in ("--db-driver_in"):
            options.db_driver_in = value
        elif opt in ("--db-user_in"):
            options.db_user_in = value
        elif opt in ("--db-password_in"):
            options.db_password_in = value
        elif opt in ("--db-database_in"):
            options.db_database_in = value
        elif opt in ("--db-hostname_in"):
            options.db_hostname_in = value
        elif opt in ("--db-port_in"):
            options.db_port_in = value
        elif opt in ("--db-driver_out"):
            options.db_driver_out = value
        elif opt in ("--db-user_out"):
            options.db_user_out = value
        elif opt in ("--db-password_out"):
            options.db_password_out = value
        elif opt in ("--db-database_out"):
            options.db_database_out = value
        elif opt in ("--db-hostname_out"):
            options.db_hostname_out = value
        elif opt in ("--db-port_out"):
            options.db_port_out = value
        else:
            usage()

    if len(args) > 0:
        options.url = args[0]
        
    if not areOptionsCorrect(options):
        printerr ("Some options are not correct")
        return 1

    if not  areDBCorrect(options):
        printerr ("The connection to database (in/out) has failed")
        #FIXME: Not implemented
        return 1
 
    bich = Bicho.Bicho ()

    bich.run ()

    return 0

if __name__ == "__main__":
    main(sys.argv)
