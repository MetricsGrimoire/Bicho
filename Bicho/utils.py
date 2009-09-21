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
import urllib
import cgi

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

                      "db_driver_out": 'mysql',
                      "db_user_out": None,
                      "db_password_out": None,
                      "db_database_out" : None,
                      "db_hostname_out": 'localhost', 
                      "db_port_out" : '3306'}

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

def get_domain(url):
    strings = url.split('/')
    return strings[0] + "//" + strings[2] + "/"

def url_join(base, *kwargs):
    retval = [base.strip('/')]

    for comp in kwargs:
        retval.append(comp.strip('/'))

    return "/".join(retval)

def url_strip_protocol(url):
    p = url.find("://")
    if p == -1:
        return url

    p += 3
    return url[p:]

def url_get_attr(url, attr=None):
    query = urllib.splitquery(url)
    try:
        if query[1] is None:
            return None;
    except IndexError:
        return None

    attrs = cgi.parse_qsl(query[1])
    if attr is None:
        return attrs

    for a in attrs:
        if attr in a:
            return a[1]

    return None   
