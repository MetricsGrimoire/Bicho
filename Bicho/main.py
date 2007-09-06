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

  -h, --help           Print this usage message.
  -t, --type           Type of bug tracking system (for the moment sf (SourceForge))

"""
  

def main (argv):
    import Bicho


    short_opts = "ht:"
    long_opts = ["help", "type="]

    
    try:
        opts, args = getopt.getopt (argv, short_opts, long_opts)
    except getopt.GetoptError, e:
        print e
        return 1


    typ = None
    url = None
    
    for opt, value in opts:
        if opt in ("-h", "--help"):
            usage ()
            return 0
        elif opt in ("-t", "--type"):
            typ = value
        else:
            usage()

    if len(args) > 0:
        url = args[0]
        

    if typ is None:
        printerr ("Required parameter --type is missing")
        return 1
    elif url is None:
        printerr ("URL was not provided")
        return 1

    
            
  
    bich = Bicho.Bicho (typ, url)

    bich.run (url)

    return 0

if __name__ == "__main__":
    main(sys.argv)
        
