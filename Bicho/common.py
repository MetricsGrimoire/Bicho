# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2011  GSyC/LibreSoft, Universidad Rey Juan Carlos
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
# Authors: Santiago Dueñas <sduenas@libresoft.es>
#          Daniel Izquierdo Cortázar <dizquierdo@libresoft.es>
#

"""
Symbols and classes shared by Bicho's modules
"""

import datetime


class People:
    """
    Identity on a issue tracking system.

    @param user_id: identifier of the user
    @type user_id: C{str}
    """
    def __init__(self, user_id):
        self.name = None
        self.email = None
        self.user_id = user_id

    def set_name(self, name):
        """
        Set the name of the identity.

        @param name: name of the identity
        @type name: C{str}
        """
        self.name = name

    def set_email(self, email):
        """
        Set the email of the identity.

        @param email: email of the identity
        @type email: C{str} 
        """
        self.email = email


class Tracker:
    """
    Issue tracker instance.
b
    @param url: URL of the issue tracker
    @type url: C{str}
    @param name: name or type of the issue tracker
    @type name: C{str}
    @param version: version of the issue tracker
    @type version: C{str}
    """
    def __init__(self, url, name, version):
        self.url = url
        self.name = name
        self.version = version


class Issue:
    """
    Generic object for managing issues. 

    @param issue: identifier of the issue
    @type issue: C{str}
    @param type: type of the issue
    @type type: C{str}
    @param summary: brief description of the issue
    @type summary: C{str}
    @param desc: long description of the issue
    @type desc: C{str}
    @param submitted_by: identity that submitted the issue
    @type submitted_by: L{People}
    @param submitted_on: date when the issue was submitted
    @type submitted_on: L{datetime.datetime}

    @raise ValueError: when the type of the parameters is not valid.
    """
    def __init__(self, issue, type, summary, desc, submitted_by, submitted_on):
        self.issue = issue
        self.type = type
        self.summary = summary
        self.description = desc
        self.status = None
        self.resolution = None
        self.priority = None
        self.assigned_to = None

        if not isinstance(submitted_by, People):
            raise ValueError('Parameter "submitted_by" should be a %s instance. %s given.' %
                             ('People', submitted_by.__class__.__name__,))

        if not isinstance(submitted_on, datetime.datetime):
            raise ValueError('Parameter "submitted_on" should be a %s instance. %s given.' %
                             ('datetime', input.__class__.__name__))

        self.submitted_by = submitted_by
        self.submitted_on = submitted_on

        self.comments = []
        self.attachments = []
        self.changes = []
        self.relationships = []
        self.temp_relationships = []
        self.watchers = []

    def set_priority(self, priority):
        """
        Set the priority of the issue.

        @param priority: priority of the issue
        @type priority: C{str}
        """
        self.priority = priority

    def set_status(self, status, resolution=None):
        """
        Set the status of the issue. Additionally, the resolution
        can also be set.

        @param status: status of the issue
        @type status: C{str}
        @param resolution: resolution of the issue
        @type resolution: C{str}
        """
        self.status = status

        if resolution is not None:
            self.resolution = resolution

    def set_assigned(self, assigned_to):
        """
        Set the identity assigned to the issue.

        @param assigned_to: identity assigned to the bug
        @param type: L{People}

        @raise ValueError: raised if the type of X{assigned_to}}
         is not valid. 
        """
        if not isinstance(assigned_to, People):
            raise ValueError('Parameter "assigned_to" should be a %s instance. %s given.' %
                             ('People', assigned_to.__class__.__name__,))
        self.assigned_to = assigned_to

    def add_comment(self, comment):
        """
        Add a comment to the issue.

        @param comment: a comment of the issue 
        @type comment: L{Comment}

        @raise ValueError: raised if the type of X{comment} is not valid.
        """
        if not isinstance(comment, Comment):
            raise ValueError('Parameter "comment" should be a %s instance. %s given.' %
                             ('Comment', comment.__class__.__name__,))
        self.comments.append(comment)

    def add_attachment(self, attachment):
        """
        Add an attachment to the issue.

        @param attachment: an attachment of the issue 
        @type attachment: L{Attachment}

        @raise ValueError: raised if the type of X{attachment} is not valid.
        """
        if not isinstance(attachment, Attachment):
            raise ValueError('Parameter "attachment" should be a %s instance. %s given.' %
                             ('Attachment', attachment.__class__.__name__,))
        self.attachments.append(attachment)

    def add_change(self, change):
        """
        Add a change to the issue.

        @param change: a change of the issue 
        @type change: L{Change}

        @raise ValueError: raised if the type of X{change} is not valid.
        """
        if not isinstance(change, Change):
            raise ValueError('Parameter "change" should be a %s instance. %s given.' %
                             ('Change', change.__class__.__name__,))
        self.changes.append(change)

    def add_relationship(self, issue, type):
        """
        Add a relationship to the issue.

        @param issue: an issue related to this issue
        @type issue: C{str}
        @param type: type of the relationship
        @type type: C{str}
        """
        self.relationships.append((issue, type))

    def add_temp_relationship(self, relationship):
        """
        Add a relationship to the issue.

        @param issue: an issue related to this issue
        @type issue: C{str}
        @param type: type of the relationship
        @type type: C{str}
        """
        if not isinstance(relationship, TempRelationship):
            raise ValueError('Parameter "relationship" should be a %s instance. %s given.' %
                             ('TempRelationship', relationship.__class__.__name__,))
        self.temp_relationships.append(relationship)


    def set_resolution(self, resolution):
        """
        Set the resolution of the issue.

        @param resolution: resolution of the issue
        @type resolution: C{str}
        """
        self.resolution = resolution

    def add_watcher(self, watcher):
        """
        Set the identity assigned to the issue.

        @param watcher: identity watching the bug
        @param type: L{People}

        @raise ValueError: raised if the type of X{assigned_to}}
        is not valid.
        """
        if not isinstance(watcher, People):
            raise ValueError('Parameter "assigned_to" should be a %s instance. %s given.' %
                             ('People', watcher.__class__.__name__,))
        self.watchers.append(watcher)


class Comment:
    """
    Comment instance.

    @param comment: brief description of the issue
    @type comment: C{str}
    @param submitted_by: identity that submitted the comment
    @type submitted_by: L{People}
    @param submitted_on: date when the comment was submitted
    @type submitted_on: L{datetime.datetime}

    @raise ValueError: raised when the type of the parameters
     is not valid.
    """
    def __init__(self, comment, submitted_by, submitted_on):
        self.comment = comment

        if not isinstance(submitted_by, People):
            raise ValueError('Parameter "submitted_by" should be a %s instance. %s given.' %
                             ('People', submitted_by.__class__.__name__,))

        if not isinstance(submitted_on, datetime.datetime):
            raise ValueError('Parameter "submitted_on" should be a %s instance. %s given.' %
                             ('datetime', input.__class__.__name__))

        self.submitted_by = submitted_by
        self.submitted_on = submitted_on


class Attachment:
    """
    Attachment instance.

    @param url: URL of the attachment
    @type url: C{str}
    @param submitted_by: submitter of the attachment
    @type submitted_by: L{People}
    @param submitted_on: date when the attachment was submitted
    @type submitted_on: L{datetime.datetime}

    @raise ValueError: raised when the type of the parameters
     is not valid.
    """
    def __init__(self, url, submitted_by=None, submitted_on=None):
        self.name = None
        self.description = None
        self.url = url

        if submitted_by is not None and not isinstance(submitted_by, People):
            raise ValueError('Parameter "submitted_by" should be a %s instance. %s given.' %
                             ('People', submitted_by.__class__.__name__,))

        if submitted_on is not None and not isinstance(submitted_on, datetime.datetime):
            raise ValueError('Parameter "submitted_on" should be a %s instance. %s given.' %
                             ('datetime', input.__class__.__name__))

        self.submitted_by = submitted_by
        self.submitted_on = submitted_on

    def set_name(self, name):
        """
        Set the name of the attachment.

        @param name: name of the attachemnt
        @type name: C{str}
        """
        self.name = name

    def set_description(self, desc):
        """
        Set the description of the attachment.

        @param desc: description of the attachment
        @type desc: C{str}
        """
        self.description = desc


class Change:
    """
    A change performed during the issue lifecycle.

    @param field: name of the field that was changed
    @type field: C{str}
    @param old_value: old value of the field
    @type old_value: C{str}
    @param new_value: new value of the field
    @type new_value: C{str}
    @param changed_by: submitter of the change
    @type changed_by: L{People}
    @param changed_on: date when the attachment was submitted
    @type changed_on: C{datetime.datetime}
    """
    def __init__(self, field, old_value, new_value, changed_by, changed_on):
        self.field = field
        self.old_value = old_value
        self.new_value = new_value

        if not isinstance(changed_by, People):
            raise ValueError('Parameter "changed_by" should be a %s instance. %s given.' %
                             ('People', changed_by.__class__.__name__,))

        if not isinstance(changed_on, datetime.datetime):
            raise ValueError('Parameter "changed_on" should be a %s instance. %s given.' %
                             ('datetime', input.__class__.__name__))

        self.changed_by = changed_by
        self.changed_on = changed_on


class TempRelationship:
    """
    """
    def __init__(self, issue, type, related_to):
        self.issue = issue
        self.type = type
        self.related_to = related_to


class Relationship:
    """
    """
    def __init__(self, issue, type, related_to):
        self.issue = issue
        self.type = type
        self.related_to = related_to
