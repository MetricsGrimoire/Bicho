# Copyright (C) 2007  GSyC/LibreSoft
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
# Authors: Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>
#

from HTMLParser import HTMLParser

import urllib
import cgi

from Bicho.utils import *

def url_join (base, *p):
    retval = [base.strip ('/')]

    for comp in p:
        retval.append (comp.strip ('/'))

    return "/".join (retval)

def url_strip_protocol (url):
    p = url.find ("://")
    if p == -1:
        return url

    p += 3
    return url[p:]

def url_get_attr (url, attr = None):
    query = urllib.splitquery (url)
    try:
        if query[1] is None:
            return None;
    except IndexError:
        return None

    attrs = cgi.parse_qsl (query[1])
    if attr is None:
        return attrs

    for a in attrs:
        if attr in a:
            return a[1]

    return None



    
class HTMLTag:

    def __init__ (self, tag, attrs):
        self.tag = tag.lower ()
        self.attrs = {}
        self.data = ""
        for name, value in attrs:
            self.attrs[name.lower ()] = value.lower ()

    def data_append (self, data):
        if self.data != "":
            self.data += ' ' + data
        else:
            self.data += data

    def get (self, name):
        retval = None
        try:
            retval = self.attrs[name.lower ()]
        except:
            pass

        return retval

    def get_data (self):
        return self.data

class Parser (HTMLParser):

    def __init__ (self):
        HTMLParser.__init__ (self)
        self.filter = []
        self.tags = {}
        self.current = []

    def error (self, msg):
        printwrn ("Parsing Error \"%s\", trying to recover..." % (msg))
        
    def __save_tag (self, tag, attrs):
        if len (self.filter) > 0 and tag not in self.filter:
            return

        if not self.tags.has_key (tag):
            self.tags[tag] = []

        self.tags[tag].append (HTMLTag (tag, attrs))
        
    def handle_starttag (self, tag, attrs):
        self.__save_tag (tag.lower (), attrs)
        if self.tags.has_key (tag):
            self.current.append (self.tags[tag][-1])
        
    def handle_startendtag (self, tag, attrs):
        self.__save_tag (tag.lower (), attrs)

    def handle_endtag (self, tag):
        if len (self.filter) > 0 and tag not in self.filter:
            return
        
        try:
            self.current.pop ()
        except:
            pass

    def handle_data (self, data):
        try:
            self.current[-1].data_append (data)
        except:
            pass

    def add_filter (self, tags):
        for tag in tags:
            self.filter.append (tag.lower ())

    def get_tags (self, tag = None, attrs = None):
        retval = []
        tags = []
        
        if tag is not None:
            try:
                tags = self.tags[tag]
            except:
                return retval
        else:
            for t in self.tags.keys ():
                tags.extend (self.tags[t])
                
        if attrs is None:
            return tags

        for t in tags:
            found = True
            for name, value in attrs:
                if t.get (name) != value:
                    found = False
                    break
                
            if found:
                retval.append (t)

        return retval

##if __name__ == "__main__":
##    import urllib
##
##    p = Parser ()
##    p.add_filter (['a'])
##    p.feed (urllib.urlopen ('http://sourceforge.net/tracker/?group_id=93438&atid=604306&set=any').read ())
##    #p.feed (urllib.urlopen ('http://gsyc.escet.urjc.es/~dizquierdo/table3.html').read ())
##    p.close ()
##    
##    links = p.get_tags ('a')
##    for  link in links:
##        print "Link to: %s Content: %s" % (link.get ('href'), link.get_data ())
##
##    #print url_join ('https://forge.morfeo-project.org/', '/projects', 'libresoft-tools')
