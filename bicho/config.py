# -*- coding: utf-8 -*-
# Copyright (C) 2013 GSyC/LibreSoft, Universidad Rey Juan Carlos
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
#        Sumana Harihareswara <sumanah@panix.com>

from backends import Backend
import info
from argparse import ArgumentParser
import os
from urllib2 import Request, urlopen, urlparse, URLError, HTTPError

# 500 is the max recommend by bugmaster@gnome.org.
# Use 1 for legacy working.
# 250 for working with bugzilla in redhat
MAX_ISSUES_PER_QUERY = 200


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


class Config():
    """
    Config objects load configuration from files and from command-line options.

    Note: this is an old-style class and does not inherit from object.
    """
    @staticmethod
    def load_from_file(config_file):
        try:
            f = open(config_file, 'r')
            exec f in Config.__dict__  # run variable assignments
            f.close()
        except Exception, e:
            raise ErrorLoadingConfig("Error reading config file %s (%s)" %
                                     (config_file, str(e)))

    @staticmethod
    def load():
        """
        Try to load a config file from known default locations.

        For the format of the config file, see 'config.sample'
        in the toplevel directory.
        """
        # FIXME: a hack to avoid circular dependencies.
        from utils import bicho_dot_dir, printout

        # First look in /etc
        # FIXME /etc is not portable
        config_file = os.path.join('/etc', 'bicho')
        if os.path.isfile(config_file):
            Config.load_from_file(config_file)

        # Then look at $HOME
        config_file = os.path.join(bicho_dot_dir(), 'config')
        if os.path.isfile(config_file):
            Config.load_from_file(config_file)
        else:
            # If there's an old file, migrate it
            old_config = os.path.join(os.environ.get('HOME'), '.bicho')
            if os.path.isfile(old_config):
                printout("Old config file found in %s, moving to %s",
                         (old_config, config_file))
                os.rename(old_config, config_file)
                Config.load_from_file(config_file)

    @staticmethod
    def check_params(check_params):
        for param in check_params:
            # raise exception if the param is None or nonexistent
            if getattr(Config, param, None) is None:
                raise InvalidConfig('Configuration parameter ''%s'' is required' % param)

    @staticmethod
    def check_config():
        """
        Check crucial configuration details for existence and workability.

        Runs checks to see whether bugtracker's URL is reachable, whether
        backend is available at the right filename, and whether the script has
        the key arguments it needs to run: URL, backend, and database details.

        The filename for the backend in the backends/ directory needs to be the
        same as the configuration argument specifying that backend. For
        instance, invoking the Launchpad backend uses 'lp', and so the filename
        is 'lp.py'.
        """
        Config.check_params(['url', 'backend'])

        if Config.backend + ".py" not in Backend.get_all_backends():
            raise InvalidConfig('Backend "' + Config.backend + '" does not exist')

        url = urlparse.urlparse(Config.url)
        check_url = urlparse.urljoin(url.scheme + '://' + url.netloc, '')
        print("Checking URL: " + check_url)
        req = Request(check_url)

        if Config.backend != 'github':
            try:
                response = urlopen(req)
            except HTTPError, e:
                raise InvalidConfig('The server could not fulfill the request '
                                    + str(e.msg) + '(' + str(e.code) + ')')
            except URLError, e:
                raise InvalidConfig('We failed to reach a server. ' + str(e.reason))
            except ValueError, e:
                print("Not an URL: " + Config.url)

        if getattr(Config, 'input', None) == 'db':
            Config.check_params(['db_driver_in', 'db_user_in',
                                 'db_password_in', 'db_hostname_in',
                                 'db_port_in', 'db_database_in'])
        if getattr(Config, 'output', None) == 'db':
            Config.check_params(['db_driver_out', 'db_user_out',
                                 'db_password_out', 'db_hostname_out',
                                 'db_port_out', 'db_database_out'])

    @staticmethod
    def clean_empty_options(options):
        """
        Create a dict of options whose values are 'None' or nonexistent.
        Also, if there's a default value that came in from argparse, we
        don't want it ending up in the Config object.

        FIXME: should use defaultdict module to provide default values.
        """
        clean_opt = {}
        d = vars(options)
        for option in d:
            if (d[option] is not None) and not hasattr(Config, option):
                clean_opt[option] = d[option]
        return clean_opt

    @staticmethod
    def set_config_options(usage):
        """
        Take command-line arguments and options from the configuration file.

        Command-line keyword arguments only, not positional -- breaking
        change November 2013.

        In case of conflict, command-line options are meant to override
        options specified in config file.
        """

        parser = ArgumentParser(description=info.DESCRIPTION)
        parser.add_argument('--version', action='version', version=info.VERSION)

        # General options
        parser.add_argument('-b', '--backend', dest='backend',
                            help='Backend used to fetch issues', default=None)
        parser.add_argument('--backend-user', dest='backend_user',
                            help='Backend user', default=None)
        parser.add_argument('--backend-password', dest='backend_password',
                            help='Backend password', default=None)
        parser.add_argument('--backend-token', dest='backend_token',
                            help='Backend authentication token', default=None)
        parser.add_argument('-c', '--cfg', dest='cfgfile',
                            help='Use a custom configuration file', default=None)
        parser.add_argument('-d', '--delay', type=int, dest='delay',
                            help='Delay in seconds betweeen petitions to avoid been banned',
                            default='5')
        parser.add_argument('-g', '--debug', action='store_true', dest='debug',
                            help='Enable debug mode', default=False)
        parser.add_argument('--gerrit-project', dest='gerrit_project',
                            help='Project to be analyzed (gerrit backend)',
                            default=None)
        parser.add_argument('-i', '--input', choices=['url', 'db'],
                            dest='input', help='Input format', default='url')
        parser.add_argument('-o', '--output', choices=['db'],
                            dest='output', help='Output format', default='db')
        parser.add_argument('-p', '--path', dest='path',
                            help='Path where downloaded URLs will be stored',
                            default=None)
        parser.add_argument('-u', '--url', dest='url',
                            help='URL to get issues from using the backend',
                            default=None)
        parser.add_argument('-l', '--logtable', action='store_true',
                            dest='logtable',
                            help='Enable generation of issues log table',
                            default=False)
        parser.add_argument('-n', '--num-issues', type=int, dest='nissues',
                            help='Number of issues requested on each query',
                            default=MAX_ISSUES_PER_QUERY)

        # Options for output database
        group = parser.add_argument_group('Output database specific options')
        group.add_argument('--db-driver-out',
                           choices=['sqlite', 'mysql', 'postgresql'],
                           dest='db_driver_out', help='Output database driver',
                           default='mysql')
        group.add_argument('--db-user-out', dest='db_user_out',
                           help='Database user name', default=None)
        group.add_argument('--db-password-out', dest='db_password_out',
                           help='Database user password', default=None)
        group.add_argument('--db-hostname-out', dest='db_hostname_out',
                           help='Name of the host where database server is running',
                           default='localhost')
        group.add_argument('--db-port-out', dest='db_port_out',
                           help='Port of the host where database server is running',
                           default='3306')
        group.add_argument('--db-database-out', dest='db_database_out',
                           help='Output database name', default=None)

        # Options for input database
        group = parser.add_argument_group('Input database specific options')
        group.add_argument('--db-driver-in',
                           choices=['sqlite', 'mysql', 'postgresql'],
                           dest='db_driver_in', help='Input database driver',
                           default=None)
        group.add_argument('--db-user-in', dest='db_user_in',
                           help='Database user name', default=None)
        group.add_argument('--db-password-in', dest='db_password_in',
                           help='Database user password', default=None)
        group.add_argument('--db-hostname-in', dest='db_hostname_in',
                           help='Name of the host where database server is running',
                           default=None)
        group.add_argument('--db-port-in', dest='db_port_in',
                           help='Port of the host where database server is running',
                           default=None)
        group.add_argument('--db-database-in', dest='db_database_in',
                           help='Input database name', default=None)

        # Maniphest options
        group = parser.add_argument_group('Maniphest options')
        group.add_argument('--no-resume', action='store_true', dest='no_resume',
                           help='Disable resume mode', default=False)

        args = parser.parse_args()

        if args.cfgfile is not None:  # if a config file was specified on the command line
            Config.load_from_file(args.cfgfile)  # try to load from that file
        else:
            Config.load()  # try to load a config file from default locations

        # Reconciling config file options with command-line options
        Config.__dict__.update(Config.clean_empty_options(args))
        Config.check_config()
