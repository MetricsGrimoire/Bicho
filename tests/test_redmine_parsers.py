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

from bicho.common import Comment, Change, IssueRelationship
from bicho.exceptions import UnmarshallingError
from bicho.backends.parsers import JSONParserError
from bicho.backends.redmine.model import RDM_RELATIONSHIP_BLOCKED,\
    RDM_RELATIONSHIP_BLOCKS, RDM_RELATIONSHIP_RELATES,\
    RedmineIdentity, RedmineStatus, RedmineIssue, RedmineAttachment
from bicho.backends.redmine.parsers import RedmineBaseParser, RedmineIdentityParser,\
    RedmineStatusesParser, RedmineIssuesSummaryParser, RedmineIssueParser
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

ISSUE_FILE = 'issue.json'
ISSUE_CHANGES_FILE = 'issue_changes.json'
ISSUE_INVALID_DATE_FILE = 'issue_invalid_date.json'
ISSUE_INVALID_COMMENT_FILE = 'issue_invalid_comment.json'
ISSUE_INVALID_ATTACHMENT_FILE = 'issue_invalid_attachment.json'
ISSUE_INVALID_CHANGE_FILE = 'issue_invalid_changes.json'
ISSUE_INVALID_RELATION_FILE = 'issue_invalid_relation.json'
ISSUE_NO_ASSIGNED_TO_FILE = 'issue_no_assigned_to.json'
ISSUE_NO_COMMENTS_FILE = 'issue_no_comments.json'
ISSUE_NO_ATTACHMENTS_FILE = 'issue_no_attachments.json'
ISSUE_NO_CHANGES_FILE = 'issue_no_changes.json'
ISSUE_NO_RELATIONSHIPS_FILE = 'issue_no_relationships.json'
ISSUE_NO_ATTACHMENTS_KEY_FILE = 'issue_no_attachments_key.json'
ISSUE_NO_JOURNALS_KEY_FILE = 'issue_no_journals_key.json'
ISSUE_NO_RELATIONSHIPS_KEY_FILE = 'issue_no_relationships_key.json'
ISSUE_UNKNOWN_RELATION_TYPE_FILE = 'issue_unknown_relation_type.json'
ISSUE_EMPTY_JOURNALS_FILE = 'issue_empty_journals.json'


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

ISSUE_JOURNALS_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('RedmineIssue', 'journals')
ISSUE_ATTACHMENTS_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('RedmineIssue', 'attachments')
ISSUE_RELATIONS_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('RedmineIssue', 'relations')

RELATION_TYPE_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('IssueRelationship', 'relation_type')

COMMENT_CREATED_ON_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('Comment', 'created_on')

ATTACHMENT_SIZE_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('RedmineAttachment', 'size')

CHANGE_NAME_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('Change', 'name')

DATETIME_MONTH_ERROR = UNMARSHALLING_ERROR_REGEXP % ('datetime', 'month must be in 1..12')
DATETIME_UNKNOWN_FORMAT = UNMARSHALLING_ERROR_REGEXP % ('datetime', 'unknown string format')

# RegExp for unkwnon types of relationships
RELATION_UNKNOWN_ERROR = 'unknown relationship type: blocked by'

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

        ts = self.parser.unmarshal_timestamp('2014/01/22 10:54:30 +0100')
        self.assertIsInstance(ts, datetime.datetime)
        self.assertEqual(2014, ts.year)
        self.assertEqual(01, ts.month)
        self.assertEqual(22, ts.day)
        self.assertEqual(10, ts.hour)
        self.assertEqual(54, ts.minute)
        self.assertEqual(30, ts.second)
        self.assertEqual(u'2014-01-22 10:54:30', unicode(ts))

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


class TestRedmineIssueParser(unittest.TestCase):

    def setUp(self):
        self.parser = None

    def test_common_data(self):
        # Test if there is no fail parsing issue common fields
        # to the rest of the trackers
        issue = self._parse(ISSUE_FILE)
        self.assertIsInstance(issue, RedmineIssue)

        self.assertEqual(u'7210', issue.issue_id)
        self.assertEqual(u'Bug', issue.issue_type)
        self.assertEqual(u'mock: issue test', issue.summary)
        self.assertEqual(u'Lorem ipsum dolor sit amet.', issue.description)
        self.assertEqual(u'New', issue.status)
        self.assertEqual(u'New', issue.resolution)
        self.assertEqual(u'Normal', issue.priority)

    def test_redmine_data(self):
        # Test if there is no fail parsing Redmine specific fields
        issue = self._parse(ISSUE_FILE)
        self.assertEqual(u'55', issue.project_id)
        self.assertEqual(u'Redmine', issue.project)
        self.assertEqual(u'1', issue.rdm_tracker_id)
        self.assertEqual(u'Bug', issue.rdm_tracker)
        self.assertEqual(u'2014-01-23 15:42:01', unicode(issue.updated_on))

    def test_submitted_by(self):
        # Test whether the parsing process does not fail
        # retrieving submitter identity
        issue = self._parse(ISSUE_FILE)
        submitter = issue.submitted_by

        self.assertIsInstance(submitter, RedmineIdentity)
        self.assertEqual(u'5', submitter.user_id)
        self.assertEqual(u'Daniel Izquierdo', submitter.name)
        self.assertEqual(None, submitter.email)

    def test_submitted_on(self):
        # Test if the submission date is parsed
        issue = self._parse(ISSUE_FILE)
        submitted_on = issue.submitted_on

        self.assertIsInstance(submitted_on, datetime.datetime)
        self.assertEqual(u'2014-01-23 15:42:01', unicode(submitted_on))

    def test_invalid_submitted_on(self):
        # Test if the parser raises an exception
        # paring the submission date
        self.assertRaisesRegexp(UnmarshallingError,
                                DATETIME_MONTH_ERROR,
                                self._parse,
                                filename=ISSUE_INVALID_DATE_FILE)

    def test_assigned_to(self):
        # Test whether the parsing process does not fail
        # retrieving asignee identity
        issue = self._parse(ISSUE_FILE)
        assigned_to = issue.assigned_to

        self.assertIsInstance(assigned_to, RedmineIdentity)
        self.assertEqual(u'461', assigned_to.user_id)
        self.assertEqual(u'Alvaro del Castillo', assigned_to.name)
        self.assertEqual(None, assigned_to.email)

    def test_no_assigned_to(self):
        # Test whether the parsing process does not fail
        # when assigned_to is not set
        issue = self._parse(ISSUE_NO_ASSIGNED_TO_FILE)
        assigned_to = issue.assigned_to
        self.assertEqual(None, assigned_to)

    def test_empty_journals(self):
        # Test if no comments are parser when
        # journals is empty
        issue = self._parse(ISSUE_EMPTY_JOURNALS_FILE)
        self.assertEqual(0, len(issue.comments))

    def test_no_journdals_key(self):
        # Test whether it raises an exception when
        # journals key is not found in the stream
        self.assertRaisesRegexp(UnmarshallingError,
                                ISSUE_JOURNALS_KEY_ERROR,
                                self._parse,
                                filename=ISSUE_NO_JOURNALS_KEY_FILE)

    def test_comments(self):
        # Test the comments parsing process
        issue = self._parse(ISSUE_FILE)
        comments = issue.comments
        self.assertEqual(2, len(comments))

        comment = comments[0]
        self.assertIsInstance(comment, Comment)
        self.assertEqual(u'Just a comment', comment.text)
        self.assertEqual(u'461', comment.submitted_by.user_id)
        self.assertEqual(u'Alvaro del Castillo', comment.submitted_by.name)
        self.assertEqual(None, comment.submitted_by.email)
        self.assertEqual(u'2014-01-21 20:44:14', unicode(comment.submitted_on))

        comment = comments[1]
        self.assertIsInstance(comment, Comment)
        self.assertEqual(u'Mock comment of this bug', comment.text)
        self.assertEqual(u'3', comment.submitted_by.user_id)
        self.assertEqual(u'Jesus Gonzalez-Barahona', comment.submitted_by.name)
        self.assertEqual(None, comment.submitted_by.email)
        self.assertEqual(u'2014-01-21 20:57:39', unicode(comment.submitted_on))

    def test_invalid_comment(self):
        # Test if the parser raises an exception
        # parsing a comment not well formed
        self.assertRaisesRegexp(UnmarshallingError,
                                COMMENT_CREATED_ON_KEY_ERROR,
                                self._parse,
                                filename=ISSUE_INVALID_COMMENT_FILE)

    def test_no_comments(self):
        # Test if nothing is parsed from a stream
        # without notes tags
        issue = self._parse(ISSUE_NO_COMMENTS_FILE)
        self.assertEqual(0, len(issue.comments))

    def test_attachments(self):
        # Test the attachments parsing process
        issue = self._parse(ISSUE_FILE)
        attachments = issue.attachments
        self.assertEqual(3, len(attachments))

        attachment = attachments[0]
        self.assertIsInstance(attachment, RedmineAttachment)
        self.assertEqual(u'clone-gits.sh', attachment.name)
        self.assertEqual(u'https://example.org/attachments/download/1/clone-gits.sh', attachment.url)
        self.assertEqual(None, attachment.description)
        self.assertEqual(u'17', attachment.submitted_by.user_id)
        self.assertEqual(u'Santiago Dueñas', attachment.submitted_by.name)
        self.assertEqual(None, attachment.submitted_by.email)
        self.assertEqual(u'2013-10-04 17:02:57', unicode(attachment.submitted_on))
        self.assertEqual(u'151', attachment.size)
        self.assertEqual(u'1', attachment.rdm_attachment_id)

        attachment = attachments[1]
        self.assertIsInstance(attachment, RedmineAttachment)
        self.assertEqual(u'setup.py', attachment.name)
        self.assertEqual(u'https://example.org/attachments/download/2/setup.py', attachment.url)
        self.assertEqual(u'Setup script', attachment.description)
        self.assertEqual(u'18', attachment.submitted_by.user_id)
        self.assertEqual(u'Daniel Izquierdo', attachment.submitted_by.name)
        self.assertEqual(None, attachment.submitted_by.email)
        self.assertEqual(u'2014-01-13 12:55:21', unicode(attachment.submitted_on))
        self.assertEqual(u'8', attachment.size)
        self.assertEqual(u'2', attachment.rdm_attachment_id)

        attachment = attachments[2]
        self.assertIsInstance(attachment, RedmineAttachment)
        self.assertEqual(u'install.sh', attachment.name)
        self.assertEqual(u'https://example.org/attachments/download/10/install.sh', attachment.url)
        self.assertEqual(u'No description', attachment.description)
        self.assertEqual(u'18', attachment.submitted_by.user_id)
        self.assertEqual(u'Daniel Izquierdo', attachment.submitted_by.name)
        self.assertEqual(None, attachment.submitted_by.email)
        self.assertEqual(u'2014-01-13 12:55:21', unicode(attachment.submitted_on))
        self.assertEqual(u'256', attachment.size)
        self.assertEqual(u'10', attachment.rdm_attachment_id)

    def test_no_attachments(self):
        # Test if nothing is parsed from a stream
        # without attachment content
        issue = self._parse(ISSUE_NO_ATTACHMENTS_FILE)
        self.assertEqual(0, len(issue.attachments))

    def test_invalid_attachment(self):
        # Test if the parser raises an exception
        # parsing an invalid attachment
        self.assertRaisesRegexp(UnmarshallingError,
                                ATTACHMENT_SIZE_KEY_ERROR,
                                self._parse,
                                filename=ISSUE_INVALID_ATTACHMENT_FILE)

    def test_no_attachments_key(self):
        # Test whether it raises an exception when
        # attachments key is not found in the stream
        self.assertRaisesRegexp(UnmarshallingError,
                                ISSUE_ATTACHMENTS_KEY_ERROR,
                                self._parse,
                                filename=ISSUE_NO_ATTACHMENTS_KEY_FILE)

    def test_changes(self):
        # Test whether there is no fail parsing the changes
        # from an issue
        issue = self._parse(ISSUE_CHANGES_FILE)
        changes = issue.changes
        self.assertEqual(8, len(changes))

        # Changes from #1 to #6 should have same values in 'changed_by'
        # and 'changed_on' attribs
        change = changes[0]
        self.assertIsInstance(change, Change)
        self.assertEqual(u'461', change.changed_by.user_id)
        self.assertEqual(u'Joao Luis', change.changed_by.name)
        self.assertEqual(None, change.changed_by.email)
        self.assertEqual(u'2014-01-16 10:16:15', unicode(change.changed_on))
        self.assertEqual(u'subject', unicode(change.field))
        self.assertEqual(u'Error ENOENT', change.old_value)
        self.assertEqual(u'mon: Error ENOENT: unrecognized pool', change.new_value)

        change = changes[1]
        self.assertIsInstance(change, Change)
        self.assertEqual(u'461', change.changed_by.user_id)
        self.assertEqual(u'Joao Luis', change.changed_by.name)
        self.assertEqual(None, change.changed_by.email)
        self.assertEqual(u'2014-01-16 10:16:15', unicode(change.changed_on))
        self.assertEqual(u'category_id', change.field)
        self.assertEqual(None, change.old_value)
        self.assertEqual(u'3', change.new_value)

        change = changes[2]
        self.assertIsInstance(change, Change)
        self.assertEqual(u'461', change.changed_by.user_id)
        self.assertEqual(u'Joao Luis', change.changed_by.name)
        self.assertEqual(None, change.changed_by.email)
        self.assertEqual(u'2014-01-16 10:16:15', unicode(change.changed_on))
        self.assertEqual(u'status_id', change.field)
        self.assertEqual(u'12', change.old_value)
        self.assertEqual(u'2', change.new_value)

        change = changes[3]
        self.assertIsInstance(change, Change)
        self.assertEqual(u'461', change.changed_by.user_id)
        self.assertEqual(u'Joao Luis', change.changed_by.name)
        self.assertEqual(None, change.changed_by.email)
        self.assertEqual(u'2014-01-16 10:16:15', unicode(change.changed_on))
        self.assertEqual(u'assigned_to_id', change.field)
        self.assertEqual(u'461', change.old_value)
        self.assertEqual(None, change.new_value)

        # changed_by, changed_on values should be different to
        # the other changes
        change = changes[6]
        self.assertIsInstance(change, Change)
        self.assertEqual(u'789', change.changed_by.user_id)
        self.assertEqual(u'Loic Dachary', change.changed_by.name)
        self.assertEqual(None, change.changed_by.email)
        self.assertEqual(u'2014-01-16 13:23:19', unicode(change.changed_on))
        self.assertEqual(u'status_id', change.field)
        self.assertEqual(u'13', change.old_value)
        self.assertEqual(u'3', change.new_value)

    def test_no_changes(self):
        # Test if nothing is parsed from a stream without a
        # table of changes
        issue = self._parse(ISSUE_NO_CHANGES_FILE)
        changes = issue.changes
        self.assertEqual(0, len(changes))

    def test_invalid_change(self):
        # Test if the parser raises an exception
        # parsing a change not well formed
        self.assertRaisesRegexp(UnmarshallingError,
                                CHANGE_NAME_KEY_ERROR,
                                self._parse,
                                filename=ISSUE_INVALID_CHANGE_FILE)

    def test_relationships(self):
        # Test whether there is no fail parsing the relationships
        # of an issue
        issue = self._parse(ISSUE_FILE)
        relationships = issue.relationships
        self.assertEqual(3, len(relationships))

        relation = relationships[0]
        self.assertIsInstance(relation, IssueRelationship)
        self.assertEqual(RDM_RELATIONSHIP_RELATES, relation.rel_type)
        self.assertEqual(u'2451', relation.related_to)

        relation = relationships[1]
        self.assertIsInstance(relation, IssueRelationship)
        self.assertEqual(RDM_RELATIONSHIP_BLOCKS, relation.rel_type)
        self.assertEqual(u'2279', relation.related_to)

        relation = relationships[2]
        self.assertIsInstance(relation, IssueRelationship)
        self.assertEqual(RDM_RELATIONSHIP_BLOCKED, relation.rel_type)
        self.assertEqual(u'2251', relation.related_to)

    def test_no_relationships(self):
        # Test if nothing is parsed from a stream
        # without relations
        issue = self._parse(ISSUE_NO_RELATIONSHIPS_FILE)
        self.assertEqual(0, len(issue.relationships))

    def test_invalid_relation(self):
        # Test if the parser raises an exception
        # when a relation is invalid
        self.assertRaisesRegexp(UnmarshallingError,
                                RELATION_TYPE_KEY_ERROR,
                                self._parse,
                                filename=ISSUE_INVALID_RELATION_FILE)

    def test_unknown_relation_type(self):
        # Test if the parser raises an exception
        # when finds an unknown type of relationship
        self.assertRaisesRegexp(UnmarshallingError,
                                RELATION_UNKNOWN_ERROR,
                                self._parse,
                                ISSUE_UNKNOWN_RELATION_TYPE_FILE)

    def test_no_relations_key(self):
        # Test whether it raises an exception when
        # relations key is not found in the stream
        self.assertRaisesRegexp(UnmarshallingError,
                                ISSUE_RELATIONS_KEY_ERROR,
                                self._parse,
                                filename=ISSUE_NO_RELATIONSHIPS_KEY_FILE)

    def _parse(self, filename):
        """Generic method to parse a Redmine summary from a JSON stream.

        :param filename: path of the file to parse
        :type filename: str
        :return: summary parsed from Redmine
        :rtype: RedmineIssuesSummary
        """
        filepath = os.path.join(TEST_FILES_DIRNAME, filename)
        json = read_file(filepath)
        self.parser = RedmineIssueParser(json)
        self.parser.parse()
        return self.parser.issue


if __name__ == "__main__":
    unittest.main()
