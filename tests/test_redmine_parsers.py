# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Bitergia
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

import datetime
import os
import sys
import unittest

if not '..' in sys.path:
    sys.path.insert(0, '..')

from bicho.exceptions import UnmarshallingError
from bicho.backends.parsers import JSONParserError
from bicho.backends.redmine.model import RedmineIdentity, RedmineStatus
from bicho.backends.redmine.parsers import RedmineBaseParser, RedmineIdentityParser,\
    RedmineStatusesParser, RedmineIssuesSummaryParser
from utilities import read_file


# Name of directory where the test input files are stored
TEST_FILES_DIRNAME = 'redmine_data'

# Test files
IDENTITY_FILE = 'identity.json'
IDENTITY_NO_USER = 'identity_no_user.json'
IDENTITY_NO_ID = 'identity_no_id.json'
IDENTITY_NO_FIRSTNAME = 'identity_no_firstname.json'
IDENTITY_NO_LASTNAME = 'identity_no_lastname.json'
IDENTITY_NO_MAIL = 'identity_no_mail.json'
IDENTITY_NO_LOGIN = 'identity_no_login.json'
IDENTITY_NO_CREATED_ON = 'identity_no_created_on.json'
IDENTITY_NO_LAST_LOGIN_ON = 'identity_no_last_login_on.json'
IDENTITY_INVALID_CREATED_ON = 'identity_invalid_created_on.json'
IDENTITY_INVALID_LAST_LOGIN_ON = 'identity_invalid_last_login_on.json'
IDENTITY_INVALID_STREAM = 'identity_invalid_stream.json'
STATUSES_FILE = 'statuses.json'
STATUSES_NO_ISSUE_STATUSES = 'statuses_no_issue_statuses.json'
STATUSES_NO_ID = 'statuses_no_id.json'
STATUSES_NO_NAME = 'statuses_no_name.json'
STATUSES_INVALID_IS_CLOSED = 'statuses_invalid_is_closed.json'
STATUSES_INVALID_IS_DEFAULT = 'statuses_invalid_is_default.json'
STATUSES_INVALID_STREAM = 'statuses_invalid_stream.json'
SUMMARY_FILE = 'summary.json'
SUMMARY_NO_ISSUES_SUMMARY = 'summary_no_issues_summary.json'
SUMMARY_NO_TOTAL_COUNT = 'summary_no_total_count.json'
SUMMARY_NO_OFFSET = 'summary_no_offset.json'
SUMMARY_NO_LIMIT = 'summary_no_limit.json'
SUMMARY_NO_ID = 'summary_no_id.json'
SUMMARY_NO_UPDATED_ON = 'summary_no_updated_on.json'
SUMMARY_INVALID_UPDATED_ON = 'summary_invalid_updated_on.json'
SUMMARY_INVALID_STREAM = 'summary_invalid_stream.json'


# RegExps for testing JSONParserError exceptions
PARSING_ERROR_REGEXP = 'error parsing JSON.+%s'
INVALID_STREAM_VALUE_ERROR = PARSING_ERROR_REGEXP % ('ValueError')

# RegExps for testing UnmarshallingError exceptions
UNMARSHALLING_ERROR_REGEXP = 'error unmarshalling object to %s.+%s'
USERS_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('RedmineIdentity', 'user')
ID_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('RedmineIdentity', 'id')
FIRSTNAME_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('RedmineIdentity', 'firstname')
LASTNAME_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('RedmineIdentity', 'lastname')
MAIL_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('RedmineIdentity', 'mail')
LOGIN_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('RedmineIdentity', 'login')
CREATED_ON_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('RedmineIdentity', 'created_on')
LAST_LOGIN_ON_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('RedmineIdentity', 'last_login_on')
ISSUE_STATUSES_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('list\(RedmineStatus\)', 'issue_statuses')
STATUSES_ID_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('RedmineStatus', 'id')
STATUSES_NAME_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('RedmineStatus', 'name')
SUMMARY_ISSUES_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('RedmineIssuesSummary', 'issues')
SUMMARY_TOTAL_COUNT_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('RedmineIssuesSummary', 'total_count')
SUMMARY_OFFSET_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('RedmineIssuesSummary', 'offset')
SUMMARY_LIMIT_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('RedmineIssuesSummary', 'limit')
SUMMARY_ID_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('IssueSummary', 'id')
SUMMARY_UPDATED_ON_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('IssueSummary', 'updated_on')
DATETIME_MONTH_ERROR = UNMARSHALLING_ERROR_REGEXP % ('datetime', 'month must be in 1..12')
DATETIME_UNKNOWN_FORMAT = UNMARSHALLING_ERROR_REGEXP % ('datetime', 'unknown string format')

# RegExps for testing TypeError exceptions
TYPE_ERROR_REGEXP = 'Parameter "%s" should be a %s instance. %s given'
IS_CLOSED_BOOL_ERROR = TYPE_ERROR_REGEXP % ('is_closed', 'bool', 'int')
IS_DEFAULT_BOOL_ERROR = TYPE_ERROR_REGEXP % ('is_default', 'bool', 'int')


# Mock class for testing RedmineBaseParser
class MockRedmineParser(RedmineBaseParser):

    def __init__(self, stream):
        super(RedmineBaseParser, self).__init__(stream)

    def unmarshal_timestamp(self, rdm_ts):
        return self._unmarshal_timestamp(rdm_ts)

    def unmarshal_str(self, rdm_str):
        return self._unmarshal_str(rdm_str)


class TestRedmineBaseParser(unittest.TestCase):

    def setUp(self):
        self.parser = MockRedmineParser('')

    def test_unmarshal_timestamp(self):
        ts = self.parser.unmarshal_timestamp('2014-01-20T17:06:31Z')
        self.assertIsInstance(ts, datetime.datetime)
        self.assertEqual(2014, ts.year)
        self.assertEqual(1, ts.month)
        self.assertEqual(20, ts.day)
        self.assertEqual(17, ts.hour)
        self.assertEqual(6, ts.minute)
        self.assertEqual(31, ts.second)
        self.assertEqual(u'2014-01-20 17:06:31', unicode(ts))

        ts = self.parser.unmarshal_timestamp('2007-10-31')
        self.assertIsInstance(ts, datetime.datetime)
        self.assertEqual(2007, ts.year)
        self.assertEqual(10, ts.month)
        self.assertEqual(31, ts.day)
        self.assertEqual(0, ts.hour)
        self.assertEqual(0, ts.minute)
        self.assertEqual(0, ts.second)
        self.assertEqual(u'2007-10-31 00:00:00', unicode(ts))

    def test_none_or_empty_timestamp(self):
        # Test invalid values
        self.assertRaises(UnmarshallingError, self.parser.unmarshal_timestamp, None)
        self.assertRaises(UnmarshallingError, self.parser.unmarshal_timestamp, '')

    def test_invalid_timestamp(self):
        # Test invalid date
        self.assertRaisesRegexp(UnmarshallingError,
                                DATETIME_MONTH_ERROR,
                                self.parser.unmarshal_timestamp,
                                '2012-13-01 01:02:03')

    def test_invalid_timestamp_format(self):
        # Test invalid date format
        self.assertRaisesRegexp(UnmarshallingError,
                                DATETIME_UNKNOWN_FORMAT,
                                self.parser.unmarshal_timestamp,
                                'invalid date')

    def test_unmarshal_str(self):
        s = self.parser.unmarshal_str('Redmine parser')
        self.assertIsInstance(s, unicode)
        self.assertEqual(u'Redmine parser', s)

        s = self.parser.unmarshal_str(None)
        self.assertIsNone(s)

        s = self.parser.unmarshal_str('')
        self.assertIsNone(s)


class TestRedmineIdentityParser(unittest.TestCase):

    def setUp(self):
        self.parser = None

    def test_common_data(self):
        # Test if there is no fail parsing identity common fields
        # to the rest of the trackers
        identity = self._parse(IDENTITY_FILE)
        self.assertIsInstance(identity, RedmineIdentity)

        self.assertEqual(u'1', identity.user_id)
        self.assertEqual(u'Santiago Dueñas', identity.name)
        self.assertEqual(u'sduenas@bitergia.com', identity.email)

    def test_redmine_data(self):
        # Test if there is no fail parsing Redmine specific fields
        identity = self._parse(IDENTITY_FILE)
        self.assertEqual(u'sduenas', identity.login)
        self.assertEqual(u'2010-01-01 03:00:36', unicode(identity.created_on))
        self.assertEqual(u'2014-01-17 11:25:45', unicode(identity.last_login_on))

    def test_no_identity_data(self):
        # Test if fails when there is no data about the identity
        # in the JSON, i.e no 'user' key set or it's empty
        self.assertRaisesRegexp(UnmarshallingError,
                                USERS_KEY_ERROR,
                                self._parse,
                                filename=IDENTITY_NO_USER)

    def test_no_values(self):
        # Test if the parser fails when the required
        # values are not present
        self.assertRaisesRegexp(UnmarshallingError,
                                ID_KEY_ERROR,
                                self._parse,
                                filename=IDENTITY_NO_ID)
        self.assertRaisesRegexp(UnmarshallingError,
                                FIRSTNAME_KEY_ERROR,
                                self._parse,
                                filename=IDENTITY_NO_FIRSTNAME)
        self.assertRaisesRegexp(UnmarshallingError,
                                LASTNAME_KEY_ERROR,
                                self._parse,
                                filename=IDENTITY_NO_LASTNAME)
        self.assertRaisesRegexp(UnmarshallingError,
                                MAIL_KEY_ERROR,
                                self._parse,
                                filename=IDENTITY_NO_MAIL)
        self.assertRaisesRegexp(UnmarshallingError,
                                LOGIN_KEY_ERROR,
                                self._parse,
                                filename=IDENTITY_NO_LOGIN)
        self.assertRaisesRegexp(UnmarshallingError,
                                CREATED_ON_KEY_ERROR,
                                self._parse,
                                filename=IDENTITY_NO_CREATED_ON)
        self.assertRaisesRegexp(UnmarshallingError,
                                LAST_LOGIN_ON_KEY_ERROR,
                                self._parse,
                                filename=IDENTITY_NO_LAST_LOGIN_ON)

    def test_invalid_create_on(self):
        # Test if the parser raises an exception
        # paring the create_on date
        self.assertRaisesRegexp(UnmarshallingError,
                                DATETIME_MONTH_ERROR,
                                self._parse,
                                filename=IDENTITY_INVALID_CREATED_ON)

    def test_invalid_last_login_on(self):
        # Test if the parser raises an exception
        # paring the create_on date
        self.assertRaisesRegexp(UnmarshallingError,
                                DATETIME_MONTH_ERROR,
                                self._parse,
                                filename=IDENTITY_INVALID_LAST_LOGIN_ON)

    def test_invalid_identity_stream(self):
        # Check whether it fails parsing an invalid
        # identity streamlist(RedmineStatus)
        self.assertRaisesRegexp(JSONParserError,
                                INVALID_STREAM_VALUE_ERROR,
                                self._parse,
                                filename=IDENTITY_INVALID_STREAM)

    def _parse(self, filename):
        """Generic method to parse a Redmine identity from a JSON stream.

        :param filename: path of the file to parse
        :type filename: str
        :return: a identity parsed from Redmine
        :rtype: RedmineIdentity
        """
        filepath = os.path.join(TEST_FILES_DIRNAME, filename)
        json = read_file(filepath)
        self.parser = RedmineIdentityParser(json)
        self.parser.parse()
        return self.parser.identity


class TestRedmineStatusesParser(unittest.TestCase):

    def setUp(self):
        self.parser = None

    def test_statuses_set(self):
        # Test if there is no fail parsing Redmine statuses
        statuses = self._parse(STATUSES_FILE)

        self.assertEqual(15, len(statuses))

        status = statuses[0]
        self.assertIsInstance(status, RedmineStatus)
        self.assertEqual(u'1', status.status_id)
        self.assertEqual(u'New', status.name)
        self.assertEqual(False, status.is_closed)
        self.assertEqual(True, status.is_default)

        status = statuses[1]
        self.assertIsInstance(status, RedmineStatus)
        self.assertEqual(u'12', status.status_id)
        self.assertEqual(u'Verified', status.name)
        self.assertEqual(False, status.is_closed)
        self.assertEqual(False, status.is_default)

        status = statuses[13]
        self.assertIsInstance(status, RedmineStatus)
        self.assertEqual(u'9', status.status_id)
        self.assertEqual(u'Can\'t reproduce', status.name)
        self.assertEqual(True, status.is_closed)
        self.assertEqual(False, status.is_default)

    def test_no_statuses_data(self):
        # Test if fails when there is no data about the identity
        # in the JSON, i.e no 'user' key set or it's empty
        self.assertRaisesRegexp(UnmarshallingError,
                                ISSUE_STATUSES_KEY_ERROR,
                                self._parse,
                                filename=STATUSES_NO_ISSUE_STATUSES)

    def test_no_values(self):
        # Test if the parser fails when the required
        # values are not present
        self.assertRaisesRegexp(UnmarshallingError,
                                STATUSES_ID_KEY_ERROR,
                                self._parse,
                                filename=STATUSES_NO_ID)
        self.assertRaisesRegexp(UnmarshallingError,
                                STATUSES_NAME_KEY_ERROR,
                                self._parse,
                                filename=STATUSES_NO_NAME)

    def test_invalid_is_closed(self):
        # Test if the parser fails when is_closed has
        # and invalid type
        self.assertRaisesRegexp(TypeError,
                                IS_CLOSED_BOOL_ERROR,
                                self._parse,
                                filename=STATUSES_INVALID_IS_CLOSED)

    def test_invalid_is_default(self):
        # Test if the parser fails when is_default has
        # and invalid types
        self.assertRaisesRegexp(TypeError,
                                IS_DEFAULT_BOOL_ERROR,
                                self._parse,
                                filename=STATUSES_INVALID_IS_DEFAULT)

    def test_invalid_statuses_stream(self):
        # Test whether it raises an exception when the
        # stream is invalid
        self.assertRaisesRegexp(JSONParserError,
                                INVALID_STREAM_VALUE_ERROR,
                                self._parse,
                                filename=STATUSES_INVALID_STREAM)

    def _parse(self, filename):
        """Generic method to parse Redmine statuses from a JSON stream.

        :param filename: path of the file to parse
        :type filename: str
        :return: a identity parsed from Redmine
        :rtype: list of RedmineStatus
        """
        filepath = os.path.join(TEST_FILES_DIRNAME, filename)
        json = read_file(filepath)
        self.parser = RedmineStatusesParser(json)
        self.parser.parse()
        return self.parser.statuses


class TestRedmineIssuesSummaryParser(unittest.TestCase):

    def setUp(self):
        self.parser = None

    def test_summary(self):
        # Test if there is no fail parsing a issues sumary from Redmine
        summary = self._parse(SUMMARY_FILE)

        self.assertEquals(u'149', summary.total_count)
        self.assertEquals(u'0', summary.offset)
        self.assertEquals(u'25', summary.limit)

        issues_summary = summary.summary
        self.assertEquals(25, len(issues_summary))

        isummary = summary.summary[0]
        self.assertEquals(u'7189', isummary.issue_id)
        self.assertEquals(u'2014-01-20 17:06:31', unicode(isummary.changed_on))

        isummary = summary.summary[1]
        self.assertEquals(u'7163', isummary.issue_id)
        self.assertEquals(u'2014-01-16 03:20:54', unicode(isummary.changed_on))

        isummary = summary.summary[24]
        self.assertEquals(u'6921', isummary.issue_id)
        self.assertEquals(u'2013-12-02 22:14:50', unicode(isummary.changed_on))

    def test_no_issues_summary_data(self):
        # Test if fails when there is no data about the issues
        # in the JSON, i.e no 'issues' key set or it's empty
        self.assertRaisesRegexp(UnmarshallingError,
                                SUMMARY_ISSUES_KEY_ERROR,
                                self._parse,
                                filename=SUMMARY_NO_ISSUES_SUMMARY)

    def test_no_values(self):
        # Test if the parser fails when the required
        # values are not present
        self.assertRaisesRegexp(UnmarshallingError,
                                SUMMARY_TOTAL_COUNT_KEY_ERROR,
                                self._parse,
                                filename=SUMMARY_NO_TOTAL_COUNT)
        self.assertRaisesRegexp(UnmarshallingError,
                                SUMMARY_OFFSET_KEY_ERROR,
                                self._parse,
                                filename=SUMMARY_NO_OFFSET)
        self.assertRaisesRegexp(UnmarshallingError,
                                SUMMARY_LIMIT_KEY_ERROR,
                                self._parse,
                                filename=SUMMARY_NO_LIMIT)
        self.assertRaisesRegexp(UnmarshallingError,
                                SUMMARY_ID_KEY_ERROR,
                                self._parse,
                                filename=SUMMARY_NO_ID)
        self.assertRaisesRegexp(UnmarshallingError,
                                SUMMARY_UPDATED_ON_KEY_ERROR,
                                self._parse,
                                filename=SUMMARY_NO_UPDATED_ON)

    def test_invalid_updated_on(self):
        # Test if the parser fails when is_closed has
        # and invalid type
        self.assertRaisesRegexp(UnmarshallingError,
                                DATETIME_UNKNOWN_FORMAT,
                                self._parse,
                                filename=SUMMARY_INVALID_UPDATED_ON)

    def test_invalid_summary_stream(self):
        # Test whether it raises an exception when the
        # stream is invalid
        self.assertRaisesRegexp(JSONParserError,
                                INVALID_STREAM_VALUE_ERROR,
                                self._parse,
                                filename=SUMMARY_INVALID_STREAM)

    def _parse(self, filename):
        """Generic method to parse a Redmine summary from a JSON stream.

        :param filename: path of the file to parse
        :type filename: str
        :return: summary parsed from Redmine
        :rtype: RedmineIssuesSummary
        """
        filepath = os.path.join(TEST_FILES_DIRNAME, filename)
        json = read_file(filepath)
        self.parser = RedmineIssuesSummaryParser(json)
        self.parser.parse()
        return self.parser.summary


if __name__ == "__main__":
    unittest.main()
