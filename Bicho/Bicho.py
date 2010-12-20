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
#      Daniel Izquierdo Cortazar <dizquierdo@gsyc.escet.urjc.es>
#      Luis Cañas Díaz <lcanas@libresoft.es>
#

import urllib
import re
import time
import Bug
from SqlBug import DBBug
from backends import create_backend
from Config import Config
from utils import printdbg


class Bicho:
    def __init__ (self):
        options = Config()
        self.backend = create_backend (options.type)
        printdbg ("Bicho object created, options and backend initialized")

    def run(self):
        self.backend.run()
