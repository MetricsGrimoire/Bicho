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
#         Santiago Dueñas <sduenas@bitergia.com>
#

import csv
import os.path
import sys
import unittest

import bs4
import lxml.objectify

if not '..' in sys.path:
    sys.path.insert(0, '..')

from bicho.backends.parsers import \
    ParserError, CSVParserError, HTMLParserError, XMLParserError, JSONParserError,\
    Parser, CSVParser, HTMLParser, XMLParser, JSONParser, JSONStruct
from utilities import read_file


# Name of directory where the test input files are stored
TEST_FILES_DIRNAME = 'parsers_data'

# Test files
CSV_VALID_FILE = 'csv_valid.csv'
CSV_DIALECT_FILE = 'csv_dialect.csv'
HTML_VALID_FILE = 'html_valid.html'
HTML_UTF8_FILE = 'html_utf8.html'
XML_VALID_FILE = 'xml_valid.xml'
XML_INVALID_FILE = 'xml_invalid.xml'
XML_UTF8_FILE = 'xml_utf8.xml'
JSON_VALID_FILE = 'json_valid.json'
JSON_INVALID_FILE = 'json_invalid.json'
JSON_UTF8_FILE = 'json_utf8.json'

# RegExps for testing exceptions
KEYERROR_ERROR_REGEXP = 'error'


class TestParserError(unittest.TestCase):

    def test_error_message(self):
        # Make sure it prints the right error
        e = ParserError()
        self.assertEqual('error parsing stream', str(e))
        self.assertEqual(u'error parsing stream', unicode(e))

        # Should ignore arguments
        e = ParserError(msg='invalid stream')
        self.assertEqual('error parsing stream', str(e))
        self.assertEqual(u'error parsing stream', unicode(e))


class TestCSVParserError(unittest.TestCase):

    def test_error_message(self):
        # Make sure that prints the correct error
        e = CSVParserError(error='Invalid CSV stream')
        self.assertEqual('error parsing CSV. Invalid CSV stream', str(e))
        self.assertEqual(u'error parsing CSV. Invalid CSV stream', unicode(e))

    def test_no_args(self):
        # Check whether raises a KeyError exception when
        # is not given a 'error' as parameter
        kwargs = {'msg' : 'error'}
        self.assertRaisesRegexp(KeyError, KEYERROR_ERROR_REGEXP,
                                CSVParserError, **kwargs)


class TestHTMLParserError(unittest.TestCase):

    def test_error_message(self):
        # Make sure that prints the correct error
        e = HTMLParserError(error='Invalid format')
        self.assertEqual('error parsing HTML. Invalid format', str(e))
        self.assertEqual(u'error parsing HTML. Invalid format', unicode(e))

    def test_no_args(self):
        # Check whether raises a KeyError exception when
        # is not given a 'error' as parameter
        kwargs = {'msg' : 'error'}
        self.assertRaisesRegexp(KeyError, KEYERROR_ERROR_REGEXP,
                                HTMLParserError, **kwargs)


class TestXMLParserError(unittest.TestCase):

    def test_error_message(self):
        # Make sure that prints the correct error
        e = XMLParserError(error='xml entity not found')
        self.assertEqual('error parsing XML. xml entity not found', str(e))
        self.assertEqual(u'error parsing XML. xml entity not found', unicode(e))

    def test_no_args(self):
        # Check whether raises a KeyError exception when
        # is not given a 'error' as parameter
        kwargs = {'msg' : 'error'}
        self.assertRaisesRegexp(KeyError, KEYERROR_ERROR_REGEXP,
                                XMLParserError, **kwargs)


class TestJSONParserError(unittest.TestCase):

    def test_error_message(self):
        # Make sure that prints the correct error
        e = JSONParserError(error='Invalid stream')
        self.assertEqual('error parsing JSON. Invalid stream', str(e))
        self.assertEqual(u'error parsing JSON. Invalid stream', unicode(e))

    def test_no_args(self):
        # Check whether raises a KeyError exception when
        # is not given a 'error' as parameter
        kwargs = {'msg' : 'error'}
        self.assertRaisesRegexp(KeyError, KEYERROR_ERROR_REGEXP,
                                JSONParserError, **kwargs)


class TestAbstractParser(unittest.TestCase):

    def test_readonly_properties(self):
        parser = Parser('stream to parse')
        self.assertRaises(AttributeError, setattr, parser, 'data', '')
        self.assertEqual(None, parser.data)

    def test_stream_property(self):
        parser = Parser('text to parse')
        self.assertEqual('text to parse', parser.stream)

    def test_parse(self):
        parser = Parser('stream to parse')
        self.assertRaises(NotImplementedError, parser.parse)


class TestCSVParser(unittest.TestCase):

    def test_readonly_properties(self):
        parser = CSVParser('')
        self.assertRaises(AttributeError, setattr, parser, 'data', '')
        self.assertEqual(None, parser.data)

    def test_parse_invalid_type_stream(self):
        parser = CSVParser(None)
        self.assertRaises(TypeError, parser.parse)

    def test_parse_valid_csv(self):
        # Check whether it parses a valid CSV stream
        filepath = os.path.join(TEST_FILES_DIRNAME, CSV_VALID_FILE)
        content = read_file(filepath)

        parser = CSVParser(content)
        parser.parse()
        self.assertIsInstance(parser.data, csv.DictReader)

        rows = [d for d in parser.data]
        self.assertEqual(5, len(rows))

        row = rows[0]
        self.assertEqual('15', row['bug_id'])
        self.assertEqual('LibreGeoSocial (Android)', row['product'])
        self.assertEqual('general', row['component'])
        self.assertEqual('rocapal', row['assigned_to'])
        self.assertEqual('RESOLVED', row['bug_status'])
        self.assertEqual('FIXED', row['resolution'])
        # Really useful assertion, a comma is included in description
        self.assertEqual('The location service runs in GPS mode, always', row['short_desc'])
        self.assertEqual('2009-07-22 15:27:25', row['changeddate'])

        row = rows[3]
        self.assertEqual('20', row['bug_id'])
        self.assertEqual('jcaden', row['assigned_to'])
        self.assertEqual('ASSIGNED', row['bug_status'])
        self.assertEqual('---', row['resolution'])

        row = rows[4]
        self.assertEqual('carlosgc', row['assigned_to'])
        self.assertEqual('---', row['resolution'])

    def test_parse_valid_cvs_using_defined_dialect(self):
        # Check whether it parses a valid CSV stream
        # using user defined parameters
        filepath = os.path.join(TEST_FILES_DIRNAME, CSV_DIALECT_FILE)
        content = read_file(filepath)

        parser = CSVParser(content, fieldnames=['id', 'country', 'city'],
                           delimiter=';', quotechar='\'')
        self.assertEqual(['id', 'country', 'city'], parser.fieldnames)
        self.assertEqual(';', parser.delimiter)
        self.assertEqual('\'', parser.quotechar)

        parser.parse()
        rows = [d for d in parser.data]
        self.assertEqual(8, len(rows))

        row = rows[0]
        self.assertEqual('1', row['id'])
        self.assertEqual('Spain', row['country'])
        self.assertEqual('Madrid', row['city'])

        row = rows[1]
        self.assertEqual('2', row['id'])
        self.assertEqual('France', row['country'])
        self.assertEqual('Paris', row['city'])

        row = rows[2]
        self.assertEqual('10', row['id'])
        self.assertEqual('England', row['country'])
        self.assertEqual('London', row['city'])

        row = rows[5]
        self.assertEqual('201', row['id'])
        self.assertEqual('Norway', row['country'])
        self.assertEqual('Oslo', row['city'])

        row = rows[7]
        self.assertEqual('500', row['id'])
        self.assertEqual('Iceland', row['country'])
        self.assertEqual('Reykjavik', row['city'])


class TestHTMLParser(unittest.TestCase):

    def test_readonly_properties(self):
        parser = HTMLParser('<html><h1>Test</h1></html>')
        self.assertRaises(AttributeError, setattr, parser, 'data', '')
        self.assertEqual(None, parser.data)

    def test_parse_invalid_type_stream(self):
        parser = HTMLParser(None)
        self.assertRaises(TypeError, parser.parse)

    def test_parse_valid_html(self):
        # Check whether it parses a valid HTML stream
        filepath = os.path.join(TEST_FILES_DIRNAME, HTML_VALID_FILE)
        html = read_file(filepath)

        parser = HTMLParser(html)
        parser.parse()

        bug = parser.data
        self.assertIsInstance(bug, bs4.BeautifulSoup)

        self.assertEqual(u'Bug 348 \u2013 Testing KESI component', bug.title.string)
        self.assertEqual(u'Last modified: 2013-07-03 11:28:03 CEST',
                         bug.find(id='information').p.string)
        self.assertEqual(10, len(bug.find_all('table')))

    def test_parse_uf8_characters_html(self):
        # Check whether it parses a valid HTML stream that
        # contains UFT-8 characters
        filepath = os.path.join(TEST_FILES_DIRNAME, HTML_UTF8_FILE)
        html = read_file(filepath)

        parser = HTMLParser(html)
        parser.parse()
        root = parser.data

        self.assertEqual(u'sdueñas', root.h1.string)
        self.assertEqual(u'\nEn el Este, éste está,está éste en el Este, pero el Este, ¿dónde está?\n',
                         root.p.string)


class TestXMLParser(unittest.TestCase):

    def test_readonly_properties(self):
        parser = XMLParser('<node id="1"/>')
        self.assertRaises(AttributeError, setattr, parser, 'data', '')
        self.assertEqual(None, parser.data)

    def test_parse_invalid_type_stream(self):
        parser = XMLParser(None)
        self.assertRaises(TypeError, parser.parse)

    def test_parse_valid_xml(self):
        # Check whether it parses a valid XML stream
        filepath = os.path.join(TEST_FILES_DIRNAME, XML_VALID_FILE)
        xml = read_file(filepath)

        parser = XMLParser(xml)
        parser.parse()

        bugs = parser.data
        self.assertIsInstance(bugs, lxml.objectify.ObjectifiedElement)

        self.assertEqual(2, len(bugs.bug))

        bug = bugs.bug[0]
        self.assertEqual('8', bug.get('id'))
        self.assertEqual('Mock bug', bug.description)
        self.assertEqual('closed', bug.status)
        self.assertEqual(2, len(bug.comment))
        self.assertEqual('1', bug.comment[0].get('id'))
        self.assertEqual('johnsmith', bug.comment[0].get('submitted_by'))
        self.assertEqual('2007-01-01', bug.comment[0].get('submitted_on'))
        self.assertEqual('A comment', bug.comment[0])
        self.assertEqual('2', bug.comment[1].get('id'))
        self.assertEqual('sduenas', bug.comment[1].get('submitted_by'))
        self.assertEqual('2013-01-01', bug.comment[1].get('submitted_on'))
        self.assertEqual('Closed', bug.comment[1])

        bug = bugs.bug[1]
        self.assertEqual("Another test bug", bug.description)
        self.assertEqual("open", bug.status)

    def test_parse_invalid_xml(self):
        # Check whether it parses an invalid XML stream
        filepath = os.path.join(TEST_FILES_DIRNAME, XML_INVALID_FILE)
        xml = read_file(filepath)

        parser = XMLParser(xml)
        self.assertRaisesRegexp(XMLParserError,
                                'error parsing XML\. XMLSyntaxError',
                                parser.parse)

    def test_parse_uf8_characters_xml(self):
        # Check whether it parses a valid XML stream that
        # contains UFT-8 characters
        filepath = os.path.join(TEST_FILES_DIRNAME, XML_UTF8_FILE)
        xml = read_file(filepath)

        parser = XMLParser(xml)
        parser.parse()
        root = parser.data

        self.assertEqual(u'sdueñas', root.comment.get('editor'))
        self.assertEqual(u'\nEn el Este, éste está,está éste en el Este, pero el Este, ¿dónde está?\n',
                         root.comment)


class TestJSONParser(unittest.TestCase):

    def test_readonly_properties(self):
        parser = JSONParser('{"user":{"id":1}}')
        self.assertRaises(AttributeError, setattr, parser, 'data', '')
        self.assertEqual(None, parser.data)

    def test_parse_invalid_type_stream(self):
        parser = JSONParser(None)
        self.assertRaises(TypeError, parser.parse)

    def test_key_error(self):
        filepath = os.path.join(TEST_FILES_DIRNAME, JSON_VALID_FILE)
        json = read_file(filepath)

        parser = JSONParser(json)
        obj = parser.data
        self.assertRaises(AttributeError, getattr, obj, 'X')

    def test_parse_valid_json(self):
        # Check whether it parses a valid JSON stream
        filepath = os.path.join(TEST_FILES_DIRNAME, JSON_VALID_FILE)
        json = read_file(filepath)

        parser = JSONParser(json)
        parser.parse()

        data = parser.data
        self.assertIsInstance(data, JSONStruct)

        self.assertEqual(5, data.total_count)
        self.assertEqual(0, data.offset)
        self.assertEqual(3, data.limit)

        issues = data.issues
        self.assertIsInstance(issues, list)
        self.assertEqual(3, len(issues))

        issue = issues[0]
        self.assertEqual(2543, issue.id)

        issue = issues[1]
        self.assertEqual(2825, issue.id)
        self.assertEqual('Data not shown in chart', issue.subject)
        self.assertEqual('Error in charts.', issue.description)
        self.assertEqual('2014/01/10 12:37:10 +0100', issue.created_on)
        self.assertEqual('Santiago Duenas', issue.author.name)
        self.assertEqual(17, issue.author.id)

        issue = issues[2]
        self.assertEqual('Management', issue.subject)
        self.assertEqual('Daniel Izquierdo', issue.author.name)
        self.assertEqual(89, issue.author.id)

    def test_parse_invalid_json(self):
        # Check whether it parses an invalid JSON stream
        filepath = os.path.join(TEST_FILES_DIRNAME, JSON_INVALID_FILE)
        json = read_file(filepath)

        parser = JSONParser(json)
        self.assertRaisesRegexp(JSONParserError,
                                'error parsing JSON\. ValueError',
                                parser.parse)

    def test_parse_uf8_characters_json(self):
        # Check whether it parses a valid JSON stream that
        # contains UFT-8 characters
        filepath = os.path.join(TEST_FILES_DIRNAME, JSON_UTF8_FILE)
        json = read_file(filepath)

        parser = JSONParser(json)
        parser.parse()
        issues = parser.data

        issue = issues.issues[0]
        self.assertEqual(u'Santiago Dueñas', issue.author.name)

        issue = issues.issues[2]
        self.assertEqual(u'Luís Cañas', issue.assigned_to.name)


if __name__ == '__main__':
    unittest.main()
