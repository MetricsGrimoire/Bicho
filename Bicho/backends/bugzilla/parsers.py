# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2013 GSyC/LibreSoft, Universidad Rey Juan Carlos
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
# Authors:
#         Santiago Dueñas <sduenas@libresoft.es>
#         Daniel Izquierdo Cortázar <dizquierdo@bitergia.com>
#         Luis Cañas Díaz <lcanas@bitergia.com>
#

"""
Parsers for Bugzilla tracker.
"""

from Bicho.backends.parsers import XMLParser
from Bicho.backends.bugzilla.model import BugzillaMetadata


# Tokens
VERSION_TOKEN = 'version'
URLBASE_TOKEN = 'urlbase'
MAINTAINER_TOKEN = 'maintainer'
EXPORTER_TOKEN = 'exporter'


class BugzillaMetadataParser(XMLParser):
    """XML parser for parsing Bugzilla metadata."""

    def __init__(self, xml):
        XMLParser.__init__(self, xml)

    @property
    def metadata(self):
        return self._marshal()

    def _marshal(self):
        return BugzillaMetadata(self._data.get(VERSION_TOKEN),
                                self._data.get(URLBASE_TOKEN),
                                self._data.get(MAINTAINER_TOKEN),
                                self._data.get(EXPORTER_TOKEN))

