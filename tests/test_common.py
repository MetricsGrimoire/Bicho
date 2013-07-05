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
import sys
import unittest

if not '..' in sys.path:
    sys.path.insert(0, '..')

from Bicho.common import Identity, Tracker, Issue, Comment, Attachment, Change


# Mock identities for testing
JOHN_SMITH = Identity('john_smith', 'John Smith', 'jsmith@example.com')
JOHN_DOE = Identity('john_doe', 'John Doe', 'johndoe@example.com')
JANE_ROE = Identity('jane_roe', 'Jane Roe', 'jr@example.com')

# Mock dates for testing
MOCK_DATETIME = datetime.datetime.utcnow()
MOCK_DATETIME_STR = '1970-01-01T00:00:01'

# RegExps for testing TypeError exceptions
TYPE_ERROR_REGEXP = '.+%s.+ should be a %s instance\. %s given'
SUBMITTED_BY_NONE_ERROR = TYPE_ERROR_REGEXP % ('submitted_by', 'Identity', 'NoneType')
SUBMITTED_BY_STR_ERROR = TYPE_ERROR_REGEXP % ('submitted_by', 'Identity', 'str')
SUBMITTED_ON_NONE_ERROR = TYPE_ERROR_REGEXP % ('submitted_on', 'datetime', 'NoneType')
SUBMITTED_ON_STR_ERROR = TYPE_ERROR_REGEXP % ('submitted_on', 'datetime', 'str')
CHANGED_BY_NONE_ERROR = TYPE_ERROR_REGEXP % ('changed_by', 'Identity', 'NoneType')
CHANGED_BY_STR_ERROR = TYPE_ERROR_REGEXP % ('changed_by', 'Identity', 'str')
CHANGED_ON_NONE_ERROR = TYPE_ERROR_REGEXP % ('changed_on', 'datetime', 'NoneType')
CHANGED_ON_STR_ERROR = TYPE_ERROR_REGEXP % ('changed_on', 'datetime', 'str')


class TestIdentity(unittest.TestCase):

    def test_simple_identity(self):
        identity = Identity('john_smith')
        self.assertEqual('john_smith', identity.user_id)
        self.assertEqual(None, identity.name)
        self.assertEqual(None, identity.email)

    def test_identity(self):
        identity = Identity('john_smith', 'John Smith', 'jsmith@example.com')
        self.assertEqual('john_smith', identity.user_id)
        self.assertEqual('John Smith', identity.name)
        self.assertEqual('jsmith@example.com', identity.email)


class TestTracker(unittest.TestCase):

    def setUp(self):
        self.tracker = Tracker('http://tracker.example.com', 'test', 'v1.0')

    def test_tracker(self): 
        self.assertEqual('http://tracker.example.com', self.tracker.url)
        self.assertEqual('test', self.tracker.name)
        self.assertEqual('v1.0', self.tracker.version)

    def test_readonly_properties(self):
        self.assertRaises(AttributeError, setattr, self.tracker, 'url', '')
        self.assertEqual('http://tracker.example.com', self.tracker.url)

        self.assertRaises(AttributeError, setattr, self.tracker, 'name', 'tracker')
        self.assertEqual('test', self.tracker.name)

        self.assertRaises(AttributeError, setattr, self.tracker, 'version', 'v2.0')
        self.assertEqual('v1.0', self.tracker.version)


class TestIssue(unittest.TestCase):

    def setUp(self):
        self.issue = Issue('1', 'bug', 'issue unit test',
                           'unit test for issue class',
                           JOHN_SMITH, MOCK_DATETIME,
                           'closed', 'fixed', 'high',
                           JOHN_DOE)

    def test_issue(self):
        self.assertEqual('1', self.issue.issue_id)
        self.assertEqual('bug', self.issue.issue_type)
        self.assertEqual('issue unit test', self.issue.summary)
        self.assertEqual( 'unit test for issue class', self.issue.description)
        self.assertEqual(JOHN_SMITH, self.issue.submitted_by)
        self.assertEqual(MOCK_DATETIME, self.issue.submitted_on)
        self.assertEqual('closed', self.issue.status)
        self.assertEqual('fixed', self.issue.resolution)
        self.assertEqual('high', self.issue.priority)
        self.assertEqual(JOHN_DOE, self.issue.assigned_to)
        self.assertListEqual([], self.issue.comments)
        self.assertListEqual([], self.issue.attachments)
        self.assertListEqual([], self.issue.changes)
        self.assertListEqual([], self.issue.watchers)

    def test_readonly_properties(self):
        self.assertRaises(AttributeError, setattr, self.issue, 'submitted_by', JANE_ROE)
        self.assertEqual(JOHN_SMITH, self.issue.submitted_by)

        self.assertRaises(AttributeError, setattr, self.issue, 'submitted_on', datetime.datetime.utcnow())
        self.assertEqual(MOCK_DATETIME, self.issue.submitted_on)

        self.assertRaises(AttributeError, setattr, self.issue, 'comments', '')
        self.assertListEqual([], self.issue.comments)

        self.assertRaises(AttributeError, setattr, self.issue, 'attachments', '')
        self.assertListEqual([], self.issue.attachments)

        self.assertRaises(AttributeError, setattr, self.issue, 'changes', '')
        self.assertListEqual([], self.issue.changes)

        self.assertRaises(AttributeError, setattr, self.issue, 'watchers', '')
        self.assertListEqual([], self.issue.watchers)

    def test_assigned_to(self):
        self.assertRaises(TypeError, setattr, self.issue, 'assigned_to', 'John Doe')
        self.assertEqual(JOHN_SMITH, self.issue.submitted_by)

        self.issue.assigned_to = None
        self.assertEqual(None, self.issue.assigned_to)
        self.issue.assigned_to = JANE_ROE
        self.assertEqual(JANE_ROE, self.issue.assigned_to)

    def test_comments(self):
        c1 = Comment('Comment #1', JOHN_SMITH, datetime.datetime.utcnow())
        c2 = Comment('Comment #2', JOHN_DOE, datetime.datetime.utcnow())
        c3 = Comment('Comment #3', JANE_ROE, datetime.datetime.utcnow())

        self.issue.add_comment(c1)
        self.issue.add_comment(c2)
        self.issue.add_comment(c3)
        self.issue.add_comment(c2)
        self.issue.add_comment(c3)
        self.issue.add_comment(c1)

        self.assertListEqual([c1, c2, c3, c2, c3, c1], self.issue.comments)
        self.assertRaises(TypeError, self.issue.add_comment, comment='')
        self.assertListEqual([c1, c2, c3, c2, c3, c1], self.issue.comments)

    def test_attachments(self):
        a1 = Attachment('file1')
        a2 = Attachment('file2', submitted_by=JOHN_DOE)

        self.issue.add_attachment(a2)
        self.issue.add_attachment(a1)
        self.issue.add_attachment(a2)
        self.issue.add_attachment(a2)
        self.issue.add_attachment(a1)

        self.assertListEqual([a2, a1, a2, a2, a1], self.issue.attachments)
        self.assertRaises(TypeError, self.issue.add_attachment, attachment=JOHN_SMITH)
        self.assertListEqual([a2, a1, a2, a2, a1], self.issue.attachments)

    def test_changes(self):
        ch1 = Change('status', 'open', 'assigned', JOHN_SMITH, datetime.datetime.utcnow())
        ch2 = Change('status', 'assigned', 'closed', JOHN_SMITH, datetime.datetime.utcnow())
        ch3 = Change('resolution', '---', 'fixed', JANE_ROE, datetime.datetime.utcnow())

        self.issue.add_change(ch1)
        self.issue.add_change(ch1)
        self.issue.add_change(ch2)
        self.issue.add_change(ch2)
        self.issue.add_change(ch1)
        self.issue.add_change(ch3)
        self.issue.add_change(ch2)

        self.assertListEqual([ch1, ch1, ch2, ch2, ch1, ch3, ch2], self.issue.changes)
        self.assertRaises(TypeError, self.issue.add_change, change=10)
        self.assertListEqual([ch1, ch1, ch2, ch2, ch1, ch3, ch2], self.issue.changes)

    def test_watchers(self):
        w1 = JOHN_DOE
        w2 = JANE_ROE
        w3 = JOHN_SMITH

        self.issue.add_watcher(w2)
        self.issue.add_watcher(w3)
        self.issue.add_watcher(w1)
        self.issue.add_watcher(w2)
        self.issue.add_watcher(w1)

        self.assertListEqual([w2, w3, w1, w2, w1], self.issue.watchers)
        self.assertRaises(TypeError, self.issue.add_watcher, watcher='John Doe')
        self.assertListEqual([w2, w3, w1, w2, w1], self.issue.watchers)

    def test_invalid_init(self):
        self.assertRaisesRegexp(TypeError, SUBMITTED_BY_NONE_ERROR,
                                Issue, issue_id='1', issue_type='bug',
                                summary='issue unit test',
                                description='unit test for issue class',
                                submitted_by=None, submitted_on=None)
        self.assertRaisesRegexp(TypeError, SUBMITTED_BY_STR_ERROR,
                                Issue, issue_id='1', issue_type='bug',
                                summary='issue unit test',
                                description='unit test for issue class',
                                submitted_by='John Doe', submitted_on=None)
        self.assertRaisesRegexp(TypeError, SUBMITTED_ON_NONE_ERROR,
                                Issue, issue_id='1', issue_type='bug',
                                summary='issue unit test',
                                description='unit test for issue class',
                                submitted_by=JANE_ROE, submitted_on=None)
        self.assertRaisesRegexp(TypeError, SUBMITTED_ON_STR_ERROR,
                                Issue, issue_id='1', issue_type='bug',
                                summary='issue unit test',
                                description='unit test for issue class',
                                submitted_by=JANE_ROE, submitted_on=MOCK_DATETIME_STR)


class TestComment(unittest.TestCase):

    def setUp(self):
        self.comment = Comment('A comment text', JOHN_SMITH, MOCK_DATETIME)

    def test_comment(self):
        self.assertEqual('A comment text', self.comment.text)
        self.assertEqual(JOHN_SMITH, self.comment.submitted_by)
        self.assertEqual(MOCK_DATETIME, self.comment.submitted_on)

    def test_readonly_properties(self):
        self.assertRaises(AttributeError, setattr, self.comment, 'text', '')
        self.assertEqual('A comment text', self.comment.text)

        self.assertRaises(AttributeError, setattr, self.comment, 'submitted_by', JOHN_DOE)
        self.assertEqual(JOHN_SMITH, self.comment.submitted_by)

        self.assertRaises(AttributeError, setattr, self.comment, 'submitted_on', datetime.datetime.utcnow())
        self.assertEqual(MOCK_DATETIME, self.comment.submitted_on)

    def test_invalid_init(self):
        self.assertRaisesRegexp(TypeError, SUBMITTED_BY_NONE_ERROR,
                                Comment, text='A comment text',
                                submitted_by=None, submitted_on=None)
        self.assertRaisesRegexp(TypeError, SUBMITTED_BY_STR_ERROR,
                                Comment, text='A comment text',
                                submitted_by='John Doe', submitted_on=None)
        self.assertRaisesRegexp(TypeError, SUBMITTED_ON_NONE_ERROR,
                                Comment, text='A comment text',
                                submitted_by=JOHN_SMITH, submitted_on=None)
        self.assertRaisesRegexp(TypeError, SUBMITTED_ON_STR_ERROR,
                                Comment, text='A comment text',
                                submitted_by=JOHN_SMITH, submitted_on=MOCK_DATETIME_STR)


class TestAttachment(unittest.TestCase):

    def setUp(self):
        self.attachment = Attachment('attachment', 'http://example.com/file',
                                     'An attachment', JOHN_SMITH, MOCK_DATETIME)

    def test_simple_attachment(self):
        attachment = Attachment('attachment')
        self.assertEqual('attachment', attachment.name)
        self.assertEqual(None, attachment.url)
        self.assertEqual(None, attachment.description)
        self.assertEqual(None, attachment.submitted_by)
        self.assertEqual(None, attachment.submitted_on)

    def test_attachment(self):
        self.assertEqual('attachment', self.attachment.name)
        self.assertEqual('http://example.com/file', self.attachment.url)
        self.assertEqual('An attachment', self.attachment.description)
        self.assertEqual(JOHN_SMITH, self.attachment.submitted_by)
        self.assertEqual(MOCK_DATETIME, self.attachment.submitted_on)

    def test_submitted_by(self):
        self.assertRaises(TypeError, setattr, self.attachment, 'submitted_by', 'John Doe')
        self.assertEqual(JOHN_SMITH, self.attachment.submitted_by)

        self.attachment.submitted_by = None
        self.assertEqual(None, self.attachment.submitted_by)
        self.attachment.submitted_by = JOHN_DOE
        self.assertEqual(JOHN_DOE, self.attachment.submitted_by)

    def test_submitted_on(self):
        self.assertRaises(TypeError, setattr, self.attachment, 'submitted_on', MOCK_DATETIME_STR)
        self.assertEqual(MOCK_DATETIME, self.attachment.submitted_on)

        self.attachment.submitted_on = None
        self.assertEqual(None, self.attachment.submitted_on)

        test_dt = datetime.datetime.utcnow()
        self.attachment.submitted_on = test_dt
        self.assertEqual(test_dt, self.attachment.submitted_on)

    def test_invalid_init(self):
        self.assertRaisesRegexp(TypeError, SUBMITTED_BY_STR_ERROR,
                                Attachment, name='attachment',
                                url='http://example.com/file',
                                description='an attachment',
                                submitted_by='John Doe', submitted_on=None)
        self.assertRaisesRegexp(TypeError, SUBMITTED_ON_STR_ERROR,
                                Attachment, name='attachment',
                                url='http://example.com/file',
                                description='an attachment',
                                submitted_by=None, submitted_on=MOCK_DATETIME_STR)


class TestChange(unittest.TestCase):

    def setUp(self):
        self.change = Change('status', 'open', 'closed', JOHN_SMITH, MOCK_DATETIME)

    def test_change(self):
        self.assertEqual('status', self.change.field)
        self.assertEqual('open', self.change.old_value)
        self.assertEqual('closed', self.change.new_value)
        self.assertEqual(JOHN_SMITH, self.change.changed_by)
        self.assertEqual(MOCK_DATETIME, self.change.changed_on)

    def test_readonly_properties(self):
        self.assertRaises(AttributeError, setattr, self.change, 'field', 'priority')
        self.assertEqual('status', self.change.field)

        self.assertRaises(AttributeError, setattr, self.change, 'old_value', 'high')
        self.assertEqual('open', self.change.old_value)

        self.assertRaises(AttributeError, setattr, self.change, 'new_value', 'low')
        self.assertEqual('closed', self.change.new_value)

        self.assertRaises(AttributeError, setattr, self.change, 'changed_by', JOHN_DOE)
        self.assertEqual(JOHN_SMITH, self.change.changed_by)

        self.assertRaises(AttributeError, setattr, self.change, 'changed_on', datetime.datetime.utcnow())
        self.assertEqual(MOCK_DATETIME, self.change.changed_on)

    def test_invalid_init(self):
        self.assertRaisesRegexp(TypeError, CHANGED_BY_NONE_ERROR,
                                Change, field='status', old_value='open', new_value='closed',
                                changed_by=None, changed_on=None)
        self.assertRaisesRegexp(TypeError, CHANGED_BY_STR_ERROR,
                                Change, field='status', old_value='open', new_value='closed',
                                changed_by='John Doe', changed_on=None)
        self.assertRaisesRegexp(TypeError, CHANGED_ON_NONE_ERROR,
                                Change, field='status', old_value='open', new_value='closed',
                                changed_by=JOHN_SMITH, changed_on=None)
        self.assertRaisesRegexp(TypeError, CHANGED_ON_STR_ERROR,
                                Change, field='status', old_value='open', new_value='closed',
                                changed_by=JOHN_SMITH, changed_on=MOCK_DATETIME_STR)


if __name__ == "__main__":
    unittest.main()
