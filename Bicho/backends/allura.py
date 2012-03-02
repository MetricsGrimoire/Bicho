# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Bitergia
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
# Authors:  Alvaro del Castillo <acs@bitergia.com>
#


from Bicho.Config import Config

from Bicho.backends import Backend
from Bicho.utils import printdbg, printout, printerr
from Bicho.db.database import DBIssue, DBBackend, get_database
from storm.locals import DateTime, Int, Reference, Unicode


class DBAlluraIssueExt(object):
    """
    """
    __storm_table__ = 'issues_ext_allura'

    id = Int(primary=True)
    issue_id = Int()
    
    issue = Reference(issue_id, DBIssue.id)
    
    def __init__(self, issue_id):
        self.issue_id = issue_id


class DBAlluraIssueExtMySQL(DBAlluraIssueExt):
    """
    MySQL subclass of L{DBBugzillaIssueExt}
    """

    __sql_table__ = 'CREATE TABLE IF NOT EXISTS issues_ext_allura ( \
                    id INTEGER NOT NULL AUTO_INCREMENT, \
                    issue_id INTEGER NOT NULL, \
                    PRIMARY KEY(id), \
                    FOREIGN KEY(issue_id) \
                    REFERENCES issues (id) \
                    ON DELETE CASCADE \
                    ON UPDATE CASCADE \
                     ) ENGINE=MYISAM;'


class DBAlluraBackend(DBBackend):
    """
    Adapter for Allura backend.
    """
    def __init__(self):
        self.MYSQL_EXT = [DBAlluraIssueExtMySQL]

class Allura():
    
    def __init__(self):
        self.delay = Config.delay
        self.url = Config.url

    def run(self):
        """
        """
        printout("Running Bicho with delay of %s seconds" % (str(self.delay)))
        
        bugsdb = get_database (DBAlluraBackend())

        

Backend.register_backend('allura', Allura)
