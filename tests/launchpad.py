#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012 GSyC/LibreSoft, Universidad Rey Juan Carlos
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
# Authors: Luis Cañas Díaz <lcanas@libresoft.es>

import MySQLdb as mdb
from launchpadlib.launchpad import Launchpad
import subprocess
import sys
import os
import pwd
from tempfile import mkdtemp
from tests import Test, register_test, remove_directory
from sets import Set

_all_status = ["New", "Incomplete", "Opinion", "Invalid", "Won't Fix",
              "Expired", "Confirmed", "Triaged", "In Progress",
              "Fix Committed", "Fix Released",
              "Incomplete (with response)",
              "Incomplete (without response)"]

_all_importance = ["Critical", "High", "Low", "Medium", "Undecided",
                   "Wishlist"]


class LaunchpadTest(Test):

    def __init__(self):
        #
        # getuser - getpassword - getdatabase
        #
        self.dbuser = "root"
        self.dbpass = "root"
        self.dbname = "launchpad_test"
        self.pname = "glance"
        self.delay = 3

        self._initialize_database()

        print("Launchpad test using the project %s" % self.pname)

        homedir = pwd.getpwuid(os.getuid()).pw_dir
        cachedir = os.path.join(homedir, ".cache/bicho/")
        if not os.path.exists(cachedir):
            os.makedirs(cachedir)
        cre_file = os.path.join(cachedir + 'launchpad-credential')
        self.lp = Launchpad.login_with('Bicho','production',
                                       credentials_file = cre_file)
        sys.stdout.write("Using credential file %s \n" % str(cre_file))

        self.all_bugs = self.lp.projects[self.pname].searchTasks(
            status=_all_status,
            omit_duplicates=False)

        self.notdupe_bugs = self.lp.projects[self.pname].searchTasks(
            status=_all_status,
            omit_duplicates=True)

        self.patches_bugs = self.lp.projects[self.pname].searchTasks(
            status=_all_status,
            omit_duplicates=False,
            has_patch=True)

    def _print_success(self, string):
        sys.stdout.write("[OK] " + string + "\n")
        sys.stdout.flush()

    def _print_error(self, string):
        sys.stderr.write("** ERROR ** " + string + "\n")
        sys.stderr.flush()

    def _initialize_database(self):
        con = mdb.connect('localhost', self.dbuser, self.dbpass)
        cur = con.cursor()
        try:
            cur.execute("DROP DATABASE " + str(self.dbname))
        except:
            # no problem, we'll create the database
            pass
        cur.execute("CREATE DATABASE " + str(self.dbname) +
                    " CHARACTER SET utf8 COLLATE utf8_unicode_ci")
        con.close()

    def _execute_query(self, query):
        # read the database and returns an integer
        con = mdb.connect('localhost', self.dbuser, self.dbpass, self.dbname)
        cur = con.cursor()
        cur.execute(query)
        data = cur.fetchone()
        con.close()
        return data

    def execution(self):
        # execute Bicho against Glance
        #
        # bicho -g --db-user-out=root --db-password-out=root
        #--db-database-out=bicho_lp lp http://launchpad.net/glance

        subprocess.call(["../bicho", "-g", "-d" + str(self.delay), \
                         "--db-user-out=" + self.dbuser, \
                         "--db-password-out=" + self.dbpass, \
                         "--db-database-out=" + self.dbname, \
                         "-b", "lp", "-u" ,"http://launchpad.net/glance"])

    def number_of_bugs(self):
        #
        # Checks the total number of bugs both in database created by Bicho
        # and launchpad
        #
        query = "SELECT COUNT(*) FROM issues"
        msg = "Total number of bugs"

        bugs_in_db = self._execute_query(query)[0]

        if len(self.all_bugs) == bugs_in_db:
            self._print_success(msg)
        else:
            self._print_error(msg)

    def bugs_per_status(self):
        #
        # Checks the number of bugs per status
        #

        # we can't use _all_status because the three incomplete statuses return
        #only 'Incomplete' when accessing to bug.status . So we'll compare the
        #result of searchTasks with the "Incomplete" status in the database

        _a_status = ["New", "Opinion", "Invalid", "Won't Fix",
                     "Expired", "Confirmed", "Triaged", "In Progress",
                     "Fix Committed", "Fix Released"]
        _b_status = ["Incomplete", "Incomplete (with response)",
                     "Incomplete (without response)"]

        query = 'SELECT COUNT(*) FROM issues WHERE status = "X"'
        msg = "Number of bugs per status"

        # first we compare the statuses of the _a_status list
        for s in _a_status:
            aux_query = query.replace('X', s)
            number = self._execute_query(aux_query)[0]
            bugs_lp = self.lp.projects[self.pname].searchTasks(
                status=s,
                omit_duplicates=False)

            aux_msg = msg + " for status " + s
            if ((len(bugs_lp) != number)):
                self._print_error(aux_msg)
            else:
                self._print_success(aux_msg)

        # second we compare the statuses of the Incomplete different names
        aux_query = query.replace('X', "Incomplete")
        number = self._execute_query(aux_query)[0]
        bugs_lp = self.lp.projects[self.pname].searchTasks(
            status=_b_status,
            omit_duplicates=False)

        aux_msg = msg + " for status Incomplete"
        if ((len(bugs_lp) != number)):
            self._print_error(aux_msg)
        else:
            self._print_success(aux_msg)

    def assignees(self):
        #
        # Checks the assignees fro the bugs below
        #
        # https://bugs.launchpad.net/glance/+bug/939257
        # https://bugs.launchpad.net/glance/+bug/950364
        # https://bugs.launchpad.net/glance/+bug/952405

        query_a = "SELECT people.user_id, name FROM issues, people "\
                  "WHERE issues.issue = '939257' "\
                  "AND issues.assigned_to = people.id"
        query_b = "SELECT people.user_id, name FROM issues, people "\
                  "WHERE issues.issue = '950364' "\
                  "AND issues.assigned_to = people.id"
        query_c = "SELECT people.user_id, name FROM issues, people "\
                  "WHERE issues.issue = '952405' "\
                  "AND issues.assigned_to = people.id"

        db_a = self._execute_query(query_a)
        db_b = self._execute_query(query_b)
        db_c = self._execute_query(query_c)

        msg = "Assignee for bug"
        error = -1

        # display name is the real name, while name is the nickname
        bug_a = self.lp.bugs['939257']
        if bug_a.bug_tasks[0].assignee:
            assignee_a = (bug_a.bug_tasks[0].assignee.name,
                          bug_a.bug_tasks[0].assignee.display_name)
            if (db_a != assignee_a):
                self._print_error(msg + " 939257")
                error = 1
        else:
            if (db_a != "('nobody', 'None')"):
                self._print_error(msg + " 939257")
                error = 1

        bug_b = self.lp.bugs['950364']
        if bug_b.bug_tasks[0].assignee:
            assignee_b = (bug_b.bug_tasks[0].assignee.name,
                          bug_b.bug_tasks[0].assignee.display_name)
            if (db_b != assignee_b):
                self._print_error(msg + " 950364")
                error = 1
        else:
            if (db_a != "('nobody', 'None')"):
                self._print_error(msg + " 950364")
                error = 1

        bug_c = self.lp.bugs['952405']
        if bug_c.bug_tasks[0].assignee:
            assignee_c = (bug_c.bug_tasks[0].assignee.name,
                          bug_c.bug_tasks[0].assignee.display_name)
            if (db_c != assignee_c):
                self._print_error(msg + " 952405")
                error = 1
        else:
            if (db_a != "('nobody', 'None')"):
                self._print_error(msg + " 952405")
                error = 1

        if (error < 1):
            self._print_success("Assignees for bugs 939257, 950364 and 952405")

    def importance(self):
        #
        # Check the variable importance from all the bugs counting them
        #

        query = "SELECT COUNT(*) FROM issues WHERE TYPE='X'"
        msg = "Number of bugs with the importance value "
        for imp in _all_importance:
            bugs = self.lp.projects[self.pname].searchTasks(
                status=_all_status,
                omit_duplicates=False,
                importance=imp)

            lp_number = len(bugs)
            aux_query = query.replace('X', imp)
            db_number = self._execute_query(aux_query)[0]
            if (lp_number == db_number):
                self._print_success(msg + str(imp))
            else:
                self._print_error(msg + str(imp))

    def duplicates(self):
        #
        # Checks the number of duplicates for the given list of bugs
        #

        msg = "Number of duplicates"

        total = Set([])
        notdupes = Set([])
        dupes = Set([])
        for b in self.all_bugs:
            total.add(b.web_link)

        for b in self.notdupe_bugs:
            notdupes.add(b.web_link)

        dupes = total - notdupes

        #print "total of dupes = " + str(len(dupes))

        ##
        ## To be done!!
        ## Bug found. We are not storing the relationships
        ##
        self._print_error(msg)

    def number_comments(self):
        #
        # Checks the number of comments for some bugs
        #

        query_nc = "SELECT COUNT(*) FROM comments WHERE issue_id IN "\
                   "(SELECT id FROM issues WHERE issue = 'X')"
        msg = "Number of comments for bug "

        bug_comments = {}

        for i in range(0, 10):
            b = self.all_bugs[i]
            bug_id = b.bug.id
            n_comments = b.bug.message_count
            bug_comments[bug_id] = n_comments

        for k in bug_comments.keys():
            aux_query = query_nc.replace('X', str(k))
            db_number = self._execute_query(aux_query)[0]
            aux_n = bug_comments[k] - 1  #1st is the description
            if (aux_n == db_number):
                self._print_success(msg + str(k))
            else:
                self._print_error(msg + str(k))

    def number_entries(self):
        #
        # Checks the number of entries in the activity log
        #

        query_ne = "SELECT COUNT(*) FROM changes WHERE issue_id IN "\
                   "(SELECT id FROM issues WHERE issue = 'X')"
        msg = "Number of entries in the activity log for bug "

        bug_changes = {}

        for i in range(10, 20):
            b = self.all_bugs[i]
            bug_id = b.bug.id
            n_changes = b.bug.activity.total_size
            bug_changes[bug_id] = n_changes

        for k in bug_changes.keys():
            aux_query = query_ne.replace('X', str(k))
            db_number = self._execute_query(aux_query)[0]
            if (bug_changes[k] == db_number):
                self._print_success(msg + str(k))
            else:
                self._print_error(msg + str(k))

    def url_patches(self):
        #
        # Checks URLs of the patches for the first 5 bugs with patches
        #

        query_a = "SELECT COUNT(*) FROM attachments WHERE issue_id IN "\
                  "(SELECT id FROM issues WHERE issue = 'X')"
        query_b = "SELECT COUNT(*) FROM attachments WHERE issue_id IN "\
                  "(SELECT id FROM issues WHERE issue = 'X') "\
                  " AND url = 'Y'"
        msg1 = "Number of attachments/patches for bug "
        msg2 = "Attachment/patch for bug "

        bug_patches = {}  # it will contain a dict of lists with urls

        for i in range(0, 5):
            b = self.patches_bugs[i]
            bug_id = b.bug.id
            urls = []
            for p in b.bug.attachments.entries:
                urls.append(p['data_link'])
            bug_patches[bug_id] = urls

        # we first check the number of attachments/patches per bug
        for k in bug_patches.keys():
            aux_query = query_a.replace('X', str(k))
            db_number = self._execute_query(aux_query)[0]
            if (len(bug_patches[k]) == db_number):
                self._print_success(msg1 + str(k))
            else:
                self._print_error(msg1 + str(k))

        # second, we check that the urls of the patches are the same

        for k in bug_patches.keys():
            aux_query = query_b.replace('X', str(k))
            for url in bug_patches[k]:
                aux_query = aux_query.replace('Y', str(url))
                db_number = self._execute_query(aux_query)[0]
                if (db_number < 1):
                    self._print_error(msg2 + str(k))
                else:
                    self._print_success(msg2 + str(k))

    def number_bugs_milestone(self):
        #
        # Check the number of bugs per milestone
        #

        query = "SELECT COUNT(*) FROM issues_ext_launchpad "\
                "WHERE milestone_name = 'X'"
        msg = "Number of bugs per milestone for "

        milestone_number = {}
        milestones = self.lp.projects[self.pname].all_milestones
        #mypro.all_milestones
        for m in milestones:
            bugs_mile = self.lp.projects[self.pname].searchTasks(
                status=_all_status,
                omit_duplicates=False,
                milestone=m)

            number = len(bugs_mile)
            if number > 0:
                milestone_number[m.name] = len(bugs_mile)

        for k in milestone_number.keys():
            aux_query = query.replace('X', k)
            db_number = self._execute_query(aux_query)[0]
            if (milestone_number[k] == db_number):
                self._print_success(msg + str(k))
            else:
                self._print_error(msg + str(k))

register_test('launchpad', LaunchpadTest)
