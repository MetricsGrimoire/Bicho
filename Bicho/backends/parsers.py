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
#

"""
Generic parsers for backends.
"""

from bs4 import BeautifulSoup, Comment
from lxml import objectify


class UnmarshallingError(Exception):
    """Exception raised when an error is found unmarshalling parsed XML objects"""

    def __init__(self, instance, error=None, cause=None):
        if error is not None and not isinstance(error, Exception):
            raise TypeError('expected type Exception in error parameter.')
        self.instance = instance
        self.error = error
        self.cause = cause

    def __str__(self):
        msg = 'error unmarshalling object to %s.' % self.instance
        if self.cause is not None:
            msg += ' %s.' % self.cause
        if self.error is not None:
            msg += ' %s' % repr(self.error)
        return msg


class HTMLParserError(Exception):
    """Exception raised when an error occurs parsing a HTML stream."""

    def __init__(self, error=None):
        if error is not None and not isinstance(error, Exception):
            raise TypeError('expected type Exception in error parameter.')
        self.error = error

    def __str__(self):
        msg = 'error parsing HTML.'
        if self.error is not None:
            msg += ' %s' % repr(self.error)
        return msg


class XMLParserError(Exception):
    """Exception raised when an error occurs parsing a XML stream."""

    def __init__(self, error=None):
        if error is not None and not isinstance(error, Exception):
            raise TypeError('expected type Exception in error parameter.')
        self.error = error

    def __str__(self):
        msg = 'error parsing XML.'
        if self.error is not None:
            msg += ' %s' % repr(self.error)
        return msg


class HTMLParser(object):
    """Generic HTML parser

    :param html: stream to parse
    :type html: str
    """
    def __init__(self, html):
        self.html = html
        self._data = None

    def parse(self):
        """Parse the HTML stream

        :raises: TypeError: when the html to parse is not a instance of str.
        :raises: HTMLParserError: when an error occurs parsing the stream.
        """
        if not isinstance(self.html, str):
            raise TypeError('expected type str in html parameter.')

        try:
            self._data = BeautifulSoup(self.html)
            self._remove_comments()
        except Exception, e:
            raise HTMLParserError(e)

    @property
    def data(self):
        """Returns the parsed data.

        :rtype: bs4.BeautifulSoup
        """
        return self._data

    def _remove_comments(self):
        comments = self._data.findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]


class XMLParser(object):
    """Generic XML parser

    :param xml: stream to parse
    :type xml: str
    """
    def __init__(self, xml):
        self.xml = xml
        self._data = None

    def parse(self):
        """Parse the XML stream

        :raises: TypeError: when the xml to parse is not a instance of str.
        :raises: XMLParserError: when an error occurs parsing the stream.
        """
        if not isinstance(self.xml, str):
            raise TypeError('expected type str in xml parameter.')

        try:
            self._data = objectify.fromstring(self.xml)
        except Exception, e:
            raise XMLParserError(e)

    @property
    def data(self):
        """Returns the parsed data.

        :rtype: lxml.objectify.ObjectifiedElement
        """
        return self._data
