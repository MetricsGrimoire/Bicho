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

"""
Redmine's tracker data model.
"""

import datetime

from bicho.common import Identity, IssueSummary, Issue, Attachment


# Redmine relationships types
RDM_RELATIONSHIP_BLOCKED = u'BLOCKED'
RDM_RELATIONSHIP_BLOCKS = u'BLOCKS'
RDM_RELATIONSHIP_RELATES = u'RELATES'


class RedmineIdentity(Identity):
    """An identity from Redmine.

    :param user_id: user identifier of the identity
    :type user_id: str
    :param name: name of the identity
    :type name: str
    :param email: email of the identity
    :type email: str
    :param login: nick of the user
    :type login: str
    :param created_on: date when this identity was created
    :type created_on: datetime.datetime
    :param last_login_on: last time this identity logged in
    :type last_login_on: datetime.datetime
    """

    def __init__(self, user_id, name=None, email=None,
                 login=None, created_on=None, last_login_on=None):
        super(RedmineIdentity, self).__init__(user_id, name, email)
        self.login = login
        self.created_on = created_on
        self.last_login_on = last_login_on

    @property
    def created_on(self):
        return self._created_on

    @created_on.setter
    def created_on(self, value):
        if value is not None and not isinstance(value, datetime.datetime):
            raise TypeError('Parameter "created_on" should be a %s instance. %s given.' %
                            ('datetime', value.__class__.__name__))
        self._created_on = value

    @property
    def last_login_on(self):
        return self._last_login_on

    @last_login_on.setter
    def last_login_on(self, value):
        if value is not None and not isinstance(value, datetime.datetime):
            raise TypeError('Parameter "last_login_on" should be a %s instance. %s given.' %
                            ('datetime', value.__class__.__name__))
        self._last_login_on = value


class RedmineStatus(object):
    """Status from Redmine.

    :param status_id: status identifier
    :type status_id: str
    :param name: name of the status
    :type name: str
    :param is_closed: indicates if the status closes a ticket
    :type is_closed: bool
    :param is_default: indicates if the status is assigned by default
    :type is_default: bool
    """
    def __init__(self, status_id, name, is_closed=False, is_default=False):
        if not isinstance(is_closed, bool):
            raise TypeError('Parameter "is_closed" should be a %s instance. %s given.' %
                            ('bool', is_closed.__class__.__name__,))

        if not isinstance(is_default, bool):
            raise TypeError('Parameter "is_default" should be a %s instance. %s given.' %
                            ('bool', is_default.__class__.__name__,))

        self._status_id = status_id
        self._name = name
        self._is_closed = is_closed
        self._is_default = is_default

    @property
    def status_id(self):
        return self._status_id

    @property
    def name(self):
        return self._name

    @property
    def is_closed(self):
        return self._is_closed

    @property
    def is_default(self):
        return self._is_default


class RedmineIssuesSummary(object):
    """Issues summary page.

    :param total_count: total number of issues available on the tracker
    :type total_count: int
    :param offset: current position of the first issue of this summary
    :type offset: int
    :param limit: max issues on this summary
    :type limit: int
    """

    def __init__(self, total_count, offset, limit):
        self._total_count = total_count
        self._offset = offset
        self._limit = limit
        self._summary = []

    @property
    def summary(self):
        return self._summary

    @property
    def total_count(self):
        return self._total_count

    @property
    def offset(self):
        return self._offset

    @property
    def limit(self):
        return self._limit

    def add_summary(self, issue_summary):
        """Add a issue summary to the list.

        :param issue_summary: a summary of the issue
        :type issue_summary: IssueSummary

        :raise TypeError: raised if the type of issue summary is not valid.
        """
        if not isinstance(issue_summary, IssueSummary):
            raise TypeError('Parameter "issue_summary" should be a %s instance. %s given.' %
                            ('IssueSummary', issue_summary.__class__.__name__,))
        self._summary.append(issue_summary)


class RedmineIssue(Issue):
    """Redmine issue

    :param issue_id: identifier of the issue
    :type issue_id: str
    :param issue_type: type of the issue
    :type issue_type: str
    :param summary: brief description of the issue
    :type summary: str
    :param description: long description of the issue
    :type description: str
    :param submitted_by: identity that submitted the issue
    :type submitted_by: RedmineIdentity
    :param submitted_on: date when the issue was submitted
    :type submitted_on: datetime.datetime
    :param status: status of the issue
    :type status: str
    :param resolution: resolution of the issue
    :type resolution: str
    :param priority: priority level of the issue
    :type priority: str
    :param assigned_to: identity assigned to the issue
    :type assigned_to: RedmineIdentity

    :raises: TypeError: when the type of the parameters is not valid.

    ..note: custom fields not supported
    """

    def __init__(self, issue_id, issue_type, summary, description,
                 submitted_by, submitted_on,
                 status=None, resolution=None, priority=None,
                 assigned_to=None):

        if not isinstance(submitted_by, RedmineIdentity):
            raise TypeError('Parameter "submitted_by" should be a %s instance. %s given.' %
                            ('RedmineIdentity', submitted_by.__class__.__name__,))

        if assigned_to is not None and not isinstance(assigned_to, RedmineIdentity):
            raise TypeError('Parameter "assigned_to" should be a %s instance. %s given.' %
                            ('RedmineIdentity', assigned_to.__class__.__name__,))

        super(RedmineIssue, self).__init__(issue_id, issue_type, summary, description,
                                           submitted_by, submitted_on, status, resolution,
                                           priority, assigned_to)
        self.project_id = None
        self.project = None
        self.rdm_tracker_id = None
        self.rdm_tracker = None
        self._updated_on = None

    @property
    def assigned_to(self):
        return self._assigned_to

    @assigned_to.setter
    def assigned_to(self, value):
        if value is not None and not isinstance(value, RedmineIdentity):
            raise TypeError('Parameter "assigned_to" should be a %s instance. %s given.' %
                            ('RemineIdentity', value.__class__.__name__,))
        self._assigned_to = value

    @property
    def updated_on(self):
        return self._updated_on

    @updated_on.setter
    def updated_on(self, value):
        if value is not None and not isinstance(value, datetime.datetime):
            raise TypeError('Parameter "updated_on" should be a %s instance. %s given.' %
                            ('datetime', value.__class__.__name__))
        self._updated_on = value


class RedmineAttachment(Attachment):
    """Redmine attachment instance.

    :param name: name of the attachemnt
    :type name: str
    :param url: URL of the attachment
    :type url: str
    :param description: description of the attachment
    :type description: str
    :param submitted_by: submitter of the attachment
    :type submitted_by: RedmineIdentity
    :param submitted_on: date when the attachment was submitted
    :type submitted_on: datetime.datetime
    :param size: file size of the attachment
    :type size: str
    :param rdm_attachment_id: id of the attachment
    :type rdm_attachment_id: int

    :raise TypeError: raised when the type of the parameters is not valid.
    """
    def __init__(self, name, url, description,
                 submitted_by, submitted_on,
                 size=None, rdm_attachment_id=None):

        if not isinstance(submitted_by, RedmineIdentity):
            raise TypeError('Parameter "submitted_by" should be a %s instance. %s given.' %
                            ('RedmineIdentity', submitted_by.__class__.__name__,))

        super(RedmineAttachment, self).__init__(name, url, description,
                                                submitted_by, submitted_on)
        self.size = size
        self.rdm_attachment_id = rdm_attachment_id
