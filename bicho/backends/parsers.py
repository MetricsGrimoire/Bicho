# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Bitergia
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

import json
from csv import DictReader

from bs4 import BeautifulSoup, Comment
from lxml import objectify

from bicho.exceptions import BichoException


class ParserError(BichoException):
    """Base exception class for parser errors.

    Parser exceptions should derive from this class.
    """
    message = 'error parsing stream'


class CSVParserError(ParserError):
    """Exception raised when an error occurs parsing a CSV stream.

    :param error: explanation of the error
    :type error: str
    """
    message = 'error parsing CSV. %(error)s'


class HTMLParserError(ParserError):
    """Exception raised when an error occurs parsing a HTML stream.

    :param error: explanation of the error
    :type error: str
    """
    message = 'error parsing HTML. %(error)s'


class XMLParserError(ParserError):
    """Exception raised when an error occurs parsing a XML stream.

    :param error: explanation of the error
    :type error: str
    """
    message = 'error parsing XML. %(error)s'


class JSONParserError(ParserError):
    """Exception raised when an error occurs parsing a JSON stream.

    :param error: explanation of the error
    :type error: str
    """
    message = 'error parsing JSON. %(error)s'


class CSVParser(object):
    """"Generic CSV parser

    :param csv: stream to parse
    :type html: str
    :param fieldnames: name of each column
    :type list of str
    :param delimiter: delimiter of fields, by default it is set to comma
    :type delimiter: str
    :param quotechar: delimiter of string fields, by default it is set to
      doble quote
    :type quotechar: str
    """
    def __init__(self, csv, fieldnames=None, delimiter=',', quotechar='"'):
        self.csv = csv
        self.fieldnames = fieldnames
        self.delimiter = delimiter
        self.quotechar = quotechar
        self._data = None

    def parse(self):
        """Parse the CSV stream

        :raises: TypeError: when the cvs to parse is not a instance of str.
        :raises: CSVParserError: when an error occurs parsing the stream.
        """
        if not isinstance(self.csv, str):
            raise TypeError('expected type str in csv parameter.')

        try:
            rows = self.csv.split('\n')
            self._data = DictReader(rows, fieldnames=self.fieldnames,
                                    delimiter=self.delimiter,
                                    quotechar=self.quotechar)
        except Exception, e:
            raise CSVParserError(error=repr(e))

    @property
    def data(self):
        """Returns the parsed data.

        :rtype: csv.DictReader
        """
        return self._data


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
            raise HTMLParserError(error=repr(e))

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
            raise XMLParserError(error=repr(e))

    @property
    def data(self):
        """Returns the parsed data.

        :rtype: lxml.objectify.ObjectifiedElement
        """
        return self._data


class JSONParser(object):
    """Generic JSON parser

    :param stream: stream to parse
    :type stream: str
    """
    def __init__(self, stream):
        self.stream = stream
        self._data = None

    def parse(self):
        """Parse the JSON stream

        :raises: TypeError: when the json to parse is not a instance of str.
        :raises: JSONParserError: when an error occurs parsing the stream.
        """
        if not isinstance(self.stream, str):
            raise TypeError('expected type str in stream parameter.')

        try:
            self._data = json.loads(self.stream)
        except Exception, e:
            raise JSONParserError(error=repr(e))

    @property
    def data(self):
        """Returns the parsed data.

        :rtype: object
        """
        return self._data
