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

import sys, glob, re, math, os, shutil
from optimizer import VarFactory

def show_usage():
    print "USAGE:"
    print "./optimize.py path/to/css path/to/views"
    print "OR"
    print "./optimize.py path/to/single/file.html\n"
    print "OPTIONAL PARAMS:"
    print "--css-file {file_name}       file to use for optimized css (defaults to optimized.css)"
    print "--view-ext {extension}       sets the extension to use for the view directory (defaults to html)"
    print "--rewrite-css                if this arg is present then header css includes are rewritten in the new views"
    print "--help                       shows this menu"

# if we only pass in one argument let's assume we are running in single file mode
single_file_mode = False
if len(sys.argv) == 2:
    single_file_mode = True
    single_file_path = sys.argv[1]
    if not os.path.isfile(single_file_path):
        print "file does not exist at path: " + single_file_path
        sys.exit()

# required arguments
if single_file_mode is False:
    try:
        css_dir = sys.argv[1].rstrip("/")
        view_dir = sys.argv[2].rstrip("/")
    except IndexError:
        show_usage()
        sys.exit()


# properties
css_file = "optimized.css"
view_extension = "html"
rewrite_css = False
letters = map(chr, range(97, 123))
all_ids = []
all_classes = []
id_index = 0
class_index = 0
relative_path = ""
if single_file_mode is False and view_dir.count('/') == css_dir.count('/'):
    relative_path = "../"

# check for optional parameters
for key, arg in enumerate(sys.argv):
    next = key + 1
    if arg == "--help":
        show_usage()
        sys.exit()
    elif arg == "--rewrite-css":
        rewrite_css = True
    elif arg == "--css-file":
        css_file = sys.argv[next]
    elif arg == "--view-ext":
        view_extension = sys.argv[next]

css_file_minimized = css_file.replace(".css", ".min.css");

if single_file_mode:
    single_file_extension = single_file_path.split(".").pop()
    single_file_opt_path = single_file_path.replace("." + single_file_extension, ".opt." + single_file_extension)

    # remove the files we are going to be recreating
    try:
        os.unlink(single_file_opt_path)
    except:
        pass

try:
    os.unlink(css_dir + "/" + css_file)
except:
    pass

try:
    os.unlink(css_dir + "/" + css_file)
except:
    pass

try:
    os.unlink(css_dir + "/" + css_file_minimized)
except:
    pass

def addIds(ids_found):
    '''adds ids to the master list of ids

    keyword arguments:
    ids_found -- list to add to global array

    returns void'''

    for id in ids_found:
        if id[1] is ';':
            continue
        if id[0] not in all_ids:
            all_ids.append(id[0])

def addClasses(classes_found):
    '''adds classes to the master list of classes

    keyword arguments:
    classes_found -- list of classes to add to global array

    returns void'''

    for class_name in classes_found:
        if class_name not in all_classes:
            all_classes.append(class_name)

def replaceCss(dictionary, content):
    ''' replaces css rules with optimized names

    todo:
    use regex here?

    keyword arguments:
    dictionary -- dictionary mapping old class names to new ones
    content -- string of content to replace

    returns string'''

    for key, value in dictionary.items():
        content = content.replace(key + "{", value + "{")
        content = content.replace(key + " {", value + " {")
        content = content.replace(key + "#", value + "#")
        content = content.replace(key + " #", value + " #")
        content = content.replace(key + ".", value + ".")
        content = content.replace(key + " .", value + " .")
        content = content.replace(key + ",", value + ",")

        # case if the style is followed by another tag
        content = content.replace(key + " ", value + " ")
    return content

def optimizeHtml(file_path):
    ''' replaces classes and ids with new values in a view file

    uses:
    replaceHtml

    keyword arguments:
    file_path -- string path to file to optimize

    returns string'''

    file = open(file_path)
    contents = file.read()
    contents = replaceHtml(id_map, contents)
    contents = replaceHtml(class_map, contents)
    return contents

def replaceHtml(dictionary, content):
    ''' replaces classes and ids with optimized names in html file

    todo:
    use regex here?

    keyword arguments:
    dictionary -- dictionary mapping old class names to new ones
    content -- string of content to replace

    returns string'''

    initial_content = content
    for key, value in dictionary.items():
        first_char = key[0]
        key = key[1:]
        value = value[1:]
        # ids are easy
        if first_char is '#':
            content = content.replace("id=\"" + key + "\"", "id=\"" + value + "\"")
            continue

        # classes are hard
        class_blocks = re.findall(r'class="(.*)"', content)
        for class_block in class_blocks:
            new_block = class_block.replace(key, value)
            content = content.replace("class=\"" + class_block + "\"", "class=\"" + new_block + "\"")
        # print class_blocks
    if content:
        return content

    return initial_content


# loop through the css files once to get all the classes and ids we are going to need
files = []

if single_file_mode:
    files.append(single_file_path)
else:
    files = glob.glob(css_dir + "/*.css")

for file in files:
    file = open(file, "r")
    contents = file.read()
    file.close()

    # find ids in file
    ids_found = re.findall(r'(#\w+)(;)?', contents)

    # find classes in file
    classes_found = re.findall(r'(?!\.[0-9])\.\w+', contents)

    # add what we found to the master lists
    addIds(ids_found)
    addClasses(classes_found)

# create definitions mapping old names to new ones
# .a => .killer_class, #a => #sweet_id
class_map = {}
for class_name in all_classes:
    class_map[class_name] = "." + VarFactory.getNext("class")
    class_index = class_index + 1

id_map = {}
for id in all_ids:
    id_map[id] = "#" + VarFactory.getNext("id")
    id_index = id_index + 1

####################
# single file mode #
####################
if single_file_mode:
    html = optimizeHtml(single_file_path)
    matches = re.compile(r'\<style type=\"text\/css\"\>(.*?)\<\/style\>', re.DOTALL).findall(html)
    result_css = ''
    for match in matches:
        match = replaceCss(class_map, match)
        match = replaceCss(id_map, match)
        result_css = result_css + match

    from minimize import minimize
    result_css = minimize(result_css)
    html = html.replace(matches[0], result_css)
    file = open(single_file_opt_path, "w")
    file.write(html)
    file.close()
    print "all done"
    sys.exit()


file_path = css_dir + "/" + css_file
master_file = open(file_path, "w");

# loop through the files a second time to rename the classes/ids based on the definitions
files = glob.glob(css_dir + "/*.css")
for file in files:
    name = file
    if file == file_path:
        continue

    print "adding " + name + " to " + file_path
    file = open(file, "r")
    contents = file.read()
    contents = replaceCss(class_map, contents)
    contents = replaceCss(id_map, contents)
    master_file.writelines("/*\n * " + name + "\n */\n" + contents + "\n\n");

master_file.close()
master_file = None

# open up the master file we just wrote to to grab the final contents
master_file = open(file_path, "r");
contents = master_file.read()
master_file.close()

# minimize the stuff
from minimize import minimize
contents = minimize(contents)

# write it back to minimized file
new_file = open(css_dir + "/" + css_file_minimized, "w")
new_file.write(contents)
new_file.close()
new_file = None

# now it is time to replace the html values
new_view_dir = view_dir + "_optimized"
try:
    shutil.rmtree(new_view_dir)
except:
    pass

# create a new directory to hold all the new views
os.mkdir(new_view_dir)

# loop through all of the views and do the magic stuff
files = glob.glob(view_dir + "/*." + view_extension)
for file in files:
    i = 0
    file_name = file.replace(view_dir + "/", "")
    print "optimizing " + file_name
    new_content = optimizeHtml(file)
    new_lines = []
    for line in new_content.split("\n"):
        if "link href" not in line or "text/css" not in line or rewrite_css is False:
            new_lines.append(line)
            continue

        if i is 0:
            new_lines.append('<link href="' + relative_path + css_dir + "/" + css_file_minimized + '" rel="stylesheet" type="text/css" />')
            i = i + 1

    new_content = "\n".join(map(str, new_lines))

    new_file = open(new_view_dir + "/" + file_name, "w")
    new_file.write(new_content)
    new_file.close()

print "all done!"
