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
import xml.sax

if not '..' in sys.path:
    sys.path.insert(0, '..')

from Bicho.backends.bugzilla.model import BugzillaMetadata
from Bicho.backends.bugzilla.parsers import BugzillaMetadataHandler


# Name of directory where the test input files are stored
TEST_FILES_DIRNAME = 'bugzilla_data'

# Test files
METADATA_FILE = 'metadata.xml'
EMPTY_METADATA_FILE = 'empty_metadata.xml'


def read_file(filename):
    with open(filename, 'r') as f:
        content = f.read()
    return content


class TestBugzillaMetadataHandler(unittest.TestCase):

    def setUp(self):
        self.handler = BugzillaMetadataHandler()
        self.parser = xml.sax.make_parser()
        self.parser.setContentHandler(self.handler)

    def test_xml_valid_metadata(self):
        # Test whether the handler parses correctly
        # a Bugzilla metadata XML stream
        filepath = os.path.join(TEST_FILES_DIRNAME, METADATA_FILE)
        content = read_file(filepath)
        self.parser.feed(content)

        metadata = self.handler.metadata
        self.assertIsInstance(metadata, BugzillaMetadata)
        self.assertEqual(u'4.2.1', metadata.version)
        self.assertEqual(u'https://bugzilla.example.com/', metadata.urlbase)
        self.assertEqual(u'sysadmin@example.com', metadata.maintainer)
        self.assertEqual(None, metadata.exporter)

    def test_xml_empty_metadata(self):
        # Test whether the handler parses correctly
        # an empty Bugzilla metadata XML stream
        filepath = os.path.join(TEST_FILES_DIRNAME, EMPTY_METADATA_FILE)
        content = read_file(filepath)
        self.parser.feed(content)

        metadata = self.handler.metadata
        self.assertIsInstance(metadata, BugzillaMetadata)
        self.assertEqual(None, metadata.version)
        self.assertEqual(None, metadata.urlbase)
        self.assertEqual(None, metadata.maintainer)
        self.assertEqual(None, metadata.exporter)

    def tearDown(self):
        self.parser.close()


if __name__ == '__main__':
    unittest.main()
