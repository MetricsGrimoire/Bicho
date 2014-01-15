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


class Parser(object):
    """Abstract parsing class.

    :param stream: stream to parse
    :type stream: str
    """

    def __init__(self, stream):
        self.stream = stream
        self._data = None

    def parse(self):
        """Parse the given stream

        Abstract method. Returns the parsed data.
        """
        raise NotImplementedError

    @property
    def data(self):
        """Returns the parsed data.

        :rtype: object
        """
        return self._data


class CSVParser(Parser):
    """"Generic CSV parser.

    :param stream: stream to parse
    :type stream: str
    :param fieldnames: name of each column
    :type list of str
    :param delimiter: delimiter of fields, by default it is set to comma
    :type delimiter: str
    :param quotechar: delimiter of string fields, by default it is set to
      doble quote
    :type quotechar: str
    """
    def __init__(self, stream, fieldnames=None, delimiter=',', quotechar='"'):
        super(CSVParser, self).__init__(stream)
        self.fieldnames = fieldnames
        self.delimiter = delimiter
        self.quotechar = quotechar

    def parse(self):
        """Parse the CSV stream.

        :returns: returns the parsed data
        :rtype: csv.DictReader
        :raises: TypeError: when the cvs to parse is not a instance of str
        :raises: CSVParserError: when an error occurs parsing the stream
        """
        if not isinstance(self.stream, str):
            raise TypeError('expected type str in csv parameter.')

        try:
            rows = self.stream.split('\n')
            self._data = DictReader(rows, fieldnames=self.fieldnames,
                                    delimiter=self.delimiter,
                                    quotechar=self.quotechar)
            return self._data
        except Exception, e:
            raise CSVParserError(error=repr(e))


class HTMLParser(Parser):
    """Generic HTML parser.

    :param stream: stream to parse
    :type stream: str
    """
    def __init__(self, stream):
        super(HTMLParser, self).__init__(stream)

    def parse(self):
        """Parse the HTML stream.

        :returns: returns the parsed data
        :rtype: bs4.BeautifulSoup
        :raises: TypeError: when the html to parse is not a instance of str.
        :raises: HTMLParserError: when an error occurs parsing the stream.
        """
        if not isinstance(self.stream, str):
            raise TypeError('expected type str in html parameter.')

        try:
            self._data = BeautifulSoup(self.stream)
            self._remove_comments()
            return self._data
        except Exception, e:
            raise HTMLParserError(error=repr(e))

    def _remove_comments(self):
        comments = self._data.findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]


class XMLParser(Parser):
    """Generic XML parser.

    :param stream: stream to parse
    :type stream: str
    """
    def __init__(self, stream):
        super(XMLParser, self).__init__(stream)

    def parse(self):
        """Parse the XML stream.

        :returns: returns the parsed data
        :rtype: lxml.objectify.ObjectifiedElement
        :raises: TypeError: when the xml to parse is not a instance of str.
        :raises: XMLParserError: when an error occurs parsing the stream.
        """
        if not isinstance(self.stream, str):
            raise TypeError('expected type str in xml parameter.')

        try:
            self._data = objectify.fromstring(self.stream)
        except Exception, e:
            raise XMLParserError(error=repr(e))


class JSONParser(Parser):
    """Generic JSON parser.

    :param stream: stream to parse
    :type stream: str
    """
    def __init__(self, stream):
        super(JSONParser, self).__init__(stream)

    def parse(self):
        """Parse the JSON stream.

        :returns: returns the parser data
        :rtype: object (dict or list)
        :raises: TypeError: when the json to parse is not a instance of str.
        :raises: JSONParserError: when an error occurs parsing the stream.
        """
        if not isinstance(self.stream, str):
            raise TypeError('expected type str in stream parameter.')

        try:
            self._data = json.loads(self.stream)
        except Exception, e:
            raise JSONParserError(error=repr(e))
