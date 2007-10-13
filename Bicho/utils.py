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
#          Added class OptionsStore by: Daniel Izquierdo Cortazar <dizquierdo@gsyc.escet.urjc.es>
#

import sys
import config

class OptionsStore:
    #Pattern singleton applied

    __shared_state = {"type": None,
                      "url" : None,
                      "path" : None,

                      "db_driver_in": None,
                      "db_user_in": None,
                      "db_password_in": None,
                      "db_database_in": None,
                      "db_hostname_in": None,
                      "db_port_in": None,

                      "db_driver_out": None,
                      "db_user_out": None,
                      "db_password_out": None,
                      "db_database_out" : None,
                      "db_hostname_out": None, 
                      "db_port_out" : None}

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
    
