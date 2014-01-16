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

from bicho.backends.redmine.model import RedmineIdentity


# Mock dates for testing
MOCK_DATETIME = datetime.datetime.utcnow()
MOCK_LAST_LOGIN_DATETIME = dateutil.parser.parse('2014-01-01')
MOCK_DATETIME_STR = '2001-01-01T00:00:01'

# RegExps for testing TypeError exceptions
TYPE_ERROR_REGEXP = '.+%s.+ should be a %s instance\. %s given'
CREATED_ON_STR_ERROR = TYPE_ERROR_REGEXP % ('created_on', 'datetime', 'str')
LAST_LOGIN_ON_STR_ERROR = TYPE_ERROR_REGEXP % ('last_login_on', 'datetime', 'str')


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


if __name__ == "__main__":
    unittest.main()
