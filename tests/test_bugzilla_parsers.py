# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Bitergia
# Copyright (C) 2007-2013 GSyC/LibreSoft, Universidad Rey Juan Carlos
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
import os.path
import sys
import unittest

if not '..' in sys.path:
    sys.path.insert(0, '..')

from bicho.common import IssueSummary
from bicho.exceptions import UnmarshallingError
from bicho.backends.bugzilla.model import BG_RELATIONSHIP_BLOCKED, BG_RELATIONSHIP_DEPENDS_ON,\
    BugzillaMetadata, BugzillaIssue
from bicho.backends.bugzilla.parsers import BugzillaMetadataParser, BugzillaIssuesSummaryParser,\
    BugzillaIssuesParser, BugzillaChangesParser
from utilities import read_file


# Name of directory where the test input files are stored
TEST_FILES_DIRNAME = 'bugzilla_data'

# Test files
METADATA_FILE = 'metadata.xml'
METADATA_EMPTY_FILE = 'metadata_empty.xml'
SUMMARY_FILE = 'summary.csv'
SUMMARY_NO_BUG_ID_HEADER = 'summary_no_bug_id_header.csv'
SUMMARY_NO_CHANGED_ON_HEADER = 'summary_no_changed_on_header.csv'
SUMMARY_NO_BUG_ID_VALUE = 'summary_no_bug_id_value.csv'
SUMMARY_NO_CHANGED_ON_VALUE = 'summary_no_bug_id_value.csv'
SUMMARY_INVALID_CHANGED_ON = 'summary_invalid_changed_on.csv'
SUMMARY_SET1 = 'summary_solid_1394.csv'
SUMMARY_SET2 = 'summary_evince_7556.csv'
SUMMARY_SET3 = 'summary_firefox_10000.csv'
ISSUE_AUTH_FILE = 'issue_auth.xml'
ISSUE_NO_AUTH_FILE = 'issue_no_auth.xml'
ISSUE_EMPTY_FILE = 'issue_empty.xml'
ISSUE_NO_VALUE_TAGS_FILE = 'issue_no_value_tags.xml'
ISSUE_INVALID_DATE_FILE = 'issue_invalid_date.xml'
ISSUE_INVALID_COMMENT_FILE = 'issue_invalid_comment.xml'
ISSUE_NO_COMMENTS_FILE = 'issue_no_comments.xml'
ISSUE_INVALID_ATTACHMENT_FILE = 'issue_invalid_attachment.xml'
ISSUE_INVALID_ATTACHMENT_BOOL_FILE = 'issue_invalid_attachment_bool.xml'
ISSUE_NO_ATTACHMENTS_FILE = 'issue_no_attachments.xml'
ISSUE_NO_QA_CONTACT = 'issue_no_qa_contact.xml'
ISSUE_NO_WATCHERS_FILE = 'issue_no_watchers.xml'
ISSUE_NO_RELATIONSHIPS_FILE = 'issue_no_relationships.xml'
ISSUES_100 = 'issues_evince_100.xml'
ISSUES_250 = 'issues_firefox_250.xml'
ISSUES_500 = 'issues_solid_500.xml'
CHANGES_NO_AUTH_FILE = 'changes_no_auth.html'
CHANGES_AUTH_FILE = 'changes_auth.html'
CHANGES_EMPTY_FILE = 'changes_empty.html'

# RegExps for testing TypeError exceptions
UNMARSHALLING_ERROR_REGEXP = 'error unmarshalling object to %s.+%s'
BUG_ID_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('IssueSummary', 'bug_id')
CHANGED_ON_KEY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('IssueSummary', 'changeddate')
CHANGED_ON_INVALID_ERROR = UNMARSHALLING_ERROR_REGEXP % ('datetime', 'unknown string format')
STR_EMPTY_ERROR = UNMARSHALLING_ERROR_REGEXP % ('str', 'string cannot be None or empty')
DATETIME_MONTH_ERROR = UNMARSHALLING_ERROR_REGEXP % ('datetime', 'month must be in 1..12')
COMMENT_WHO_ERROR = UNMARSHALLING_ERROR_REGEXP % ('Comment', 'no such child: who.')
ATTACHMENT_FILENAME_ERROR = UNMARSHALLING_ERROR_REGEXP % ('BugzillaAttachment', 'no such child: filename.')
ATTACHMENT_BOOL_ERROR = UNMARSHALLING_ERROR_REGEXP % ('bool', 'Value should be either 0 or 1.')


class TestBugzillaMetadataParser(unittest.TestCase):

    def test_xml_valid_metadata(self):
        # Test whether the handler parses correctly
        # a Bugzilla metadata XML stream
        filepath = os.path.join(TEST_FILES_DIRNAME, METADATA_FILE)
        xml = read_file(filepath)
        parser = BugzillaMetadataParser(xml)
        parser.parse()

        metadata = parser.metadata
        self.assertIsInstance(metadata, BugzillaMetadata)
        self.assertEqual(u'4.2.1', metadata.version)
        self.assertEqual(u'https://bugzilla.example.com/', metadata.urlbase)
        self.assertEqual(u'sysadmin@example.com', metadata.maintainer)
        self.assertEqual(None, metadata.exporter)

    def test_xml_empty_metadata(self):
        # Test whether the handler parses correctly
        # an empty Bugzilla metadata XML stream
        filepath = os.path.join(TEST_FILES_DIRNAME, METADATA_EMPTY_FILE)
        xml = read_file(filepath)
        parser = BugzillaMetadataParser(xml)
        parser.parse()

        metadata = parser.metadata
        self.assertIsInstance(metadata, BugzillaMetadata)
        self.assertEqual(None, metadata.version)
        self.assertEqual(None, metadata.urlbase)
        self.assertEqual(None, metadata.maintainer)
        self.assertEqual(None, metadata.exporter)


class TestBugzillaIssuesSummaryParser(unittest.TestCase):

    def setUp(self):
        self.parser = None

    def test_summary_set(self):
        # Test if there is no fail parsing a summary set
        summaries = self._parse(SUMMARY_FILE)
        self.assertEqual(5, len(summaries))

        summary = summaries[0]
        self.assertIsInstance(summary, IssueSummary)
        self.assertEqual('3', summary.issue_id)
        self.assertEqual(u'2009-07-01 12:16:03', unicode(summary.changed_on))

        summary = summaries[1]
        self.assertIsInstance(summary, IssueSummary)
        self.assertEqual('9', summary.issue_id)
        self.assertEqual(u'2009-07-01 13:45:31', unicode(summary.changed_on))

        summary = summaries[2]
        self.assertIsInstance(summary, IssueSummary)
        self.assertEqual('13', summary.issue_id)
        self.assertEqual(u'2009-07-02 13:40:35', unicode(summary.changed_on))

        summary = summaries[3]
        self.assertIsInstance(summary, IssueSummary)
        self.assertEqual('15', summary.issue_id)
        self.assertEqual(u'2009-07-22 15:27:25', unicode(summary.changed_on))

        summary = summaries[4]
        self.assertIsInstance(summary, IssueSummary)
        self.assertEqual('18', summary.issue_id)
        self.assertEqual(u'2009-07-28 20:09:20', unicode(summary.changed_on))

    def test_no_value_headers(self):
        # Test if the parser fails when the required headers
        # are not present in the CSV stream
        self.assertRaisesRegexp(UnmarshallingError,
                                BUG_ID_KEY_ERROR,
                                self._parse,
                                filename=SUMMARY_NO_BUG_ID_HEADER)
        self.assertRaisesRegexp(UnmarshallingError,
                                CHANGED_ON_KEY_ERROR,
                                self._parse,
                                filename=SUMMARY_NO_CHANGED_ON_HEADER)

    def test_no_values(self):
        # Test if the parser fails when the required
        # values are not present
        self.assertRaisesRegexp(UnmarshallingError,
                                STR_EMPTY_ERROR,
                                self._parse,
                                filename=SUMMARY_NO_BUG_ID_VALUE)
        self.assertRaisesRegexp(UnmarshallingError,
                                STR_EMPTY_ERROR,
                                self._parse,
                                filename=SUMMARY_NO_CHANGED_ON_VALUE)

    def test_invalid_changed_on(self):
        # Test if the parser fails when an invalid date
        # is parsed from the CSV stream
        self.assertRaisesRegexp(UnmarshallingError,
                                CHANGED_ON_INVALID_ERROR,
                                self._parse,
                                filename=SUMMARY_INVALID_CHANGED_ON)

    def test_big_summary_sets(self):
        # Test the parser using several streams with large
        # amount of rows
        summaries = self._parse(SUMMARY_SET1)
        self.assertEqual(1394, len(summaries))

        # This test case only contains two columns: bug_id, changeddate
        summaries = self._parse(SUMMARY_SET2)
        self.assertEqual(7556, len(summaries))

        summaries = self._parse(SUMMARY_SET3)
        self.assertEqual(10000, len(summaries))

    def _parse(self, filename):
        """Generic method to parse changes on Bugzilla issues
        summary from a CSV stream

        :param filename: path of the file to parse
        :type filename: str
        :return: a set of issue summaries parsed from Bugzilla
        :rtype: list of BugzillaIssueSummary
        """
        filepath = os.path.join(TEST_FILES_DIRNAME, filename)
        csv = read_file(filepath)
        self.parser = BugzillaIssuesSummaryParser(csv)
        self.parser.parse()
        return self.parser.summary


class TestBugzillaIssuesParser(unittest.TestCase):
    # TODO: test time tracking fields

    def setUp(self):
        self.parser = None

    def test_common_data(self):
        # Test if there is no fail parsing issue common fields
        # to the rest of the trackers
        issues = self._parse(ISSUE_NO_AUTH_FILE)
        self.assertEqual(1, len(issues))

        issue = issues[0]
        self.assertIsInstance(issue, BugzillaIssue)

        self.assertEqual(u'355', issue.issue_id)
        self.assertEqual(None, issue.issue_type)
        self.assertEqual(u'Mock bug for testing purposes', issue.summary)
        self.assertEqual(u'Lorem ipsum dolor sit amet.', issue.description)
        self.assertEqual(u'RESOLVED', issue.status)
        self.assertEqual(u'FIXED', issue.resolution)
        self.assertEqual(u'high', issue.priority)

    def test_bugzilla_data(self):
        # Test if there is no fail parsing Bugzilla specific fields
        issue = self._parse(ISSUE_NO_AUTH_FILE)[0]
        self.assertEqual(u'1', issue.classification_id)
        self.assertEqual(u'Data Analysis Tools', issue.classification)
        self.assertEqual(u'Kesi-tester', issue.product)
        self.assertEqual(u'fake-component', issue.component)
        self.assertEqual(u'unspecified', issue.version)
        self.assertEqual(u'Macintosh', issue.platform)
        self.assertEqual(u'Mac OS', issue.op_sys)
        self.assertEqual(None, issue.alias)
        self.assertEqual(u'1', issue.bug_file_loc)
        self.assertEqual(u'1', issue.cclist_accessible)
        self.assertEqual(None, issue.dup_id)
        self.assertEqual(u'0', issue.everconfirmed)
        self.assertEqual(u'1', issue.reporter_accessible)
        self.assertEqual(u'0', issue.status_whiteboard)
        self.assertEqual(u'core', issue.target_milestone)
        self.assertEqual(None, issue.votes)
        self.assertEqual(u'2013-06-25 12:04:11', unicode(issue.delta_ts))
        self.assertEqual(None, issue.estimated_time)
        self.assertEqual(None, issue.remaining_time)
        self.assertEqual(None, issue.actual_time)
        self.assertEqual(None, issue.deadline)

    def test_no_issues(self):
        # Test if nothing is parsed from a stream that does not
        # contain bug tags
        issues = self._parse(ISSUE_EMPTY_FILE)
        self.assertListEqual([], issues)

    def test_no_value_tags(self):
        # We consider the default Bugzilla value '---', in a tag,
        # like None. In addition, tags with no content have to
        # be parsed as None.
        # Test whether this value is set to None in the test cases.
        issue = self._parse(ISSUE_NO_VALUE_TAGS_FILE)[0]
        self.assertEqual(None, issue.resolution)
        self.assertEqual(None, issue.target_milestone)
        self.assertEqual(None, issue.status_whiteboard)
        self.assertEqual(None, issue.bug_file_loc)
        self.assertEqual(None, issue.everconfirmed)

    def test_submitted_by(self):
        # Test whether the parsing process does not fail
        # retrieving submitter identity
        issue = self._parse(ISSUE_NO_AUTH_FILE)[0]
        submitter = issue.submitted_by
        self.assertEqual(u'sduenas', submitter.user_id)
        self.assertEqual(u'Santiago Dueñas', submitter.name)
        self.assertEqual(None, submitter.email)

    def test_submitted_on(self):
        # Test if the submission date is parsed
        issue = self._parse(ISSUE_NO_AUTH_FILE)[0]
        submitted_on = issue.submitted_on
        self.assertIsInstance(submitted_on, datetime.datetime)
        self.assertEqual(u'2013-06-25 11:49:00', unicode(submitted_on))

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
        issue = self._parse(ISSUE_NO_AUTH_FILE)[0]
        assigned_to = issue.assigned_to
        self.assertEqual(u'dizquierdo', assigned_to.user_id)
        self.assertEqual(u'Daniel Izquierdo Cortazar', assigned_to.name)
        self.assertEqual(None, assigned_to.email)

    def test_qa_contact(self):
        # Test whether the parsing process does not fail
        # retrieving QA contact identity
        issue = self._parse(ISSUE_NO_AUTH_FILE)[0]
        qa_contact = issue.qa_contact
        self.assertEqual(u'lcanas', qa_contact.user_id)
        self.assertEqual(u'Luis Cañas', qa_contact.name)
        self.assertEqual(None, qa_contact.email)

    def test_no_qa_contact(self):
        # Test if nothing is parsed from a stream
        # without QA contact tag
        issue = self._parse(ISSUE_NO_QA_CONTACT)[0]
        qa_contact = issue.qa_contact
        self.assertEqual(None, qa_contact)

    def test_comments(self):
        # Test the comments parsing process
        issue = self._parse(ISSUE_NO_AUTH_FILE)[0]
        comments = issue.comments
        self.assertEqual(3, len(comments))

        comment = comments[0]
        self.assertEqual(u'A mock patch for this bug', comment.text)
        self.assertEqual(u'sduenas', comment.submitted_by.user_id)
        self.assertEqual(u'Santiago Dueñas', comment.submitted_by.name)
        self.assertEqual(None, comment.submitted_by.email)
        self.assertEqual(u'2013-06-25 11:55:46', unicode(comment.submitted_on))

        comment = comments[1]
        self.assertEqual(u'Invalid patch', comment.text)
        self.assertEqual(u'dizquierdo', comment.submitted_by.user_id)
        self.assertEqual(u'Daniel Izquierdo', comment.submitted_by.name)
        self.assertEqual(None, comment.submitted_by.email)
        self.assertEqual(u'2013-06-25 11:57:23', unicode(comment.submitted_on))

        comment = comments[2]
        self.assertEqual(u'Bug fixed', comment.text)
        self.assertEqual(u'sduenas', comment.submitted_by.user_id)
        self.assertEqual(u'Santiago Dueñas', comment.submitted_by.name)
        self.assertEqual(None, comment.submitted_by.email)
        self.assertEqual(u'2013-06-25 11:59:07', unicode(comment.submitted_on))

    def test_invalid_comment(self):
        # Test if the parser raises an exception
        # parsing a comment not well formed
        self.assertRaisesRegexp(UnmarshallingError,
                                COMMENT_WHO_ERROR,
                                self._parse,
                                filename=ISSUE_INVALID_COMMENT_FILE)

    def test_no_comments(self):
        # Test if nothing is parsed from a stream
        # without comment tags
        issue = self._parse(ISSUE_NO_COMMENTS_FILE)[0]
        self.assertEqual(None, issue.description)
        self.assertEqual(0, len(issue.comments))

    def test_attachments(self):
        # Test the attachments parsing process
        issue = self._parse(ISSUE_NO_AUTH_FILE)[0]
        attachments = issue.attachments
        self.assertEqual(2, len(attachments))

        attachment = attachments[0]
        self.assertEqual(u'mock_patch.patch', attachment.name)
        self.assertEqual(None, attachment.url)
        self.assertEqual(u'Mock patch', attachment.description)
        self.assertEqual(u'sduenas', attachment.submitted_by.user_id)
        self.assertEqual(None, attachment.submitted_by.name)
        self.assertEqual(None, attachment.submitted_by.email)
        self.assertEqual(u'2013-06-25 11:55:00', unicode(attachment.submitted_on))
        self.assertEqual('text/plain', attachment.filetype)
        self.assertEqual('14', attachment.size)
        self.assertEqual(u'2013-06-25 11:57:23', unicode(attachment.delta_ts))
        self.assertEqual(True, attachment.is_patch)
        self.assertEqual(True, attachment.is_obsolete)

        attachment = attachments[1]
        self.assertEqual(u'invalid_patch.txt', attachment.name)
        self.assertEqual(None, attachment.url)
        self.assertEqual(u'Invalid patch', attachment.description)
        self.assertEqual(u'dizquierdo', attachment.submitted_by.user_id)
        self.assertEqual(None, attachment.submitted_by.name)
        self.assertEqual(None, attachment.submitted_by.email)
        self.assertEqual(u'2013-06-25 11:57:00', unicode(attachment.submitted_on))
        self.assertEqual('text/plain', attachment.filetype)
        self.assertEqual('8', attachment.size)
        self.assertEqual(u'2013-06-25 11:57:23', unicode(attachment.delta_ts))
        self.assertEqual(False, attachment.is_patch)
        self.assertEqual(False, attachment.is_obsolete)

    def test_invalid_attachment(self):
        # Test if the parser raises an exception
        # parsing an attachment not well formed
        self.assertRaisesRegexp(UnmarshallingError,
                                ATTACHMENT_FILENAME_ERROR,
                                self._parse,
                                filename=ISSUE_INVALID_ATTACHMENT_FILE)

    def test_invalid_attachment_bool_field(self):
        self.assertRaisesRegexp(UnmarshallingError,
                                ATTACHMENT_BOOL_ERROR,
                                self._parse,
                                filename=ISSUE_INVALID_ATTACHMENT_BOOL_FILE)

    def test_no_attachments(self):
        # Test if nothing is parsed from a stream
        # without attachment tags
        issue = self._parse(ISSUE_NO_ATTACHMENTS_FILE)[0]
        self.assertEqual(0, len(issue.attachments))

    def test_watchers(self):
        # Test the watchers parsing process
        issue = self._parse(ISSUE_NO_AUTH_FILE)[0]
        watchers = issue.watchers
        self.assertEqual(3, len(watchers))

        watcher = watchers[0]
        self.assertEqual(u'sduenas', watcher.user_id)
        self.assertEqual(None, watcher.name)
        self.assertEqual(None, watcher.email)

        watcher = watchers[1]
        self.assertEqual(u'dizquierdo', watcher.user_id)
        self.assertEqual(None, watcher.name)
        self.assertEqual(None, watcher.email)

        watcher = watchers[2]
        self.assertEqual(u'lcanas', watcher.user_id)
        self.assertEqual(None, watcher.name)
        self.assertEqual(None, watcher.email)

    def test_no_watchers(self):
        # Test if nothing is parsed from a stream
        # without watcher tags
        issue = self._parse(ISSUE_NO_WATCHERS_FILE)[0]
        self.assertEqual(0, len(issue.watchers))

    def test_relationships(self):
        # Test the relationships parsing process
        issue = self._parse(ISSUE_NO_AUTH_FILE)[0]
        relationships = issue.relationships
        self.assertEqual(4, len(relationships))

        relationship = relationships[0]
        self.assertEqual(BG_RELATIONSHIP_BLOCKED, relationship.rel_type)
        self.assertEqual('349', relationship.related_to)

        relationship = relationships[1]
        self.assertEqual(BG_RELATIONSHIP_BLOCKED, relationship.rel_type)
        self.assertEqual('354', relationship.related_to)

        relationship = relationships[2]
        self.assertEqual(BG_RELATIONSHIP_DEPENDS_ON, relationship.rel_type)
        self.assertEqual('348', relationship.related_to)

        relationship = relationships[3]
        self.assertEqual(BG_RELATIONSHIP_DEPENDS_ON, relationship.rel_type)
        self.assertEqual('350', relationship.related_to)

    def test_no_relationships(self):
        # Test if nothing is parsed from a stream
        # without relationships tags
        issue = self._parse(ISSUE_NO_RELATIONSHIPS_FILE)[0]
        self.assertEqual(0, len(issue.relationships))

    def test_auth_identities(self):
        # Test whether identities are parsed from a XML stream.
        # This XML was retrieved from a Bugzilla tracker
        # using authentication
        issue = self._parse(ISSUE_AUTH_FILE)[0]

        submitter = issue.submitted_by
        self.assertEqual(u'sduenas', submitter.user_id)
        self.assertEqual(u'Santiago Dueñas', submitter.name)
        self.assertEqual(u'sduenas@example.org', submitter.email)

        assigned_to = issue.assigned_to
        self.assertEqual(u'dizquierdo', assigned_to.user_id)
        self.assertEqual(u'Daniel Izquierdo Cortazar', assigned_to.name)
        self.assertEqual(u'dizquierdo@example.com', assigned_to.email)

        qa_contact = issue.qa_contact
        self.assertEqual(u'lcanas', qa_contact.user_id)
        self.assertEqual(u'Luis Cañas', qa_contact.name)
        self.assertEqual(u'lcanas@example.com', qa_contact.email)

        # Check comments identities
        comments = issue.comments

        comment = comments[0]
        self.assertEqual(u'sduenas', comment.submitted_by.user_id)
        self.assertEqual(u'Santiago Dueñas', comment.submitted_by.name)
        self.assertEqual(u'sduenas@example.org', comment.submitted_by.email)

        comment = comments[1]
        self.assertEqual(u'dizquierdo', comment.submitted_by.user_id)
        self.assertEqual(u'Daniel Izquierdo', comment.submitted_by.name)
        self.assertEqual(u'dizquierdo@example.com', comment.submitted_by.email)

        comment = comments[2]
        self.assertEqual(u'sduenas', comment.submitted_by.user_id)
        self.assertEqual(u'Santiago Dueñas', comment.submitted_by.name)
        self.assertEqual(u'sduenas@example.org', comment.submitted_by.email)

        # Check attachments identities
        attachments = issue.attachments

        attachment = attachments[0]
        self.assertEqual(u'sduenas', attachment.submitted_by.user_id)
        self.assertEqual(None, attachment.submitted_by.name)
        self.assertEqual(u'sduenas@example.org', attachment.submitted_by.email)

        attachment = attachments[1]
        self.assertEqual(u'dizquierdo', attachment.submitted_by.user_id)
        self.assertEqual(None, attachment.submitted_by.name)
        self.assertEqual(u'dizquierdo@example.com', attachment.submitted_by.email)

        # Check watchers
        watchers = issue.watchers

        watcher = watchers[0]
        self.assertEqual(u'sduenas', watcher.user_id)
        self.assertEqual(None, watcher.name)
        self.assertEqual(u'sduenas@example.org', watcher.email)

        watcher = watchers[1]
        self.assertEqual(u'dizquierdo', watcher.user_id)
        self.assertEqual(None, watcher.name)
        self.assertEqual(u'dizquierdo@example.com', watcher.email)

        watcher = watchers[2]
        self.assertEqual(u'lcanas', watcher.user_id)
        self.assertEqual(None, watcher.name)
        self.assertEqual(u'lcanas@example.com', watcher.email)

    def test_issues(self):
        # Test the parser using several streams with a different
        # number of issues
        issues = self._parse(ISSUES_100)
        self.assertEqual(100, len(issues))

        issues = self._parse(ISSUES_250)
        self.assertEqual(250, len(issues))

        issues = self._parse(ISSUES_500)
        self.assertEqual(500, len(issues))

    def _parse(self, filename):
        """Generic method to parse Bugzilla issues from a XML stream

        :param filename: path of the file to parse
        :type filename: str
        :return: a set of issues parsed from Bugzilla
        :rtype: list of BugzillaIssue
        """
        filepath = os.path.join(TEST_FILES_DIRNAME, filename)
        xml = read_file(filepath)
        self.parser = BugzillaIssuesParser(xml)
        self.parser.parse()
        return self.parser.issues


class TestBugzillaChangesParser(unittest.TestCase):

    def setUp(self):
        self.parser = None

    def test_changes(self):
        # Test whether there is no fail parsing the changes
        # from an issue
        changes = self._parse(CHANGES_NO_AUTH_FILE)
        self.assertEqual(14, len(changes))

        change = changes[0]
        self.assertEqual(u'sduenas', change.changed_by.user_id)
        self.assertEqual(None, change.changed_by.name)
        self.assertEqual(None, change.changed_by.email)
        self.assertEqual(u'2013-06-25 11:57:23', unicode(change.changed_on))
        self.assertEqual(u'Attachment #172 Attachment is obsolete', unicode(change.field))
        self.assertEqual(u'0', change.old_value)
        self.assertEqual(u'1', change.new_value)

        # Changes from #1 to #11 should have same values in 'changed_by'
        # and 'changed_on' attribs
        change = changes[3]
        self.assertEqual(u'sduenas', change.changed_by.user_id)
        self.assertEqual(None, change.changed_by.name)
        self.assertEqual(None, change.changed_by.email)
        self.assertEqual(u'2013-06-25 11:59:07', unicode(change.changed_on))
        self.assertEqual(u'CC', change.field)
        self.assertEqual(u'kesitesting', change.old_value)
        self.assertEqual(None, change.new_value)

        change = changes[4]
        self.assertEqual(u'sduenas', change.changed_by.user_id)
        self.assertEqual(None, change.changed_by.name)
        self.assertEqual(None, change.changed_by.email)
        self.assertEqual(u'2013-06-25 11:59:07', unicode(change.changed_on))
        self.assertEqual(u'Hardware', change.field)
        self.assertEqual(u'All', change.old_value)
        self.assertEqual(u'Macintosh', change.new_value)

        change = changes[10]
        self.assertEqual(u'sduenas', change.changed_by.user_id)
        self.assertEqual(None, change.changed_by.name)
        self.assertEqual(None, change.changed_by.email)
        self.assertEqual(u'2013-06-25 11:59:07', unicode(change.changed_on))
        self.assertEqual(u'Severity', change.field)
        self.assertEqual(u'normal', change.old_value)
        self.assertEqual(u'trivial', change.new_value)

        change = changes[12]
        self.assertEqual(u'dizquierdo', change.changed_by.user_id)
        self.assertEqual(None, change.changed_by.name)
        self.assertEqual(None, change.changed_by.email)
        self.assertEqual(u'2013-06-25 12:04:11', unicode(change.changed_on))
        self.assertEqual(u'Blocks', change.field)
        self.assertEqual(None, change.old_value)
        self.assertEqual(u'354 , 349', change.new_value)

    def test_no_values_tags(self):
        # We consider the default Bugzilla value '---', in a tag,
        # like None. In addition, tags with no content have to
        # be parsed as None.
        # Test whether this value is set to None in the test cases.
        changes = self._parse(CHANGES_NO_AUTH_FILE)

        change = changes[6]
        self.assertEqual(u'sduenas', change.changed_by.user_id)
        self.assertEqual(None, change.changed_by.name)
        self.assertEqual(None, change.changed_by.email)
        self.assertEqual(u'2013-06-25 11:59:07', unicode(change.changed_on))
        self.assertEqual(u'Depends on', change.field)
        self.assertEqual(u'350', change.old_value)
        self.assertEqual(None, change.new_value)

        change = changes[8]
        self.assertEqual(u'sduenas', change.changed_by.user_id)
        self.assertEqual(None, change.changed_by.name)
        self.assertEqual(None, change.changed_by.email)
        self.assertEqual(u'2013-06-25 11:59:07', unicode(change.changed_on))
        self.assertEqual(u'Resolution', change.field)
        self.assertEqual(None, change.old_value)
        self.assertEqual('FIXED', change.new_value)

        change = changes[13]
        self.assertEqual(u'dizquierdo', change.changed_by.user_id)
        self.assertEqual(None, change.changed_by.name)
        self.assertEqual(None, change.changed_by.email)
        self.assertEqual(u'2013-06-25 12:04:11', unicode(change.changed_on))
        self.assertEqual(u'Depends on', change.field)
        self.assertEqual(None, change.old_value)
        self.assertEqual(u'350', change.new_value)

    def test_identities_no_auth(self):
        # Test whether there is no fail parsing identities from
        # no auth streams
        changes = self._parse(CHANGES_NO_AUTH_FILE)

        change = changes[0]
        self.assertEqual(u'sduenas', change.changed_by.user_id)
        self.assertEqual(None, change.changed_by.name)
        self.assertEqual(None, change.changed_by.email)

        change = changes[1]
        self.assertEqual(u'sduenas', change.changed_by.user_id)
        self.assertEqual(None, change.changed_by.name)
        self.assertEqual(None, change.changed_by.email)

        change = changes[11]
        self.assertEqual(u'sduenas', change.changed_by.user_id)
        self.assertEqual(None, change.changed_by.name)
        self.assertEqual(None, change.changed_by.email)

        change = changes[12]
        self.assertEqual(u'dizquierdo', change.changed_by.user_id)
        self.assertEqual(None, change.changed_by.name)
        self.assertEqual(None, change.changed_by.email)

        change = changes[13]
        self.assertEqual(u'dizquierdo', change.changed_by.user_id)
        self.assertEqual(None, change.changed_by.name)
        self.assertEqual(None, change.changed_by.email)

    def test_identities_auth(self):
        # Test whether there is no fail parsing identities from
        # auth streams
        changes = self._parse(CHANGES_AUTH_FILE)

        change = changes[0]
        self.assertEqual(u'sduenas', change.changed_by.user_id)
        self.assertEqual(None, change.changed_by.name)
        self.assertEqual(u'sduenas@example.org', change.changed_by.email)

        change = changes[1]
        self.assertEqual(u'sduenas', change.changed_by.user_id)
        self.assertEqual(None, change.changed_by.name)
        self.assertEqual(u'sduenas@example.org', change.changed_by.email)

        change = changes[11]
        self.assertEqual(u'sduenas', change.changed_by.user_id)
        self.assertEqual(None, change.changed_by.name)
        self.assertEqual(u'sduenas@example.org', change.changed_by.email)

        change = changes[12]
        self.assertEqual(u'dizquierdo', change.changed_by.user_id)
        self.assertEqual(None, change.changed_by.name)
        self.assertEqual(u'dizquierdo@example.com', change.changed_by.email)

        change = changes[13]
        self.assertEqual(u'dizquierdo', change.changed_by.user_id)
        self.assertEqual(None, change.changed_by.name)
        self.assertEqual(u'dizquierdo@example.com', change.changed_by.email)

    def test_no_changes(self):
        # Test if nothing is parsed from a stream without a
        # table of changes
        changes = self._parse(CHANGES_EMPTY_FILE)
        self.assertEqual(0, len(changes))

    def _parse(self, filename):
        """Generic method to parse changes on Bugzilla issues
        from a HTML stream

        :param filename: path of the file to parse
        :type filename: str
        :return: a set of issues parsed from Bugzilla
        :rtype: list of Change
        """
        filepath = os.path.join(TEST_FILES_DIRNAME, filename)
        html = read_file(filepath)
        self.parser = BugzillaChangesParser(html)
        self.parser.parse()
        return self.parser.changes


if __name__ == '__main__':
    unittest.main()
