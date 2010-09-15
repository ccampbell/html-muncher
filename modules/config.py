#!/usr/bin/env python
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

import sys, getopt
from optimizer import Optimizer

class Config(object):
    """configuration object for handling all config options for html-muncher"""
    def __init__(self):
        """config object constructor

        Returns:
        void

        """
        self.css = []
        self.views = []
        self.js = []
        self.ignore = []
        self.class_selectors = ["getElementsByClassName", "hasClass", "addClass", "removeClass"]
        self.id_selectors = ["getElementById"]
        self.custom_selectors = ["document.querySelector"]
        self.framework = None
        self.view_extension = "html"
        self.show_savings = False
        self.compress_html = False
        self.verbose = False

    def getArgCount(self):
        """gets the count of how many arguments are present

        Returns:
        int

        """
        return len(sys.argv)

    def setIgnore(self, value):
        """sets what classes and ids we should ignore and not shorten

        Arguments:
        value -- comma separated list of classes or ids

        Returns:
        void

        """
        for name in value.split(","):
            self.ignore.append(name)

    def setCustomSelectors(self, value):
        for value in value.split(","):
            self.custom_selectors.append(value.lstrip("."))

    def addClassSelectors(self, value):
        for value in value.split(","):
            self.class_selectors.append(value)

    def addIdSelectors(self, value):
        for value in value.split(","):
            self.id_selectors.append(value)

    def setCssFiles(self, value):
        for value in value.split(","):
            self.css.append(value.rstrip("/"))

    def setViewFiles(self, value):
        for value in value.split(","):
            self.views.append(value.rstrip("/"))

    def setJsFiles(self, value):
        for value in value.split(","):
            self.js.append(value.rstrip("/"))

    def setFramework(self, name):
        self.framework = name.lower()
        if self.framework == "jquery":
            self.custom_selectors.append("$").append("jQuery")
        elif self.framework == "mootools":
            self.id_selectors.append("$")
            self.custom_selectors.append("getElement")

    def processArgs(self):
        """processes arguments passed in via command line and sets config settings accordingly

        Returns:
        void

        """
        try:
            opts, args = getopt.getopt(sys.argv[1:], "v:cjheifsldmor", ["css=", "views=", "js=", "help", "view-ext=", "ignore=", "framework=", "selectors=", "class-selectors=", "id-selectors=", "compress-html", "show-savings", "verbose"])
        except:
            Optimizer.showUsage()

        views_set = False

        for key, value in opts:
            if key in ("-h", "--help"):
                Optimizer.showUsage()
            elif key in ("-c", "--css"):
                self.setCssFiles(value)
            elif key in ("-v", "--views"):
                views_set = True
                self.setViewFiles(value)
            elif key in ("-j", "--js"):
                self.setJsFiles(value)
            elif key in ("-i", "--ignore"):
                self.setIgnore(value)
            elif key in ("-e", "--view-ext"):
                self.view_extension = value
            elif key in ("-f", "--framework"):
                self.setFramework(value)
            elif key in ("-s", "--selectors"):
                self.setCustomSelectors(value)
            elif key in ("-l", "--class-selectors"):
                self.addClassSelectors(value)
            elif key in ("-d", "--id-selectors"):
                self.addIdSelectors(value)
            elif key in ("-m", "--compress-html"):
                self.compress_html = True
            elif key in ("-o", "--show-savings"):
                self.show_savings = True
            elif key in ("-r", "--verbose"):
                self.verbose = True

        # you have to at least have a view
        if views_set is False:
            Optimizer.showUsage()
