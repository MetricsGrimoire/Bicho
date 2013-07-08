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

import os.path
import sys
import unittest
import lxml.objectify

if not '..' in sys.path:
    sys.path.insert(0, '..')

from Bicho.backends.parsers import UnmarshallingError, XMLParserError, XMLParser


# Name of directory where the test input files are stored
TEST_FILES_DIRNAME = 'parsers_data'

# Test files
XML_VALID_FILE = 'valid_xml.xml'
XML_INVALID_FILE = 'invalid_xml.xml'
XML_UTF8_FILE = 'utf8_xml.xml'


def read_file(filename):
    with open(filename, 'r') as f:
        content = f.read()
    return content


class TestUnmarshallingError(unittest.TestCase):

    def test_type(self):
        # Check whether raises a TypeError exception when
        # is not given an Exception class as third parameter
        self.assertRaises(TypeError, UnmarshallingError,
                          'Identity', True, 'invalid name',)

    def test_error_message(self):
        # Make sure that prints the correct error
        e = UnmarshallingError('Attachment')
        self.assertEqual('error unmarshalling object to Attachment.', str(e))

        e = UnmarshallingError('Identity', AttributeError())
        self.assertEqual('error unmarshalling object to Identity. AttributeError()',
                         str(e))

        e = UnmarshallingError('Identity', AttributeError(), 'Invalid email address')
        self.assertEqual('error unmarshalling object to Identity. Invalid email address. AttributeError()',
                         str(e))

        e = UnmarshallingError('Comment', cause='Invalid date')
        self.assertEqual('error unmarshalling object to Comment. Invalid date.',
                         str(e))


class TestXMLParserError(unittest.TestCase):

    def test_type(self):
        # Check whether raises a TypeError exception when
        # is not given an Exception class as first parameter
        self.assertRaises(TypeError, XMLParserError, 'error')

    def test_error_message(self):
        # Make sure that prints the correct error
        e = XMLParserError()
        self.assertEqual('error parsing XML.', str(e))

        e = XMLParserError(Exception())
        self.assertEqual('error parsing XML. Exception()', str(e))


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


if __name__ == '__main__':
    unittest.main()
