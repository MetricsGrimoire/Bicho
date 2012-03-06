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
#        Carlos Garcia Campos <carlosgc@libresoft.es>
#        Luis Cañas Díaz <lcanas@libresoft.es>
#        Alvaro del Castillo <acs@bitergia.com>
#
# We should migrate to argparse. optparse is deprecated since Python 2.7

from backends import Backend
import info
from optparse import OptionGroup, OptionParser
import pprint
import sys
from urllib2 import Request, urlopen, URLError, HTTPError

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

    @staticmethod
    def load_from_file (config_file):
        try:
            f = open (config_file, 'r')
            exec f in Config.__dict__
            f.close ()
        except Exception, e:
            raise ErrorLoadingConfig ("Error reading config file %s (%s)" % (\
                    config_file, str (e)))
        # print dir(Config)          
    
    @staticmethod        
    def load ():
        import os
        from utils import bicho_dot_dir, printout

        # First look in /etc
        # FIXME /etc is not portable
        config_file = os.path.join ('/etc', 'bicho')
        if os.path.isfile (config_file):
            Config.load_from_file (config_file)

        # Then look at $HOME
        config_file = os.path.join (bicho_dot_dir (), 'config')
        if os.path.isfile (config_file):
            Config.load_from_file (config_file) 
        else:
            # If there's an old file, migrate it
            old_config = os.path.join (os.environ.get ('HOME'), '.bicho')
            if os.path.isfile (old_config):
                printout ("Old config file found in %s, moving to %s", \
                              (old_config, config_file))
                os.rename (old_config, config_file)
                Config.load_from_file (config_file)

    @staticmethod
    def check_config():
        """
        """        
        
        if not vars(Config).has_key('backend') or  Config.backend is None:
            raise InvalidConfig('Configuration parameter ''backend'' is required')
        else:
            if Config.backend+".py" not in Backend.get_all_backends():
                raise InvalidConfig('Backend "'+ Config.backend + '" does not exists')
        if not vars(Config).has_key('url') or Config.url is None:
            raise InvalidConfig('Configuration parameter ''url'' is required')
        else:
            req = Request(Config.url)
            try:
                print "Opening URL: ", Config.url
                response = urlopen(req)
            except HTTPError, e:
                raise InvalidConfig('The server could not fulfill the request '
                                   + str(e.msg) + '('+ str(e.code)+')')
            except URLError, e:
                raise InvalidConfig('We failed to reach a server. ' + str(e.reason))
            else:
                print Config.url, "OK"
                retval = True    
                    
            if vars(Config).has_key('input') and Config.input == 'db':
                Config.check_db_in_config()
            if vars(Config).has_key('output') and Config.output == 'db':
                Config.check_db_out_config()
                            
    @staticmethod
    def check_db_in_config():
        """
        """
        
        param = None
    
        if Config.db_driver_in is None:
            param = 'db-driver-in'
        elif Config.db_user_in is None:
            param = 'db-user-in'
        elif Config.db_password_in is None:
            param = 'db-password-in'
        elif Config.db_hostname_in is None:
            param = 'db-hostname-in'
        elif Config.db_port_in is None:
            param = 'db-port-in'
        elif Config.db_database_in is None:
            param = 'db-database-in'        
    
        if param is not None:
            raise InvalidConfig('Configuration parameter ''%s'' is required' % param)
    
    @staticmethod
    def check_db_out_config():
        """
        """
        param = None
    
        if Config.db_driver_out is None:
            param = 'db-driver-out'
        elif Config.db_user_out is None:
            param = 'db-user-out'
        elif Config.db_password_out is None:
            param = 'db-password-out'
        elif Config.db_hostname_out is None:
            param = 'db-hostname-out'
        elif Config.db_port_out is None:
            param = 'db-port-out'
        elif Config.db_database_out is None:
            param = 'db-database-out'
    
        if param is not None:
            raise InvalidConfig('Configuration parameter ''%s'' is required' % param)
        
    @staticmethod
    def clean_empty_options(options):
        clean_opt = {};        
        for option in vars(options):
            if vars(options)[option] is not None:
                clean_opt[option]=vars(options)[option]
        return clean_opt
        
    @staticmethod
    def set_config_options(usage):
        """
        """
        
        parser = OptionParser(usage=usage, description=info.DESCRIPTION,
                              version=info.VERSION)

        # General options
        parser.add_option('-b', '--backend', dest='backend',
                          help='Backend used to fetch issues', default=None)
        parser.add_option('-c', '--cfg', dest='cfgfile', 
                          help='Use a custom configuration file', default=None)
        parser.add_option('-d', '--delay', type='int', dest='delay',
                          help='Delay in seconds betweeen petitions to avoid been banned',
                          default='0')
        parser.add_option('-g', '--debug', action='store_true', dest='debug',
                          help='Enable debug mode', default=False)
        parser.add_option('-i', '--input', choices=['url', 'db'],
                          dest='input', help='Input format', default='url')
        parser.add_option('-o', '--output', choices=['db'],
                          dest='output', help='Output format', default='db')
        parser.add_option('-p', '--path', dest='path',
                          help='Path where downloaded URLs will be stored',
                          default=None)
        parser.add_option('-u', '--url', dest='url',
                          help='URL to get issues from using the backend',
                          default=None)
    
        # Options for output database
        group = OptionGroup(parser, 'Output database specific options')
        group.add_option('--db-driver-out',
                         choices=['sqlite','mysql','postgresql'],
                         dest='db_driver_out', help='Output database driver',
                         default='mysql')
        group.add_option('--db-user-out', dest='db_user_out',
                         help='Database user name', default=None)
        group.add_option('--db-password-out', dest='db_password_out',
                         help='Database user password', default=None)
        group.add_option('--db-hostname-out', dest='db_hostname_out',
                         help='Name of the host where database server is running',
                         default='localhost')
        group.add_option('--db-port-out', dest='db_port_out',
                         help='Port of the host where database server is running',
                         default='3306')
        group.add_option('--db-database-out', dest='db_database_out',
                         help='Output database name', default=None)
        parser.add_option_group(group)
    
        # Options for input database
        group = OptionGroup(parser, 'Input database specific options')
        group.add_option('--db-driver-in',
                         choices=['sqlite', 'mysql', 'postgresql'],
                         dest='db_driver_in', help='Input database driver',
                         default=None)
        group.add_option('--db-user-in', dest='db_user_in',
                         help='Database user name', default=None)
        group.add_option('--db-password-in', dest='db_password_in',
                         help='Database user password', default=None)
        group.add_option('--db-hostname-in', dest='db_hostname_in',
                         help='Name of the host where database server is running',
                         default=None)
        group.add_option('--db-port-in', dest='db_port_in',
                         help='Port of the host where database server is running',
                         default=None)
        group.add_option('--db-database-in', dest='db_database_in',
                         help='Input database name', default=None)
        parser.add_option_group(group)
                
        (options, args) = parser.parse_args()
                            
        if options.cfgfile is not None:
            Config.load_from_file(options.cfgfile)
        else:
            Config.load()
                        
        # Command line options have preference
        # Backwards compatibility
        if (len(args) > 0):
            Config.backend=args[0]
        if (len(args) == 2):
            Config.url=args[1]
            
        # Not remove config file options with empty default values                               
        Config.__dict__.update(Config.clean_empty_options(options))

        Config.check_config ()
