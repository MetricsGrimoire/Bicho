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

import xml.sax.handler

from Bicho.backends.bugzilla.model import BugzillaMetadata


BUGZILLA_TOKEN = 'bugzilla'


class BugzillaMetadataHandler(xml.sax.handler.ContentHandler):
    """XML handler for parsing Bugzilla metadata."""

    def __init__ (self):
        self._init_metadata()

    @property
    def metadata(self):
        return BugzillaMetadata(self._metadata['version'],
                                self._metadata['urlbase'],
                                self._metadata['maintainer'],
                                self._metadata['exporter'])

    def startDocument(self):
        self._init_metadata()

    def startElement(self, name, attrs):
        if name != BUGZILLA_TOKEN:
            return

        for name, value in attrs.items():
            self._metadata[name] = unicode(value)

    def _init_metadata(self):
        self._metadata = {
                          'version' : None,
                          'urlbase' : None,
                          'maintainer' : None,
                          'exporter' : None
                         }
