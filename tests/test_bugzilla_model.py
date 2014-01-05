# -*- coding: utf-8 -*-
#
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
#         Santiago Dueñas <sduenas@libresoft.es>
#

import datetime
import dateutil.parser
import sys
import unittest

if not '..' in sys.path:
    sys.path.insert(0, '..')

from bicho.backends.bugzilla.model import BugzillaMetadata, BugzillaIssueSummary,\
    BugzillaIssue, BugzillaAttachment
from bicho.common import Identity, Attachment


# Mock identities for testing
JOHN_SMITH = Identity('john_smith', 'John Smith', 'jsmith@example.com')
JOHN_DOE = Identity('john_doe', 'John Doe', 'johndoe@example.com')
JANE_ROE = Identity('jane_roe', 'Jane Roe', 'jr@example.com')

# Mock dates for testing
MOCK_DATETIME = datetime.datetime.utcnow()
MOCK_DELTA_TS = dateutil.parser.parse('2003-06-27')
MOCK_DATETIME_STR = '2001-01-01T00:00:01'

# RegExps for testing TypeError exceptions
TYPE_ERROR_REGEXP = '.+%s.+ should be a %s instance\. %s given'
CHANGED_ON_NONE_ERROR = TYPE_ERROR_REGEXP % ('changed_on', 'datetime', 'NoneType')
CHANGED_ON_STR_ERROR = TYPE_ERROR_REGEXP % ('changed_on', 'datetime', 'str')
DELTA_TS_STR_ERROR = TYPE_ERROR_REGEXP % ('delta_ts', 'datetime', 'str')
IS_PATCH_STR_ERROR = TYPE_ERROR_REGEXP % ('is_patch', 'bool', 'str')
IS_OBSOLETE_STR_ERROR = TYPE_ERROR_REGEXP % ('is_obsolete', 'bool', 'str')


class TestBugzillaMetadata(unittest.TestCase):

    def test_metadata(self):
        metadata = BugzillaMetadata(1, 'http://example.com/bugzilla',
                                    'maintainer@example.com', 'test')
        self.assertEqual(1, metadata.version)
        self.assertEqual('http://example.com/bugzilla', metadata.urlbase)
        self.assertEqual('maintainer@example.com', metadata.maintainer)
        self.assertEqual('test', metadata.exporter)


class TestBugzillaIssueSummary(unittest.TestCase):

    def setUp(self):
        self.summary = BugzillaIssueSummary('1', MOCK_DATETIME)

    def test_summary(self):
        self.assertEqual('1', self.summary.issue_id)
        self.assertEqual(MOCK_DATETIME, self.summary.changed_on)

    def test_readonly_properties(self):
        self.assertRaises(AttributeError, setattr, self.summary, 'changed_on', datetime.datetime.utcnow())
        self.assertEqual(MOCK_DATETIME, self.summary.changed_on)

    def test_invalid_init(self):
        self.assertRaisesRegexp(TypeError, CHANGED_ON_NONE_ERROR,
                                BugzillaIssueSummary,
                                issue_id='1', changed_on=None)
        self.assertRaisesRegexp(TypeError, CHANGED_ON_STR_ERROR,
                                BugzillaIssueSummary,
                                issue_id='1', changed_on=MOCK_DATETIME_STR)


class TestBugzillaIssue(unittest.TestCase):

    def setUp(self):
        self.issue = BugzillaIssue('1', 'bug', 'issue unit test',
                                   'unit test for issue class',
                                   JOHN_SMITH, MOCK_DATETIME,
                                   'open', None, 'low',
                                   JANE_ROE)

    def test_issue(self):
        self.assertEqual('1', self.issue.issue_id)
        self.assertEqual('bug', self.issue.issue_type)
        self.assertEqual('issue unit test', self.issue.summary)
        self.assertEqual( 'unit test for issue class', self.issue.description)
        self.assertEqual(JOHN_SMITH, self.issue.submitted_by)
        self.assertEqual(MOCK_DATETIME, self.issue.submitted_on)
        self.assertEqual('open', self.issue.status)
        self.assertEqual(None, self.issue.resolution)
        self.assertEqual('low', self.issue.priority)
        self.assertEqual(JANE_ROE, self.issue.assigned_to)

    def test_delta_ts(self):
        self.assertRaises(TypeError, setattr, self.issue, 'delta_ts', MOCK_DATETIME_STR)
        self.assertEqual(None, self.issue.delta_ts)

        test_dt = datetime.datetime.utcnow()
        self.issue.delta_ts = test_dt
        self.assertEqual(test_dt, self.issue.delta_ts)

        self.issue.delta_ts = None
        self.assertEqual(None, self.issue.delta_ts)

    def test_qa_contact(self):
        self.assertRaises(TypeError, setattr, self.issue, 'qa_contact', 'John Doe')
        self.assertEqual(None, self.issue.qa_contact)

        self.issue.qa_contact = JOHN_DOE
        self.assertEqual(JOHN_DOE, self.issue.qa_contact)

        self.issue.qa_contact = None
        self.assertEqual(None, self.issue.qa_contact)

    def test_estimated_time(self):
        self.assertRaises(TypeError, setattr, self.issue, 'estimated_time', MOCK_DATETIME_STR)
        self.assertEqual(None, self.issue.estimated_time)

        test_dt = datetime.datetime.utcnow()
        self.issue.estimated_time = test_dt
        self.assertEqual(test_dt, self.issue.estimated_time)

        self.issue.estimated_time = None
        self.assertEqual(None, self.issue.estimated_time)

    def test_remaining_time(self):
        self.assertRaises(TypeError, setattr, self.issue, 'remaining_time', MOCK_DATETIME_STR)
        self.assertEqual(None, self.issue.remaining_time)

        test_dt = datetime.datetime.utcnow()
        self.issue.remaining_time = test_dt
        self.assertEqual(test_dt, self.issue.remaining_time)

        self.issue.remaining_time = None
        self.assertEqual(None, self.issue.remaining_time)

    def test_actual_time(self):
        self.assertRaises(TypeError, setattr, self.issue, 'actual_time', MOCK_DATETIME_STR)
        self.assertEqual(None, self.issue.actual_time)

        test_dt = datetime.datetime.utcnow()
        self.issue.actual_time = test_dt
        self.assertEqual(test_dt, self.issue.actual_time)

        self.issue.actual_time = None
        self.assertEqual(None, self.issue.actual_time)

    def test_deadline(self):
        self.assertRaises(TypeError, setattr, self.issue, 'deadline', MOCK_DATETIME_STR)
        self.assertEqual(None, self.issue.deadline)

        test_dt = datetime.datetime.utcnow()
        self.issue.deadline = test_dt
        self.assertEqual(test_dt, self.issue.deadline)

        self.issue.deadline = None
        self.assertEqual(None, self.issue.deadline)

    def test_bugzilla_attachment(self):
        attachment = Attachment('attachment')
        self.assertRaises(TypeError, self.issue.add_attachment, attachment=attachment)

        attachment = BugzillaAttachment('file',
                                        'http://bg.example.com/file',
                                        'attachment',
                                        JOHN_DOE, MOCK_DATETIME)
        self.issue.add_attachment(attachment)
        self.issue.add_attachment(attachment)
        self.assertListEqual([attachment, attachment], self.issue.attachments)


class TestBugzillaAttachment(unittest.TestCase):

    def setUp(self):
        self.attachment = BugzillaAttachment('at1',
                                             'http://bg.example.com/at1',
                                             'an attachment',
                                             JOHN_DOE, MOCK_DATETIME,
                                             'text/plain', '8',
                                             MOCK_DELTA_TS, is_patch=True,
                                             is_obsolete=False)

    def test_simple_attachment(self):
        attachment = BugzillaAttachment('at1',
                                        'http://bg.example.com/at1',
                                        'an attachment',
                                        JOHN_DOE, MOCK_DATETIME)
        self.assertEqual('at1', attachment.name)
        self.assertEqual('http://bg.example.com/at1', attachment.url)
        self.assertEqual('an attachment', attachment.description)
        self.assertEqual(JOHN_DOE, attachment.submitted_by)
        self.assertEqual(MOCK_DATETIME, attachment.submitted_on)
        self.assertEqual(None, attachment.filetype)
        self.assertEqual(None, attachment.size)
        self.assertEqual(None, attachment.delta_ts)
        self.assertEqual(None, attachment.is_patch)
        self.assertEqual(None, attachment.is_obsolete)

    def test_attachment(self):
        self.assertEqual('at1', self.attachment.name)
        self.assertEqual('http://bg.example.com/at1', self.attachment.url)
        self.assertEqual('an attachment', self.attachment.description)
        self.assertEqual(JOHN_DOE, self.attachment.submitted_by)
        self.assertEqual(MOCK_DATETIME, self.attachment.submitted_on)
        self.assertEqual('text/plain', self.attachment.filetype)
        self.assertEqual('8', self.attachment.size)
        self.assertEqual(MOCK_DELTA_TS, self.attachment.delta_ts)
        self.assertEqual(True, self.attachment.is_patch)
        self.assertEqual(False, self.attachment.is_obsolete)

    def test_delta_ts(self):
        self.assertRaises(TypeError, setattr, self.attachment, 'delta_ts', MOCK_DATETIME_STR)
        self.assertEqual(MOCK_DELTA_TS, self.attachment.delta_ts)

        self.attachment.delta_ts = None
        self.assertEqual(None, self.attachment.delta_ts)

        test_dt = datetime.datetime.utcnow()
        self.attachment.delta_ts = test_dt
        self.assertEqual(test_dt, self.attachment.delta_ts)

    def test_is_patch(self):
        self.assertRaises(TypeError, setattr, self.attachment, 'is_patch', 'True')
        self.assertEqual(True, self.attachment.is_patch)

        self.attachment.is_patch = None
        self.assertEqual(None, self.attachment.is_patch)

        self.attachment.is_patch = False
        self.assertEqual(False, self.attachment.is_patch)

    def test_is_obsolete(self):
        self.assertRaises(TypeError, setattr, self.attachment, 'is_obsolete', 'False')
        self.assertEqual(False, self.attachment.is_obsolete)

        self.attachment.is_obsolete = None
        self.assertEqual(None, self.attachment.is_obsolete)

        self.attachment.is_obsolete = True
        self.assertEqual(True, self.attachment.is_obsolete)

    def test_invalid_init(self):
        self.assertRaisesRegexp(TypeError, DELTA_TS_STR_ERROR,
                                BugzillaAttachment, name='at1',
                                url='http://bg.example.com/at1',
                                description='an attachment',
                                submitted_by=JOHN_DOE, submitted_on=MOCK_DATETIME,
                                filetype='text/plain', size='8',
                                delta_ts=MOCK_DATETIME_STR,
                                is_patch=None, is_obsolete=None)
        self.assertRaisesRegexp(TypeError, IS_PATCH_STR_ERROR,
                                BugzillaAttachment, name='at1',
                                url='http://bg.example.com/at1',
                                description='an attachment',
                                submitted_by=JOHN_DOE, submitted_on=MOCK_DATETIME,
                                filetype='text/plain', size='8',
                                delta_ts=MOCK_DELTA_TS,
                                is_patch='True', is_obsolete=None)
        self.assertRaisesRegexp(TypeError, IS_OBSOLETE_STR_ERROR,
                                BugzillaAttachment, name='at1',
                                url='http://bg.example.com/at1',
                                description='an attachment',
                                submitted_by=JOHN_DOE, submitted_on=MOCK_DATETIME,
                                filetype='text/plain', size='8',
                                delta_ts=MOCK_DELTA_TS,
                                is_patch=False, is_obsolete='False')


if __name__ == "__main__":
    unittest.main()
