#!/usr/bin/python

# Copyright 2010 Craig Campbell
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os, shutil

class Util:
    """collection of various utility functions"""
    @staticmethod
    def fileExists(path):
        """determines if a file exists

        Arguments:
        path -- path to file on disk

        Returns:
        bool

        """
        return os.path.isfile(path)
        
    @staticmethod
    def isDir(path):
        """determines if a path is a directory

        Arguments:
        path -- path on disk

        Returns:
        bool

        """
        return os.path.isdir(path)

    @staticmethod
    def dump(obj):
        """displays an object as a string for debugging

        Arguments:
        obj -- object

        Returns:
        string

        """
        for attr in dir(obj):
            print "obj.%s = %s" % (attr, getattr(obj, attr))

    @staticmethod
    def getExtension(path):
        """gets the extension from a file

        Arguments:
        path -- string of the file name

        Returns:
        string

        """
        return path.split(".").pop()

    @staticmethod
    def getBasePath(path):
        """gets the base directory one level up from the current path

        Arguments:
        path -- path to file or directory

        Returns:
        string

        """
        bits = path.split("/")
        last_bit = bits.pop()
        return "/".join(bits)
        # return "/".join(bits).rstrip(last_bit)

    @staticmethod
    def unlink(path):
        """deletes a file on disk

        Arguments:
        path -- path to file on disk

        Returns:
        void

        """
        if Util.fileExists(path):
            os.unlink(path)

    @staticmethod
    def unlinkDir(path):
        """removes an entire directory on disk

        Arguments:
        path -- path to directory to remove

        Returns:
        void

        """
        try:
            shutil.rmtree(path)
        except:
            pass

    @staticmethod
    def fileGetContents(path):
        """gets the contents of a file

        Arguments:
        path -- path to file on disk

        Returns:
        string

        """
        if not Util.fileExists(path):
            print "file does not exist at path " + path
            print "skipping"
        file = open(path, "r")
        contents = file.read()
        file.close()
        return contents

    @staticmethod
    def filePutContents(path, contents):
        """puts contents into a file

        Arguments:
        path -- path to file to write to
        contents -- contents to put into file

        Returns:
        void

        """
        file = open(path, "w")
        file.write(contents)
        file.close()
