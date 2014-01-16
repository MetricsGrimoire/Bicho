# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Bitergia
# Copyright (C) 2011-2013 GSyC/LibreSoft, Universidad Rey Juan Carlos
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

import sys
import unittest

if not '..' in sys.path:
    sys.path.insert(0, '..')

from bicho.exceptions import InvalidBaseURLError
from bicho.backends.bugzilla.urls import BugzillaURLGenerator


# Test case URLs
BUGZILLA_URL = 'http://bugzilla.example.com/issues/'
BUGZILLA_URL_WITHOUT_SLASH = 'http://bugzilla.example.com/issues'
ISSUE_TRACKER_URL = 'http://bugs.example.org/'
QUERY_URL = 'http://bugzilla.example.com/issues/show_bug.cgi?id=555&ctype=xml'
CGI_URL = 'http://bugzilla.example.com/issues/show_bug.cgi?'
CGI_SUBSTRING_URL = 'http://bugzilla.example.cgi/.cgis/'

# Test case dates
ISSUE_DATE = '2001-01-01'
ISSUE_TIMESTAMP = '2003-06-27 22:10:08'


class TestBugzillaURLGenerator(unittest.TestCase):

    def test_login_url(self):
        generator = BugzillaURLGenerator(BUGZILLA_URL)
        self.assertEqual('http://bugzilla.example.com/issues/index.cgi',
                         generator.get_login_url())

    def test_metadata_url(self):
        generator = BugzillaURLGenerator(BUGZILLA_URL)
        self.assertEqual('http://bugzilla.example.com/issues/show_bug.cgi?ctype=xml',
                         generator.get_metadata_url())

    def test_issues_summary_url(self):
        generator = BugzillaURLGenerator(BUGZILLA_URL)
        self.assertEqual('http://bugzilla.example.com/issues/buglist.cgi?columnlist=bug_id%2Cchangeddate&order=changeddate&ctype=csv',
                         generator.get_issues_summary_url())

    def test_issues_summary_url_with_params(self):
        generator = BugzillaURLGenerator(BUGZILLA_URL)
        self.assertEqual('http://bugzilla.example.com/issues/buglist.cgi?columnlist=bug_id%2Cchangeddate&chfieldfrom=2001-01-01&order=changeddate&ctype=csv',
                         generator.get_issues_summary_url(from_date=ISSUE_DATE))
        self.assertEqual('http://bugzilla.example.com/issues/buglist.cgi?columnlist=bug_id%2Cchangeddate&chfieldfrom=2003-06-27+22%3A10%3A08&order=changeddate&ctype=csv',
                         generator.get_issues_summary_url(from_date=ISSUE_TIMESTAMP))
        self.assertEqual('http://bugzilla.example.com/issues/buglist.cgi?columnlist=bug_id%2Cchangeddate&product=fake-product&order=changeddate&ctype=csv',
                         generator.get_issues_summary_url(product='fake-product'))
        self.assertEqual('http://bugzilla.example.com/issues/buglist.cgi?columnlist=bug_id%2Cchangeddate&product=fake-product&chfieldfrom=2003-06-27+22%3A10%3A08&order=changeddate&ctype=csv',
                         generator.get_issues_summary_url(product='fake-product', from_date=ISSUE_TIMESTAMP))

    def test_old_style_issues_summary_url(self):
        generator = BugzillaURLGenerator(BUGZILLA_URL, version='3.2.3')
        self.assertEqual('http://bugzilla.example.com/issues/buglist.cgi?columnlist=bug_id%2CLast%2BChanged&chfieldfrom=2001-01-01&order=Last%2BChanged&ctype=csv',
                         generator.get_issues_summary_url(from_date=ISSUE_DATE))
        self.assertEqual('http://bugzilla.example.com/issues/buglist.cgi?columnlist=bug_id%2CLast%2BChanged&chfieldfrom=2003-06-27+22%3A10%3A08&order=Last%2BChanged&ctype=csv',
                         generator.get_issues_summary_url(from_date=ISSUE_TIMESTAMP))
        self.assertEqual('http://bugzilla.example.com/issues/buglist.cgi?columnlist=bug_id%2CLast%2BChanged&product=fake-product&order=Last%2BChanged&ctype=csv',
                         generator.get_issues_summary_url(product='fake-product'))
        self.assertEqual('http://bugzilla.example.com/issues/buglist.cgi?columnlist=bug_id%2CLast%2BChanged&product=fake-product&chfieldfrom=2003-06-27+22%3A10%3A08&order=Last%2BChanged&ctype=csv',
                         generator.get_issues_summary_url(product='fake-product', from_date=ISSUE_TIMESTAMP))

    def test_issues_description_url(self):
        generator = BugzillaURLGenerator(BUGZILLA_URL)
        self.assertEqual('http://bugzilla.example.com/issues/show_bug.cgi?excludefield=attachmentdata&ctype=xml&id=33&id=47&id=78',
                         generator.get_issues_description_url(['33', '47', '78']))
        self.assertEqual('http://bugzilla.example.com/issues/show_bug.cgi?excludefield=attachmentdata&ctype=xml&id=1',
                         generator.get_issues_description_url('1'))

    def test_issues_description_url_invalid_list(self):
        generator = BugzillaURLGenerator(BUGZILLA_URL)
        self.assertRaisesRegexp(ValueError, 'issues cannot be None or empty',
                                generator.get_issues_description_url, issues=None)
        self.assertRaisesRegexp(ValueError, 'issues cannot be None or empty',
                                generator.get_issues_description_url, issues=[])
        self.assertRaisesRegexp(ValueError, 'issues cannot be None or empty',
                                generator.get_issues_description_url, issues='')

    def test_activity_url(self):
        generator = BugzillaURLGenerator(BUGZILLA_URL)
        self.assertEqual('http://bugzilla.example.com/issues/show_activity.cgi?id=88',
                         generator.get_activity_url('88'))

    def test_activity_url_invalid_id(self):
        generator = BugzillaURLGenerator(BUGZILLA_URL)
        self.assertRaisesRegexp(ValueError, 'issue_id cannot be None or empty',
                                generator.get_activity_url, issue_id=None)
        self.assertRaisesRegexp(ValueError, 'issue_id cannot be None or empty',
                                generator.get_activity_url, issue_id='')

    def test_invalid_urls(self):
        # Test if the generator fails when a new instance is created
        # passing invalid URLs
        self.assertRaisesRegexp(InvalidBaseURLError, 'Empty URL',
                                BugzillaURLGenerator, base_url=None)
        self.assertRaisesRegexp(InvalidBaseURLError, 'Empty URL',
                                BugzillaURLGenerator, base_url='')
        self.assertRaisesRegexp(InvalidBaseURLError, 'Query parameters found',
                                BugzillaURLGenerator, base_url=QUERY_URL)
        self.assertRaisesRegexp(InvalidBaseURLError, 'URL related to a CGI',
                                BugzillaURLGenerator, base_url=CGI_URL)

        # Do not raise any error because it's a valid URL
        generator = BugzillaURLGenerator(CGI_SUBSTRING_URL)
        self.assertEqual(CGI_SUBSTRING_URL, generator.base_url)

    def test_trailing_slash(self):
        # Test if a trailing slash is added to base URL
        generator = BugzillaURLGenerator(BUGZILLA_URL_WITHOUT_SLASH)
        self.assertEqual(BUGZILLA_URL, generator.base_url)

    def test_assign_base_url(self):
        # Test whether fails or not assigning invalid URLs
        generator = BugzillaURLGenerator(BUGZILLA_URL)

        self.assertRaisesRegexp(InvalidBaseURLError, 'Empty URL',
                                setattr, generator, 'base_url', None)
        self.assertEqual(BUGZILLA_URL, generator.base_url)

        self.assertRaisesRegexp(InvalidBaseURLError, 'Empty URL',
                                setattr, generator, 'base_url', '')
        self.assertEqual(BUGZILLA_URL, generator.base_url)

        self.assertRaisesRegexp(InvalidBaseURLError, 'Query parameters found',
                                setattr, generator, 'base_url', QUERY_URL)
        self.assertEqual(BUGZILLA_URL, generator.base_url)

        self.assertRaisesRegexp(InvalidBaseURLError, 'URL related to a CGI',
                                setattr, generator, 'base_url', CGI_URL)
        self.assertEqual(BUGZILLA_URL, generator.base_url)

        generator.base_url = ISSUE_TRACKER_URL
        self.assertEqual(ISSUE_TRACKER_URL, generator.base_url)


if __name__ == "__main__":
    unittest.main()
