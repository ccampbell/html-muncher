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

import sys, re, glob, os
from operator import itemgetter
from util import Util
from varfactory import VarFactory
from sizetracker import SizeTracker

class Muncher(object):
    def __init__(self, config):
        """constructor

        Returns:
        void

        """
        self.id_counter = {}
        self.class_counter = {}
        self.id_map = {}
        self.class_map = {}
        self.config = config

    @staticmethod
    def showUsage():
        """shows usage information for this script"""
        print "\n---------------------------------"
        print " html-muncher"
        print "---------------------------------"

        print "\n" + '\033[91m' + "USAGE:" + '\033[0m'
        print "munch --css file1.css,/path/to/css1,file2.css,file3.css --html /path/to/views1,file1.html,/path/to/views2/,file3.html --js main.js,/path/to/js"
        print "\n" + '\033[91m' + "REQUIRED ARGUMENTS:" + '\033[0m'
        print "--html {path/to/views}       html files to rewrite (comma separated list of directories and files)"
        print "\n" + '\033[91m' + "OPTIONAL ARGUMENTS:" + '\033[0m'
        print "--css {path/to/css}          css files to rewrite (comma separated list of directories and files)"
        print ""
        print "--js {path/to/js}            js files to rewrite (comma separated list of directories and files)"
        print ""
        print "--view-ext {extension}       sets the extension to look for in the view directory (defaults to html)"
        print ""
        print "--ignore {classes,ids}       comma separated list of classes or ids to ignore when rewriting css (ie .sick_class,#sweet_id)"
        print ""
        print "--compress-html              strips new line characters to compress html files specified with --html"
        print "                             be careful when using this becuase it has not been thoroughly tested"
        print ""
        print "--framework                  name of js framework to use for selectors (currently only jquery or mootools)"
        print ""
        print "--selectors                  comma separated custom selectors using css selectors"
        print "                             for example if you have $.qs(\"#test .div\") this param would be qs"
        print ""
        print "--id-selectors               comma separated id selectors with strings"
        print "                             for example if you are using .addId(\"test\") this param would be addId"
        print ""
        print "--class-selectors            comma separated class selectors with strings"
        print "                             for example if you have selectClass(\"my_class\") this param would be selectClass"
        print ""
        print "--js-manifest                path to a js file containing class name/id constants"
        print ""
        print "--rewrite-constants          when using a manifest file this will take any constants with values as strings"
        print "                             and rewrite the values to be numbers"
        print ""
        print "--show-savings               will output how many bytes were saved by munching"
        print ""
        print "--verbose                    output more information while the script runs"
        print ""
        print "--help                       shows this menu\n"
        sys.exit(2)

    def run(self):
        """runs the optimizer and does all the magic

        Returns:
        void

        """
        self.output("searching for classes and ids...", False)

        if self.config.js_manifest is not None:
            self.outputJsWarnings()

        self.processCss()
        self.processViews()

        if self.config.js_manifest is None:
            self.processJs()
        else:
            self.processJsManifest()

        self.output("mapping classes and ids to new names...", False)
        # maps all classes and ids found to shorter names
        self.processMaps()

        # optimize everything
        self.output("munching css files...", False)
        self.optimizeFiles(self.config.css, self.optimizeCss)

        self.output("munching html files...", False)
        self.optimizeFiles(self.config.views, self.optimizeHtml, self.config.view_extension, self.config.compress_html)

        self.output("munching js files...", False)

        if self.config.js_manifest is None:
            self.optimizeFiles(self.config.js, self.optimizeJavascript)
        else:
            self.optimizeJsManifest()

        self.output("done", False)

        if self.config.show_savings:
            self.output(SizeTracker.savings(), False)

    def outputJsWarnings(self):
        pass

    def output(self, text, verbose_only = True):
        """outputs text during the script run

        Arguments:
        text -- string of text to output
        verbose_only -- should we only show this in verbose mode?

        Returns:
        void

        """
        if verbose_only and not self.config.verbose:
            return

        print text

    def processCssDirectory(self, file):
        """processes a directory of css files

        Arguments:
        file -- path to directory

        Returns:
        void

        """
        if ".svn" in file:
            return

        for dir_file in Util.getFilesFromDir(file):
            if Util.isDir(dir_file):
                self.processCssDirectory(dir_file)
                continue

            self.processCssFile(dir_file)

    def processCss(self):
        """gets all css files from config and processes them to see what to replace

        Returns:
        void

        """
        files = self.config.css
        for file in files:
            if not Util.isDir(file):
                self.processCssFile(file)
                continue
            self.processCssDirectory(file)

    def processViewDirectory(self, file):
        """processes a directory of view files

        Arguments:
        file -- path to directory

        Returns:
        void

        """
        if ".svn" in file:
            return

        for dir_file in Util.getFilesFromDir(file):
            if Util.isDir(dir_file):
                self.processViewDirectory(dir_file)
                continue

            self.processView(dir_file)

    def processViews(self):
        """processes all view files

        Returns:
        void

        """
        files = self.config.views
        for file in files:
            if not Util.isDir(file):
                self.processView(file)
                continue
            self.processViewDirectory(file)

    def processJsDirectory(self, file):
        """processes a directory of js files

        Arguments:
        file -- path to directory

        Returns:
        void

        """
        if ".svn" in file:
            return

        for dir_file in Util.getFilesFromDir(file):
            if Util.isDir(dir_file):
                self.processJsDirectory(dir_file)
                continue
            self.processJsFile(dir_file)

    def processJs(self):
        """gets all js files from config and processes them to see what to replace

        Returns:
        void

        """
        files = self.config.js
        for file in files:
            if not Util.isDir(file):
                self.processJsFile(file)
                continue
            self.processJsDirectory(file)

    def processView(self, file):
        """processes a single view file

        Arguments:
        file -- path to directory

        """
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

        ids_found = re.findall(r'((?<!\:\s)(?<!\:)#\w+)(\.|\{|,|\s|#)', contents, re.DOTALL)
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

        selectors = self.getJsSelectors(contents, self.config)
        for selector in selectors:
            if selector[0] in self.config.id_selectors:
                if ',' in selector[2]:
                    id_to_add = re.search(r'(\'|\")(.*?)(\'|\")', selector[2])
                    if id_to_add is None:
                        continue

                    if not id_to_add.group(2):
                        continue

                    self.addId("#" + id_to_add.group(2))

                # if this is something like document.getElementById(variable) don't add it
                if not '\'' in selector[2] and not '"' in selector[2]:
                    continue

                self.addId("#" + selector[2].strip("\"").strip("'"))
                continue

            if selector[0] in self.config.class_selectors:
                class_to_add = re.search(r'(\'|\")(.*?)(\'|\")', selector[2])
                if class_to_add is None:
                    continue

                if not class_to_add.group(2):
                    continue

                self.addClass("." + class_to_add.group(2))
                continue

            if selector[0] in self.config.custom_selectors:
                matches = re.findall(r'((#|\.)[a-zA-Z0-9_]*)', selector[2])
                for match in matches:
                    if match[1] == "#":
                        self.addId(match[0])
                        continue

                    self.addClass(match[0])

    def processJsManifest(self):
        contents = Util.fileGetContents(self.config.js_manifest)
        ids = re.findall(r'\s+?(var\s)?\${1}([A-Z0-9_]+)\s?=\s?[\'|\"](.*?)[\'|\"][,|;]', contents)
        classes = re.findall(r'\s+?(var\s)?\${2}([A-Z0-9_]+)\s?=\s?[\'|\"](.*?)[\'|\"][,|;]', contents)

        self.manifest_ids = {}
        self.manifest_classes = {}

        for id in ids:
            self.addId("#" + id[2])
            self.manifest_ids[id[1]] = id[2]

        for manifest_class in classes:
            self.addClass("." + manifest_class[2])
            self.manifest_classes[manifest_class[1]] = manifest_class[2]

    def optimizeJsManifest(self):
        contents = Util.fileGetContents(self.config.js_manifest)

        for key, value in self.manifest_ids.items():
            if "#" + value in self.id_map:
                contents = re.sub(r'((?<!\$)\${1}[A-Z0-9_]+\s?=\s?[\'|\"])(' + value + ')([\'|\"][,|;])', r'\1' + self.id_map["#" + value].replace("#", "") + r'\3', contents)

        for key, value in self.manifest_classes.items():
            if "." + value in self.class_map:
                contents = re.sub(r'(\${2}[A-Z0-9_]+\s?=\s?[\'|\"])(' + value + ')([\'|\"][,|;])', r'\1' + self.class_map["." + value].replace(".", "") + r'\3', contents)

        if self.config.rewrite_constants:
            constants = re.findall(r'(\s+?(var\s)?([A-Z0-9_]+)\s?=\s?[\'|\"](.*?)[\'|\"][,|;])', contents)
            new_constants = {}
            i = 0
            for constant in constants:
                # underscore variables are ignored
                if constant[2][0] == "_":
                    continue

                i += 1
                new_constant = re.sub(r'=(.*)([,|;])','= ' + str(i) + r'\2', constant[0])
                contents = contents.replace(constant[0], new_constant)

        new_manifest = Util.prependExtension("opt", self.config.js_manifest)
        Util.filePutContents(new_manifest, contents)

        if self.config.show_savings:
            SizeTracker.trackFile(self.config.js_manifest, new_manifest)

    def processMaps(self):
        """loops through classes and ids to process to determine shorter names to use for them
        and creates a dictionary with these mappings

        Returns:
        void

        """
        # reverse sort so we can figure out the biggest savings
        classes = self.class_counter.items()
        classes.sort(key = itemgetter(1), reverse=True)

        for class_name, savings in classes:
            small_class = "." + VarFactory.getNext("class")

            # adblock extensions may block class "ad" so we should never generate it
            # also if the generated class already exists as a class to be processed
            # we can't use it or bad things will happen
            while small_class == ".ad" or Util.keyInTupleList(small_class, classes):
                small_class = "." + VarFactory.getNext("class")

            self.class_map[class_name] = small_class

        ids = self.id_counter.items()
        ids.sort(key = itemgetter(1), reverse=True)

        for id, savings in ids:
            small_id = "#" + VarFactory.getNext("id")

            # same holds true for ids as classes
            while small_id == "#ad" or Util.keyInTupleList(small_id, ids):
                small_id = "#" + VarFactory.getNext("id")

            self.id_map[id] = small_id

    def incrementIdCounter(self, name):
        """called for every time an id is added to increment the bytes we will save

        Arguments:
        name -- string of id

        Returns:
        void

        """
        length = len(name)

        if not name in self.id_counter:
            self.id_counter[name] = length
            return

        self.id_counter[name] += length

    def incrementClassCounter(self, name):
        """called for every time a class is added to increment the bytes we will save

        Arguments:
        name -- string of class

        Returns:
        void

        """
        length = len(name)

        if not name in self.class_counter:
            self.class_counter[name] = length
            return

        self.class_counter[name] += length

    def incrementCounter(self, name):
        """called everytime a class or id is added

        Arguments:
        name -- string of class or id name

        Returns:
        void

        """
        if name[0] == "#":
            return self.incrementIdCounter(name)

        return self.incrementClassCounter(name)

    def addId(self, id):
        """adds a single id to the master list of ids

        Arguments:
        id -- single id to add

        Returns:
        void

        """
        if id in self.config.ignore or id is '#':
            return

        # skip $ ids from manifest
        if self.config.js_manifest is not None and id[1] == '$':
            return

        self.incrementCounter(id)

    def addIds(self, ids):
        """adds a list of ids to the master id list to replace

        Arguments:
        ids -- list of ids to add

        Returns:
        void

        """
        for id in ids:
            self.addId(id[0])

    def addClass(self, class_name):
        """adds a single class to the master list of classes

        Arguments:
        class_name -- single class to add

        Returns:
        void

        """
        if class_name in self.config.ignore or class_name is '.':
            return

        # skip $$ class names from manifest
        if self.config.js_manifest is not None and class_name[1:2] == '$$':
            return

        self.incrementCounter(class_name)

    def addClasses(self, classes):
        """adds a list of classes to the master class list to replace

        Arguments:
        classes -- list of classes to add

        Returns:
        void

        """
        for class_name in classes:
            self.addClass(class_name)

    def optimizeFiles(self, paths, callback, extension = "", minimize = False):
        """loops through a bunch of files and directories, runs them through a callback, then saves them to disk

        Arguments:
        paths -- array of files and directories
        callback -- function to process each file with

        Returns:
        void

        """
        for file in paths:
            if not Util.isDir(file):
                self.optimizeFile(file, callback, minimize)
                continue

            self.optimizeDirectory(file, callback, extension, minimize)

    def optimizeFile(self, file, callback, minimize = False, new_path = None, prepend = "opt"):
        """optimizes a single file

        Arguments:
        file -- path to file
        callback -- function to run the file through
        minimize -- whether or not we should minimize the file contents (html)
        prepend -- what extension to prepend

        Returns:
        void

        """
        content = callback(file)
        if new_path is None:
            new_path = Util.prependExtension(prepend, file)
        if minimize is True:
            self.output("minimizing " + file)
            content = self.minimize(content)
        self.output("optimizing " + file + " to " + new_path)
        Util.filePutContents(new_path, content)

        if self.config.show_savings:
            SizeTracker.trackFile(file, new_path)

    def prepareDirectory(self, path):
        if ".svn" in path:
            return True

        if Util.isDir(path):
            return False

        Util.unlinkDir(path)
        self.output("creating directory " + path)
        os.mkdir(path)
        return False

    def optimizeDirectory(self, path, callback, extension = "", minimize = False):
        """optimizes a directory

        Arguments:
        path -- path to directory
        callback -- function to run the file through
        extension -- extension to search for in the directory
        minimize -- whether or not we should minimize the file contents (html)

        Returns:
        void

        """
        directory = path + "_opt"
        skip = self.prepareDirectory(directory)
        if skip is True:
            return

        for dir_file in Util.getFilesFromDir(path, extension):
            if Util.isDir(dir_file):
                self.optimizeSubdirectory(dir_file, callback, directory, extension, minimize)
                continue

            new_path = directory + "/" + Util.getFileName(dir_file)
            self.optimizeFile(dir_file, callback, minimize, new_path)

    def optimizeSubdirectory(self, path, callback, new_path, extension = "", minimize = False):
        """optimizes a subdirectory within a directory being optimized

        Arguments:
        path -- path to directory
        callback -- function to run the file through
        new_path -- path to optimized parent directory
        extension -- extension to search for in the directory
        minimize -- whether or not we should minimize the file contents (html)

        Returns:
        void

        """
        subdir_path = new_path + "/" + path.split("/").pop()
        skip = self.prepareDirectory(subdir_path)
        if skip is True:
            return

        for dir_file in Util.getFilesFromDir(path, extension):
            if Util.isDir(dir_file):
                self.optimizeSubdirectory(dir_file, callback, subdir_path, extension, minimize)
                continue

            new_file_path = subdir_path + "/" + Util.getFileName(dir_file)
            self.optimizeFile(dir_file, callback, minimize, new_file_path)

    def minimize(self, content):
        content = re.sub(r'\n', '', content)
        content = re.sub(r'\s\s+', '', content)
        content = re.sub(r'(<!--(?!\[if)(.*?)-->)', '', content, re.MULTILINE)
        return content

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
        Muncher.replaceHtml

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
        return re.compile(r'\<style.*?\>(.*)\<\/style\>', re.DOTALL).findall(html)

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
            # if key == ".svg":
                # print "replacing " + key + " with " + value

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
            new_js = match
            if self.config.compress_html:
                matches = re.findall(r'((:?)\/\/.*?\n|\/\*.*?\*\/)', new_js, re.DOTALL)
                for single_match in matches:
                    if single_match[1] == ':':
                        continue
                    new_js = new_js.replace(single_match[0], '');
            new_js = self.replaceJavascript(new_js)
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
    def getJsSelectors(js, config):
        """finds all js selectors within a js block

        Arguments:
        js -- contents of js file to search

        Returns:
        list

        """
        valid_selectors = "|".join(config.custom_selectors) + "|" + "|".join(config.id_selectors) + "|" + "|".join(config.class_selectors)
        valid_selectors = valid_selectors.replace('$', '\$')
        return re.findall(r'(' + valid_selectors + ')(\(([^<>]*?)\))', js, re.DOTALL)

    def replaceJsFromDictionary(self, dictionary, js):
        """replaces any instances of classes and ids based on a dictionary

        Arguments:
        dictionary -- map of classes or ids to replace
        js -- contents of javascript to replace

        Returns:
        string

        """
        for key, value in dictionary.items():
            blocks = self.getJsSelectors(js, self.config)
            for block in blocks:
                if key[0] == "#" and block[0] in self.config.class_selectors:
                    continue

                if key[0] == "." and block[0] in self.config.id_selectors:
                    continue

                old_selector = block[0] + block[1]

                # custom selectors
                if block[0] in self.config.custom_selectors:
                    new_selector = old_selector.replace(key + ".", value + ".")
                    new_selector = new_selector.replace(key + " ", value + " ")
                    new_selector = new_selector.replace(key + "\"", value + "\"")
                    new_selector = new_selector.replace(key + "\'", value + "\'")
                else:
                    new_selector = old_selector.replace("'" + key[1:] + "'", "'" + value[1:] + "'")
                    new_selector = new_selector.replace("\"" + key[1:] + "\"", "\"" + value[1:] + "\"")

                js = js.replace(old_selector, new_selector)

        return js
