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

import sys
import os

__all__ = [
        'Test',
        'remove_directory',
        'register_test',
        'get_test'
]


class Test:

    def execution(self):
        """
        Execution of Bicho using the different extensions
        """
        pass

    def number_of_bugs(self):
        """
        Total number of bugs
        """
        pass

    def bugs_per_status(self):
        """
        Total number of bugs per status
        """
        pass

    def assignees(self):
        """
        Assignees for a couple of bugs
        """
        pass

    def importance(self):
        """
        Importance of the bugs
        """
        pass

    def duplicates(self):
        """
        Number of duplicates for a list of bugs
        """
        pass

    def number_comments(self):
        """
        Number of comments
        """
        pass

    def number_entries(self):
        """
        Number of entries in the activity log
        """
        pass

    def urls(self):
        """
        URLs of the ..
        """
        pass

    def number_bugs_milestone(self):
        """
        Number of bugs per milestone
        """
        pass

    def run(self):
        self.execution()
        self.number_of_bugs()
        self.bugs_per_status()
        self.assignees()
        self.importance()
        self.duplicates()
        self.number_comments()
        self.number_entries()
        self.url_patches()
        self.number_bugs_milestone()


def remove_directory(path):
    if not os.path.exists(path):
        return

    for root, dirs, files in os.walk(path, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))

    os.rmdir(path)


_tests = {}


def register_test(test_name, test_class):
    _tests[test_name] = test_class


def get_test(test_name):
    if test_name not in _tests:
        """try:
            __import__(test_name)
        except:
            pass"""
        __import__(test_name)

    if test_name not in _tests:
        sys.stderr.write('Test %s not found\n' % (test_name))
        return None

    return _tests[test_name]
