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

from bicho.common import Identity, IssueSummary
from bicho.backends.redmine.model import RedmineIdentity, RedmineStatus,\
    RedmineIssuesSummary, RedmineIssue, RedmineAttachment


# Mock dates for testing
MOCK_DATETIME = datetime.datetime.utcnow()
MOCK_LAST_LOGIN_DATETIME = dateutil.parser.parse('2014-01-01')
MOCK_JANE_DATETIME = datetime.datetime.utcnow()
MOCK_LAST_LOGIN_JANE_DATETIME = dateutil.parser.parse('2014-08-09')
MOCK_DATETIME_STR = '2001-01-01T00:00:01'

# Mock identities for testing
JOHN_SMITH = RedmineIdentity('john_smith', 'John Smith', 'jsmith@example.com',
                             MOCK_DATETIME, MOCK_LAST_LOGIN_DATETIME)
JANE_ROE = RedmineIdentity('jane_roe', 'Jane Roe', 'jr@example.com',
                           MOCK_JANE_DATETIME, MOCK_LAST_LOGIN_JANE_DATETIME)
JOHN_DOE = Identity('john_doe', 'John Doe', 'johndoe@example.com')

# RegExps for testing TypeError exceptions
TYPE_ERROR_REGEXP = '.+%s.+ should be a %s instance\. %s given'
ASSIGNED_TO_IDENTITY_ERROR = TYPE_ERROR_REGEXP % ('assigned_to', 'RedmineIdentity', 'Identity')
CREATED_ON_STR_ERROR = TYPE_ERROR_REGEXP % ('created_on', 'datetime', 'str')
LAST_LOGIN_ON_STR_ERROR = TYPE_ERROR_REGEXP % ('last_login_on', 'datetime', 'str')
IS_CLOSED_NONE_ERROR = TYPE_ERROR_REGEXP % ('is_closed', 'bool', 'NoneType')
IS_CLOSED_STR_ERROR = TYPE_ERROR_REGEXP % ('is_closed', 'bool', 'str')
IS_DEFAULT_NONE_ERROR = TYPE_ERROR_REGEXP % ('is_default', 'bool', 'NoneType')
IS_DEFAULT_STR_ERROR = TYPE_ERROR_REGEXP % ('is_default', 'bool', 'str')
SUBMITTED_BY_IDENTITY_ERROR = TYPE_ERROR_REGEXP % ('submitted_by', 'RedmineIdentity', 'Identity')


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


class TestRedmineIssuesSummary(unittest.TestCase):

    def setUp(self):
        self.summary = RedmineIssuesSummary('150', '0', '25')

    def test_summary(self):
        self.assertEqual('150', self.summary.total_count)
        self.assertEqual('0', self.summary.offset)
        self.assertEqual('25', self.summary.limit)
        self.assertListEqual([], self.summary.summary)

    def test_readonly_properties(self):
        self.assertRaises(AttributeError, setattr, self.summary, 'total_count', '')
        self.assertEqual('150', self.summary.total_count)

        self.assertRaises(AttributeError, setattr, self.summary, 'offset', '')
        self.assertEqual('0', self.summary.offset)

        self.assertRaises(AttributeError, setattr, self.summary, 'limit', True)
        self.assertEqual('25', self.summary.limit)

    def test_issue_summary(self):
        isummary1 = 'Issue Summary #1'
        self.assertRaises(TypeError, self.summary.add_summary,
                          issue_summary=isummary1)

        isummary1 = IssueSummary('1', MOCK_DATETIME)
        isummary2 = IssueSummary('2', MOCK_LAST_LOGIN_DATETIME)
        self.summary.add_summary(isummary1)
        self.summary.add_summary(isummary2)
        self.assertListEqual([isummary1, isummary2], self.summary.summary)


class TestRedmineIssue(unittest.TestCase):

    def setUp(self):
        self.issue = RedmineIssue('1', 'Bug', 'redmine issue unit test',
                                  'unit test for RedmineIssue class',
                                  JOHN_SMITH, MOCK_DATETIME,
                                  'New', None, 'Low',
                                  JANE_ROE)

    def test_issue(self):
        self.assertEqual(u'1', self.issue.issue_id)
        self.assertEqual(u'Bug', self.issue.issue_type)
        self.assertEqual(u'redmine issue unit test', self.issue.summary)
        self.assertEqual(u'unit test for RedmineIssue class', self.issue.description)
        self.assertEqual(JOHN_SMITH, self.issue.submitted_by)
        self.assertEqual(MOCK_DATETIME, self.issue.submitted_on)
        self.assertEqual(u'New', self.issue.status)
        self.assertEqual(None, self.issue.resolution)
        self.assertEqual(u'Low', self.issue.priority)
        self.assertEqual(JANE_ROE, self.issue.assigned_to)

    def test_assigned_to(self):
        self.assertRaises(TypeError, setattr, self.issue, 'assigned_to', JOHN_DOE)
        self.assertEqual(JANE_ROE, self.issue.assigned_to)

        self.issue.assigned_to = None
        self.assertEqual(None, self.issue.assigned_to)
        self.issue.assigned_to = JANE_ROE
        self.assertEqual(JANE_ROE, self.issue.assigned_to)

    def test_updated_on(self):
        self.assertRaises(TypeError, setattr, self.issue, 'updated_on', MOCK_DATETIME_STR)
        self.assertEqual(None, self.issue.updated_on)

        test_dt = datetime.datetime.utcnow()
        self.issue.updated_on = test_dt
        self.assertEqual(test_dt, self.issue.updated_on)

    def test_invalid_init(self):
        self.assertRaisesRegexp(TypeError, SUBMITTED_BY_IDENTITY_ERROR,
                                RedmineIssue, issue_id='1', issue_type='Bug',
                                summary='redmine issue unit test',
                                description='unit test for RedmineIssue class',
                                submitted_by=JOHN_DOE, submitted_on=MOCK_DATETIME)
        self.assertRaisesRegexp(TypeError, ASSIGNED_TO_IDENTITY_ERROR,
                                RedmineIssue, issue_id='1', issue_type='Bug',
                                summary='redmine issue unit test',
                                description='unit test for RedmineIssue class',
                                submitted_by=JANE_ROE, submitted_on=MOCK_DATETIME,
                                assigned_to=JOHN_DOE)


class TestRedmineAttachment(unittest.TestCase):

    def test_attachment(self):
        attachment = RedmineAttachment('attch1',
                                       'http://redmine.example.com/1',
                                       'an attachment',
                                       JANE_ROE, MOCK_DATETIME,
                                       size='8', rdm_attachment_id='1')
        self.assertEqual('attch1', attachment.name)
        self.assertEqual('http://redmine.example.com/1', attachment.url)
        self.assertEqual('an attachment', attachment.description)
        self.assertEqual(JANE_ROE, attachment.submitted_by)
        self.assertEqual(MOCK_DATETIME, attachment.submitted_on)
        self.assertEqual('8', attachment.size)
        self.assertEqual('1', attachment.rdm_attachment_id)

    def test_invalid_init(self):
        self.assertRaisesRegexp(TypeError, SUBMITTED_BY_IDENTITY_ERROR,
                                RedmineAttachment, name='attch1',
                                url='http://redmine.example.com/1',
                                description='an attachment',
                                submitted_by=JOHN_DOE, submitted_on=MOCK_DATETIME,
                                size='8', rdm_attachment_id='1')


if __name__ == "__main__":
    unittest.main()
