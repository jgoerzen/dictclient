#!/usr/bin/env python2.2

# $Id: setup.py,v 1.3 2002/04/18 14:51:59 jgoerzen Exp $

# Python client for DICT protocol.
# COPYRIGHT #
# Copyright (C) 2002 John Goerzen
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# END OF COPYRIGHT #


from distutils.core import setup
import dictclient

setup(name = "dictclient",
      version = "1.0",
      description = "Client library for the dict protocol",
      author = "John Goerzen",
      author_email = 'jgoerzen@complete.org',
      url = 'gopher://quux.org/1/devel/dictclient',
      py_modules = ['dictclient'],
      license = "GPL version 2"
)

