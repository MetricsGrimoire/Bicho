# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Bitergia
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
# Authors:  Alvaro del Castillo <acs@bitergia.com>
#


from Bicho.Config import Config

from Bicho.backends import Backend
from Bicho.utils import printdbg, printout, printerr


class Allura():
    
    def __init__(self):
        self.delay = Config.delay
        self.url = Config.url

    def run(self):
        """
        """
        printout("Running Bicho with delay of %s seconds" % (str(self.delay)))

Backend.register_backend('allura', Allura)