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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
#
# Authors:  Santiago Dueñas <sduenas@libresoft.es>
#           Luis Cañas Díaz <lcanas@bitergia.com>
#

import os


class LoggerUnknownError (Exception):
    '''Unkown engine type'''


class IssueLogger:

    _loggers = {}

    @staticmethod
    def register_logger(logger_name, logger_class):
        IssueLogger._loggers[logger_name] = logger_class

    @staticmethod
    def _get_logger(logger_name):
        if logger_name not in IssueLogger._loggers:
            try:
                __import__('Bicho.post_processing.issues_log_%s' % logger_name)
            except ImportError:
                raise

        if logger_name not in IssueLogger._loggers:
            raise LoggerUnknownError('Logger type %s not registered'
                                      % logger_name)
        return IssueLogger._loggers[logger_name]

    @staticmethod
    def create_logger(logger_name):
        logger_class = IssueLogger._get_logger(logger_name)
        return logger_class()
