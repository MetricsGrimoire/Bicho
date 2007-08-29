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

import urllib
from utils import *
#from HTMLUtils import *
#from HTMLParser import HTMLParser
#from ParserSFBugs import *
import re
import time
#import SqlBug
import Bug

from backends import create_backend

class Bicho:
    def __init__ (self, type, url_base):
        self.backend = create_backend (type)
        self.url = url_base
        debug ("Bicho object created")
        
   
    def run(self, url):
        self.backend.run(self.url)
                
            
        
        
        
        
