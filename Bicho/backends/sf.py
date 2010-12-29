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
# Authors:  Daniel Izquierdo Cortazar   <dizquierdo@glibresoft.es>
#           Ronaldo Maia                <romaia@async.com.br>
#           Santiago Dueñas <sduenas@libresoft.es>
#
#

import re
import random
import urllib
import datetime
import os

from BeautifulSoup import BeautifulSoup

from Bicho.utils import url_get_attr
from Bicho.backends import register_backend
from Bicho.utils import debug, OptionsStore
from Bicho.database import *
from Bicho.common import *

# import from baseparser.py BFComment used in remove_comments method
from BeautifulSoup import Comment as BFComment

class SourceForgeParser():
    # FIXME: Sourceforge assignee is the full name instead of the username.
    # All other fields are the username.

    paths = dict(
        summary     = '/html/body/div/div[2]/div[4]/div/div/span[2]/strong',
        description = '/html/body/div/div[2]/div[4]/div[2]/p[1]',
        datesubmitted    = '/html/body/div/div[2]/div[4]/div[2]/div[1]/p[1]',
        submittedby    = '/html/body/div/div[2]/div[4]/div[2]/div/p/a',
        priority    = '/html/body/div/div[2]/div[4]/div[2]/div[1]/p[2]',
        status      = '/html/body/div/div[2]/div[4]/div[2]/div[1]/p[3]',
        resolution  = '/html/body/div/div[2]/div[4]/div[2]/div[1]/p[4]',
        assignedto    = '/html/body/div/div[2]/div[4]/div[2]/div[2]/p[1]',
        category    = '/html/body/div/div[2]/div[4]/div[2]/div[2]/p[2]',
        group       = '/html/body/div/div[2]/div[4]/div[2]/div[2]/p[3]',
    )

    field_map = {
        'status_id': u'status',
        'resolution_id': u'resolution',
        'assigned_to': u'assignedto',
    }

    # FIXME: We should have a way to detecte reponened bugs
    status_map = {
        'Open': u'OPEN',
        'Pending': u'RESOLVED', #XXX
        'Closed': u'RESOLVED',
        'Deleted': u'RESOLVED',
    }

    resolution_map = {
        'Fixed': u'FIXED',
        'Invalid': u'INVALID',
        'Duplicate': u'DUPLICATE',
        "Works For Me": u'INVALID'
        # Remind, Accepted
    }
    
    # str_to_date function convert a string with the form YYYY-MM-DD HH:MM
    # to an accepted (well-formed) date from baseparsers.py
    
    def str_to_date(self,string):
      if not string:
        return
      
      date, time, extra = string.split(' ')
      params = [int(i) for i in date.split('-') + time.split(':')]
      full_date = datetime.datetime(*params)
      return full_date
    
    # In order to use the same name of Dani's code I changed the names of
    # mathods to capital
    def get_comments(self,dataBugs,soup):
        try :
          if self.getNumChAttComm('Comment',soup):
            for tg in soup({'h4':True}):
              # This can be done using an if may be a loop is not necessary, but it works
              for ed in tg.findAllNext({'tr':True},id=re.compile('artifact\_comment\_\d+')):
                text = ''
                datesub = ''
                sender = ''
                aux = ed.findAll({'p':True})
                datesub = aux[0].contents[0].split('Date:')[1]
                # Some bugs has been sent by a user not registered maybe or a
                # user who is not in ddbb anymore (I am not sure) why is it
                # possible to have a "nobody" sender?, so if the user is not
                # registered we took "nobody" as default because if the user is
                # registered should have its own user name

                # This bug has "nobody" as sender
                # http://sourceforge.net/tracker/?func=detail&aid=1711119&group_id=138511&atid=740882
                try :
                  sender = aux[0].contents[3].contents[0]
                except:
                  sender = "nobody"

                r = re.compile('google\_ad\_section\_(start|end)')
                text = r.sub('',''.join(aux[1].findAll(text=True))).strip()
                
                c = Comment(text, sender, self.str_to_date(datesub.strip()))
                dataBugs["Comments:"].append(c)
                #debug("Comments : %s" % comments  )
                #return comments
          else :
            try:
              #NoneDate = self.str_to_date("1975-05-18 04:00")
              #comnt = Bug.Comment()
              #comnt.IdBug = None
              #comnt.DateSubmitted = NoneDate
              #comnt.SubmittedBy = None
              #comnt.Comment = None
              #comments.append(comnt)
              #return comments
              pass
            except:
              debug("Error Comments None")
        except :
          debug("Errors getting Comments")

    # New change method because the old one does not work at all
    def get_changes(self,dataBugs,soup):
      changes = []
      try:
        if self.getNumChAttComm('Change',soup):
          for tg in soup('h4'): 
            if tg.has_key('id') and tg['id'] == 'changebar':
              for tgg in tg.findNext({'tbody':True}).findAllNext({'tr':True}):
                aux = tgg.findAll({'td':True})
                field = str(aux[0].contents[0]).strip()
                old_value = str(aux[1].contents[0]).strip()
                new_value = 'unknown' # FIXME
                changed_on = self.str_to_date(str(aux[2].contents[0]).strip())
                changed_by = str(aux[3].contents[0]).strip()
                
                change = Change(field, old_value, new_value, changed_by, changed_on)
                
                dataBugs["Changes:"].append(change)
              #debug("Changes : %s" % changes)
              #return changes
        else :
          try:
            #NoneDate = self.str_to_date("1975-05-18 04:00")
            #change = Bug.Change()
            #change.IdBug = None
            #change.Field = None
            #change.OldValue = None
            #change.Date = NoneDate
            #change.SubmittedBy = None
            #changes.append(change)
            #return changes
            pass
          except :
            debug("Error Changes None")
      except : 
        debug("Errors getting the Changes")

    # New attachment method because the old one does not work at all
    def get_attachments(self,dataBugs, soup):
      attachs = []
      try :
        if self.getNumChAttComm('Attached File',soup):
          for tg in soup('h4'):
            if tg.has_key('id') and tg['id'] == 'filebar':
              for att in soup({'tbody':True})[1].findAll({'tr':True}):
                aux = att.findAll({'td':True})
                
                name = str(aux[0].contents[1])
                description = str(aux[1].contents[1])
                url = str(SourceForgeFrontend.domain+aux[2].a['href'])
                
                attachment = Attachment(url)
                attachment.set_name(name)
                attachment.set_description(description)
                dataBugs["Attachments:"].append(attachment)
                #debug("Attach : %s" % attachs)
                #return attachs
        else :
          try:
            #attach = Bug.Attachment()
            #attach.IdBug = None
            #attach.Name = None
            #attach.Description = None
            #attach.Url = None
            #attachs.append(attach) 
            #return attachs
            pass
          except:
            debug("Error Attachs None")
      except :
        debug("Errors getting Attachments") 
        #return attachs

    def getNumChAttComm(self,which, soup):
      # This is one way to know if there are info
      # of comments, changes or attachments
      # SF has a Changes|Attachments|Comments ( X )
      # This calculate the length of the line and if it is
      # more than 3 it *has* a number
      # Another way is to find a number inside the string
      try:
        for tg in soup({'h4':True}):
          if str(tg.contents).find(which) > 0:
            for l in str(tg.contents):
              if l.isdigit():
                return True
            return False
      except:
        debug("Error getting ChAttComm")

    
    def get_submitted_by(self,dataBugs, soup):
      try:
        for tg in soup.findAll({'a':True}):
          if tg.parent.name == 'p' and "/users/" in tg["href"]:
            #debug("SubmittedBy : %s" % tg.contents[0])
            dataBugs["Submitted By:"] = tg.contents[0]
      except Exception, e:
        print "Error getting SubmittedBy. %s" % e

    
    def get_submitted_on(self,dataBugs, soup):
      try:
        for pvc in soup({'label':True}):
          if 'Submitted' in str(pvc.contents):
            datex = pvc.findNext({'p':True})
        submd = str(datex).split(' - ')[1][:-4]
        final_date = self.str_to_date(submd)
        #debug("DateSubmitted %s " % final_date)
        dataBugs["Date Submitted:"] = final_date
      except Exception, e:
        print "Error getting submitted_on. %s" % e
    
    
    def get_priority(self,dataBugs,soup):
      try:
        for priority in soup({'label':True}):
          if 'Priority' in str(priority.contents):
            #debug("Priority : %s" % priority.findNext('p').contents)
            dataBugs["Priority: "] = priority.findNext('p').contents[0]
      except:
        debug("Error getting Priority")
      

    def get_resolution(self,dataBugs,soup):
      try:
        for resolution in soup({'label':True}):
          if 'Resolution' in str(resolution.contents):
            #debug("Resolution : %s" % resolution.findNext('p').contents)
            dataBugs["Resolution: "] = resolution.findNext('p').contents[0]
      except:
        debug("Error getting Resolution")
    
    def get_status(self,dataBugs,soup):
      try:
        for status in soup({'label':True}):
          if 'Status' in str(status.contents):
            #debug("Status : %s" % status.findNext('p').contents)
            dataBugs["Status: "] = status.findNext('p').contents[0]
      except:
        debug("Error getting Status")
    
    def get_group(self,dataBugs,soup):
      try:
        for group in soup({'label':True}):
          if 'Group' in str(group.contents):
            #debug("Group : %s" % group.findNext('p').contents)
            dataBugs["Group: "] = group.findNext('p').contents[0]
      except:
        debug("Error getting Group")


    def get_visibility(self,soup): # Not used
      try:
        for visibility in soup({'label':True}):
          if 'Visibility' in str(visibility.contents):
            #debug("Visibility : %s" % visibility.findNext('p').contents)
            return visibility.findNext('p').contents  
      except:
        debug("Error getting Visbility")
    
    def get_category(self,dataBugs,soup):
      try:
        for category in soup({'label':True}):
          if 'Category' in str(category.contents):
            #debug("Category : %s" % category.findNext('p').contents)
            dataBugs["Category: "] = category.findNext('p').contents[0]
      except:
        debug("Error getting Category")

    def get_summary(self,dataBugs, soup):
      try:
        for tg in soup.findAll({'strong':True}):
          if tg.parent.name == 'span':
            if 'ID:' in tg.contents[0]:
              summary, idBug = tg.contents[0].split(' - ID: ') 
              #debug("Summary : %s" % summary  )
              dataBugs["Summary: "] = summary
      except:
        debug("Error getting Summary")

    def get_id(self, dataBugs, soup): # this is the id of the bug
      try :
        for tg in soup.findAll({'strong':True}):
          if tg.parent.name == 'span':
            if 'ID:' in tg.contents[0]:
              summary, idBug = tg.contents[0].split(' - ID: ')
              dataBugs['IdBug'] = int(idBug)
              return int(idBug)
      except:
        debug("Error getting idBug")

    def get_description(self,dataBugs, soup):
      try:
        for detail in soup({'label':True}):
          if "Details:" in str(detail.contents):
            
            r = re.compile('google\_ad\_section\_(start|end)')
            desc = r.sub('',''.join(detail.findNext({'p':True})(text=True))).strip()
            #debug("Description : %s" % det  )
            dataBugs["Description:"] = desc
      except:
        debug("Error getting Description")

    
    def get_assigned_to(self, dataBugs,soup):
      try:
        for pvc in soup({'label':True}):
          if 'Assigned:' in str(pvc.contents):
            aux = pvc.findNext({'p':True})
            #debug("AssignedTo : %s" % str(aux.contents[0]))
            dataBugs["Assigned To: "] = str(aux.contents[0])
      except:
        debug("Error getting Assigned")

    @classmethod
    def get_total_bugs(cls, html):
        soup = BeautifulSoup(html)
        aux = soup(text=True)
        for tg in aux:
          if "Results" and "Display" in tg:
            total_bugs = tg.split('&nbsp')[4].split(';')[1]
            return int(total_bugs)

    @classmethod
    def get_bug_links(cls, html):
        soup = BeautifulSoup(html)
        bugs = []

        links = soup.findAll({'a':True})
        for link in links:
            url_str = str(link.get('href'))

            # Bugs URLs
            if re.search("tracker", url_str) and re.search("aid", url_str):
                bugs.append(url_get_attr(url_str, 'aid'))

        return bugs


class SourceForgeFrontend():
    required_fields = ['project', 'group_id', 'atid']
    domain = "http://sourceforge.net"
    # the following are the stuff added because of compatibility and
    # functionality
    # added for compatibility with dani's bicho
    # getting url from options and extracting group_id and atid
    options = OptionsStore()
    url = options.url
    group_id = url.split('?')[1].split('=')[1]
    atid = url.split('&')[1].split('=')[1]
    sfparser = SourceForgeParser()  # instance used in _get_field method
    total_bugs = 0
    _current_bug = 0
    _cache = {}
    # very important dictionary where all data is going to be sotred
    dataBugs = {"Submitted By:" : "",
                "Date Submitted:" : "",
                "Last Updated By:" : "", # not used
                "Date Last Updated:" : "", # not used
                "Number of Comments:" : "", # not used
                "Number of Attachments:" : "", # not used
                "Category: " : "",
                "Group: " : "",
                "Assigned To: " : "",
                "Priority: " : "",
                "Status: " : "",
                "Resolution: " : "",
                "Summary: " : "",
                "Private: " : "", # not used
                "Description:" : "",
                "URL:" : "",
                "IdBug:" : "",
                "Comments:" : [],
                "Attachments:" : [],
                "Changes:" : []}
    
    fields = ['comments', 'changes', 'attachments', 'submitted_by', 'submitted_on',
              'priority', 'status', 'resolution', 'group', 'visibility', 'category',
              'summary', 'id', 'description', 'assigned_to']

    def get_bug_url(self, idBug):
        bug_url = "%s/tracker/?func=detail&aid=%s&group_id=%s&atid=%s" % (
                    self.domain, idBug, self.group_id, self.atid)
        return bug_url

    def prepare(self):
        bugs = []
        urls = []

        #self.group_id = self.options['group_id']
        #self.atid = self.options['atid']
        print self.url
        url = "%s/tracker/?limit=100&group_id=%s&atid=%s" % (
                    self.domain, self.group_id, self.atid)
        html = self.read_page(url)

        urls = []
        self.total_bugs = SourceForgeParser.get_total_bugs(html)
        for i in xrange(0, self.total_bugs, 100):
            urls.append(url+'&offset=%s' % i)

        for url in urls:
            html = self.read_page(url)
            bugs.extend(SourceForgeParser.get_bug_links(html))
            #debug ("Total %s " % len(bugs))
        self.bugs = bugs
    
    def read_page(self, url):
        debug('Reading page: %s' % url)
        if url.startswith('http:'):
            data = urllib.urlopen(url).read()
        else:
            data = file(url).read()

        return data

    #def get_total_bugs(self):
      #   return len(self.bugs)

    def get_next_bug(self):
        try:
            bug = self.bugs[self._current_bug]
        except IndexError:
            return None
        self._current_bug += 1
        return bug
    
    
    # methods from baseparser.py
    def remove_comments(cls, soup):
        cmts = soup.findAll(text=lambda text:isinstance(text,
                            BFComment))
        [comment.extract() for comment in cmts] 

    
    def set_html(self, html):
      self.soup = BeautifulSoup(html)
   
    def xpath(cls, path, soup):
        elements = path.split('/')

        cur = soup
        for e in elements:
            if not e:
                continue

            index = 0
            if e.endswith(']'):
               e, index = e.strip(']').split('[')
               index = int(index)-1
            
            children = cur.findAll(e, recursive=False)
            try:
                cur = children[index]
            except IndexError:
                # Try to workaround tbody being optional.
                if e == 'tbody':
                    continue
                #return None
        return cur
    
    def remove_br(cls, soup):
        cls.remove_tag(soup, 'br')

    def remove_tag(cls, soup, tag):
        [t.extract() for t in soup.findAll(tag)]
    
    def getDataBug(self):
        issue = Issue(self.dataBugs["IdBug:"], 'bug', self.dataBugs["Summary: "], 
                      self.dataBugs["Description:"], 
                      People(self.dataBugs["Submitted By:"]),
                      self.dataBugs["Date Submitted:"])
        issue.set_priority(self.dataBugs["Priority: "])
        issue.set_status(self.dataBugs["Status: "], self.dataBugs["Resolution: "])
        issue.set_assigned(People(self.dataBugs["Assigned To: "]))

        # FIXME: a class is needed to store this fields
        #bug.Category = self.dataBugs["Category: "]
        #bug.Group = self.dataBugs["Group: "]

        for comment in self.dataBugs["Comments:"]:
            issue.add_comment(comment)

        for attachment in self.dataBugs["Attachments:"]:
            issue.add_attachment(attachment)

        for change in self.dataBugs["Changes:"]:
            issue.add_changes(change)

        return issue

    def _get_field(self, dataBugs, field, soup): 
      # object is the SourceForgeParser class because it has get field methods

        value = None
        if hasattr(self.sfparser, 'get_%s' % field):
            method = getattr(self.sfparser, 'get_%s' % field)
            try:
                method(dataBugs,soup)
            except:
              print "Fallo Method %s" % field
        elif field in self.sfparser.paths.keys():
            tag = self.xpath(self.sfparser.paths[field], soup)
            if tag and tag.contents:
                value = tag.contents[0].strip()
    
    
    def parse_bug(self, html=None):
      #bug = Bug.Bug() # Very important bug object because of the compatibility with
                # Dani's code, is almost the same as ours but it works different
        if html:
            soup = BeautifulSoup(html)
        else:
            soup = self.soup
        self.remove_comments(soup)
        
        for field in self.fields:
            self._get_field(self.dataBugs, field, soup)

        #try:
        issue = self.getDataBug()
        #except Exception, e:
        #    print "Fallo DataBug. %s" % e
        #    return None

        return issue 

    def analyze_bug(self, bug_id):
        url = self.get_bug_url(bug_id)

        html = self.read_page(url)
        #self.parser.set_html(html)
        self.set_html(html)
        self.dataBugs["URL:"] = url
        self.dataBugs["IdBug:"] = bug_id

        #return self.parser.parse_bug()
        return self.parse_bug()

    def run(self):
        self.prepare()
        random.seed()
        url = self.url
        db = getDatabase()

        i = 0
        #total = self.get_total_bugs()
        #debug("Total number of bugs %s" % total)
        print "Total number of bugs %s" % self.total_bugs

        db_trk = db.insert_tracker(Tracker(url, 'sf'))

        while True:
            bug_id = self.get_next_bug()
            if not bug_id:
                break

            i+=1
            print 'Analyzing bug # %s of %s' % (i, self.total_bugs)

            issue = self.analyze_bug(bug_id)

            if issue is None:
                print 'Error retrieving bug %s' % bug_id
                #print 'Error retrieving bug %s' % bug_id
                continue

            db.insert_issue(issue, db_trk.id)
            debug('Bug # %s analyzed' % i)         

  # methods to store data from Dani
    def storeData(self, data, idBug):
      opt = OptionsStore()
      if not os.path.exists(opt.path):
        os.makedirs(opt.path)
      if not os.path.exists(os.path.join(opt.path, opt.db_database_out)):
        os.makedirs(os.path.join(opt.path, opt.db_database_out))

      #creating file to store data
      file = open(os.path.join(os.path.join(opt.path, opt.db_database_out), str(idBug)), 'w')
      file.write(data)
      file.close

register_backend("sf", SourceForgeFrontend)

if __name__ == "__main__":
    #sf = "http://sourceforge.net/tracker/index.php?"
    #url = "%sfunc=detail&aid=1251682&group_id=2435&atid=102435" % sf
    #cont = urllib.urlopen(url).read()

    fname = 'samples/sf2.html'
    cont = file(fname).read()

    parser = SourceForgeParser(cont)
    bug = parser.parse_bug()

    print bug
    for change in bug.changes:
        print change
 
