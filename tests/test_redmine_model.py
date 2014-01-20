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
import dateutil.parser
import sys
import unittest

if not '..' in sys.path:
    sys.path.insert(0, '..')

from bicho.backends.redmine.model import RedmineIdentity, RedmineStatus


# Mock dates for testing
MOCK_DATETIME = datetime.datetime.utcnow()
MOCK_LAST_LOGIN_DATETIME = dateutil.parser.parse('2014-01-01')
MOCK_DATETIME_STR = '2001-01-01T00:00:01'

# RegExps for testing TypeError exceptions
TYPE_ERROR_REGEXP = '.+%s.+ should be a %s instance\. %s given'
CREATED_ON_STR_ERROR = TYPE_ERROR_REGEXP % ('created_on', 'datetime', 'str')
LAST_LOGIN_ON_STR_ERROR = TYPE_ERROR_REGEXP % ('last_login_on', 'datetime', 'str')
IS_CLOSED_NONE_ERROR = TYPE_ERROR_REGEXP % ('is_closed', 'bool', 'NoneType')
IS_CLOSED_STR_ERROR = TYPE_ERROR_REGEXP % ('is_closed', 'bool', 'str')
IS_DEFAULT_NONE_ERROR = TYPE_ERROR_REGEXP % ('is_default', 'bool', 'NoneType')
IS_DEFAULT_STR_ERROR = TYPE_ERROR_REGEXP % ('is_default', 'bool', 'str')


class TestRedmineIdentity(unittest.TestCase):

    def setUp(self):
        self.identity = RedmineIdentity('1', 'John Smith',
                                        'jsmith@example.com', 'jsmith',
                                        MOCK_DATETIME,
                                        MOCK_LAST_LOGIN_DATETIME)

    def test_simple_identity(self):
        identity = RedmineIdentity('1')
        self.assertEqual('1', identity.user_id)
        self.assertEqual(None, identity.name)
        self.assertEqual(None, identity.email)
        self.assertEqual(None, identity.login)
        self.assertEqual(None, identity.created_on)
        self.assertEqual(None, identity.last_login_on)

    def test_identity(self):
        identity = RedmineIdentity('1', 'John Smith',
                                   'jsmith@example.com', 'jsmith',
                                   MOCK_DATETIME, MOCK_LAST_LOGIN_DATETIME)
        self.assertEqual('1', identity.user_id)
        self.assertEqual('John Smith', identity.name)
        self.assertEqual('jsmith@example.com', identity.email)
        self.assertEqual('jsmith', identity.login)
        self.assertEqual(MOCK_DATETIME, identity.created_on)
        self.assertEqual(MOCK_LAST_LOGIN_DATETIME, identity.last_login_on)

    def test_created_on(self):
        self.assertRaises(TypeError, setattr, self.identity, 'created_on', MOCK_DATETIME_STR)
        self.assertEqual(MOCK_DATETIME, self.identity.created_on)

        self.identity.created_on = None
        self.assertEqual(None, self.identity.created_on)

        test_dt = datetime.datetime.utcnow()
        self.identity.created_on = test_dt
        self.assertEqual(test_dt, self.identity.created_on)

    def test_last_login_on(self):
        self.assertRaises(TypeError, setattr, self.identity, 'last_login_on', MOCK_DATETIME_STR)
        self.assertEqual(MOCK_LAST_LOGIN_DATETIME, self.identity.last_login_on)

        self.identity.last_login_on = None
        self.assertEqual(None, self.identity.last_login_on)

        test_dt = datetime.datetime.utcnow()
        self.identity.last_login_on = test_dt
        self.assertEqual(test_dt, self.identity.last_login_on)

    def test_invalid_init(self):
        self.assertRaisesRegexp(TypeError, CREATED_ON_STR_ERROR,
                                RedmineIdentity, user_id='1',
                                name='John Doe', email='johndoe@example.com',
                                created_on=MOCK_DATETIME_STR,
                                last_login_on=None)
        self.assertRaisesRegexp(TypeError, LAST_LOGIN_ON_STR_ERROR,
                                RedmineIdentity, user_id='1',
                                name='John Doe', email='johndoe@example.com',
                                created_on=MOCK_DATETIME,
                                last_login_on=MOCK_DATETIME_STR)


class TestRedmineStatus(unittest.TestCase):

    def setUp(self):
        self.status = RedmineStatus('88', 'Open')

    def test_simple_status(self):
        self.assertEqual('88', self.status.status_id)
        self.assertEqual('Open', self.status.name)
        self.assertEqual(False, self.status.is_closed)
        self.assertEqual(False, self.status.is_default)

    def test_status(self):
        status = RedmineStatus('1', 'Fixed', True, True)
        self.assertEqual('1', status.status_id)
        self.assertEqual('Fixed', status.name)
        self.assertEqual(True, status.is_closed)
        self.assertEqual(True, status.is_default)

        status = RedmineStatus('2', 'New', False, True)
        self.assertEqual(False, status.is_closed)
        self.assertEqual(True, status.is_default)

    def test_read_only_properties(self):
        self.assertRaises(AttributeError, setattr, self.status, 'status_id', '')
        self.assertEqual('88', self.status.status_id)

        self.assertRaises(AttributeError, setattr, self.status, 'name', '')
        self.assertEqual('Open', self.status.name)

        self.assertRaises(AttributeError, setattr, self.status, 'is_closed', True)
        self.assertEqual(False, self.status.is_closed)

        self.assertRaises(AttributeError, setattr, self.status, 'is_default', True)
        self.assertEqual(False, self.status.is_default)

    def test_invalid_init(self):
        self.assertRaisesRegexp(TypeError, IS_CLOSED_NONE_ERROR,
                                RedmineStatus, status_id='1', name='Closed',
                                is_closed=None)
        self.assertRaisesRegexp(TypeError, IS_CLOSED_STR_ERROR,
                                RedmineStatus, status_id='1', name='Closed',
                                is_closed='')
        self.assertRaisesRegexp(TypeError, IS_DEFAULT_NONE_ERROR,
                                RedmineStatus, status_id='1', name='Closed',
                                is_default=None)
        self.assertRaisesRegexp(TypeError, IS_DEFAULT_STR_ERROR,
                                RedmineStatus, status_id='1', name='Closed',
                                is_default='')

if __name__ == "__main__":
    unittest.main()
