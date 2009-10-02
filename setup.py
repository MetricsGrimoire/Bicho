#!/usr/bin/python
# Copyright (C) 2006 Alvaro Navarro Clemente
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#

import commands
import os
import sys
from distutils.core import setup

try:
  import BeautifulSoup
except:
  print "BeautifulSoup is not installed please install it..."
  sys.exit(-1)

try:
  import storm
except:
  print "Storm is not installed please install it..."
  sys.exit(-1) 

setup(name = "Bicho",
      version = "0.3-1",
      author =  "LibreSoft",
      author_email = "libresoft-tools-devel@lists.morfeo-project.org",
      description = "An analysis tool for you Bug Tracker System",
      url = "https://forge.morfeo-project.org/projects/libresoft-tools/",      
      packages = ['Bicho', 'Bicho.backends','Bicho.bicho-web'],
      scripts = ["bin/bicho"])
