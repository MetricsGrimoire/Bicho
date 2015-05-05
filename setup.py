#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 GSyC/LibreSoft, Universidad Rey Juan Carlos
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
# Authors: Daniel Izquierdo Cortazar <dizquierdo@gsyc.es>
#          Francisco Rivas <frivas@libresoft.es>
#          Luis Cañas Díaz <lcanas@libresoft.es>
#
from distutils.core import setup

setup(name="Bicho",
      version="0.9",
      author="GSyC/LibreSoft, Universidad Rey Juan Carlos",
      author_email="metrics-grimoire@lists.libresoft.es",
      description="Analysis tool for Issue/Bug Tracking Systems",
      url="http://metricsgrimoire.github.com/Bicho/",
      packages=['bicho', 'bicho.backends', 'bicho.db',
                  'bicho.post_processing'],
      data_files=[('share/man/man1', ['doc/bicho.1'])],
      scripts=["bin/bicho"])
