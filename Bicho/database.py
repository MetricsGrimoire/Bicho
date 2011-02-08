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
"""

import datetime
from storm.locals import *
from utils import *


class NotFoundError(Exception):
    """
    Exception raised when an entry is not found into the database.

    @param msg: explanation of the error
    @type msg: C{str}
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class DBDatabase:
    """
    """
    def __init__(self):
        self.database = None
        self.store = None

    def insert_tracker(self, tracker):
        """
        Insert the given tracker.
        
        @param tracker: tracker to insert
        @type tracker: L{Tracker}
        
        @return: the inserted tracker
        @rtype: L{DBTracker}
        """
        try:
            db_tracker = DBTracker(tracker.url, tracker.type)
            self.store.add(db_tracker)
            self.store.commit()
        except:
            db_tracker = self._get_db_tracker(tracker.url)
            db_tracker.retrieved_on = datetime.datetime.now()
            self.store.commit()
        return db_tracker
    
    def insert_people(self, people, tracker_id):
        """
        Insert the given identity.
        
        @param people: identity to insert
        @type people: L{People}
        
        @return: the inserted identity
        @rtype: L{People}
        """
        try:
            db_people = DBPeople(people.user_id, tracker_id)
            db_people.set_name(people.name)
            db_people.set_email(people.email)
            self.store.add(db_people)
            self.store.commit()
        except:
            db_people = self._get_db_people(people.user_id, tracker_id)
        return db_people

    def insert_issue(self, issue, tracker_id):
        """
        Insert the given issue managed by the tracker with X{tracker_id}.

        @param issue: issue to insert
        @type issue: L{Issue}
        @param tracker_id: identifier of the tracker
        @type tracker_id: C{int}
        
        @return: the inserted issue
        @rtype: L{DBIssue} 
        """
        try:
            db_issue = DBIssue(issue.issue, tracker_id)
            db_issue.type = unicode(issue.type)
            db_issue.summary = unicode(issue.summary)
            db_issue.description = unicode(issue.description)
            db_issue.status = unicode(issue.status)
            db_issue.resolution = unicode(issue.resolution)
            db_issue.resolution = unicode(issue.resolution)
            db_issue.priority = unicode(issue.priority)
            db_issue.submitted_by = self.insert_people(issue.submitted_by, 
                                                       tracker_id).id
            db_issue.submitted_on = issue.submitted_on
            db_issue.assigned_to = self.insert_people(issue.assigned_to, 
                                                      tracker_id).id

            self.store.add(db_issue)
            self.store.flush()
        
            # Insert relationships
        
            # Insert comments
            for comment in issue.comments:
                self._insert_comment(comment, db_issue.id, tracker_id)
        
            # Insert attachments
            for attachment in issue.attachments:
                self._insert_attachment(attachment, db_issue.id, tracker_id)
        
            # Insert changes
            for change in issue.changes:
                self._insert_change(change, db_issue.id, tracker_id)
        
            self.store.commit()
            
            return db_issue
        except:
            self.store.rollback()
            raise

    def _insert_relationship(self, rel_id, type, issue_id):
        """
        Insert a relationship between the given issues.

        @param rel_id: related issued
        @type rel_id: C{int}
        @param type: type of the relationship
        @type type: C{str}
        @param issue_id: issue identifier 
        @type issue_id: C{int}

        @return: the inserted relationship
        @rtype: L{DBIssueRelationship}
        """
        db_rel = DBIssueRelationship(rel_id, type, issue_id)
        self.store.add(db_rel)
        self.store.flush()
        return db_rel

    def _insert_comment(self, comment, issue_id, tracker_id):
        """
        Insert a comment for the issue X{issue_id}

        @param comment: comment to insert
        @type comment: L{Comment}
        @param issue_id: issue identifier 
        @type issue_id: C{int}
        @param tracker_id: identifier of the tracker
        @type tracker_id: C{int}

        @return: the inserted comment
        @rtype: L{DBComment}
        """
        submitted_by = self.insert_people(comment.submitted_by, tracker_id)

        db_comment = DBComment(comment.comment, submitted_by, 
                               comment.submitted_on, issue_id)
        self.store.add(db_comment)
        self.store.flush()
        return db_comment

    def _insert_attachment(self, attachment, issue_id, tracker_id):
        """
        Insert an attachment for the issue X{issue_id}

        @param attachment: attachment to insert
        @type attachment: L{Attachment}
        @param issue_id: issue identifier 
        @type issue_id: C{int}
        @param tracker_id: identifier of the tracker
        @type tracker_id: C{int}

        @return: the inserted attachment
        @rtype: L{DBAttachment}
        """
        submitted_by = self.insert_people(attachment.submitted_by, tracker_id)

        db_attachment = DBAttachment(attachment.name, attachment.description,
                                     attachment.url, submitted_by, 
                                     attachment.submitted_on, issue_id)
        self.store.add(db_attachment)
        self.store.flush()
        return db_attachment

    def _insert_change(self, change, issue_id):
        """
        Insert a change for the issue X{issue_id}

        @param change: change to insert
        @type change: L{Change}
        @param issue_id: issue identifier 
        @type issue_id: C{int}
        @param tracker_id: identifier of the tracker
        @type tracker_id: C{int}

        @return: the inserted change
        @rtype: L{DBChange}
        """
        changed_by = self.insert_people(change.changed_by, tracker_id)
        
        db_change = DBChange(change.field, change.old_value, change.new_value, 
                             changed_by, change.changed_on, issue_id)
        self.store.add(db_change)
        self.store.flush()
        return db_change

    def _get_db_tracker(self, url):
        """
        Get the tracker based on the given URL.

        @param url: URL of the tracker
        @type url: C{str}

        @return: The selected tracker.
        @rtype: L{DBTracker}

        @raise NotFoundError: When the tracker is not found.
        """
        db_tracker = self.store.find(DBTracker,
                                     DBTracker.url == unicode(url)).one()
        if not db_tracker:
            raise NotFoundError('Tracker %s not found' % url)
        return db_tracker
    
    def _get_db_people(self, user_id, tracker_id):
        """
        Get the identity based on the given id.

        @param user_id: user identifier
        @type user_id: C{str}
        @param tracker_id: identifier of the tracker
        @type tracker_id: C{int}

        @return: The selected identity.
        @rtype: L{DBPeople}

        @raise NotFoundError: When the identity is not found.
        """
        db_people = self.store.find(DBPeople,
                                    DBPeople.user_id == unicode(user_id),
                                    DBPeople.tracker_id == tracker_id).one()
        if not db_people:
            raise NotFoundError('Idenitity %s not found in tracker %s' % 
                                (user_id, tracker_id))
        return db_people


class DBMySQL(DBDatabase):
    """
    MySQL database.
    """

    def __init__(self):       
        opts = Config()
        
        self.database = create_database('mysql://' + opts.db_user_out + ':'
                                        + opts.db_password_out + '@'
                                        + opts.db_hostname_out + ':'
                                        + opts.db_port_out + '/'
                                        + opts.db_database_out)
        self.store = Store(self.database)

        # Table 'trackers'
        self.store.execute('CREATE TABLE IF NOT EXISTS trackers (' +
                           'id INTEGER NOT NULL AUTO_INCREMENT,' +
                           'url VARCHAR(255) NOT NULL,' +
                           'type VARCHAR(64) NOT NULL,' +
                           'retrieved_on DATETIME NOT NULL,' +
                           'PRIMARY KEY(id),' +
                           'UNIQUE KEY(url)' +
                           ')')

        # Table 'people'
        self.store.execute('CREATE TABLE IF NOT EXISTS people (' +
                           'id INTEGER NOT NULL AUTO_INCREMENT,' +
                           'name VARCHAR(64) NULL,' +
                           'email VARCHAR(64) NULL,' +
                           'user_id VARCHAR(64) NOT NULL,' +
                           'tracker_id INTEGER NOT NULL,' +
                           'PRIMARY KEY(id),'
                           'UNIQUE KEY(user_id, tracker_id),' +
                           'INDEX people_tracker_idx(tracker_id),' +
                           'FOREIGN KEY(tracker_id)' +
                           '  REFERENCES trackers(id)' +
                           '    ON DELETE CASCADE' +
                           '    ON UPDATE CASCADE' +
                           ')')                           

        # Table 'issues'
        self.store.execute('CREATE TABLE IF NOT EXISTS issues (' +
                           'id INTEGER NOT NULL AUTO_INCREMENT,' +
                           'tracker_id INTEGER NOT NULL,' +
                           'issue VARCHAR(255) NOT NULL,' +
                           'type VARCHAR(32) NULL,' +
                           'summary VARCHAR(255) NOT NULL,' +
                           'description TEXT NOT NULL,' +
                           'status VARCHAR(32) NOT NULL,' +
                           'resolution VARCHAR(32) NULL,' +
                           'priority VARCHAR(32) NULL,' +
                           'submitted_by INTEGER UNSIGNED NOT NULL,' +
                           'submitted_on DATETIME NOT NULL,' +
                           'assigned_to INTEGER UNSIGNED NOT NULL,' +
                           'PRIMARY KEY(id),' +
                           'UNIQUE KEY(issue, tracker_id),' +
                           'INDEX issues_submitted_idx(submitted_by),' +
                           'INDEX issues_assigned_idx(assigned_to),' +
                           'INDEX issues_tracker_idx(tracker_id),' +
                           'FOREIGN KEY(submitted_by)' +
                           '  REFERENCES people(id)' +
                           '    ON DELETE SET NULL' +
                           '    ON UPDATE CASCADE,' +
                           'FOREIGN KEY(assigned_to)' +
                           '  REFERENCES people(id)' +
                           '    ON DELETE SET NULL' +
                           '    ON UPDATE CASCADE,' +
                           'FOREIGN KEY(tracker_id)' +
                           '  REFERENCES trackers(id)' +
                           '    ON DELETE CASCADE' +
                           '    ON UPDATE CASCADE' +
                           ')')

        # Table 'related_to'
        self.store.execute('CREATE TABLE IF NOT EXISTS related_to (' +
                           'issue_id INTEGER UNSIGNED NOT NULL,' +
                           'related_to INTEGER UNSIGNED NOT NULL,' +
                           'type INTEGER UNSIGNED NOT NULL,' +
                           'PRIMARY KEY(issue_id, related_to),' +
                           'INDEX issues_related_idx1(issue_id),' +
                           'INDEX issues_related_idx2(related_to),' +
                           'FOREIGN KEY(issue_id)' +
                           '  REFERENCES issues(id)' +
                           '    ON DELETE CASCADE' +
                           '    ON UPDATE CASCADE,' +
                           'FOREIGN KEY(related_to)' +
                           '  REFERENCES issues(id)' +
                           '    ON DELETE CASCADE' +
                           '    ON UPDATE CASCADE' +
                           ')')

        # Table 'changes'
        self.store.execute('CREATE TABLE IF NOT EXISTS changes (' +
                           'id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT,' +
                           'issue_id INTEGER UNSIGNED NOT NULL,' +
                           'field VARCHAR(64) NOT NULL,' +
                           'old_value VARCHAR(255) NOT NULL,' +
                           'new_value VARCHAR(255) NOT NULL,' +
                           'changed_by INTEGER UNSIGNED NOT NULL,' +
                           'changed_on DATETIME NOT NULL,' +
                           'PRIMARY KEY(id),' +
                           'INDEX changes_issue_idx(issue_id),' +
                           'INDEX changes_changed_idx(changed_by),' +
                           'FOREIGN KEY(issue_id)' +
                           '  REFERENCES issues(id)' +
                           '    ON DELETE CASCADE' +
                           '    ON UPDATE CASCADE,' +
                           'FOREIGN KEY(changed_by)' +
                           '  REFERENCES people(id)' +
                           '    ON DELETE SET NULL' +
                           '    ON UPDATE CASCADE' +
                           ')')

        # Table 'comments'
        self.store.execute('CREATE TABLE IF NOT EXISTS comments (' +
                           'id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT,' +
                           'issue_id INTEGER UNSIGNED NOT NULL,' +
                           'comment TEXT NOT NULL,' +
                           'submitted_by INTEGER UNSIGNED NOT NULL,' +
                           'submitted_on DATETIME NOT NULL,' +
                           'PRIMARY KEY(id),' +
                           'INDEX comments_submitted_idx(submitted_by),' +
                           'INDEX comments_issue_idx(issue_id),' +
                           'FOREIGN KEY(submitted_by)' +
                           '  REFERENCES people(id)' +
                           '    ON DELETE SET NULL' +
                           '    ON UPDATE CASCADE,' +
                           'FOREIGN KEY(issue_id)' +
                           '  REFERENCES issues(id)' +
                           '    ON DELETE CASCADE' +
                           '    ON UPDATE CASCADE' +
                           ')')


class DBTracker(object):
    """
    Maps elements from X{trackers} table.

    @param url: URL of the tracker
    @type url: C{str}
    @param type: type of the tracker
    @type type: C{str}

    @ivar __storm_table__: Name of the database table.
    @type __storm_table__: C{str}

    @ivar id: Tracker identifier.
    @type id: L{storm.locals.Int}
    @ivar url: URL of the tracker.
    @type url: L{storm.locals.Unicode}
    @ivar type: Type of the tracker.
    @type type: L{storm.locals.Unicode}
    @ivar retrieved_on: Shows when the tracker was retrieved.
    @type retrieved_on: L{storm.locals.DateTime}
    """
    __storm_table__ = 'trackers'

    id = Int(primary=True)
    url = Unicode()
    type = Unicode()
    retrieved_on = DateTime()

    def __init__(self, url, type):
        self.url = unicode(url)
        self.type = unicode(type)
        self.retrieved_on = datetime.datetime.now()


class DBPeople(object):
    """
    Maps elements form X{people} table.

    @param user_id: identifier used by this identity in the tracker
    @type user_id: C{str}
    @param tracker_id: identifier of the tracker
    @type tracker_id: C{int}

    @ivar __storm_table__: Name of the database table.
    @type __storm_table__: C{str}

    @ivar id: Identity identifier.
    @type id: L{storm.locals.Int}
    @ivar name: Name of the identity.
    @type name: L{storm.locals.Unicode}
    @ivar email: EMail of the identity.
    @type email: L{storm.locals.Unicode}
    @ivar user_id: Identity identifier used in the tracker.
    @type user_id: L{storm.locals.Unicode}
    @ivar tracker_id: Identifier of the tracker.
    @type tracker_id: L{storm.locals.Int} 
    @ivar tracker: Reference to {DBTracker} object.
    @type tracker: L{storm.locals.Reference}
    """
    __storm_table__ = 'people'

    id = Int(primary=True)
    name = Unicode()
    email = Unicode()
    user_id = Unicode()
    tracker_id = Int()

    tracker = Reference(tracker_id, DBTracker.id)

    def __init__(self, user_id, tracker_id):
        self.user_id = unicode(user_id)
        self.tracker_id = tracker_id

    def set_name(self, name):
        """
        Set the name of the identity.
        
        @param name: name of the identity
        @type name: C{str}
        """
        self.name = unicode(name)

    def set_email(self, email):
        """
        Set the email of the identity.
        
        @param email: email of the identity
        @type email: C{str}
        """
        self.email = unicode(email)


class DBIssue(object):
    """
    Maps elements from X{issues} table.

    @param issue: identifier of the issue
    @type issue: C{str}
    @param tracker_id: identifier of the tracker
    @type tracker_id: C{int}

    @ivar __storm_table__: Name of the database table.
    @type __storm_table__: C{str}

    @ivar id: Database issue identifier.
    @type id: L{storm.locals.Int}
    @ivar issue: Issue identifier. 
    @type issue: L{storm.locals.Unicode}
    @ivar type: Type of the issue.
    @type type: L{storm.locals.Unicode}
    @ivar summary: Summary of the issue.
    @type summary: L{storm.locals.Unicode}
    @ivar description: Description of the issue.
    @type description: L{storm.locals.Unicode}
    @ivar status: Status of the issue.
    @type status: L{storm.locals.Unicode}
    @ivar resolution: Resolution of the issue.
    @type resolution: L{storm.locals.Unicode}
    @ivar priority: Priority of the issue.
    @type priority: L{storm.locals.Unicode}
    @ivar submitted_by: Identifier of the user that submitted the issue.
    @type submitted_by: L{storm.locals.Int}
    @ivar submitted_on: Date when the issue was submitted
    @type submitted_on: L{storm.locals.DateTime}
    @ivar assigned_to: Identifier of the user assigned to this issue.
    @type assigned_to: L{storm.locals.Int}
    @ivar tracker_id: Tracker identifier.
    @type tracker_id: L{storm.locals.Int}
    @ivar tracker: Reference to L{DBTracker} object.
    @type tracker: L{storm.locals.Reference}
    @ivar submitted: Reference to L{DBPeople} object.
    @type submitted: L{storm.locals.Reference}
    @ivar assigned: Reference to L{DBPeople} object.
    @type assigned: L{storm.locals.Reference}
    """
    __storm_table__ = 'issues'

    id = Int(primary=True)
    issue = Unicode()
    type = Unicode()
    summary = Unicode()
    description = Unicode()
    status = Unicode()
    resolution = Unicode()
    priority = Unicode()
    submitted_by = Int()
    submitted_on = DateTime()
    assigned_to = Int()
    tracker_id = Int()
    
    tracker = Reference(tracker_id, DBTracker.id)
    submitted = Reference(submitted_by, DBPeople.id)
    assigned = Reference(assigned_to, DBPeople.id)
    
    def __init__(self, issue, tracker_id):
        self.issue = unicode(issue)
        self.tracker_id = tracker_id


class DBIssueRelationship(object):
    """
    Maps elements from X{related_to} table.

    @param related_to: identifier of the issue related to this one
    @type related_to: C{int}
    @param type: type of relationship
    @type type: C{str}
    @param issue_id: identifier of the issue
    @type issue_id: C{int}

    @ivar __storm_table__: Name of the database table.
    @type __storm_table__: C{str}

    @ivar id: Relationship identifier.
    @type id: L{storm.locals.Int}
    @ivar related_to: Identifier of the issue related to this one
    @type related_to: L{storm.locals.Int}
    @ivar type: Type of the relationship.
    @type type: L{storm.locals.Unicode}
    @ivar issue_id: Issue identifier. 
    @type issue_id: L{storm.locals.Int}
    @ivar issue: Reference to L{DBIssue} object.
    @type issue: L{storm.locals.Reference}
    @ivar relationship: Reference to L{DBIssue} object.
    @type relationship: L{storm.locals.Reference}
    """
    __storm_table__ = 'related_to'

    id = Int(primary=True)
    related_to = Int()
    type = Unicode()
    issue_id = Int()

    issue = Reference(issue_id, DBIssue.id)
    relationship = Reference(related_to, DBIssue.id)

    def __init__(self, related_to, type, issue_id):
        self.related_to = related_to
        self.type = unicode(type)
        self.issue_id = issue_id


class DBComment(object):
    """
    Maps elements from X{comments} table.

    @param comment: comment of the issue
    @type comment: C{str}
    @param submitted_by: identifier of the user that submitted the comment
    @type submitted_by: C{int}
    @param submitted_on: date when the comment was submitted
    @type submitted_on: L{datetime.datetime}
    @param issue_id: identifier of the issue
    @type issue_id: C{int}

    @ivar __storm_table__: Name of the database table.
    @type __storm_table__: C{str}

    @ivar id: Comment identifier.
    @type id: L{storm.locals.Int}
    @ivar comment: Comment of the issue. 
    @type comment: L{storm.locals.Unicode}
    @ivar submitted_by: Identifier of the submitter.
    @type submitted_by: L{storm.locals.Int}
    @ivar submitted_on: Date when the comment was submitted
    @type submitted_on: L{storm.locals.DateTime}
    @ivar issue: Reference to L{DBIssue} object.
    @type issue: L{storm.locals.Reference}
    @ivar submitted: Reference to L{DBPeople} object.
    @type submitted: L{storm.locals.Reference}
    @ivar issue_id: Issue identifier.
    @type issue_id: L{storm.locals.Int}   
    """
    __storm_table__ = 'comments'

    id = Int(primary=True)
    comment = Unicode()
    submitted_by = Int()
    submitted_on = DateTime()
    issue_id = Int()

    issue = Reference(issue_id, DBIssue.id)
    submitted = Reference(submitted_by, DBPeople.id)
    
    def __init__(self, comment, submitted_by, submitted_on, issue_id):
        self.comment = unicode(comment)
        self.submitted_by = submitted_by
        self.submitted_on = submitted_on
        self.issue_id = issue_id


class DBAttachment(object):
    """
    Maps elements from X{attachments} table.

    @param name: name of the attachment
    @param description: description of the attachment
    @param url: URL of the attachement
    @param submitted_by: identifier of the user that uploaded the attachment
    @type submitted_by: C{int}
    @param submitted_on: date when the attachment was uploaded
    @type submitted_on: L{datetime.datetime}
    @param issue_id: identifier of the issue
    @type issue_id: C{int}

    @ivar __storm_table__: Name of the database table.
    @type __storm_table__: C{str}

    @ivar id: Attachment identifier.
    @type id: L{storm.locals.Int}
    @ivar name: Name of the attachment. 
    @type name: L{storm.locals.Unicode}
    @ivar description: Description of the attachment. 
    @type description: L{storm.locals.Unicode}
    @ivar url: URL of the attachment. 
    @type url: L{storm.locals.Unicode}
    @ivar submitted_by: Identifier of the submitter.
    @type submitted_by: L{storm.locals.Int}
    @ivar submitted_on: Date when the attachment was uploaded
    @type submitted_on: L{storm.locals.DateTime}
    @ivar issue_id: Issue identifier.
    @type issue_id: L{storm.locals.Int}
    @ivar issue: Reference to L{DBIssue} object.
    @type issue: L{storm.locals.Reference}
    @ivar submitted: Reference to L{DBPeople} object.
    @type submitted: L{storm.locals.Reference}   
    """
    __storm_table__ = 'attachments'

    id = Int(primary=True)
    name = Unicode()
    description = Unicode()
    url = Unicode()
    submitted_by = Int()
    submitted_on = DateTime()
    issue_id = Int()

    issue = Reference(issue_id, DBIssue.id)
    submitted = Reference(submitted_by, DBPeople.id)

    def __init__(self, name, description, url, submitted_by, submitted_on, issue_id):
        self.name = unicode(name)
        self.description = unicode(description)
        self.url = unicode(url)
        self.submitted_by = submitted_by
        self.submitted_on = submitted_on
        self.issue_id = issue_id


class DBChange(object):
    """
    Maps elements from X{changes} table.

    @param field: name field that was change
    @type field: C{str}
    @param old_value: old field value
    @type old_value: C{str}
    @param new_value: new field value
    @type new_value: C{str}
    @param changed_by: identifier of the user that made the change
    @type changed_by: C{int}
    @param changed_on: date when the change was made
    @type changed_on: L{datetime.datetime}
    @param issue_id: identifier of the issue
    @type issue_id: C{int}

    @ivar __storm_table__: Name of the database table.
    @type __storm_table__: C{str}

    @ivar id: Change identifier.
    @type id: L{storm.locals.Int}
    @ivar field: Field that was changed. 
    @type field: L{storm.locals.Unicode}
    @ivar old_value: Old field value. 
    @type old_value: L{storm.locals.Unicode}
    @ivar new_value: New field value. 
    @type new_value: L{storm.locals.Unicode}
    @ivar changed_by: Identifier of the user that made the change.
    @type changed_by: L{storm.locals.Int}
    @ivar changed_on: Date when the change was produced
    @type changed_on: L{storm.locals.DateTime}
    @ivar issue_id: Issue identifier.
    @type issue_id: L{storm.locals.Int}
    @ivar issue: Reference to L{DBIssue} object.
    @type issue: L{storm.locals.Reference}
    @ivar people: Reference to L{DBPeople} object.
    @type people: L{storm.locals.Reference}   
    """
    __storm_table__ = 'changes'

    id = Int(primary=True)
    field = Unicode()
    old_value = Unicode()
    new_value = Unicode()
    changed_by = Int()
    changed_on = DateTime()
    issue_id = Int()

    issue = Reference(issue_id, DBIssue.id)
    people = Reference(changed_by, DBPeople.id)

    def __init__(self, field, old_value, new_value, changed_by, changed_on, issue_id):
        self.field = unicode(field)
        self.old_value = unicode(old_value)
        self.new_value = unicode(new_value)
        self.changed_by = changed_by
        self.changed_on = changed_on
        self.issue_id = issue_id


def getDatabase():
    """
    """
    opts = Config()

    if opts.db_driver_out == "mysql":
        return DBMySQL()
