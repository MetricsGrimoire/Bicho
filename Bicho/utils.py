# -*- coding: utf-8 -*-
# Copyright (C) 2011 GSyC/LibreSoft, Universidad Rey Juan Carlos
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
#       Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>
#       Daniel Izquierdo Cortazar <dizquierdo@gsyc.escet.urjc.es>
#       Luis Cañas Díaz <lcanas@libresoft.es>
#

import cgi
import errno
import os
import random
import sys
import time
import urllib

from Config import Config

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
    if Config.quiet:
        return

    printerr ("WRN: " + str)

def printdbg (str = '\n'):
    if not Config.debug:
        return
    t = time.strftime("%d/%b/%Y-%X")
    printout ("DBG: [" + t +"] "+ str)

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

def rdelay():
    # it adds a random delay
    random.seed()
    if Config.delay:
        printdbg("delay")
        time.sleep(random.randint(0,20))

_dirs = {}

def create_dir(dir):
    try:
        os.mkdir (dir, 0700)
    except OSError, e:
        if e.errno == errno.EEXIST:
            if not os.path.isdir (dir):
                raise
        else:
            raise


def bicho_dot_dir ():
    try:
        return _dirs['dot']
    except KeyError:
        pass

    dot_dir = os.path.join (os.environ.get ('HOME'), '.bicho')
    create_dir (dot_dir)
    create_dir (os.path.join(dot_dir, "cache"))
        
    _dirs['dot'] = dot_dir

    return dot_dir

# http://stackoverflow.com/questions/8733233/filtering-out-certain-bytes-in-python
def valid_XML_char_ordinal(i):
    return (
            # Conditions ordered by presumed frequency
            0x20 <= i <= 0xD7FF
            or i in (0x9, 0xA, 0xD)
            or 0xE000 <= i <= 0xFFFD
            or 0x10000 <= i <= 0x10FFFF
    )
