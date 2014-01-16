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
from bicho.backends.redmine.urls import RedmineURLGenerator


# Test case URLs
REDMINE_URL = 'http://example.org/redmine/'
REDMINE_URL_WITHOUT_SLASH = 'http://example.org/redmine'
ISSUE_TRACKER_URL = 'http://example.org/redmine/'
QUERY_URL = 'http://example.org/redmine/issues.json?status_id=*&page=77'
JSON_URL = 'http://example.org/redmine/issues.json?'
JSON_SUBSTRING_URL = 'http://example.json/.jsons/'

# Test case dates
ISSUE_DATE = '2001-01-01'
ISSUE_TIMESTAMP = '2003-06-27 22:10:08'


class TestRedmineURLGenerator(unittest.TestCase):

    def test_issues_summary_url(self):
        generator = RedmineURLGenerator(REDMINE_URL)
        self.assertEqual('http://example.org/redmine/issues.json?sort=updated_on&status_id=%2A',
                         generator.get_issues_summary_url())

    def test_issues_summary_url_with_params(self):
        generator = RedmineURLGenerator(REDMINE_URL)
        self.assertEqual('http://example.org/redmine/issues.json?sort=updated_on&updated_on=%3E%3D2001-01-01&status_id=%2A',
                         generator.get_issues_summary_url(from_date=ISSUE_DATE))
        self.assertEqual('http://example.org/redmine/projects/fake-product/issues.json?sort=updated_on&status_id=%2A',
                         generator.get_issues_summary_url(product='fake-product'))
        self.assertEqual('http://example.org/redmine/issues.json?sort=updated_on&page=3&status_id=%2A',
                         generator.get_issues_summary_url(page='3'))
        self.assertEqual('http://example.org/redmine/projects/fake-product/issues.json?sort=updated_on&updated_on=%3E%3D2001-01-01&page=3&status_id=%2A',
                         generator.get_issues_summary_url(product='fake-product', from_date=ISSUE_DATE, page='3'))

    def test_issue_url(self):
        generator = RedmineURLGenerator(REDMINE_URL)
        self.assertEqual('http://example.org/redmine/issues/88.json?include=journals',
                         generator.get_issue_url('88'))

    def test_issue_url_invalid_id(self):
        generator = RedmineURLGenerator(REDMINE_URL)
        self.assertRaisesRegexp(ValueError, 'issue_id cannot be None or empty',
                                generator.get_issue_url, issue_id=None)
        self.assertRaisesRegexp(ValueError, 'issue_id cannot be None or empty',
                                generator.get_issue_url, issue_id='')

    def test_issues_description_url_invalid_list(self):
        generator = RedmineURLGenerator(REDMINE_URL)
        self.assertRaisesRegexp(ValueError, 'issue_id cannot be None or empty',
                                generator.get_issue_url, issue_id=None)
        self.assertRaisesRegexp(ValueError, 'issue_id cannot be None or empty',
                                generator.get_issue_url, issue_id='')

    def test_statuses_url(self):
        generator = RedmineURLGenerator(REDMINE_URL)
        self.assertEqual('http://example.org/redmine/issue_statuses.json',
                         generator.get_statuses_url())

    def test_user_url(self):
        generator = RedmineURLGenerator(REDMINE_URL)
        self.assertEqual('http://example.org/redmine/users/12.json',
                         generator.get_user_url('12'))

    def test_user_url_invalid_id(self):
        generator = RedmineURLGenerator(REDMINE_URL)
        self.assertRaisesRegexp(ValueError, 'user_id cannot be None or empty',
                                generator.get_user_url, user_id=None)
        self.assertRaisesRegexp(ValueError, 'user_id cannot be None or empty',
                                generator.get_user_url, user_id='')

    def test_invalid_urls(self):
        # Test if the generator fails when a new instance is created
        # passing invalid URLs
        self.assertRaisesRegexp(InvalidBaseURLError, 'Empty URL',
                                RedmineURLGenerator, base_url=None)
        self.assertRaisesRegexp(InvalidBaseURLError, 'Empty URL',
                                RedmineURLGenerator, base_url='')
        self.assertRaisesRegexp(InvalidBaseURLError, 'Query parameters found',
                                RedmineURLGenerator, base_url=QUERY_URL)
        self.assertRaisesRegexp(InvalidBaseURLError, 'URL related to a JSON',
                                RedmineURLGenerator, base_url=JSON_URL)

        # Do not raise any error because it's a valid URL
        generator = RedmineURLGenerator(JSON_SUBSTRING_URL)
        self.assertEqual(JSON_SUBSTRING_URL, generator.base_url)

    def test_trailing_slash(self):
        # Test if a trailing slash is added to base URL
        generator = RedmineURLGenerator(REDMINE_URL_WITHOUT_SLASH)
        self.assertEqual(REDMINE_URL, generator.base_url)

    def test_assign_base_url(self):
        # Test whether fails or not assigning invalid URLs
        generator = RedmineURLGenerator(REDMINE_URL)

        self.assertRaisesRegexp(InvalidBaseURLError, 'Empty URL',
                                setattr, generator, 'base_url', None)
        self.assertEqual(REDMINE_URL, generator.base_url)

        self.assertRaisesRegexp(InvalidBaseURLError, 'Empty URL',
                                setattr, generator, 'base_url', '')
        self.assertEqual(REDMINE_URL, generator.base_url)

        self.assertRaisesRegexp(InvalidBaseURLError, 'Query parameters found',
                                setattr, generator, 'base_url', QUERY_URL)
        self.assertEqual(REDMINE_URL, generator.base_url)

        self.assertRaisesRegexp(InvalidBaseURLError, 'URL related to a JSON',
                                setattr, generator, 'base_url', JSON_URL)
        self.assertEqual(REDMINE_URL, generator.base_url)

        generator.base_url = ISSUE_TRACKER_URL
        self.assertEqual(ISSUE_TRACKER_URL, generator.base_url)


if __name__ == "__main__":
    unittest.main()
