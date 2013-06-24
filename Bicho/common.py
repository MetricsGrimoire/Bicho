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
#         Daniel Izquierdo Cortázar <dizquierdo@bitergia.com>
#

"""
Symbols and classes shared by Bicho modules
"""

import datetime


class Identity(object):
    """Identity on a issue tracking system.

    :param user_id: user identifier of the identity
    :type user_id: str
    :param name: name of the identity
    :type name: str
    :param email: email of the identity
    :type email: str
    """
    def __init__(self, user_id, name=None, email=None):
        self.user_id = user_id
        self.name = name
        self.email = email


class Tracker(object):
    """Issue tracker instance.

    :param url: URL of the issue tracker
    :type url: str
    :param name: name or type of the issue tracker
    :type name: str
    :param version: version of the issue tracker
    :type version: str
    """
    def __init__(self, url, name, version):
        self._url = url
        self._name = name
        self._version = version

    @property
    def url(self):
        return self._url

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version


class Issue(object):
    """Generic object for managing issues.

    :param issue: identifier of the issue
    :type issue: str
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
    """
    def __init__(self, issue_id, issue_type, summary, description,
                 submitted_by, submitted_on,
                 status=None, resolution=None, priority=None,
                 assigned_to=None):
        if not isinstance(submitted_by, Identity):
            raise TypeError('Parameter "submitted_by" should be a %s instance. %s given.' %
                            ('Identity', submitted_by.__class__.__name__,))

        if not isinstance(submitted_on, datetime.datetime):
            raise TypeError('Parameter "submitted_on" should be a %s instance. %s given.' %
                            ('datetime', submitted_on.__class__.__name__))

        self.issue_id = issue_id
        self.issue_type = issue_type
        self.summary = summary
        self.description = description
        self._submitted_by = submitted_by
        self._submitted_on = submitted_on
        self.status = status
        self.resolution = resolution
        self.priority = priority
        self.assigned_to = assigned_to
        self._comments = []
        self._attachments = []
        self._changes = []
        self._relationships = []
        self._temp_relationships = []
        self._watchers = []

    @property
    def submitted_by(self):
        return self._submitted_by

    @property
    def submitted_on(self):
        return self._submitted_on

    @property
    def assigned_to(self):
        return self._assigned_to

    @assigned_to.setter
    def assigned_to(self, value):
        if value is not None and not isinstance(value, Identity):
            raise TypeError('Parameter "assigned_by" should be a %s instance. %s given.' %
                            ('Identity', value.__class__.__name__,))
        self._assigned_to = value

    @property
    def comments(self):
        return self._comments

    def add_comment(self, comment):
        """Add a comment to the issue.

        :param comment: a comment of the issue
        :type comment: Comment

        :raise TypeError: raised if the type of comment is not valid.
        """
        if not isinstance(comment, Comment):
            raise TypeError('Parameter "comment" should be a %s instance. %s given.' %
                            ('Comment', comment.__class__.__name__,))
        self._comments.append(comment)

    @property
    def attachments(self):
        return self._attachments

    def add_attachment(self, attachment):
        """Add an attachment to the issue.

        :param attachment: an attachment of the issue
        :type attachment: Attachment

        :raise TypeError: raised if the type of attachment is not valid.
        """
        if not isinstance(attachment, Attachment):
            raise TypeError('Parameter "attachment" should be a %s instance. %s given.' %
                            ('Attachment', attachment.__class__.__name__,))
        self._attachments.append(attachment)

    @property
    def changes(self):
        return self._changes

    def add_change(self, change):
        """Add a change to the issue.

        :param change: a change of the issue
        :type change: L{Change}

        :raise TypeError: raised if the type of change is not valid.
        """
        if not isinstance(change, Change):
            raise TypeError('Parameter "change" should be a %s instance. %s given.' %
                            ('Change', change.__class__.__name__,))
        self._changes.append(change)

    @property
    def watchers(self):
        return self._watchers

    def add_watcher(self, watcher):
        """Set a watcher assigned to the issue.

        :param watcher: identity watching the bug
        :type watcher: Identity

        :raise TypeError: raised if the type of assigned_to is not valid.
        """
        if not isinstance(watcher, Identity):
            raise TypeError('Parameter "watcher" should be a %s instance. %s given.' %
                            ('Identity', watcher.__class__.__name__,))
        self._watchers.append(watcher)


class Comment(object):
    """Comment to an issue.

    :param text: text of the comment
    :type text: str
    :param submitted_by: identity that submitted the comment
    :type submitted_by: Identity
    :param submitted_on: date when the comment was submitted
    :type submitted_on: datetime.datetime

    :raise TypeError: raised when the type of the parameters is not valid.
    """
    def __init__(self, text, submitted_by, submitted_on):
        if not isinstance(submitted_by, Identity):
            raise TypeError('Parameter "submitted_by" should be a %s instance. %s given.' %
                            ('Identity', submitted_by.__class__.__name__,))

        if not isinstance(submitted_on, datetime.datetime):
            raise TypeError('Parameter "submitted_on" should be a %s instance. %s given.' %
                            ('datetime', submitted_on.__class__.__name__))

        self._text = text
        self._submitted_by = submitted_by
        self._submitted_on = submitted_on

    @property
    def text(self):
        return self._text

    @property
    def submitted_by(self):
        return self._submitted_by

    @property
    def submitted_on(self):
        return self._submitted_on


class Attachment(object):
    """Attachment instance.

    :param url: URL of the attachment
    :type url: str
    :param name: name of the attachemnt
    :type name: str
    :param description: description of the attachment
    :type description: str
    :param submitted_by: submitter of the attachment
    :type submitted_by: Identity
    :param submitted_on: date when the attachment was submitted
    :type submitted_on: datetime.datetime

    :raise TypeError: raised when the type of the parameters is not valid.
    """
    def __init__(self, url, name=None, description=None,
                 submitted_by=None, submitted_on=None):
        self.url = url
        self.name = name
        self.description = description
        self.submitted_by = submitted_by
        self.submitted_on = submitted_on

    @property
    def submitted_by(self):
        return self._submitted_by

    @submitted_by.setter
    def submitted_by(self, value):
        if value is not None and not isinstance(value, Identity):
            raise TypeError('Parameter "submitted_by" should be a %s instance. %s given.' %
                            ('Identity', value.__class__.__name__,))
        self._submitted_by = value

    @property
    def submitted_on(self):
        return self._submitted_on

    @submitted_on.setter
    def submitted_on(self, value):
        if value is not None and not isinstance(value, datetime.datetime):
            raise TypeError('Parameter "submitted_on" should be a %s instance. %s given.' %
                             ('datetime', value.__class__.__name__))
        self._submitted_on = value


class Change(object):
    """A change performed during the issue lifecycle.

    :param field: name of the field that was changed
    :type field: str
    :param old_value: old value of the field
    :type old_value: str
    :param new_value: new value of the field
    :type new_value: str
    :param changed_by: submitter of the change
    :type changed_by: Identity
    :param changed_on: date when the attachment was submitted
    :type changed_on: datetime.datetime

    :raise TypeError: raised when the type of the parameters is not valid.
    """
    def __init__(self, field, old_value, new_value, changed_by, changed_on):
        if not isinstance(changed_by, Identity):
            raise TypeError('Parameter "changed_by" should be a %s instance. %s given.' %
                            ('Identity', changed_by.__class__.__name__,))

        if not isinstance(changed_on, datetime.datetime):
            raise TypeError('Parameter "changed_on" should be a %s instance. %s given.' %
                            ('datetime', changed_on.__class__.__name__))

        self._field = field
        self._old_value = old_value
        self._new_value = new_value
        self._changed_by = changed_by
        self._changed_on = changed_on

    @property
    def field(self):
        return self._field

    @property
    def old_value(self):
        return self._old_value

    @property
    def new_value(self):
        return self._new_value

    @property
    def changed_by(self):
        return self._changed_by

    @property
    def changed_on(self):
        return self._changed_on
