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

class Opt_CommandLine:
    #Pattern singleton applied

    __shared_state = {"type": None,
                      "url" : None,
                      "db_driver": "sqlite",
                      "db_user": "operator",
                      "db_password": "operator",
                      "db_database" : "bicho",
                      "db_hostname": "localhost", 
                      "db_port" : "3306"}

    def __init__ (self):
        self.__dict__ = self.__shared_state


    def __getattr__(self, attr):
        return self.__dict__[attr]


    def __setattr__(self, attr, value):
        self.__dict__[attr] = value



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
    
