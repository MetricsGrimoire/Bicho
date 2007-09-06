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



def usage ():
    print "Usage: bicho [options] [URL]"
    print """
It extracts data from bug tracking systems from a project given

Options:

  -h, --help		Print this usage message.
  -t, --type            Type of bug tracking system (for the moment sf (SourceForge))


Database output specific options:

      --db-driver	Output database driver [sqlite|mysql|postgres] (sqlite)
  -u, --db-user		Database user name (operator)
  -p, --db-password	Database user password (operator)
  -d, --db-database	Database name (bicho)
  -H, --db-hostname	Name of the host where database server is running (localhost)
  -o, --db-port		Port where the database is (3306-mysql)

"""
  

def main (argv):
    import Bicho


    short_opts = "ht:u:p:d:H:o:"
    long_opts = ["help", "type=", "db-driver=", "db-user=", "db-password=",
                 "db-database=", "db-hostname=", "db-port="]

    
    try:
        opts, args = getopt.getopt (argv, short_opts, long_opts)
    except getopt.GetoptError, e:
        print e
        return 1

    #from utils.py
    options = Opt_CommandLine()

    for opt, value in opts:
        if opt in ("-h", "--help"):
            usage ()
            return 0
        elif opt in ("-t", "--type"):
            options.type = value
        elif opt in ("--db-driver"):
            options.db_driver = value
        elif opt in ("-u", "--db-user"):
            options.db_user = value
        elif opt in ("-p", "--db-password"):
            options.db_password = value
        elif opt in ("-d", "--db-database"):
            options.db_database = value
        elif opt in ("-H", "--db-hostname"):
            options.db_hostname = value
        elif opt in ("-o","--db-port"):
            options.db_port = value
        else:
            usage()

    if len(args) > 0:
        options.url = args[0]
        

    if options.type is None:
        printerr ("Required parameter --type is missing")
        return 1
    elif options.url is None:
        printerr ("URL was not provided")
        return 1

    
            
  
    bich = Bicho.Bicho ()

    bich.run ()

    return 0

if __name__ == "__main__":
    main(sys.argv)
        
