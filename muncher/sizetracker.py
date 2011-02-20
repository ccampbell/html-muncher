#!/usr/bin/env python
# Copyright 2011 Craig Campbell
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

import sys, os, gzip
from util import Util

class SizeTracker(object):
    original_size = 0
    original_size_gzip = 0
    new_size = 0
    new_size_gzip = 0

    @staticmethod
    def addSize(path, new = False):

        # gzip the file to get that size
        gzip_path = path + '.gz'
        f_in = open(path, 'rb')
        f_out = gzip.open(gzip_path, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()

        size = os.path.getsize(path)
        gzip_size = os.path.getsize(gzip_path)

        if new is False:
            SizeTracker.original_size += size
            SizeTracker.original_size_gzip += gzip_size
        else:
            SizeTracker.new_size += size
            SizeTracker.new_size_gzip += gzip_size

        Util.unlink(gzip_path)

    @staticmethod
    def trackFile(path, new_path):
        SizeTracker.addSize(path)
        SizeTracker.addSize(new_path, True)

    @staticmethod
    def getSize(bytes):
        if bytes < 1024:
            return str(bytes) + " bytes"

        kb = float(bytes) / 1024
        kb = round(kb, 2)
        return str(kb) + " KB"

    @staticmethod
    def savings():
        percent = 100 - (float(SizeTracker.new_size) / float(SizeTracker.original_size)) * 100
        gzip_percent = 100 - (float(SizeTracker.new_size_gzip) / float(SizeTracker.original_size_gzip)) * 100

        string = "\noriginal size:   " + SizeTracker.getSize(SizeTracker.original_size) + " (" + SizeTracker.getSize(SizeTracker.original_size_gzip) + " gzipped)"
        string += "\nmunched size:    " + SizeTracker.getSize(SizeTracker.new_size) + " (" + SizeTracker.getSize(SizeTracker.new_size_gzip) + " gzipped)"
        string += "\n                 saved " + str(round(percent, 2)) + "% off the original size (" + str(round(gzip_percent, 2)) + "% off the gzipped size)\n"
        return string
