# -*- coding: utf-8 -*-
#
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
#       Daniel Izquierdo Cortazar <dizquierdo@libresoft.es>
#       Luis Cañas Díaz <lcanas@libresoft.es>
#       Santiago Dueñas <sduenas@libresoft.es>
#

import sys
from optparse import OptionGroup, OptionParser

from Config import check_config, Config, ErrorLoadingConfig, InvalidConfig
import Bicho
import info
from utils import printerr

def set_config_options(type, uri, options):
    """
    """
    config = Config()

    if options.cfgfile is not None:
        config.load_from_file(options.cfgfile)
    else:
        config.load()

    # Generic options
    config.type = type
    config.url = uri
    if options.debug:
        config.debug = options.debug
    if options.delay:
        config.delay = options.delay
    if options.path:
        config.path = options.path
    if options.input:
        config.input = options.input
    if options.output:
        config.output = options.output

    # Output database options
    if options.db_driver_out:
        config.db_driver_out = options.db_driver_out
    if options.db_user_out:
        config.db_user_out = options.db_user_out
    if options.db_password_out:
        config.db_password_out = options.db_password_out
    if options.db_hostname_out:
        config.db_hostname_out = options.db_hostname_out
    if options.db_port_out:
        config.db_port_out = options.db_port_out
    if options.db_database_out:
        config.db_database_out = options.db_database_out

    # Input database options
    if options.db_driver_in:
        config.db_driver_in = options.db_driver_in
    if options.db_user_in:
        config.db_user_in = options.db_user_in
    if options.db_password_in:
        config.db_password_in = options.db_password_in
    if options.db_hostname_in:
        config.db_hostname_in = options.db_hostname_in
    if options.db_port_in:
        config.db_port_in = options.db_port_in
    if options.db_database_in:
        config.db_database_in = options.db_database_in

    return config

def main():
    """
    """
    # Note: Default values for options are defined on
    # configuration module
    usage = 'Usage: %prog [options] <type> <URI>'

    parser = OptionParser(usage=usage, description=info.DESCRIPTION,
                          version=info.VERSION)

    # General options
    parser.add_option('--cfg', dest='cfgfile', default=None,
                      help='Use a custom configuration file')
    parser.add_option('-g', '--debug', action='store_true', dest='debug',
                      help='Enable debug mode')
    parser.add_option('-d', '--delay', type='int', dest='delay',
                      help='Delay in seconds betweeen petitions to avoid been banned')
    parser.add_option('-i', '--input', choices=['url', 'db'],
                      dest='input', help='Input format')
    parser.add_option('-o', '--output', choices=['db'],
                      dest='output', help='Output format')
    parser.add_option('-p', '--path', dest='path',
                      help='Path where downloaded URLs will be stored')

    # Options for output database
    group = OptionGroup(parser, 'Output database specific options')
    group.add_option('--db-driver-out',
                     choices=['sqlite','mysql','postgresql'],
                     dest='db_driver_out', help='Output database driver')
    group.add_option('--db-user-out', dest='db_user_out',
                     help='Database user name')
    group.add_option('--db-password-out', dest='db_password_out',
                     help='Database user password')
    group.add_option('--db-hostname-out', dest='db_hostname_out',
                     help='Name of the host where database server is running')
    group.add_option('--db-port-out', dest='db_port_out',
                     help='Port of the host where database server is running')
    group.add_option('--db-database-out', dest='db_database_out',
                     help='Output database name')
    parser.add_option_group(group)

    # Options for input database
    group = OptionGroup(parser, 'Input database specific options')
    group.add_option('--db-driver-in',
                     choices=['sqlite', 'mysql', 'postgresql'],
                     dest='db_driver_in', help='Input database driver')
    group.add_option('--db-user-in', dest='db_user_in',
                     help='Database user name')
    group.add_option('--db-password-in', dest='db_password_in',
                     help='Database user password')
    group.add_option('--db-hostname-in', dest='db_hostname_in',
                     help='Name of the host where database server is running')
    group.add_option('--db-port-in', dest='db_port_in',
                     help='Port of the host where database server is running')
    group.add_option('--db-database-in', dest='db_database_in',
                     help='Input database name')
    parser.add_option_group(group)

    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error('Incorrect number of arguments')

    try:
        config = set_config_options(args[0], args[1], options)
        check_config(config)
    except (ErrorLoadingConfig, InvalidConfig), e:
        printerr(str(e))
        sys.exit(2)

    bicho = Bicho.Bicho ()
    bicho.run(args[1])


if __name__ == "__main__":
    main()
