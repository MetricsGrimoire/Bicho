import sys
import xml.sax.handler
from xml.sax._exceptions import SAXParseException

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
 
    def getTitle(self): 
        return self.title
    def setTitle(self,title):
        self.title = title
    def setLink(self,link):
        self.link = link
    def setDescription(self,description):
        self.description = description
    def setEnviroment(self,enviroment):
        self.enviroment = enviroment
    def setSummary(self,summary):
        self.summary = summary
    def setBug_type(self,bug_type):
        self.bug_type = bug_type
    def setStatus(self,status):
        self.status = status
    def setResolution(self,resolution):
        self.resolution = resolution
    def setSecurity(self,security):
        self.security = security
    def setCreated(self,created):
        self.created = created
    def setUpdated(self,updated):
        self.updated = updated
    def setVersion(self,version):
        self.version = version
    def setComponent(self,component):
        self.component = component
    def setVotes(self,votes):
        self.votes = votes

    def reset(self):
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

class BugsHandler(xml.sax.handler.ContentHandler):

    def __init__ (self):
        
        #store all bugs
        self.mapping = []
 
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
    
    def characters(self, ch):
        if self.is_title:
            self.title = str(ch)
        elif self.is_link:
            self.link = str(ch)
        elif self.is_description:
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



    def endElement(self, name):
        if name == 'title':
            self.is_title = False
        elif name == 'link':
            self.is_link = False
        elif name == 'description':
            self.is_description = False
        elif name == 'enviroment':
            self.is_enviroment = False
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
            
            newbug = Bug()
            newbug.setTitle(self.title)
            newbug.setLink(self.link)
            newbug.setDescription(self.description)
            newbug.setEnviroment(self.enviroment)
            newbug.setSummary(self.summary)
            newbug.setBug_type(self.bug_type)
            newbug.setStatus(self.status)
            newbug.setResolution(self.resolution)
            newbug.setSecurity(self.security)
            newbug.setCreated(self.created)
            newbug.setUpdated(self.updated)
            newbug.setVersion(self.version)
            newbug.setComponent(self.component)
            newbug.setVotes(self.votes)
            
            self.mapping.append(newbug)

    def printDataBug(self):
        for oneBug in self.mapping:
            print oneBug.title

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
