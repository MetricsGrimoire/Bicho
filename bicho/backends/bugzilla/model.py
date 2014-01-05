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

"""
Bugzilla's tracker data model.
"""

import datetime

from bicho.common import Identity, Issue, Attachment


# Bugzilla relationships types
BG_RELATIONSHIP_BLOCKED = u'BLOCKED'
BG_RELATIONSHIP_DEPENDS_ON = u'DEPENDS ON'


class BugzillaMetadata(object):
    """Issue tracker metadata

    :param version: version of the tracker
    :type version: str
    :param urlbase: url of the tracker
    :type urlbase: str
    :param maintainer: user id set as maintainer of the tracker
    :type maintainer: str
    :param exporter: user used to retrieve information from the tracker
    :type exporter: str
    """
    def __init__(self, version, urlbase, maintainer, exporter):
        self.version = version
        self.urlbase = urlbase
        self.maintainer = maintainer
        self.exporter = exporter


class BugzillaIssueSummary(object):
    """Summary of an issue

    :param issue_id: identifier of the issue
    :type issue_id: str
    :param changed_on: last update of the issue
    :type change_on: datetime.datetime

    :raises: TypeError: when the type of any parameter is not valid.
    """
    def __init__(self, issue_id, changed_on):
        if not isinstance(changed_on, datetime.datetime):
            raise TypeError('Parameter "changed_on" should be a %s instance. %s given.' %
                            ('datetime', changed_on.__class__.__name__))

        self.issue_id = issue_id
        self._changed_on = changed_on

    @property
    def changed_on(self):
        return self._changed_on


class BugzillaIssue(Issue):
    """Bugzilla issue

    :param issue_id: identifier of the issue
    :type issue_id: str
    :param issue_type: type of the issue
    :type issue_type: str
    :param summary: brief description of the issue
    :type summary: str
    :param description: long description of the issue
    :type description: str
    :param submitted_by: identity that submitted the issue
    :type submitted_by: Identity
    :param submitted_on: date when the issue was submitted
    :type submitted_on: datetime.datetime
    :param status: status of the issue
    :type status: str
    :param resolution: resolution of the issue
    :type resolution: str
    :param priority: priority level of the issue
    :type priority: str
    :param assigned_to: identity assigned to the issue
    :type assigned_to: Identity

    :raises: TypeError: when the type of the parameters is not valid.

    ..note: keywords, groups and flags not supported
    """
    def __init__(self, issue_id, issue_type, summary, description,
                 submitted_by, submitted_on, status=None, resolution=None,
                 priority=None, assigned_to=None):
        Issue.__init__(self, issue_id, issue_type, summary, description,
                       submitted_by, submitted_on, status, resolution,
                       priority, assigned_to)
        self.classification_id = None
        self.classification = None
        self.product = None
        self.component = None
        self.version = None
        self.platform = None
        self.op_sys = None
        self.alias = None
        self.bug_file_loc = None
        self.cclist_accessible = None
        self.dup_id = None
        self.everconfirmed = None
        self.reporter_accessible = None
        self.status_whiteboard = None
        self.target_milestone = None
        self.votes = None
        self._delta_ts = None
        self._qa_contact = None
        self._estimated_time = None
        self._remaining_time = None
        self._actual_time = None
        self._deadline = None

    @property
    def delta_ts(self):
        return self._delta_ts

    @delta_ts.setter
    def delta_ts(self, value):
        if value is not None and not isinstance(value, datetime.datetime):
            raise TypeError('Parameter "delta_ts" should be a %s instance. %s given.' %
                            ('datetime', value.__class__.__name__))
        self._delta_ts = value

    @property
    def qa_contact(self):
        return self._qa_contact

    @qa_contact.setter
    def qa_contact(self, value):
        if value is not None and not isinstance(value, Identity):
            raise TypeError('Parameter "qa_contact" should be a %s instance. %s given.' %
                            ('Identity', value.__class__.__name__))
        self._qa_contact = value

    @property
    def estimated_time(self):
        return self._estimated_time

    @estimated_time.setter
    def estimated_time(self, value):
        if value is not None and not isinstance(value, datetime.datetime):
            raise TypeError('Parameter "estimated_time" should be a %s instance. %s given.' %
                            ('datetime', value.__class__.__name__))
        self._estimated_time = value

    @property
    def remaining_time(self):
        return self._remaining_time

    @remaining_time.setter
    def remaining_time(self, value):
        if value is not None and not isinstance(value, datetime.datetime):
            raise TypeError('Parameter "remaining_time" should be a %s instance. %s given.' %
                            ('datetime', value.__class__.__name__))
        self._remaining_time = value

    @property
    def actual_time(self):
        return self._actual_time

    @actual_time.setter
    def actual_time(self, value):
        if value is not None and not isinstance(value, datetime.datetime):
            raise TypeError('Parameter "actual_time" should be a %s instance. %s given.' %
                            ('datetime', value.__class__.__name__))
        self._actual_time = value

    @property
    def deadline(self):
        return self._deadline

    @deadline.setter
    def deadline(self, value):
        if value is not None and not isinstance(value, datetime.datetime):
            raise TypeError('Parameter "deadline" should be a %s instance. %s given.' %
                            ('datetime', value.__class__.__name__))
        self._deadline = value

    def add_attachment(self, attachment):
        """Add a Bugzilla attachment to the issue.

        Overwrites add_attachment method from Attachment.

        :param attachment: an attachment of the issue
        :type attachment: BugzillaAttachment

        :raise TypeError: raised if the type of attachment is not valid.
        """
        if not isinstance(attachment, BugzillaAttachment):
            raise TypeError('Parameter "attachment" should be a %s instance. %s given.' %
                            ('BugzillaAttachment', attachment.__class__.__name__,))
        self._attachments.append(attachment)


class BugzillaAttachment(Attachment):
    """Bugzilla attachment instance

    :param name: name of the attachemnt
    :type name: str
    :param url: URL of the attachment
    :type url: str
    :param description: description of the attachment
    :type description: str
    :param submitted_by: submitter of the attachment
    :type submitted_by: Identity
    :param submitted_on: date when the attachment was submitted
    :type submitted_on: datetime.datetime
    :param filetype: file type of the attachment
    :type filetype: str
    :param size: file size of the attachment
    :type size: str
    :param delta_ts: delta timestamp of the attachment
    :type delta_ts: datetime.datetime
    :param is_patch: sets whether the attachment is a code patch
    :type is_patch: bool
    :param is_obsolete: sets whether the attachment is deprecated
    :type is_obsolete: bool

    :raise TypeError: raised when the type of the parameters is not valid.
    """
    def __init__(self, name, url, description,
                 submitted_by, submitted_on,
                 filetype=None, size=None, delta_ts=None,
                 is_patch=None, is_obsolete=None):
        Attachment.__init__(self, name, url, description,
                            submitted_by, submitted_on)
        self.filetype = filetype
        self.size = size
        self.delta_ts = delta_ts
        self.is_patch = is_patch
        self.is_obsolete = is_obsolete

    @property
    def delta_ts(self):
        return self._delta_ts

    @delta_ts.setter
    def delta_ts(self, value):
        if value is not None and not isinstance(value, datetime.datetime):
            raise TypeError('Parameter "delta_ts" should be a %s instance. %s given.' %
                            ('datetime', value.__class__.__name__))
        self._delta_ts = value

    @property
    def is_patch(self):
        return self._is_patch

    @is_patch.setter
    def is_patch(self, value):
        if value is not None and not isinstance(value, bool):
            raise TypeError('Parameter "is_patch" should be a %s instance. %s given.' %
                            ('bool', value.__class__.__name__))
        self._is_patch = value

    @property
    def is_obsolete(self):
        return self._is_obsolete

    @is_obsolete.setter
    def is_obsolete(self, value):
        if value is not None and not isinstance(value, bool):
            raise TypeError('Parameter "is_obsolete" should be a %s instance. %s given.' %
                            ('bool', value.__class__.__name__))
        self._is_obsolete = value
