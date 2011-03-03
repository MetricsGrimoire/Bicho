import sys
import xml.sax.handler
from xml.sax._exceptions import SAXParseException

class Comment():
    def __init__(self):
        self.comment = None
        self.comment_id = None
        self.comment_author = None
        self.comment_created = None

class Attachment():
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

#bug class
class Bug():
    
    def __init__ (self):
        self.title = None
        self.link = None
        self.description = None
        self.enviroment = None
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
        self.key = None
        self.key_id = None
        self.assignee = None
        self.assignee_usarname = None
        self.reporter = None
        self.reporter_username = None
        
        self.comments = [] 
        self.attachments = []
        self.customfields = []

class BugsHandler(xml.sax.handler.ContentHandler):

    def __init__ (self):
        
        #store all bugs
        self.mapping = []
        self.comments = []
        self.attachments = []
        self.customfields = []

        self.title = None
        self.link = None
        self.description = None
        self.enviroment = None
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
        self.key = None
        self.key_id = None
        self.assignee = None
        self.assignee_username = None
        self.reporter = None
        self.reporter_username = None
        self.comment = None
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
        self.is_title = False
        self.is_link = False
        self.is_description = False
        self.is_enviroment = False
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
        self.is_key = False
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
        elif name == 'enviroment':
            self.is_enviroment = True
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
            self.is_key = True
            self.key_id = str(attrs['id'])
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
            #problems with ascii, not support str() function
            self.description = ch
        elif self.is_enviroment:
            self.enviroment = str(ch)
        elif self.is_summary:
            self.summary = str(ch)
        elif self.is_bug_type:
            self.bug_type = str(ch)
        elif self.is_status:
            self.status = str(ch)
        elif self.is_resolution:
            self.resolution = str(ch)
        elif self.is_security:
            self.security = str(ch)
        elif self.is_assignee:
            #problems with ascii, not support str() function
            self.assignee = ch
        elif self.is_reporter:
            #problems with ascii, not support str() function
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
            self.votes = str(ch)
        elif self.is_project:
            self.project = str(ch)
        elif self.is_key:
            self.key = str(ch)
        elif self.is_comment:
            #problems with ascii, not support str() function
            self.comment = ch
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
        elif name == 'enviroment':
            self.is_enviroment = False
        elif name == 'key':
            self.is_key = False
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
            newComment = Comment()
            newComment.comment = self.comment
            newComment.comment_id = self.comment_id
            newComment.comment_author = self.comment_author
            newComment.comment_created = self.comment_created
            self.comments.append(newComment)  
        elif name == 'attachment':
            newAttachment = Attachment()
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
 
        elif name == 'customfields':
            newbug = Bug()
            newbug.title = self.title
            newbug.link = self.link
            newbug.description = self.description
            newbug.enviroment = self.enviroment
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
            newbug.key = self.key
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

    def printDataBug(self):
        for oneBug in self.mapping:
            print oneBug.title
            #for customfield in oneBug.customfields:
            #    print customfield.customfieldname
            #    print customfield.customfieldvalue
            print "......."

    def getIdBug(self):
        return self.bug_id

    def getDataBug(self):
        return self.bug_id
 

if __name__ == "__main__":
    parser = xml.sax.make_parser(  )
    handler = BugsHandler(  )
    parser.setContentHandler(handler)
    parser.parse(sys.argv[1])
    handler.printDataBug()
