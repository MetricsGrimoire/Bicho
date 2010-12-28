# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2011  GSyC/LibreSoft, Universidad Rey Juan Carlos
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# Authors: Daniel Izquierdo Cortazar <dizquierdo@libresoft.es>
#          Santiago Dueñas <sduenas@libresoft.es>
#

import urllib
from utils import *
import re
import time

from backends import create_backend

class Bicho:
    def __init__ (self):
        options = OptionsStore()


        self.backend = create_backend (options.type)
        debug ("Bicho object created")
        
   
    def run(self):
        self.backend.run()
                
            
        
        
        
        
