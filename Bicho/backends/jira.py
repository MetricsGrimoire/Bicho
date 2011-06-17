# -*- coding: utf-8 -*-
# Copyright (C) 2007-2011 GSyC/LibreSoft, Universidad Rey Juan Carlos
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Authors: Daniel Izquierdo Cortazar <dizquierdo@gsyc.es>
#          Juan Francisco Gato Luis <jfcogato@libresoft.es>
#          Luis Cañas Díaz <lcanas@libresoft.es>
#          Santiago Dueñas <sduenas@libresoft.es>

import datetime
import urllib
import time

from storm.locals import Int, DateTime, Unicode, Reference

from dateutil.parser import parse

from Bicho.common import Issue, People, Tracker, Comment, Change, Attachment
from Bicho.backends import Backend, register_backend
from Bicho.db.database import DBIssue, DBBackend, get_database
from Bicho.Config import Config
from Bicho.utils import printout, printerr, printdbg

from BeautifulSoup import BeautifulSoup
#from BeautifulSoup import NavigableString
from BeautifulSoup import Comment as BFComment
#from Bicho.Config import Config
#from Bicho.utils import *

import xml.sax.handler
#from xml.sax._exceptions import SAXParseException



class DBJiraIssueExt(object):
    """
    """
    __storm_table__ = 'issues_ext_jira'

    id = Int(primary=True)
    issue_key = Unicode()
    link = Unicode()
    title = Unicode()
    environment = Unicode()    
    security = Unicode()
    updated = DateTime()
    version = Unicode()
    component = Unicode()
    votes = Int()
    project = Unicode()
    project_id = Int
    project_key = Unicode()
    status = Unicode()
    resolution = Unicode()

    issue_id = Int()

    issue = Reference(issue_id, DBIssue.id)

    def __init__(self, issue_id):
        self.issue_id = issue_id


class DBJiraIssueExtMySQL(DBJiraIssueExt):
    """
    MySQL subclass of L{DBJiraIssueExt}
    """

    __sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_ext_jira ( \
                     id INTEGER NOT NULL AUTO_INCREMENT, \
                     issue_key VARCHAR(32) NOT NULL, \
                     link VARCHAR(100) NOT NULL, \
                     title VARCHAR(100) NOT NULL, \
                     environment VARCHAR(35) NOT NULL, \
                     security VARCHAR(35) NOT NULL, \
                     updated DATETIME NOT NULL, \
                     version VARCHAR(35) NOT NULL, \
                     component VARCHAR(35) NOT NULL, \
                     votes INTEGER UNSIGNED, \
                     project VARCHAR(35) NOT NULL, \
                     project_id INTEGER UNSIGNED, \
                     project_key VARCHAR(35) NOT NULL, \
                     status  VARCHAR(35) NOT NULL, \
                     resolution VARCHAR(35) NOT NULL, \
                     issue_id INTEGER NOT NULL, \
                     PRIMARY KEY(id), \
                     UNIQUE KEY(issue_id), \
                     INDEX ext_issue_idx(issue_id), \
                     FOREIGN KEY(issue_id) \
                       REFERENCES issues (id) \
                         ON DELETE CASCADE \
                         ON UPDATE CASCADE \
                     );'


class DBJiraBackend(DBBackend):
    """
    Adapter for Jira backend.
    """
    def __init__(self):
        self.MYSQL_EXT = [DBJiraIssueExtMySQL]

    def insert_issue_ext(self, store, issue, issue_id):
        """
        Insert the given extra parameters of issue with id X{issue_id}.

        @param store: database connection
        @type store: L{storm.locals.Store}
        @param issue: issue to insert
        @type issue: L{JiraIssue}
        @param issue_id: identifier of the issue
        @type issue_id: C{int}

        @return: the inserted extra parameters issue
        @rtype: L{DBJiraIssueExt}
        """
        
        newIssue = False;

        try:
            db_issue_ext = store.find(DBJiraIssueExt,
                                    DBJiraIssueExt.issue_id == issue_id).one()
            if not db_issue_ext:
                newIssue = True
                db_issue_ext = DBJiraIssueExt(issue_id)
            
            db_issue_ext.title = self.__return_unicode(issue.title)
            db_issue_ext.issue_key = self.__return_unicode(issue.issue_key)
            db_issue_ext.link = self.__return_unicode(issue.link)
            db_issue_ext.environment = self.__return_unicode(issue.environment)
            db_issue_ext.security = self.__return_unicode(issue.security)
            db_issue_ext.updated = issue.updated
            db_issue_ext.version = self.__return_unicode(issue.version)
            db_issue_ext.component = self.__return_unicode(issue.component)
            db_issue_ext.votes = issue.votes
            db_issue_ext.project = self.__return_unicode(issue.project)
            db_issue_ext.project_id = issue.project_id
            db_issue_ext.project_key = self.__return_unicode(issue.project_key)
            db_issue_ext.status = self.__return_unicode(issue.status)
            db_issue_ext.resolution = self.__return_unicode(issue.resolution)

            if newIssue == True:
                store.add(db_issue_ext)

            store.flush()
            return db_issue_ext
        except:
            store.rollback()
            raise

    def __return_unicode(self, str):
        """
        Decodes string and pays attention to empty ones
        """
        if str:
            return unicode(str)
        else:
            return unicode('')
    def insert_comment_ext(self, store, comment, comment_id):
        """
        Does nothing
        """
        pass

    def insert_attachment_ext(self, store, attch, attch_id):
        """
        Does nothing
        """
        pass

    def insert_change_ext(self, store, change, change_id):
        """
        Does nothing
        """
        pass


####################################

class JiraIssue(Issue):
    """
    Ad-hoc Issue extensions for jira's issue
    """
    def __init__(self,issue, type, summary, description, submitted_by, submitted_on):
        Issue.__init__(self,issue, type, summary, description, submitted_by, submitted_on)
        
        self.title = None
        self.issue_key = None
        self.link = None
        self.environment = None
        self.security = None
        self.updated = None
        self.version = None
        self.component = None
        self.votes = None
        self.project = None
        self.project_id = None
        self.project_key = None
        self.status = None
        self.resolution = None

    def setStatus(self, status):
        self.status = status

    def setResolution(self, resolution):
        self.resolution = resolution

    def setTitle(self, title): 
        self.title = title

    def setIssue_key(self, issue_key):
        self.issue_key = issue_key

    def setLink(self, link):
        self.link = link

    def setEnvironment(self, environment):
        self.environment = environment

    def setSecurity(self, security):
        self.security = security;

    def setUpdated(self, updated):
        self.updated = updated
    
    def setVersion(self, version):
        self.version = version

    def setComponent(self, component):
        self.component = component

    def setVotes(self, votes):
        self.votes = votes

    def setProject(self, project):
        self.project = project
    
    def setProject_id(self, project_id):
        self.project_id = project_id
    
    def setProject_key(self, project_key):
        self.project_key = project_key
    
class JiraComment():
    def __init__(self):
        self.comment = None
        self.comment_id = None
        self.comment_author = None
        self.comment_created = None

class JiraAttachment():
    def __init__(self):
        self.attachment_id = None
        self.attachment_name = None
        self.attachment_size = None
        self.attachment_author = None
        self.attachment_created = None

class Customfield():
    def __init__(self):
        self.customfield_id = None
        self.customfield_key = None
        self.customfieldname = None
        self.customfieldvalue = None

class Bug():
    
    def __init__ (self):
        self.title = None
        self.link = None
        self.description = ""
        self.environment = None
        self.summary = None
        self.bug_type = None
        self.status = None
        self.resolution = None
        self.security = None
        self.created = None
        self.updated = None
        self.version = None
        self.component = None
        self.votes = None   
        self.project = None
        self.project_id = None
        self.project_key = None
        self.issue_key = None
        self.key_id = None
        self.assignee = None
        self.assignee_usarname = None
        self.reporter = None
        self.reporter_username = None
        
        self.comments = [] 
        self.attachments = []
        self.customfields = []

class SoupHtmlParser():

    def __init__ (self, html, idBug):
        self.html = html
        self.idBug = idBug

    def remove_comments(self, soup):
        cmts = soup.findAll(text=lambda text:isinstance(text, BFComment))
        [comment.extract() for comment in cmts]

    def parse_changes(self):
        soup = BeautifulSoup(self.html)
        self.remove_comments(soup)
        remove_tags = ['a', 'span','i']
        try:
            [i.replaceWith(i.contents[0]) for i in soup.findAll(remove_tags)]
        except Exception:
            None
        
        changes = []      
        #FIXME The id of the changes are not stored
        tables = soup.findAll("div", {"class": "actionContainer"})
        table = None
    
        for table in tables:
            change_author = table.find("div", {"class": "action-details"})
            
            if change_author == None:
                break
            author = People(change_author.contents[2].strip())
            date = parse(change_author.contents[4]).replace(tzinfo=None)
 
            rows = list(table.findAll('tr'))
            for row in rows:
                cols = list(row.findAll('td'))
                if len(cols) == 3:
                    field = unicode(cols[0].contents[0].strip())
                    old = unicode(cols[1].contents[0].strip())
                    new = unicode(cols[2].contents[0].strip())
                    
                    change = Change(field, old, new, author, date)
                    changes.append(change)
        return changes

class BugsHandler(xml.sax.handler.ContentHandler):

    def __init__ (self):
        
        #store all bugs
        self.mapping = []
        self.comments = []
        self.attachments = []
        self.customfields = []

        self.title = None
        self.link = None
        self.description = ""
        self.environment = ""
        self.summary = None
        self.bug_type = None
        self.status = None
        self.resolution = None
        self.security = None
        self.created = None
        self.updated = None
        self.version = None
        self.component = None
        self.votes = None

        self.project = None
        self.project_id = None
        self.project_key = None
        self.issue_key = None
        self.key_id = None
        self.assignee = None
        self.assignee_username = None
        self.reporter = None
        self.reporter_username = None
        self.comment = ""
        self.comment_id = None
        self.comment_author = None
        self.comment_created = None
        self.attachment_id = None
        self.attachment_name = None
        self.attachment_size = None
        self.attachment_author = None
        self.attachment_created = None
        self.customfield_id = None
        self.customfield_key = None
        self.customfieldname = None
        self.customfieldvalue = None

        #control data
        self.first_desc = True
        self.is_title = False
        self.is_link = False
        self.is_description = False
        self.is_environment = False
        self.is_summary = False
        self.is_bug_type = False
        self.is_status = False
        self.is_resolution = False
        self.is_security = False
        self.is_created = False
        self.is_updated = False
        self.is_version = False
        self.is_component = False
        self.is_votes = False

        self.is_project = False
        self.is_issue_key = False
        self.is_assignee = False
        self.is_reporter = False
        self.is_comment = False
        self.is_customfieldname = False
        self.is_customfieldvalue = False

    def startElement(self, name, attrs):      
        if name == 'title':
            self.is_title = True
        elif name == 'link':
            self.is_link = True
        elif name == 'description':
            self.is_description = True
        elif name == 'environment':
            self.is_environment = True
        elif name == 'summary':
            self.is_summary = True
        elif name == 'type':
            self.is_bug_type = True
        elif name == 'status':
            self.is_status = True
        elif name == 'resolution':
            self.is_resolution = True
        elif name == 'security':
            self.is_security = True
        elif name == 'created':
            self.is_created = True
        elif name == 'updated':
            self.is_updated = True
        elif name == 'version':
            self.is_version = True
        elif name == 'component':
            self.is_component = True
        elif name == 'votes':
            self.is_votes = True
        elif name == 'project':
            self.is_project = True
            self.project_id = str(attrs['id'])
            self.project_key = str(attrs['key'])
        elif name == 'key':
            self.is_issue_key = True
            self.key_id = attrs['id']
        elif name == 'assignee':
            self.is_assignee = True
            self.assignee_username = str(attrs['username'])
        elif name == 'reporter':
            self.is_reporter = True
            self.reporter_username = str(attrs['username'])
        elif name == 'comment':
            self.is_comment = True
            self.comment_id = attrs['id']
            self.comment_author = attrs['author']
            self.comment_created = attrs['created']
        elif name == 'attachment':
            #no data in characters
            self.attachment_id = attrs['id']
            self.attachment_name = attrs['name']
            self.attachment_size = attrs['size']
            self.attachment_author = attrs['author']
            self.attachment_created = attrs['created']
        elif name == 'customfield':
            self.customfield_id = attrs['id']
            self.customfield_key = attrs['key']
        elif name == 'customfieldname':
            self.is_customfieldname = True
        elif name == 'customfieldvalues':
            self.is_customfieldvalue = True    


    def characters(self, ch):
        if self.is_title:
            self.title = str(ch)
        elif self.is_link:
            self.link = str(ch)
        elif self.is_description:
            #FIXME problems with ascii, not support str() function
            if (self.first_desc == True):
                self.first_desc = False
            else:
                self.description = self.description + ch.strip()
        elif self.is_environment:
            self.environment = self.environment + str(ch)
        elif self.is_summary:
            self.summary = str(ch)
        elif self.is_bug_type:
            self.bug_type = str(ch)
        elif self.is_status:
            self.status = str(ch)
        elif self.is_resolution:
            self.resolution = str(ch)
        elif self.is_security:
            print str(ch)
            self.security = str(ch)
        elif self.is_assignee:
            #FIXME problems with ascii, not support str() function
            self.assignee = ch
        elif self.is_reporter:
            #FIXME problems with ascii, not support str() function
            self.reporter = ch
        elif self.is_created:
            self.created = str(ch)
        elif self.is_updated:
            self.updated = str(ch)
        elif self.is_version:
            self.version = str(ch)
        elif self.is_component:
            self.component = str(ch)
        elif self.is_votes:
            self.votes = int(ch)
        elif self.is_project:
            self.project = str(ch)
        elif self.is_issue_key:
            self.issue_key = str(ch)
        elif self.is_comment:
            #FIXME problems with ascii, not support str() function
            self.comment = self.comment + ch
        elif self.is_customfieldname:
            self.customfieldname = ch
        elif self.is_customfieldvalue:
            if ch.lstrip().__len__() != 0:
                self.customfieldvalue = ch.lstrip()


    def endElement(self, name):
        if name == 'title':
            self.is_title = False
        elif name == 'link':
            self.is_link = False
        elif name == 'project':
            self.is_project = False
        elif name == 'description':
            self.is_description = False
        elif name == 'environment':
            self.is_environment = False
        elif name == 'key':
            self.is_issue_key = False
        elif name == 'summary':
            self.is_summary = False
        elif name == 'type':
            self.is_bug_type = False
        elif name == 'status':
            self.is_status = False
        elif name == 'resolution':
            self.is_resolution = False
        elif name == 'security':
            self.is_security = False
        elif name == 'assignee':
            self.is_assignee = False
        elif name == 'reporter':
            self.is_reporter = False
        elif name == 'created':
            self.is_created = False
        elif name == 'updated':
            self.is_updated = False
        elif name == 'version':
            self.is_version = False
        elif name == 'component':
            self.is_component = False
        elif name == 'votes':
            self.is_votes = False
        elif name == 'comment':
            self.is_comment = False
            newComment = JiraComment()
            newComment.comment = self.comment
            newComment.comment_id = self.comment_id
            newComment.comment_author = self.comment_author
            newComment.comment_created = self.comment_created
            self.comments.append(newComment)  
            self.comment = ""
        
        elif name == 'attachment':
            newAttachment = JiraAttachment()
            newAttachment.attachment_id = self.attachment_id
            newAttachment.attachment_name = self.attachment_name
            newAttachment.attachment_size = self.attachment_size
            newAttachment.attachment_author = self.attachment_author
            newAttachment.attachment_created = self.attachment_created
            self.attachments.append(newAttachment)
        
        elif name == 'customfieldname':
            self.is_customfieldname = False
        elif name == 'customfieldvalues':
            self.is_customfieldvalue = False
        
        elif name == 'customfield':
            newCustomfield = Customfield()
            newCustomfield.customfield_id = self.customfield_id
            newCustomfield.customfield_Key = self.customfield_key
            newCustomfield.customfieldname = self.customfieldname
            newCustomfield.customfieldvalue = self.customfieldvalue
            self.customfields.append(newCustomfield)           
 
        elif name == 'item':
            newbug = Bug()
            newbug.title = self.title
            newbug.link = self.link
            newbug.description = self.description
            newbug.environment = self.environment
            newbug.summary = self.summary
            newbug.bug_type = self.bug_type
            newbug.status = self.status
            newbug.resolution = self.resolution
            newbug.security = self.security
            newbug.created = self.created
            newbug.updated = self.updated
            newbug.version = self.version
            newbug.component = self.component
            newbug.votes = self.votes
            newbug.project = self.project
            newbug.project_id = self.project_id
            newbug.project_key = self.project_key
            newbug.issue_key = self.issue_key
            newbug.key_id = self.key_id
            newbug.assignee = self.assignee
            newbug.assignee_username = self.assignee_username
            newbug.reporter = self.reporter
            newbug.reporter_username = self.reporter_username
            newbug.comments = self.comments
            newbug.attachments = self.attachments
            newbug.customfields = self.customfields

            self.mapping.append(newbug)
            self.comments = []
            self.attachments = []
            self.customfields = []
            self.first_desc = True
            self.description = ""
            self.environment = ""

    def getIssue(self):
        #Return the parse data bug into issue object
        for bug in self.mapping:

            issue_id = bug.key_id
            issue_type = bug.bug_type
            summary = bug.summary
            description = bug.description
            status = bug.status
            resolution = bug.resolution

            submitted_by = People(bug.assignee_username)
            submitted_by.set_name(bug.assignee)            

            assigned_by = People(bug.reporter_username)
            assigned_by.set_name(bug.reporter)
            
            submitted_on = parse(bug.created).replace(tzinfo=None)

            issue = JiraIssue(issue_id, issue_type, summary, description, submitted_by, submitted_on)
            issue.set_assigned(assigned_by)
            issue.setIssue_key(bug.issue_key)
            issue.setTitle(bug.title)
            issue.setLink(bug.link)
            issue.setEnvironment(bug.environment)
            issue.setSecurity(bug.security)
            issue.setUpdated(parse(bug.updated).replace(tzinfo=None))
            issue.setVersion(bug.version)
            issue.setComponent(bug.component)
            issue.setVotes(bug.votes)
            issue.setProject(bug.project)
            issue.setProject_id(bug.project_id)
            issue.setProject_key(bug.project_key)
            issue.setStatus(status)
            issue.setResolution(resolution)
            
            bug_activity_url = bug.link + '?page=com.atlassian.jira.plugin.system.issuetabpanels%3Achangehistory-tabpanel'
            data_activity = urllib.urlopen(bug_activity_url).read()
            parser = SoupHtmlParser(data_activity, bug.key_id)
            changes = parser.parse_changes()
            for c in changes:
                issue.add_change(c)     

            for comment in bug.comments:
                comment_by = People(comment.comment_author)
                comment_on = parse(comment.comment_created).replace(tzinfo=None)
                com = Comment(comment.comment, comment_by, comment_on)
                issue.add_comment(com)

            for attachment in bug.attachments:
                url = "/secure/attachment/" + attachment.attachment_id + "/" + attachment.attachment_name
                attachment_by = People(attachment.attachment_author)
                attachment_on = parse(attachment.attachment_created).replace(tzinfo=None)
                attach = Attachment(url, attachment_by, attachment_on)
                issue.add_attachment(attach)
            #FIXME customfield are not stored in db because is the fields has the same in all the bugs
    
            return issue

class JiraBackend(Backend):
    """
    Jira Backend
    """

    def __init__(self):
        options = Config()
        self.delay = options.delay
   
    def bugsNumber(self,url):
        serverUrl = url.split("/browse/")[0]
        oneBug = serverUrl + "/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=project+%3D+" + url.split("/browse/")[1] + "&tempMax=1"
        data_url = urllib.urlopen(oneBug).read()
        bugs = data_url.split("<issue")[1].split('\"/>')[0].split("total=\"")[1]
        return bugs
 
    def run(self,url):
        printout("Running Bicho with delay of %s seconds" % (str(self.delay)))

        bugsdb = get_database(DBJiraBackend())

        bugsdb.insert_supported_traker("jira","4.1.2")
        trk = Tracker(url.split("-")[0], "jira", "4.1.2")
        dbtrk = bugsdb.insert_tracker(trk)

        serverUrl = url.split("/browse/")[0]
        query = "/si/jira.issueviews:issue-xml/"
        project = url.split("/browse/")[1]

        if (project.split("-").__len__() > 1):
            bug_key = project
            project = project.split("-")[0]
            bugs_number = 1

            printdbg(serverUrl + query + bug_key + "/" + bug_key + ".xml")

            parser = xml.sax.make_parser(  )
            handler = BugsHandler(  )
            parser.setContentHandler(handler)
            try:
                parser.parse(serverUrl + query + bug_key + "/" + bug_key + ".xml")
                issue = handler.getIssue()
                bugsdb.insert_issue(issue, dbtrk.id)
            except Exception, e:
                #printerr(e)
                print(e)

        else:
            bugs_number = self.bugsNumber(url)

            for i in range(int(bugs_number)+1):
                if i != 0:
                    bug_key = project + "-" + str(i)
                    printdbg(serverUrl + query + bug_key + "/" + bug_key + ".xml")

                    parser = xml.sax.make_parser(  )
                    handler = BugsHandler(  )
                    parser.setContentHandler(handler)
                    try:
                        parser.parse(serverUrl + query + bug_key + "/" + bug_key + ".xml")
                        issue = handler.getIssue()
                        bugsdb.insert_issue(issue, dbtrk.id)
                    except Exception, e:
                        printerr(e)
                        print(e)
                    time.sleep(self.delay)

        printout("Done. %s bugs analyzed" % (bugs_number))

register_backend ("jira", JiraBackend)
