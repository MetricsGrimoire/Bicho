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
Database module
"""

import datetime

from storm.exceptions import IntegrityError # DatabaseError,
from storm.locals import DateTime, Int, Reference, Unicode

from Bicho.utils import printdbg
from Bicho.Config import Config


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
    def __init__(self, backend=None):
        self.database = None
        self.store = None
        self.backend = backend

    def create_tables(self, clsl):
        """
        Create the database tables.

        SQL query with the structure of each table is stored into 
        X{__sql_table__} attribute of database classes. 

        @param clsl: a list of database classes
        @type clsl: C{list} of L{object}
        """
        for c in clsl:
            self.store.execute(c.__sql_table__)

    def insert_supported_traker(self, name, version):
        """
        Insert a supported type of tracker.

        @param name: name or type of the tracker
        @type name: C{str}
        @param version: version of the tracker
        @type version: C{str}

        @return: the inserted type
        @rtype: L{DBSupportedTracker}
        """
        try:
            db_sup = DBSupportedTracker(name, version)
            self.store.add(db_sup)
            self.store.commit()
        except:
            db_sup = self._get_db_supported_tracker(name, version)
        return db_sup

    def insert_tracker(self, tracker):
        """
        Insert the given tracker.

        @param tracker: tracker to insert
        @type tracker: L{Tracker}

        @return: the inserted tracker
        @rtype: L{DBTracker}
        """
        try:
            db_sup = self._get_db_supported_tracker(tracker.name,
                                                    tracker.version)
        except:
            raise

        try:
            db_tracker = DBTracker(tracker.url, db_sup.id)
            self.store.add(db_tracker)
            self.store.commit()
        except:
            db_tracker = self._get_db_tracker(tracker.url)
            db_tracker.retrieved_on = datetime.datetime.now()
            self.store.commit()
        return db_tracker

    def insert_people(self, people):
        """
        Insert the given identity.

        @param people: identity to insert
        @type people: L{People}

        @return: the inserted identity
        @rtype: L{People}
        """
        try:
            db_people = DBPeople(people.user_id)
            db_people.set_name(people.name)
            db_people.set_email(people.email)
            self.store.add(db_people)
            self.store.commit()
        except IntegrityError:
            db_people = self._get_db_people(people.user_id)
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

        newIssue = False;

        try:
            db_issue = self._get_db_issue(issue.issue, tracker_id)

            #if issue does not in the tracker, we create a new one
            if db_issue == -1:
                newIssue = True
                db_issue = DBIssue(issue.issue, tracker_id)

            #update the data, or take the new one
            db_issue.type = unicode(issue.type)
            db_issue.summary = unicode(issue.summary)
            db_issue.description = unicode(issue.description)
            db_issue.status = unicode(issue.status)
            db_issue.resolution = unicode(issue.resolution)
            db_issue.priority = unicode(issue.priority)
            db_issue.submitted_by = self.insert_people(issue.submitted_by).id
            

            db_issue.submitted_on = issue.submitted_on
            
            if issue.assigned_to is not None:
                db_issue.assigned_to = self.insert_people(issue.assigned_to).id

            #if issue is new, we add to the data base before the flush()
            if newIssue == True:
                self.store.add(db_issue)

            self.store.flush()

            # Insert extra data of the issue, if any
            if self.backend is not None:
                self.backend.insert_issue_ext(self.store, issue, db_issue.id)

            # Insert temporal relationships
            for trel in issue.temp_relationships:
                db_trel = self._get_db_temp_rel(trel, db_issue.id)
                if db_trel == -1:
                    db_trel = self._insert_temp_rel(trel, db_issue.id, tracker_id)
                    if self.backend is not None:
                        self.backend.insert_temp_rel(self.store, trel, db_trel, tracker_id)

            # Insert comments
            for comment in issue.comments:
                db_comment = self._get_db_comment(comment, db_issue.id, tracker_id)
                if db_comment == -1:
                    db_comment = self._insert_comment(comment, db_issue.id, tracker_id)
                    if self.backend is not None:
                        self.backend.insert_comment_ext(self.store, comment, db_comment.id)

            # Insert attachments
            for attachment in issue.attachments:
                db_attch = self._get_db_attachment(attachment, db_issue.id, tracker_id)
                if db_attch == -1:
                    db_attch = self._insert_attachment(attachment, db_issue.id, tracker_id)
                    if self.backend is not None:
                        self.backend.insert_attachment_ext(self.store, attachment, db_attch.id)

            # Insert changes
            for change in issue.changes:
                db_change = self._get_db_change(change, db_issue.id, tracker_id)
                if db_change == -1:
                    db_change = self._insert_change(change, db_issue.id, tracker_id)
                    if self.backend is not None:
                        self.backend.insert_change_ext(self.store, change, db_change.id)

            # Insert CC/watchers
            for person in issue.watchers:
                try:
                    #db_issues_watchers = self._insert_issues_watchers(person, db_issue.id,
                    #                                                  tracker_id)
                    self._insert_issues_watchers(person, db_issue.id, tracker_id)
                except:
                    None

            self.store.commit()

            return db_issue
        except:
            self.store.rollback()
            raise

    def get_last_modification_date(self, state = None):
        """
        Return last modification date stored in database
        """
        if self.backend is not None:
            # in the github backend we need to get both open and closed
            # issues in two different petitions
            if state:
                return self.backend.get_last_modification_date(self.store, state)
            else:
                return self.backend.get_last_modification_date(self.store)

    def _insert_relationship(self, issue_id, type, rel_id):
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

    def _insert_temp_rel(self, relationship, issue_id, tracker_id):
        """
        Insert temporal relationships for the issue X{issue_id}

        @return: the inserted relationship
        @rtype: L{DBComment}
        """
        db_temp_rel = DBIssueTempRelationship(relationship.issue,
                                              relationship.type,
                                              relationship.related_to,
                                              tracker_id)

        self.store.add(db_temp_rel)
        self.store.flush()
        return db_temp_rel

    def store_final_relationships(self):
        """
        """
        temp_rels = self.store.find(DBIssueTempRelationship)

        for tr in temp_rels:
            aux_issue_id = self._get_db_issue(tr.issue_id, tr.tracker_id)
            aux_related_to = self._get_db_issue(tr.related_to, tr.tracker_id)
            if (aux_related_to != -1 and aux_issue_id != -1):
                self._insert_relationship(aux_issue_id.id, tr.type, aux_related_to.id)
            else:
                printdbg("Issue %s belongs to a different tracker and won't be stored" % tr.related_to)

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
        submitted_by = self.insert_people(comment.submitted_by)

        db_comment = DBComment(comment.comment, submitted_by.id,
                               comment.submitted_on, issue_id)
        self.store.add(db_comment)
        try:
            self.store.flush()
        except UnicodeEncodeError:
            print("UnicodeEncodeError: one of the comments of the issue_id " + \
                  "%s couldn't be stored" % (issue_id))
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
        if attachment.submitted_by is not None:
            submitter = self.insert_people(attachment.submitted_by)
            submitted_by = submitter.id
        else:
            submitted_by = None

        db_attachment = DBAttachment(attachment.name, attachment.description,
                                     attachment.url, submitted_by, 
                                     attachment.submitted_on, issue_id)
        self.store.add(db_attachment)
        self.store.flush()
        return db_attachment

    def _insert_change(self, change, issue_id, tracker_id):
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
        changed_by = self.insert_people(change.changed_by)

        db_change = DBChange(change.field, change.old_value, change.new_value, 
                             changed_by.id, change.changed_on, issue_id)
        self.store.add(db_change)
        self.store.flush()
        return db_change

    def _insert_issues_watchers(self, people, issue_id, tracker_id):
        """
        Insert watchers for the issue X{issue_id}

        @return: the inserted comment
        @rtype: L{DBComment}
        """
        watcher = self.insert_people(people)

        db_issues_watchers = DBIssuesWatchers(issue_id, watcher.id)

        self.store.add(db_issues_watchers)
        self.store.flush()
        return db_issues_watchers

    def _get_db_supported_tracker(self, name, version):
        """
        Get the supported tracker based on the given name and version.

        @param name: name or type of the tracker
        @type name: C{str}
        @param version: version ot the tracker
        @type version: C{str}

        @return: The selected supported tracker.
        @rtype: L{DBSupportedTracker}

        @raise NotFoundError: when the supported type of tracker is not found.
        """
        db_sup = self.store.find(DBSupportedTracker,
                                 DBSupportedTracker.name == unicode(name),
                                 DBSupportedTracker.version == unicode(version)).one()
        if not db_sup:
            raise NotFoundError('Supported tracker %s (v. %s) not found' % (name, version))
        return db_sup

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

    def _get_db_people(self, user_id):
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
        try:
            db_people = self.store.find(DBPeople,
                                        DBPeople.user_id == unicode(user_id)).one()
        except Exception, e:
            print e
            
        if not db_people:
            raise NotFoundError('Idenitity %s not found in tracker %s' % 
                                (user_id, tracker_id))
        return db_people

    def _get_db_issue(self, issue, tracker_id):
        """
        Get the identity based on the given id.

        @param issue: issue identifier
        @type issue: C{str}
        @param tracker_id: identifier of the tracker
        @type tracker_id: C{int}

        @return: The selected identity.
        @rtype: L{DBIssue}

        @raise NotFoundError: When the identity is not found.
        """
        db_issue = self.store.find(DBIssue,
                                    DBIssue.issue == unicode(issue),
                                    DBIssue.tracker_id == tracker_id).one()
        if not db_issue:
            #if the issue is not stored, return -1 to know its a new one
            db_issue = -1

        return db_issue

    def _get_db_comment(self,comment, issue_id, tracker_id):
        """
        Search a comment for the issue X{issue_id}

        @param comment: comment to insert
        @type comment: L{Comment}
        @param issue_id: issue identifier
        @type issue_id: C{int}
        @param tracker_id: identifier of the tracker
        @type tracker_id: C{int}

        """
        db_comment = self.store.find(DBComment,
                                    DBComment.issue_id == issue_id,
                                    DBComment.text == comment.comment,
                                    DBComment.submitted_on == comment.submitted_on).one()
        if not db_comment:
            #if comment is not stored, return -1 to know it's a new one
            db_comment = -1

        return db_comment

    def _get_db_change(self,change, issue_id, tracker_id):
        """
        Search a change for the issue X{issue_id}

        @param change: change to insert
        @type change: L{Change}
        @param issue_id: issue identifier 
        @type issue_id: C{int}
        @param tracker_id: identifier of the tracker
        @type tracker_id: C{int}

        """
        #source forge don't have new_value so we recived
        #a string that must be unicode
        if change.new_value == "unknown":
            change.new_value = unicode(change.new_value)

        db_change = self.store.find(DBChange,
                                    DBChange.issue_id == issue_id,
                                    DBChange.field == change.field,
                                    DBChange.changed_on == change.changed_on,
                                    DBChange.old_value == change.old_value,
                                    DBChange.new_value == change.new_value).one()
        if not db_change:
            #if change is not stored, return -1 to know it's a new one
            db_change = -1

        return db_change

    def _get_db_attachment(self, attachment, issue_id, tracker_id):
        """
        Search an attachment for the issue X{issue_id}

        @param attachment: attachment to insert
        @type attachment: L{Attachment}
        @param issue_id: issue identifier 
        @type issue_id: C{int}
        @param tracker_id: identifier of the tracker
        @type tracker_id: C{int}

        """
        db_attachment = self.store.find(DBAttachment,
                                    DBAttachment.issue_id == issue_id,
                                    DBAttachment.url == attachment.url,
                                    DBAttachment.submitted_on == attachment.submitted_on).one()
        if not db_attachment:
            #if attachment is not stored, return -1 to know it's a new one
            db_attachment = -1

        return db_attachment

    def _get_db_temp_rel(self, t_relationship, issue_id):
        """
        """
        #DBIssueTempRelationship
        db_temp_rel = self.store.find(DBIssueTempRelationship,
                                      DBIssueTempRelationship.issue_id == issue_id,
                                      DBIssueTempRelationship.type == t_relationship.type,
                                      DBIssueTempRelationship.related_to == t_relationship.related_to).one()

        if not db_temp_rel:
            db_temp_rel = -1

        return db_temp_rel                                      


class DBSupportedTracker(object):
    """
    Maps elements from X{supported_trackers} table.

    @param name: name or type of the supported tracker
    @type type: C{str}
    @param version: version of tracker
    @type version: C{str}

    @ivar __storm_table__: Name of the database table.
    @type __storm_table__: C{str}

    @ivar id: Supported tracker identifier.
    @type id: L{storm.locals.Int}
    @ivar type: name or type of the supported tracker.
    @type type: L{storm.locals.Unicode}
    @ivar version: version of tracker.
    @type version: L{storm.locals.Unicode}
    """
    __storm_table__ = 'supported_trackers'

    id = Int(primary=True)
    name = Unicode()
    version = Unicode()

    def __init__(self, name, version):
        self.name = unicode(name)
        self.version = unicode(version)


class DBTracker(object):
    """
    Maps elements from X{trackers} table.

    @param url: URL of the tracker
    @type url: C{str}
    @param type: type of tracker
    @type type: C{str}

    @ivar __storm_table__: Name of the database table.
    @type __storm_table__: C{str}

    @ivar id: Tracker identifier.
    @type id: L{storm.locals.Int}
    @ivar url: URL of the tracker.
    @type url: L{storm.locals.Unicode}
    @ivar type: Type of supported tracker.
    @type type: L{storm.locals.Unicode}
    @ivar retrieved_on: Shows when the tracker was retrieved.
    @type retrieved_on: L{storm.locals.DateTime}
    @ivar trktype: Reference to {DBTrackerType} object.
    @type trktype: L{storm.locals.Reference}
    """
    __storm_table__ = 'trackers'

    id = Int(primary=True)
    url = Unicode()
    type = Int()
    retrieved_on = DateTime()

    supported = Reference(type, DBSupportedTracker.id)

    def __init__(self, url, type):
        self.url = unicode(url)
        self.type = type
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

    def __init__(self, user_id):
        self.user_id = unicode(user_id)

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

class DBIssuesWatchers(object):
    """
    Relates elements from X{People} and X{Issues} tables

    """
    __storm_table__ = 'issues_watchers'

    id = Int(primary=True)
    issue_id = Int()
    person_id = Int()
    issue = Reference(issue_id, DBIssue.id)
    person = Reference(person_id, DBPeople.id)

    def __init__(self, issue_id, person_id):
        self.issue_id = issue_id
        self.person_id = person_id


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

class DBIssueTempRelationship(object):
    """
    Store temporal relationships between issues

    @param related_to: identifier of the issue related to this one
    @type related_to: C{int}
    @param type: type of relationship
    @type type: C{str}
    @param issue_id: identifier of the issue in the tracker
    @type issue_id: C{str}
    @param tracker: identifier of the tracker of both issues
    @type tracker: C{int}

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
    __storm_table__ = 'temp_related_to'

    id = Int(primary=True)
    issue_id = Int()
    type = Unicode()
    related_to = Unicode()
    tracker_id = Int()

    issue = Reference(issue_id, DBIssue.id)
    #relationship = Reference(related_to, DBIssue.id)

    def __init__(self, issue_id, type, related_to, tracker_id):
        self.related_to = related_to
        self.type = unicode(type)
        self.issue_id = issue_id
        self.tracker_id = tracker_id


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
    text = Unicode()
    submitted_by = Int()
    submitted_on = DateTime()
    issue_id = Int()

    issue = Reference(issue_id, DBIssue.id)
    submitted = Reference(submitted_by, DBPeople.id)

    def __init__(self, text, submitted_by, submitted_on, issue_id):
        self.text = unicode(text)
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


class DBBackend:
    """
    """
    def __init__(self):
        self.MYSQL_EXT = None

    def insert_issue_ext(self, ext, issue_id):
        """
        Abstract method for inserting extra data related to an issue
        """
        raise NotImplementedError

    def insert_comment_ext(self, comment, comment_id):
        """
        Abstract method for inserting extra data related to a comment
        """
        raise NotImplementedError

    def insert_attachment_ext(self, attch, attch_id):
        """
        Abstract method for inserting extra data related to an attachment
        """
        raise NotImplementedError

    def insert_change_ext(self, change, change_id):
        """
        Abstract method for inserting extra data related to a change
        """
        raise NotImplementedError

    def get_last_modification_date(self, ext):
        """
        Abstract method for obtaining the last change stored in the database
        """
        raise NotImplementedError


def get_database(backend=None):
    """
    """
    opts = Config
    if not vars(Config).has_key('url'):
        opts = Config()

    if opts.db_driver_out == "mysql":
        from Bicho.db.mysql import DBMySQL
        return DBMySQL(backend)
    
