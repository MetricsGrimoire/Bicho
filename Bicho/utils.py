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
# Authors: Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>
#

import sys
import config


def printout (str = '\n'):
    if str != '\n':
        str += '\n'
    sys.stdout.write (str)
    sys.stdout.flush ()

def printerr (str = '\n'):
    if str != '\n':
        str += '\n'
    sys.stderr.write (str)
    sys.stderr.flush ()

def printwrn (str = '\n'):
    if config.quiet:
        return

    printerr ("WRN: " + str)

def debug (str = '\n'):
    if not config.debug:
        return

    printout ("DBG: " + str)
    
