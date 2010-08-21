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

import sys, re, glob, os, getopt
from util import Util
from varfactory import VarFactory

class Optimizer(object):
    def __init__(self, config):
        """constructor

        Returns:
        void

        """
        self.ids = []
        self.classes = []
        self.id_map = {}
        self.class_map = {}
        self.config = config

    @staticmethod
    def showUsage():
        """shows usage information for this script"""
        print "\n======================"
        print "CSS-Optimizer thingy"
        print "======================"

        print "\nUSAGE:"
        # print "single file:"
        # print "entire directories:"
        # print "list of files:"
        print "./optimize.py --css file1.css,/path/to/css1,file2.css,file3.css --views /path/to/views1,file1.html,/path/to/views2/,file3.html --js main.js,/path/to/js"
        print "\nREQUIRED ARGUMENTS:"
        print "--views {path/to/views}      html files to rewrite (comma separated list of directories and files)"
        print "                             NOTE: if you pass views alone they are treated as if they have inline css/js"
        print "\nOPTIONAL ARGUMENTS:"
        print "--css {path/to/css}          css files to rewrite (comma separated list of directories and files)"
        print "--js {path/to/js}            js files to rewrite (comma separated list of directories and files)"
        print "--view-ext {extension}       sets the extension to look for in the view directory (defaults to html)"
        print "--ignore {classes,ids}       comma separated list of classes or ids to ignore when rewriting css (ie .sick_class,#sweet_id)"
        print "--tidy                       uses css tidy to optimize and minimize css after all the other optimizing is complete"
        print "--help                       shows this menu\n"
        sys.exit(2)

    def run(self):
        """runs the optimizer and does all the magic

        Returns:
        void

        """
        self.processCss()
        self.processViews()
        self.processJs()

        # maps all classes and ids found to shorter names
        self.processMaps()

        # optimize everything
        self.optimizeFiles(self.config.getCssFiles(), self.optimizeCss)
        self.optimizeFiles(self.config.getViewFiles(), self.optimizeHtml, self.config.view_extension)
        self.optimizeFiles(self.config.getJsFiles(), self.optimizeJavascript)

    def processCss(self):
        """gets all css files from config and processes them to see what to replace

        Returns:
        void

        """
        files = self.config.getCssFiles()
        for file in files:
            if not Util.isDir(file):
                self.processCssFile(file)
                continue
            for dir_file in Util.getFilesFromDir(file):
                self.processCssFile(dir_file)

    def processViews(self):
        files = self.config.getViewFiles()
        for file in files:
            if not Util.isDir(file):
                self.processView(file)
                continue
            for dir_file in Util.getFilesFromDir(file):
                self.processView(dir_file)

    def processJs(self):
        """gets all js files from config and processes them to see what to replace

        Returns:
        void

        """
        files = self.config.getJsFiles()
        for file in files:
            if not Util.isDir(file):
                self.processJsFile(file)
                continue
            for dir_file in Util.getFilesFromDir(file):
                self.processJsFile(dir_file)

    def processView(self, file):
        self.processCssFile(file, True)
        self.processJsFile(file, True)

    def processCssFile(self, path, inline = False):
        """processes a single css file to find all classes and ids to replace

        Arguments:
        path -- path to css file to process

        Returns:
        void

        """
        contents = Util.fileGetContents(path)
        if inline is True:
            blocks = self.getCssBlocks(contents)
            contents = ""
            for block in blocks:
                contents = contents + block

        ids_found = re.findall(r'(#\w+)(.*;)?', contents)
        classes_found = re.findall(r'(?!\.[0-9])\.\w+', contents)
        self.addIds(ids_found)
        self.addClasses(classes_found)

    def processJsFile(self, path, inline = False):
        """processes a single js file to find all classes and ids to replace

        Arguments:
        path -- path to css file to process

        Returns:
        void

        """
        contents = Util.fileGetContents(path)
        if inline is True:
            blocks = self.getJsBlocks(contents)
            contents = ""
            for block in blocks:
                contents = contents + block

        selectors = self.getJsSelectors(contents)
        for selector in selectors:
            id_selectors = ["getElementById"]

            if self.config.framework == "mootools":
                id_selectors.append("$")

            if selector[0] in id_selectors:
                self.addId("#" + selector[3])
                continue

            class_selectors = ["getElementsByClassName", "hasClass", "addClass", "removeClass"]
            if selector[0] in class_selectors:
                self.addClass("." + selector[3])
                continue

            bits = selector[3].split(" ")
            for bit in bits:
                if not bit:
                    continue

                if bit[0] == ".":
                    self.addClass(bit)
                elif bit[0] == "#":
                    self.addId(bit)

    def processMaps(self):
        """loops through classes and ids to process to determine shorter names to use for them
        and creates a dictionary with these mappings

        Returns:
        void

        """
        for class_name in self.classes:
            self.class_map[class_name] = "." + VarFactory.getNext("class")

        for id in self.ids:
            self.id_map[id] = "#" + VarFactory.getNext("id")

    def addId(self, id):
        """adds a single id to the master list of ids

        Arguments:
        id -- single id to add

        Returns:
        void

        """
        if id in self.config.ignore:
            return

        if id not in self.ids:
            self.ids.append(id)

    def addIds(self, ids):
        """adds a list of ids to the master id list to replace

        Arguments:
        ids -- list of ids to add

        Returns:
        void

        """
        for id in ids:
            if id[1] is '':
                self.addId(id[0])

    def addClass(self, class_name):
        """adds a single class to the master list of classes

        Arguments:
        class_name -- single class to add

        Returns:
        void

        """
        if class_name in self.config.ignore:
            return

        if class_name not in self.classes:
            self.classes.append(class_name)

    def addClasses(self, classes):
        """adds a list of classes to the master class list to replace

        Arguments:
        classes -- list of classes to add

        Returns:
        void

        """
        for class_name in classes:
            self.addClass(class_name)

    def optimizeFiles(self, paths, callback, extension = ""):
        """loops through a bunch of files and directories, runs them through a callback, then saves them to disk

        Arguments:
        paths -- array of files and directories
        callback -- function to process each file with

        Returns:
        void

        """
        for file in paths:
            if not Util.isDir(file):
                content = callback(file)
                new_path = Util.prependExtension("opt", file)
                print "optimizing " + file + " to " + new_path
                Util.filePutContents(new_path, content)
                continue

            directory = file + "_opt"
            Util.unlinkDir(directory)
            print "creating directory " + directory
            os.mkdir(directory)
            for dir_file in Util.getFilesFromDir(file, extension):
                content = callback(dir_file)
                new_path = directory + "/" + Util.getFileName(dir_file)
                print "optimizing " + dir_file + " to " + new_path
                Util.filePutContents(new_path, content)

    def optimizeCss(self, path):
        """replaces classes and ids with new values in a css file

        Arguments:
        path -- string path to css file to optimize

        Returns:
        string

        """
        css = Util.fileGetContents(path)
        return self.replaceCss(css)

    def optimizeHtml(self, path):
        """replaces classes and ids with new values in an html file

        Uses:
        Optimizer.replaceHtml

        Arguments:
        path -- string path to file to optimize

        Returns:
        string

        """
        html = Util.fileGetContents(path)
        html = self.replaceHtml(html)
        html = self.optimizeCssBlocks(html)
        html = self.optimizeJavascriptBlocks(html)

        return html

    def replaceHtml(self, html):
        """replaces classes and ids with new values in an html file

        Arguments:
        html -- contents to replace

        Returns:
        string

        """
        html = self.replaceHtmlIds(html)
        html = self.replaceHtmlClasses(html)
        return html

    def replaceHtmlIds(self, html):
        """replaces any instances of ids in html markup

        Arguments:
        html -- contents of file to replaces ids in

        Returns:
        string

        """
        for key, value in self.id_map.items():
            key = key[1:]
            value = value[1:]
            html = html.replace("id=\"" + key + "\"", "id=\"" + value + "\"")

        return html

    def replaceClassBlock(self, class_block, key, value):
        """replaces a class string with the new class name

        Arguments:
        class_block -- string from what would be found within class="{class_block}"
        key -- current class
        value -- new class

        Returns:
        string

        """
        key_length = len(key)
        classes = class_block.split(" ")
        i = 0
        for class_name in classes:
            if class_name == key:
                classes[i] = value

            # allows support for things like a.class_name as one of the js selectors
            elif key[0] in (".", "#") and class_name[-key_length:] == key:
                classes[i] = class_name.replace(key, value)
            i = i + 1

        return " ".join(classes)

    def replaceHtmlClasses(self, html):
        """replaces any instances of classes in html markup

        Arguments:
        html -- contents of file to replace classes in

        Returns:
        string

        """
        for key, value in self.class_map.items():
            key = key[1:]
            value = value[1:]
            class_blocks = re.findall(r'class\=((\'|\")(.*?)(\'|\"))', html)
            for class_block in class_blocks:
                new_block = self.replaceClassBlock(class_block[2], key, value)
                html = html.replace("class=" + class_block[0], "class=" + class_block[1] + new_block + class_block[3])

        return html

    def optimizeCssBlocks(self, html):
        """rewrites css blocks that are part of an html file

        Arguments:
        html -- contents of file we are replacing

        Returns:
        string

        """
        result_css = ""
        matches = self.getCssBlocks(html)
        for match in matches:
            match = self.replaceCss(match)
            result_css = result_css + match

            if self.config.tidy is True:
                from tidier import Tidier
                result_css = Tidier.run(result_css)

        if len(matches):
            return html.replace(matches[0], result_css)

        return html

    @staticmethod
    def getCssBlocks(html):
        """searches a file and returns all css blocks <style type="text/css"></style>

        Arguments:
        html -- contents of file we are replacing

        Returns:
        list

        """
        return re.compile(r'\<style.*?\>(.*?)\<\/style\>', re.DOTALL).findall(html)

    def replaceCss(self, css):
        """single call to handle replacing ids and classes

        Arguments:
        css -- contents of file to replace

        Returns:
        string

        """
        css = self.replaceCssFromDictionary(self.class_map, css)
        css = self.replaceCssFromDictionary(self.id_map, css)
        return css

    def replaceCssFromDictionary(self, dictionary, css):
        """replaces any instances of classes and ids based on a dictionary

        Arguments:
        dictionary -- map of classes or ids to replace
        css -- contents of css to replace

        Returns:
        string

        """
        # this really should be done better
        for key, value in dictionary.items():
            css = css.replace(key + "{", value + "{")
            css = css.replace(key + " {", value + " {")
            css = css.replace(key + "#", value + "#")
            css = css.replace(key + " #", value + " #")
            css = css.replace(key + ".", value + ".")
            css = css.replace(key + " .", value + " .")
            css = css.replace(key + ",", value + ",")
            css = css.replace(key + " ", value + " ")
            css = css.replace(key + ":", value + ":")

        return css

    def optimizeJavascriptBlocks(self, html):
        """rewrites javascript blocks that are part of an html file

        Arguments:
        html -- contents of file we are replacing

        Returns:
        string

        """
        matches = self.getJsBlocks(html)

        for match in matches:
            new_js = self.replaceJavascript(match)
            html = html.replace(match, new_js)

        return html

    @staticmethod
    def getJsBlocks(html):
        """searches a file and returns all javascript blocks: <script type="text/javascript"></script>

        Arguments:
        html -- contents of file we are replacing

        Returns:
        list

        """
        return re.compile(r'\<script(?! src).*?\>(.*?)\<\/script\>', re.DOTALL).findall(html)

    def optimizeJavascript(self, path):
        """optimizes javascript for a specific file

        Arguments:
        path -- path to js file on disk that we are optimizing

        Returns:
        string -- contents to replace file with

        """
        js = Util.fileGetContents(path)
        return self.replaceJavascript(js)

    def replaceJavascript(self, js):
        """single call to handle replacing ids and classes

        Arguments:
        js -- contents of file to replace

        Returns:
        string

        """
        js = self.replaceJsFromDictionary(self.id_map, js)
        js = self.replaceJsFromDictionary(self.class_map, js)
        return js

    @staticmethod
    def getJsSelectors(js):
        """finds all js selectors within a js block

        Arguments:
        js -- contents of js file to search

        Returns:
        list

        """
        return re.findall(r'(getElementById|getElementsByClassName|hasClass|addClass|removeClass|\$)?(\((\'|\")(.*?)(\'|\")\))', js)

    def replaceJsFromDictionary(self, dictionary, js):
        """replaces any instances of classes and ids based on a dictionary

        Arguments:
        dictionary -- map of classes or ids to replace
        js -- contents of javascript to replace

        Returns:
        string

        """
        class_selectors = ["getElementsByClassName", "hasClass", "addClass", "removeClass"]
        id_selectors = ["getElementById"]

        if self.config.framework == "mootools":
            id_selectors.append("$")

        for key, value in dictionary.items():
            blocks = self.getJsSelectors(js)
            for block in blocks:
                id_selectors
                if block[0] in id_selectors and key[0] == "#" and key[1:] == block[3]:
                    js = js.replace(block[0] + block[1], block[0] + "(" + block[2] + value[1:] + block[4] + ")")
                    continue

                if block[0] in class_selectors and key[0] == "." and key[1:] == block[3]:
                    js = js.replace(block[0] + block[1], block[0] + "(" + block[2] + value[1:] + block[4] + ")")
                    continue

                new_block = self.replaceClassBlock(block[3], key, value)
                js = js.replace(block[1], "(" + block[2] + new_block + block[4] + ")")

        return js

class Config(object):
    """configuration object for handling all config options for css-optimizer"""
    def __init__(self):
        """config object constructor

        Returns:
        void

        """
        self.css = []
        self.views = []
        self.js = []
        self.ignore = []
        self.framework = None
        self.view_extension = "html"
        self.tidy = False

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

    def setCssFiles(self, value):
        for value in value.split(","):
            self.css.append(value.rstrip("/"))

    def getCssFiles(self):
        return self.css

    def setViewFiles(self, value):
        for value in value.split(","):
            self.views.append(value.rstrip("/"))

    def getViewFiles(self):
        return self.views

    def setJsFiles(self, value):
        for value in value.split(","):
            self.js.append(value.rstrip("/"))

    def getJsFiles(self):
        return self.js

    def processArgs(self):
        """processes arguments passed in via command line and sets config settings accordingly

        Returns:
        void

        """
        try:
            opts, args = getopt.getopt(sys.argv[1:], "v:cjhetif", ["css=", "views=", "js=", "help", "view-ext=", "tidy", "ignore=", "framework="])
        except:
            Optimizer.showUsage()
            sys.exit(2)

        views_set = False

        for key, value in opts:
            if key in ("-h", "--help"):
                Optimizer.showUsage()
                sys.exit(2)
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
            elif key in ("-t", "--tidy"):
                self.tidy = True
            elif key in ("-f", "--framework"):
                self.framework = value

        # you have to at least have a view
        if views_set is False:
            Optimizer.showUsage()
            sys.exit(2)
