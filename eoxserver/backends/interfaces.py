#-------------------------------------------------------------------------------
# $Id$
#
# Project: EOxServer <http://eoxserver.org>
# Authors: Stephan Krause <stephan.krause@eox.at>
#          Stephan Meissl <stephan.meissl@eox.at>
#
#-------------------------------------------------------------------------------
# Copyright (C) 2011 EOX IT Services GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies of this Software or works derived from this Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#-------------------------------------------------------------------------------


class AbstractStorageInterface(object):
    @property
    def name(self):
        "Name of the storage implementation."

    def validate(self, url):
        """ Validates the given storage locator and raises a ValidationError
            if errors occurred.
        """

class FileStorageInterface(AbstractStorageInterface):
    """ Interface for storages that provide access to files and allow the 
        retrieval of those.
    """

    def retrieve(self, url, location, path):
        """ Retrieve a remote file from the storage specified by the given `url` 
            and location and store it to the given `path`. Storages that don't
            need to actually retrieve and store files, just need to return a 
            path to a local file instead of storing it under `path`.
        """


class ConnectedStorageInterface(AbstractStorageInterface):
    """ Interface for storages that do not store "files" but provide access to
        data in a different fashion.
    """
    
    def connect(self, url, location):
        """ Return a connection string for a remote dataset residing on a 
            storage specified by the given `url` and `location`.
        """


class PackageInterface(object):

    @property
    def name(self):
        "Name of the package implementation."


    def extract(self, package_filename, location, path):
        """ Extract a file specified by the `location` from the package to the 
            given `path` specification.
        """
