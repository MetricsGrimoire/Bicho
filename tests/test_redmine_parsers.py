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

import os
import sys
import unittest

if not '..' in sys.path:
    sys.path.insert(0, '..')

from bicho.exceptions import UnmarshallingError
from bicho.backends.parsers import JSONParserError
from bicho.backends.redmine.model import RedmineIdentity, RedmineStatus
from bicho.backends.redmine.parsers import RedmineIdentityParser, RedmineStatusesParser
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
DATETIME_MONTH_ERROR = UNMARSHALLING_ERROR_REGEXP % ('datetime', 'month must be in 1..12')

# RegExps for testing TypeError exceptions
TYPE_ERROR_REGEXP = 'Parameter "%s" should be a %s instance. %s given'
IS_CLOSED_BOOL_ERROR = TYPE_ERROR_REGEXP % ('is_closed', 'bool', 'int')
IS_DEFAULT_BOOL_ERROR = TYPE_ERROR_REGEXP % ('is_default', 'bool', 'int')


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


if __name__ == "__main__":
    unittest.main()
