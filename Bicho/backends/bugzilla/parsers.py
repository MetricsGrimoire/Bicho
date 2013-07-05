# -*- coding: utf-8 -*-
#
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

"""
Parsers for Bugzilla tracker.
"""

import dateutil.parser

from Bicho.backends.parsers import UnmarshallingError, XMLParser
from Bicho.backends.bugzilla.model import BugzillaMetadata, BugzillaIssue, BugzillaAttachment
from Bicho.common import Identity, Comment


# Tokens
ALIAS_TOKEN = 'alias'
ATTACHMENT_TOKEN = 'attachment'
BUG_TOKEN = 'bug'
BUG_FILE_LOC_TOKEN = 'bug_file_loc'
CC_TOKEN = 'cc'
DEADLINE_TOKEN = 'deadline'
DELTA_TS_TOKEN = 'delta_ts'
DUP_ID_TOKEN = 'dup_id'
EVERCONFIRMED_TOKEN = 'everconfirmed'
ESTIMATED_TIME_TOKEN = 'estimated_time'
EXPORTER_TOKEN = 'exporter'
IS_PATCH_TOKEN = 'ispatch'
IS_OBSOLETE_TOKEN = 'isobsolete'
LONG_DESC_TOKEN = 'long_desc'
MAINTAINER_TOKEN = 'maintainer'
NAME_TOKEN = 'name'
NO_VALUE_TOKEN = '---'
QA_CONTACT_TOKEN = 'qa_contact'
STATUS_WHITEBOARD_TOKEN = 'status_whiteboard'
TARGET_MILESTONE_TOKEN = 'target_milestone'
URLBASE_TOKEN = 'urlbase'
VERSION_TOKEN = 'version'
VOTES_TOKEN = 'votes'


class BugzillaMetadataParser(XMLParser):
    """XML parser for parsing Bugzilla metadata"""

    def __init__(self, xml):
        XMLParser.__init__(self, xml)

    @property
    def metadata(self):
        return self._unmarshal()

    def _unmarshal(self):
        return BugzillaMetadata(self._data.get(VERSION_TOKEN),
                                self._data.get(URLBASE_TOKEN),
                                self._data.get(MAINTAINER_TOKEN),
                                self._data.get(EXPORTER_TOKEN))


class BugzillaIssuesParser(XMLParser):
    """XML handler for parsing Bugzilla issues

    ..TODO: timezones, URL attachment, issue type
    """
    BG_OPTIONAL_FIELDS = [ALIAS_TOKEN, BUG_FILE_LOC_TOKEN,
                          DUP_ID_TOKEN, EVERCONFIRMED_TOKEN,
                          STATUS_WHITEBOARD_TOKEN,
                          TARGET_MILESTONE_TOKEN, VOTES_TOKEN]

    def __init__(self, xml):
        XMLParser.__init__(self, xml)

    @property
    def issues(self):
        return self._unmarshal()

    def _unmarshal(self):
        bg_issues = self._data.iterchildren(tag=BUG_TOKEN)
        return [self._unmarshal_issue(bg_issue)
                for bg_issue in bg_issues]

    def _unmarshal_issue(self, bg_issue):
        try:
            # Unmarshal common tags
            issue_id = self._unmarshal_str(bg_issue.bug_id)
            issue_type = None
            summary = self._unmarshal_str(bg_issue.short_desc)
            submitted_by = self._unmarshal_identity(bg_issue.reporter)
            submitted_on = self._unmarshal_timestamp(bg_issue.creation_ts)
            status = self._unmarshal_str(bg_issue.bug_status)
            resolution = self._unmarshal_str(bg_issue.resolution, True)
            priority = self._unmarshal_str(bg_issue.priority)
            assigned_to = self._unmarshal_identity(bg_issue.assigned_to)

            # Unmarshal comments
            comments = self._unmarshal_issue_comments(bg_issue)

            # In Bugzilla, the first comment is the description
            # of the bug
            if len(comments) > 0:
                desc = comments.pop(0).text
            else:
                desc = None

            # Unmarshal attachments
            attachments = self._unmarshal_issue_attachments(bg_issue)
            # Unmarshal watchers
            watchers = self._unmarshal_issue_watchers(bg_issue)

            # Create issue instance
            issue = BugzillaIssue(issue_id, issue_type, summary, desc,
                                  submitted_by, submitted_on, status,
                                  resolution, priority, assigned_to)
            for comment in comments:
                issue.add_comment(comment)
            for attachment in attachments:
                issue.add_attachment(attachment)
            for watcher in watchers:
                issue.add_watcher(watcher)
            self._unmarshal_issue_custom_tags(bg_issue, issue)

            return issue
        except AttributeError, e:
            raise UnmarshallingError('BugzillaIssue', e)

    def _unmarshal_issue_custom_tags(self, bg_issue, issue):
        # Unmarshal required tags
        try:
            issue.classification_id = self._unmarshal_str(bg_issue.classification_id)
            issue.classification = self._unmarshal_str(bg_issue.classification)
            issue.product = self._unmarshal_str(bg_issue.product)
            issue.component = self._unmarshal_str(bg_issue.component)
            issue.version = self._unmarshal_str(bg_issue.version)
            issue.platform = self._unmarshal_str(bg_issue.rep_platform)
            issue.op_sys = self._unmarshal_str(bg_issue.op_sys)
            issue.cclist_accessible = self._unmarshal_str(bg_issue.cclist_accessible)
            issue.delta_ts = self._unmarshal_timestamp(bg_issue.delta_ts)
            issue.reporter_accessible = self._unmarshal_str(bg_issue.reporter_accessible)
        except AttributeError, e:
            raise UnmarshallingError('BugzillaIssue', e)

        # Unmarshal optional tags
        for field in BugzillaIssuesParser.BG_OPTIONAL_FIELDS:
            if hasattr(bg_issue, field):
                value = self._unmarshal_str(getattr(bg_issue, field), True)
                setattr(issue, field, value)

        if hasattr(bg_issue, QA_CONTACT_TOKEN):
            issue.qa_contact = self._unmarshal_identity(bg_issue.qa_contact)

        if hasattr(bg_issue, ESTIMATED_TIME_TOKEN):
            # If estimated_time tag is set, remaining_time and actual_time
            # have to be set, too.
            try:
                issue.estimated_time = self._unmarshal_timestamp(bg_issue.estimated_time)
                issue.remaining_time = self._unmarshal_timestamp(bg_issue.remaining_time)
                issue.actual_time = self._unmarshal_timestamp(bg_issue.actual_time)
            except AttributeError, e:
                raise UnmarshallingError('BugzillaIssue', e)

        if hasattr(bg_issue, DEADLINE_TOKEN):
            issue.deadline = self._unmarshal_timestamp(bg_issue.deadline)

    def _unmarshal_issue_comments(self, bg_issue):
        bg_comments = bg_issue.iterchildren(tag=LONG_DESC_TOKEN)
        return [self._unmarshal_comment(bg_comment)
                for bg_comment in bg_comments]

    def _unmarshal_comment(self, bg_comment):
        try:
            text = self._unmarshal_str(bg_comment.thetext)
            submitted_by = self._unmarshal_identity(bg_comment.who)
            submitted_on = self._unmarshal_timestamp(bg_comment.bug_when)
            return Comment(text, submitted_by, submitted_on)
        except AttributeError, e:
            raise UnmarshallingError('Comment', e)

    def _unmarshal_issue_attachments(self, bg_issue):
        bg_attachments = bg_issue.iterchildren(tag=ATTACHMENT_TOKEN)
        return [self._unmarshal_attachment(bg_attachment)
                for bg_attachment in bg_attachments]

    def _unmarshal_attachment(self, bg_attachment):
        try:
            name = self._unmarshal_str(bg_attachment.filename)
            desc = self._unmarshal_str(bg_attachment.desc)
            submitted_by = self._unmarshal_identity(bg_attachment.attacher)
            submitted_on = self._unmarshal_timestamp(bg_attachment.date)
            filetype = self._unmarshal_str(bg_attachment.type)
            size = self._unmarshal_str(bg_attachment.size)
            is_patch = self._unmarshal_bool(bg_attachment.get(IS_PATCH_TOKEN))
            is_obsolete = self._unmarshal_bool(bg_attachment.get(IS_OBSOLETE_TOKEN))

            # delta_ts is not required in some Bugzilla trackers
            if hasattr(bg_attachment, DELTA_TS_TOKEN):
                delta_ts = self._unmarshal_timestamp(bg_attachment.delta_ts)
            else:
                delta_ts = None

            return BugzillaAttachment(name, None, desc,
                                      submitted_by, submitted_on,
                                      filetype, size, delta_ts,
                                      is_patch, is_obsolete)
        except AttributeError, e:
            raise UnmarshallingError('BugzillaAttachment', e)

    def _unmarshal_issue_watchers(self, bg_issue):
        bg_watchers = bg_issue.iterchildren(tag=CC_TOKEN)
        return [self._unmarshal_watcher(bg_watcher)
                for bg_watcher in bg_watchers]

    def _unmarshal_watcher(self, bg_watcher):
        return self._unmarshal_identity(bg_watcher)

    def _unmarshal_str(self, s, not_empty=False):
        if s is None:
            return None
        elif s == NO_VALUE_TOKEN:
            return None
        elif not_empty and s == u'':
            return None
        return unicode(s)

    def _unmarshal_bool(self, b):
        if b == '0':
            return False
        elif b == '1':
            return True
        else:
            raise UnmarshallingError('bool',
                                     cause='Value should be either 0 or 1. %s provided' % str(b))

    def _unmarshal_identity(self, bg_id):
        try:
            user_id = self._unmarshal_str(bg_id)
            if '@' in user_id:
                user_id = user_id.split('@')[0]
                email = self._unmarshal_str(bg_id)
            else:
                email = None

            name = self._unmarshal_str(bg_id.get(NAME_TOKEN))

            return Identity(user_id, name, email)
        except Exception, e:
            raise UnmarshallingError('Identity', e)

    def _unmarshal_timestamp(self, bg_ts):
        try:
            str_ts = self._unmarshal_str(bg_ts)
            return dateutil.parser.parse(str_ts).replace(tzinfo=None)
        except Exception, e:
            raise UnmarshallingError('datetime', e)
