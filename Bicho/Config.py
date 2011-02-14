# -*- coding: utf-8 -*-
# Copyright (C) 2011 GSyC/LibreSoft, Universidad Rey Juan Carlos
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
# Authors:
#       Carlos Garcia Campos <carlosgc@libresoft.es>
#       Luis Cañas Díaz <lcanas@libresoft.es>
#

class ErrorLoadingConfig(Exception):
    """
    Error loading configuration file.
    """
    pass


class InvalidConfig(Exception):
    """
    Invalid configuration.
    """
    pass


class Config:
    #Pattern singleton applied

    __shared_state = {'type': None,
                      'url' : None,
                      'path' : None,
                      'debug': False,
                      'quiet': False,
                      'delay': False,
                      'config_file': None,
                      'input': 'url',
                      'output': 'db',
                      # output database
                      'db_driver_out': 'mysql',
                      'db_user_out': None,
                      'db_password_out': None,
                      'db_database_out' : None,
                      'db_hostname_out': 'localhost',
                      'db_port_out' : '3306',
                      # input database
                      'db_driver_in': None,
                      'db_user_in': None,
                      'db_password_in': None,
                      'db_database_in': None,
                      'db_hostname_in': None,
                      'db_port_in': None}

    def __init__ (self):
        self.__dict__ = self.__shared_state

    def __getattr__(self, attr):
        return self.__dict__[attr]

    def __setattr__(self, attr, value):
        self.__dict__[attr] = value

    def __load_from_file (self, config_file):
        try:
            from types import ModuleType
            config = ModuleType ('bicho-config')
            f = open (config_file, 'r')
            exec f in config.__dict__
            f.close ()
        except Exception, e:
            raise ErrorLoadingConfig ("Error reading config file %s (%s)" % (\
                    config_file, str (e)))

        # general options
        try:
            self.debug = config.debug
        except:
            pass
        try:
            self.quiet = config.quiet
        except:
            pass
        try:
            self.type = config.type
        except:
            pass
        try:
            self.path = config.path
        except:
            pass
        try:
            self.delay = config.delay
        except:
            pass
        try:
            self.url = config.url
        except:
            pass
        try:
            self.input = config.input
        except:
            pass
        try:
            self.output = config.output
        except:
            pass

        # output database
        try:
            self.db_driver_out = config.db_driver_out
        except:
            pass
        try:
            self.db_user_out = config.db_user_out
        except:
            pass
        try:
            self.db_password_out = config.db_password_out
        except:
            pass
        try:
            self.db_database_out = config.db_database_out
        except:
            pass
        try:
            self.db_hostname_out = config.db_hostname_out
        except:
            pass
        try:
            self.db_port_out = config.db_port_out
        except:
            pass

        # input database
        try:
            self.db_driver_in = config.db_driver_in
        except:
            pass
        try:
            self.db_user_in = config.db_user_in
        except:
            pass
        try:
            self.db_password_in = config.db_password_in
        except:
            pass
        try:
            self.db_database_in = config.db_database_in
        except:
            pass
        try:
            self.db_hostname_in = config.db_hostname_in
        except:
            pass
        try:
            self.db_port_in = config.db_port_in
        except:
            pass

    def load (self):
        import os
        from utils import bicho_dot_dir, printout

        # First look in /etc
        # FIXME /etc is not portable
        config_file = os.path.join ('/etc', 'bicho')
        if os.path.isfile (config_file):
            self.__load_from_file (config_file)

        # Then look at $HOME
        config_file = os.path.join (bicho_dot_dir (), 'config')
        if os.path.isfile (config_file):
            self.__load_from_file (config_file)
        else:
            # If there's an old file, migrate it
            old_config = os.path.join (os.environ.get ('HOME'), '.bicho')
            if os.path.isfile (old_config):
                printout ("Old config file found in %s, moving to %s", \
                              (old_config, config_file))
                os.rename (old_config, config_file)
                self.__load_from_file (config_file)

    def load_from_file (self, path):
        self.__load_from_file (path)


def check_config(config):
    """
    """
    if config.type is None:
        raise InvalidConfig('Configuration parameter ''type'' is required')
    if config.url is None:
        raise InvalidConfig('Configuration parameter ''url'' is required')

    if config.input == 'db':
        check_db_in_config(config)
    if config.output == 'db':
        check_db_out_config(config)

def check_db_in_config(config):
    """
    """
    param = None

    if config.db_driver_in is None:
        param = 'db-driver-in'
    elif config.db_user_in is None:
        param = 'db-user-in'
    elif config.db_password_in is None:
        param = 'db-password-in'
    elif config.db_hostname_in is None:
        param = 'db-hostname-in'
    elif config.db_port_in is None:
        param = 'db-port-in'
    elif config.db_database_in is None:
        param = 'db-database-in'

    if param is not None:
        raise InvalidConfig('Configuration parameter ''%s'' is required' % param)

def check_db_out_config(config):
    """
    """
    param = None

    if config.db_driver_out is None:
        param = 'db-driver-out'
    elif config.db_user_out is None:
        param = 'db-user-out'
    elif config.db_password_out is None:
        param = 'db-password-out'
    elif config.db_hostname_out is None:
        param = 'db-hostname-out'
    elif config.db_port_out is None:
        param = 'db-port-out'
    elif config.db_database_out is None:
        param = 'db-database-out'

    if param is not None:
        raise InvalidConfig('Configuration parameter ''%s'' is required' % param)
