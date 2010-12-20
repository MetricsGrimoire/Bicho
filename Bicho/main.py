# -*- coding: utf-8 -*-
# Copyright (C) 2010 GSyC/LibreSoft, Universidad Rey Juan Carlos
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
# Authors:
#       Daniel Izquierdo Cortazar <dizquierdo@gsyc.escet.urjc.es>
#       Luis Cañas Díaz <lcanas@libresoft.es>



import getopt
import sys
import ConfigParser

from Config import Config, ErrorLoadingConfig
from utils import *
from info import *

def usage ():
    print "%s %s - %s" % (PACKAGE, VERSION, DESCRIPTION)
    print COPYRIGHT
    print
    print "Usage: bicho [options] [URL]"
    print """
Analyze the given URI or database to extract information about the bugs in the 
output database

Options:

  -h, --help		Print this usage message.
  -V, --version         Show version
  -g, --debug           Enable debug mode
  -t, --type            Type of bug tracking system (sf|bg) SourceForge or \
Bugzilla
  -p, --path		Path where downloaded URLs will be stored (/tmp/bicho/)
  -d, --delay           Random delay between 0 and 20 seconds to avoid been \
banned
  -f, --config-file     Use a custom configuration file

Database output specific options:

  --db-driver_out	Output database driver [sqlite|mysql|postgres] (mysql)
  --db-user_out		Database user name (operator)
  --db-password_out	Database user password
  --db-database_out	Database name (bicho)
  --db-hostname_out	Name of the host where database server is running \
(localhost)
  --db-port_out		Port where the database is (3306)

Database input specific options:
  --db-driver_in	Input database driver [sqlite|mysql|postgres]
  --db-user_in		Database user name
  --db-password_in	Database user password
  --db-database_in	Database name
  --db-hostname_in	Name of the host where database server is running
  --db-port_in		Port where the database server is running
"""

def are_dbout_correct(options):
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

def are_dbin_correct(options):

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

def are_options_correct(options):
    #return False if an error is encountered
    correct = True

    if options.type is None:
        printerr ("Required parameter 'type' is missing")
        correct = False
    elif options.url is None:
        if not are_dbin_correct(options):
            correct = False
        printdbg ("URL was not provided")
    elif not are_dbout_correct(options):
        correct = False

    return correct

def are_db_correct(options):
    #return False if some of the connections to DB fail.
    #FIXME: Not implemented 
    return True


def main (argv):
    import Bicho

    #Shared object
    options = Config()

    # Short (one letter) options. Those requiring argument followed by :
    short_opts = "hVgdt:f:p:"
    # Long options (all started by --). Those requiring argument followed by =
    long_opts = ["help", "version", "debug", "delay", "type=",
                 "config-file=", "path=", "db-driver_in=", "db-user_in=",
                 "db-password_in=", "db-database_in=", "db-hostname_in=",
                 "db-port_in=", "db-driver_out=", "db-user_out=",
                 "db-password_out=", "db-database_out=", "db-hostname_out=",
                 "db-port_out="]

    try:
        opts, args = getopt.getopt (argv, short_opts, long_opts)
    except getopt.GetoptError, e:
        print e
        return 1

    options = Config()

    for opt, value in opts:
        if opt in ("-h", "--help", "-help"):
            usage ()
            return 0
        elif opt in ("-V", "--version"):
            print VERSION
            return 0
        elif opt in ("-g", "--debug"):
            options.debug = True
        elif opt in ("-t", "--type"):
            options.type = value
        elif opt in ("-p", "--path"):
            options.path = value
        elif opt in ("-d", "--delay"):
            options.delay = True
        elif opt in ("-f", "--config-file"):
            options.config_file = value
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

    try:
        if options.config_file is not None:
            config.load_from_file (options.config_file)
        else:
            config.load ()
    except ErrorLoadingConfig, e:
        printerr (e.message)
        return 1

    if len(args) > 0:
        options.url = args[0]

    if not are_options_correct(options):
        printerr ("Some options are not correct")
        return 1

    if not are_db_correct(options):
        printerr ("The connection to database (in/out) has failed")
        #FIXME: Not implemented
        return 1

    bich = Bicho.Bicho ()

    bich.run ()

    return 0

if __name__ == "__main__":
    main(sys.argv)
