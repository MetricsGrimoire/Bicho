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
#         Santiago Dueñas <sduenas@bitergia.com>
#         Alvaro del Castillo <acs@bitergia.com>
#

"""
Parsers for Redmine tracker.
"""

import dateutil.parser

from bicho.common import IssueSummary, Comment, Change, IssueRelationship
from bicho.exceptions import UnmarshallingError
from bicho.backends.parsers import JSONParser
from bicho.backends.redmine.model import RDM_RELATIONSHIP_BLOCKED,\
    RDM_RELATIONSHIP_BLOCKS, RDM_RELATIONSHIP_RELATES,\
    RedmineIdentity, RedmineStatus, RedmineIssuesSummary, RedmineIssue, RedmineAttachment


# Tokens
ASSIGNED_TO_TOKEN = 'assigned_to'
BLOCKS_TOKEN = 'blocks'
DETAILS_TOKEN = 'details'
IS_CLOSED_TOKEN = 'is_closed'
IS_DEFAULT_TOKEN = 'is_default'
NEW_VALUE_TOKEN = 'new_value'
NOTES_TOKEN = 'notes'
OLD_VALUE_TOKEN = 'old_value'
RELATES_TOKEN = 'relates'


class RedmineBaseParser(JSONParser):
    """Redmine base parser.

    :param stream: JSON stream to parse
    :type stream: str
    """

    def __init__(self, stream):
        super(RedmineBaseParser, self).__init__(stream)

    def _unmarshal_timestamp(self, rdm_ts):
        """Unmarshal Redmine string dates.

        :param rdm_ts: Redmine date in string format.
        :type rdm_ts: str
        :returns: datetime.
        :rtype: datetime
        :raise UnmarshallinError: when the date is None, empty or an error
            occurs unmarshalling the gitven date.
        """
        if not rdm_ts:
            raise UnmarshallingError(instance='datetime',
                                     cause='rdm_ts cannot be None or empty')
        try:
            str_ts = self._unmarshal_str(rdm_ts)
            return dateutil.parser.parse(str_ts).replace(tzinfo=None)
        except Exception, e:
            raise UnmarshallingError(instance='datetime', cause=repr(e))

    def _unmarshal_str(self, rdm_str):
        """Unmarshal strings from Redmine.

        :param rdm_str: Redmine string to parse.
        :type rdm_str: str
        :returns: unicode string, None if the string is empty or None.
        :rtype: unicode
        """
        if rdm_str is None:
            return None
        elif rdm_str == u'':
            return None
        return unicode(rdm_str)


class RedmineIdentityParser(RedmineBaseParser):
    """JSON parser for parsing identities from Redmine.

    :param json: JSON stream containing identities
    :type json: str
    """

    def __init__(self, json):
        super(RedmineIdentityParser, self).__init__(json)

    @property
    def identity(self):
        return self._unmarshal()

    def _unmarshal(self):
        try:
            rdm_user = self._data.user
            return self._unmarshal_identity(rdm_user)
        except KeyError, e:
            raise UnmarshallingError(instance='RedmineIdentity', cause=repr(e))

    def _unmarshal_identity(self, rdm_user):
        try:
            user_id = self._unmarshal_str(rdm_user.id)
            mail = self._unmarshal_str(rdm_user.mail)
            login = self._unmarshal_str(rdm_user.login)
            created_on = self._unmarshal_timestamp(rdm_user.created_on)
            last_login_on = self._unmarshal_timestamp(rdm_user.last_login_on)

            # Unmarshal identity name
            firstname = rdm_user.firstname
            lastname = rdm_user.lastname
            name = self._unmarshal_name(firstname, lastname)

            return RedmineIdentity(user_id, name, mail, login,
                                   created_on, last_login_on)
        except KeyError, e:
            raise UnmarshallingError(instance='RedmineIdentity', cause=repr(e))

    def _unmarshal_name(self, firstname, lastname):
        name = self._unmarshal_str(firstname) + ' ' + self._unmarshal_str(lastname)
        return name


class RedmineStatusesParser(RedmineBaseParser):
    """JSON parser for parsing available statuses on Redmine.

    :param json: JSON stream with a list of statuses
    :type json: str
    """

    def __init__(self, json):
        super(RedmineStatusesParser, self).__init__(json)

    @property
    def statuses(self):
        return self._unmarshal()

    def _unmarshal(self):
        try:
            rdm_statuses = self._data.issue_statuses
            return [self._unmarshal_status(rdm_status)\
                    for rdm_status in rdm_statuses]
        except KeyError, e:
            raise UnmarshallingError(instance='list(RedmineStatus)', cause=repr(e))

    def _unmarshal_status(self, rdm_status):
        try:
            status_id = self._unmarshal_str(rdm_status.id)
            name = self._unmarshal_str(rdm_status.name)

            if IS_CLOSED_TOKEN in rdm_status:
                is_closed = rdm_status.is_closed
            else:
                is_closed = False

            if IS_DEFAULT_TOKEN in rdm_status:
                is_default = rdm_status.is_default
            else:
                is_default = False

            return RedmineStatus(status_id, name, is_closed, is_default)
        except KeyError, e:
            raise UnmarshallingError(instance='RedmineStatus', cause=repr(e))


class RedmineIssuesSummaryParser(RedmineBaseParser):
    """JSON parser for parsing a summary of issues.

    :param json: JSON stream with a list of issues
    :type json: str
    """

    def __init__(self, json):
        super(RedmineIssuesSummaryParser, self).__init__(json)

    @property
    def summary(self):
        return self._unmarshal()

    def _unmarshal(self):
        rdm_summary = self._data

        try:
            # Unmarshal metadata
            total_count = self._unmarshal_str(rdm_summary.total_count)
            offset = self._unmarshal_str(rdm_summary.offset)
            limit = self._unmarshal_str(rdm_summary.limit)

            # Unmarshal issues summary
            issues_summary = self._unmarshal_summary(rdm_summary.issues)

            # Create summary instance
            summary = RedmineIssuesSummary(total_count, offset, limit)

            for issue_summary in issues_summary:
                summary.add_summary(issue_summary)

            return summary
        except KeyError, e:
            raise UnmarshallingError(instance='RedmineIssuesSummary', cause=repr(e))

    def _unmarshal_summary(self, rdm_issues):
        return [self._unmarshal_issue_summary(rdm_issue)
                for rdm_issue in rdm_issues]

    def _unmarshal_issue_summary(self, rdm_issue):
        try:
            issue_id = self._unmarshal_str(rdm_issue.id)
            changed_on = self._unmarshal_timestamp(rdm_issue.updated_on)
            return IssueSummary(issue_id, changed_on)
        except KeyError, e:
            raise UnmarshallingError(instance='IssueSummary', cause=repr(e))


class RedmineIssueParser(RedmineBaseParser):
    """JSON parser for parsing a summary of issues.

    :param json: JSON stream containing a Redmine issue
    :type json: str

    ..TODO: timezones and custom defined tags
    ..FIXME: resolution value is set to status
    """

    def __init__(self, json):
        super(RedmineIssueParser, self).__init__(json)

    @property
    def issue(self):
        return self._unmarshal()

    def _unmarshal(self):
        try:
            rdm_issue = self._data.issue
            return self._unmarshal_issue(rdm_issue)
        except KeyError, e:
            raise UnmarshallingError(instance='RedmineIssue', cause=repr(e))

    def _unmarshal_issue(self, rdm_issue):
        try:
            # Unmarshal common fields
            issue_id = self._unmarshal_str(rdm_issue.id)
            issue_type = self._unmarshal_str(rdm_issue.tracker.name)
            summary = self._unmarshal_str(rdm_issue.subject)
            desc = self._unmarshal_str(rdm_issue.description)
            submitted_by = self._unmarshal_identity(rdm_issue.author)
            submitted_on = self._unmarshal_timestamp(rdm_issue.created_on)
            status = self._unmarshal_str(rdm_issue.status.name)
            resolution = status #FIXME
            priority = self._unmarshal_str(rdm_issue.priority.name)

            if ASSIGNED_TO_TOKEN in rdm_issue:
                assigned_to = self._unmarshal_identity(rdm_issue.assigned_to)
            else:
                assigned_to = None

            # Unmarshal comments, attachments, changes and relationships
            comments = self._unmarshal_issue_comments(rdm_issue.journals)
            attachments = self._unmarshal_issue_attachments(rdm_issue.attachments)
            changes = self._unmarshal_issue_changes(rdm_issue.journals)
            relationships = self._unmarshal_issue_relationships(rdm_issue.relations, issue_id)

            issue = RedmineIssue(issue_id, issue_type, summary, desc,
                                 submitted_by, submitted_on,
                                 status, resolution, priority,
                                 assigned_to)

            for comment in comments:
                issue.add_comment(comment)
            for attachment in attachments:
                issue.add_attachment(attachment)
            for change in changes:
                issue.add_change(change)
            for relation in relationships:
                issue.add_relationship(relation)
            self._unmarshal_issue_custom_tags(rdm_issue, issue)

            return issue
        except KeyError, e:
            raise UnmarshallingError(instance='RedmineIssue', cause=repr(e))

    def _unmarshal_issue_custom_tags(self, rdm_issue, issue):
        # Unmarshal required tags
        try:
            issue.project_id = self._unmarshal_str(rdm_issue.project.id)
            issue.project = self._unmarshal_str(rdm_issue.project.name)
            issue.rdm_tracker_id = self._unmarshal_str(rdm_issue.tracker.id)
            issue.rdm_tracker = self._unmarshal_str(rdm_issue.tracker.name)
            issue.updated_on = self._unmarshal_timestamp(rdm_issue.created_on)
        except KeyError, e:
            raise UnmarshallingError(instance='RedmineIssue', cause=repr(e))

    def _unmarshal_issue_comments(self, rdm_journals):
        return [self._unmarshal_issue_comment(rdm_journal)
                for rdm_journal in rdm_journals
                if NOTES_TOKEN in rdm_journal
                and rdm_journal.notes]

    def _unmarshal_issue_comment(self, rdm_journal):
        try:
            text = self._unmarshal_str(rdm_journal.notes)
            submitted_by = self._unmarshal_identity(rdm_journal.user)
            submitted_on = self._unmarshal_timestamp(rdm_journal.created_on)
            return Comment(text, submitted_by, submitted_on)
        except KeyError, e:
            raise UnmarshallingError(instance='Comment', cause=repr(e))

    def _unmarshal_issue_attachments(self, rdm_attachments):
        return [self._unmarshal_issue_attachment(rdm_attachment)
                for rdm_attachment in rdm_attachments]

    def _unmarshal_issue_attachment(self, rdm_attachment):
        try:
            name = self._unmarshal_str(rdm_attachment.filename)
            url = self._unmarshal_str(rdm_attachment.content_url)
            desc = self._unmarshal_str(rdm_attachment.description)
            submitted_by = self._unmarshal_identity(rdm_attachment.author)
            submitted_on = self._unmarshal_timestamp(rdm_attachment.created_on)
            size = self._unmarshal_str(rdm_attachment.filesize)
            rdm_attachment_id = self._unmarshal_str(rdm_attachment.id)

            return RedmineAttachment(name, url, desc,
                                     submitted_by, submitted_on,
                                     size, rdm_attachment_id)
        except KeyError, e:
            raise UnmarshallingError(instance='RedmineAttachment', cause=repr(e))

    def _unmarshal_issue_changes(self, rdm_journals):
        try:
            changes = []

            for rdm_journal in rdm_journals:
                if not DETAILS_TOKEN in rdm_journal:
                    continue

                changed_by = self._unmarshal_identity(rdm_journal.user)
                changed_on = self._unmarshal_timestamp(rdm_journal.created_on)

                for detail in rdm_journal.details:
                    old_value = None
                    new_value = None

                    field = detail.name

                    if OLD_VALUE_TOKEN in detail:
                        old_value = unicode(detail.old_value)
                    if NEW_VALUE_TOKEN in detail:
                        new_value = unicode(detail.new_value)

                    change = Change(field, old_value, new_value, changed_by, changed_on)
                    changes.append(change)
            return changes
        except KeyError, e:
            raise UnmarshallingError(instance='Change', cause=repr(e))

    def _unmarshal_issue_relationships(self, rdm_relationships, issue_id):
        return [self._unmarshal_issue_relation(rdm_relation, issue_id)
                for rdm_relation in rdm_relationships]

    def _unmarshal_issue_relation(self, rdm_relation, issue_id):
        try:
            related_to = self._unmarshal_str(rdm_relation.issue_to_id)

            if rdm_relation.relation_type == BLOCKS_TOKEN:
                # issue_id is required in order to know if the parsed
                # issue blocks or is blocked
                if issue_id == related_to:
                    # the current issue is blocked by 'rdm_relation.issue_id'
                    rel_type = RDM_RELATIONSHIP_BLOCKED
                    related_to = self._unmarshal_str(rdm_relation.issue_id)
                else:
                    # the current issue blocks 'rdm_relation.issue_id'
                    rel_type =  RDM_RELATIONSHIP_BLOCKS
            elif rdm_relation.relation_type == RELATES_TOKEN:
                rel_type = RDM_RELATIONSHIP_RELATES
            else:
                cause = 'unknown relationship type: %s' % rdm_relation.relation_type
                raise UnmarshallingError(instance='IssueRelationship', cause=cause)

            return IssueRelationship(rel_type, related_to)
        except KeyError, e:
            raise UnmarshallingError(instance='IssueRelationship', cause=repr(e))

    def _unmarshal_identity(self, rdm_id):
        try:
            user_id = self._unmarshal_str(rdm_id.id)
            name = self._unmarshal_str(rdm_id.name)
            return RedmineIdentity(user_id, name=name)
        except Exception, e:
            raise UnmarshallingError(instance='RedmineIdentity', cause=repr(e))
