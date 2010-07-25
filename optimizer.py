import math, sys, os, re, glob, shutil

class Optimizer(object):
    ids = []
    classes = []
    id_map = {}
    class_map = {}

    def __init__(self, config):
        self.config = config

    @staticmethod
    def showUsage():
        print "USAGE:"
        print "./optimize.py path/to/css path/to/views"
        print "OR"
        print "./optimize.py path/to/single/file.html\n"
        print "OPTIONAL PARAMS:"
        print "--css-file {file_name}       file to use for optimized css (defaults to optimized.css)"
        print "--view-ext {extension}       sets the extension to look for the view directory (defaults to html)"
        print "--rewrite-css                if this arg is present then header css includes are rewritten in the new views"
        print "--help                       shows this menu"
        sys.exit(2)

    def setupFiles(self):
        Util.unlink(self.config.getCssFile())
        Util.unlink(self.config.getCssMinFile())
        Util.unlinkDir(self.config.view_dir + "_optimized")

    def addIds(self, ids):
        for id in ids:
            if id[1] is ';':
                continue
            if id[0] not in self.ids:
                self.ids.append(id[0])

    def addClasses(self, classes):
        for class_name in classes:
            if class_name not in self.classes:
                self.classes.append(class_name)

    def processFile(self, path):
        contents = Util.fileGetContents(path)

        ids_found = re.findall(r'(#\w+)(;)?', contents)
        classes_found = re.findall(r'(?!\.[0-9])\.\w+', contents)

        self.addIds(ids_found)
        self.addClasses(classes_found)
    
    def processStyles(self):
        files = self.config.getCssFiles()
        for file in files:
            self.processFile(file)
    
    def processMaps(self):
        for class_name in self.classes:
            self.class_map[class_name] = "." + VarFactory.getNext("class")
        
        for id in self.ids:
            self.id_map[id] = "#" + VarFactory.getNext("id")

    def replaceHtml(self, html):
        html = self.replaceHtmlIds(html)
        html = self.replaceHtmlClasses(html)
        return html
    
    def replaceCss(self, css):
        css = self.replaceCssFromDictionary(self.class_map, css)
        css = self.replaceCssFromDictionary(self.id_map, css)
        return css
    
    def replaceJavascript(self, js):
        js = self.replaceJsFromDictionary(self.id_map, js)
        js = self.replaceJsFromDictionary(self.class_map, js)
        return js
    
    def replaceHtmlIds(self, html):
        for key, value in self.id_map.items():
            key = key[1:]
            value = value[1:]
            html = html.replace("id=\"" + key + "\"", "id=\"" + value + "\"")
        
        return html

    def replaceHtmlClasses(self, html):
        for key, value in self.class_map.items():       
            key = key[1:]
            value = value[1:]     
            class_blocks = re.findall(r'class="(.*)"', html)
            for class_block in class_blocks:
                new_block = class_block.replace(key, value)
                html = html.replace("class=\"" + class_block + "\"", "class=\"" + new_block + "\"")

        return html
    
    def replaceCssFromDictionary(self, dictionary, css):
        for key, value in dictionary.items():
            css = css.replace(key + "{", value + "{")
            css = css.replace(key + " {", value + " {")
            css = css.replace(key + "#", value + "#")
            css = css.replace(key + " #", value + " #")
            css = css.replace(key + ".", value + ".")
            css = css.replace(key + " .", value + " .")
            css = css.replace(key + ",", value + ",")
            css = css.replace(key + " ", value + " ")

        return css

    def replaceJsFromDictionary(self, dictionary, js):
        for key, value in dictionary.items():
            blocks = re.findall(r'\((\'|\")(.*)(\'|\")\)', js)
            for block in blocks:
                new_block = block[1].replace(key, value)
                js = js.replace("(" + block[0] + block[1] + block[2] + ")", "(" + block[0] + new_block + block[2] + ")")
        
        return js
        
    def optimizeCss(self, paths):
        combined_css = ""
        for path in paths:
            print "adding " + path + " to " + self.config.getCssFile()
            css = Util.fileGetContents(path)
            css = self.replaceCss(css)
            combined_css = combined_css + "/*\n * " + path + "\n */\n" + css + "\n\n"
        
        return combined_css

    def getCssBlocks(self, html):
        return re.compile(r'\<style type=\"text\/css\"\>(.*?)\<\/style\>', re.DOTALL).findall(html)

    def getJsBlocks(self, html):
        return re.compile(r'\<script type=\"text\/javascript\"\>(.*?)\<\/script\>', re.DOTALL).findall(html)

    def optimizeJavascriptBlocks(self, html):
        matches = self.getJsBlocks(html)

        for match in matches:
            new_js = self.replaceJavascript(match)
            html = html.replace(match, new_js)

        return html

    def optimizeCssBlocks(self, html):
        result_css = ""
        matches = self.getCssBlocks(html)
        for match in matches:
            match = self.replaceCss(match)
            result_css = result_css + match

        result_css = Minimizer.minimize(result_css)

        if len(matches):
            return html.replace(matches[0], result_css)
        
        return html

    def rewriteHeaderCss(self, html):
        new_lines = []
        i = 0
        prefix = ""
        
        base_view_path = Util.getBasePath(self.config.view_dir)
        base_css_path = Util.getBasePath(self.config.css_dir)
        
        if base_css_path == base_view_path:
            prefix = ".."
        
        for line in html.split("\n"):
            if "link href" not in line or "text/css" not in line:
                new_lines.append(line)
                continue

            if i is 0:
                css_min_file = self.config.getCssMinFile().replace(base_view_path, "")
                new_lines.append('    <link href="' + prefix + css_min_file + '" rel="stylesheet" type="text/css" />')
                i = i + 1

        html = "\n".join(map(str, new_lines))
        return html

    def optimizeHtml(self, path, rewrite_css):
        ''' replaces classes and ids with new values in a view file

        uses:
        Optimizer.replaceHtml

        keyword arguments:
        file_path -- string path to file to optimize

        returns string'''

        html = Util.fileGetContents(path)
        html = self.replaceHtml(html)
        html = self.optimizeCssBlocks(html)
        html = self.optimizeJavascriptBlocks(html)
        
        if rewrite_css is True:
            html = self.rewriteHeaderCss(html)

        return html
    
    def run(self):
        self.processStyles()
        self.processMaps()
        
        # first optimize all the css files
        css = self.optimizeCss(self.config.getCssFiles())
        minimized_css = Minimizer.minimize(css)
        Util.filePutContents(self.config.getCssFile(), css)
        Util.filePutContents(self.config.getCssMinFile(), minimized_css)
        
        # next optimize the views
        paths = self.config.getViewFiles()
        os.mkdir(self.config.view_dir + "_optimized")
        for path in paths:
            html = self.optimizeHtml(path, self.config.rewrite_css)
            Util.filePutContents(self.config.view_dir + "_optimized/" + path.split("/").pop(), html)
        

class OptimizerSingleFile(Optimizer):
    def setupFiles(self):
        ext = Util.getExtension(self.config.single_file_path)
        self.config.single_file_opt_path = self.config.single_file_path.replace("." + ext, ".opt." + ext)
        Util.unlink(self.config.single_file_opt_path)
    
    def run(self):
        self.processStyles()
        self.processMaps()
        html = self.optimizeHtml(self.config.single_file_path, False)
        Util.filePutContents(self.config.single_file_opt_path, html);
        print "all done"


class Config(object):
    def __init__(self):
        self.single_file_mode = False
        self.css_file = "optimized.css"
        self.view_extension = "html"
        self.rewrite_css = False
        self.ids_to_replace = []
        self.classes_to_replace = []
        relative_path = ""

    def getArgCount(self):
        return len(sys.argv)

    def getCssFile(self):
        return self.css_dir + "/" + self.css_file

    def getCssMinFile(self):
        return self.getCssFile().replace(".css", ".min.css");

    def getCssFiles(self):
        files = []
        if self.single_file_mode is True:
            files.append(self.single_file_path)
            return files
        
        return glob.glob(self.css_dir + "/*.css")
    
    def getViewFiles(self):
        files = []
        if self.single_file_mode is True:
            files.append(self.single_file_path)
            return files

        return glob.glob(self.view_dir + "/*." + self.view_extension)

    def processArgs(self):
        # if we only pass in one argument let's assume we are running in single file mode
        if self.getArgCount() == 2:
            self.single_file_mode = True
            self.single_file_path = sys.argv[1]
            if not Util.fileExists(self.single_file_path):
                print "file does not exist at path: " + self.single_file_path
                sys.exit(2)

        # required arguments
        if self.single_file_mode is False:
            try:
                self.css_dir = sys.argv[1].rstrip("/")
                self.view_dir = sys.argv[2].rstrip("/")
            except IndexError:
                Optimizer.showUsage()

        # this is a hack and won't work in all situations
        if self.single_file_mode is False and self.view_dir.count('/') == self.css_dir.count('/'):
            self.relative_path = "../"

        # check for optional parameters
        for key, arg in enumerate(sys.argv):
            next = key + 1
            if arg == "--help":
                Optimizer.showUsage()
            elif arg == "--rewrite-css":
                self.rewrite_css = True
            elif arg == "--css-file":
                self.css_file = sys.argv[next]
            elif arg == "--view-ext":
                self.view_extension = sys.argv[next]


class Util:
    @staticmethod
    def fileExists(path):
        '''determines if a file exists

        keyword arguments:
        path -- path to file on disk

        returns bool'''

        return os.path.isfile(path)

    @staticmethod
    def dump(obj):
        for attr in dir(obj):
            print "obj.%s = %s" % (attr, getattr(obj, attr))

    @staticmethod
    def getExtension(path):
        return path.split(".").pop()

    @staticmethod
    def getBasePath(path):
        bits = path.split("/")
        last_bit = bits.pop()
        return "/".join(bits).rstrip(last_bit)

    @staticmethod
    def unlink(path):
        '''deletes a file on disk

        keyword arguments:
        path -- path to file on disk

        returns void'''

        if Util.fileExists(path):
            os.unlink(path)

    @staticmethod
    def unlinkDir(path):
        try:
            shutil.rmtree(path)
        except:
            pass

    @staticmethod
    def fileGetContents(path):
        '''gets the contents of a file

        keyword arguments:
        path -- path to file on disk

        returns string'''

        if not Util.fileExists(path):
            print "file does not exist at path " + path
            print "skipping"
        file = open(path, "r")
        contents = file.read()
        file.close()
        return contents

    @staticmethod
    def filePutContents(path, contents):
        file = open(path, "w")
        file.write(contents)
        file.close()


class VarFactory:
    '''class to keep multiple counters and turn numeric counters into alphabet ones'''
    types = {}
    letters = map(chr, range(97, 123))

    @staticmethod
    def getNext(type):
        '''gets the next letter name based on counter name

        keyword arguments:
        type -- name of counter we want the next value for

        returns string'''

        i = VarFactory.getVersion(type)
        return VarFactory.getSmallName(i)

    @staticmethod
    def getVersion(type):
        '''gets the next number in the counter for this type

        keyword arguments:
        type -- name of counter we are incrementing

        returns int'''

        if not type in VarFactory.types:
            VarFactory.types[type] = 0
            return 0

        VarFactory.types[type] += 1

        return VarFactory.types[type]

    @staticmethod
    def getSmallName(index):
        '''gets a letter index based on the numeric index

        keyword arguments:
        index -- the number you are looking for

        returns string'''

        # total number of combinations for this index size
        combinations = 0
        letters = 0
        while (combinations + (((letters - 1) * 26) - 1) < index):
            letters += 1
            combinations = int(math.pow(len(VarFactory.letters), letters))

        if (index > 701):
            raise Exception("until my math skillz get better we can only support 702 possibilities!")

        index = int(index)

        string = ''
        while index >= 0:
            if index < len(VarFactory.letters):
                string = string + VarFactory.letters[index]
                break

            index_for_this_letter = int(math.floor(index / len(VarFactory.letters))) - 1
            index = index % len(VarFactory.letters)
            string = string + VarFactory.letters[index_for_this_letter]

        return string

# @see http://stackoverflow.com/questions/222581/python-script-for-minifying-css
class Minimizer(object):
    @staticmethod
    def minimize(css):
        # remove comments - this will break a lot of hacks :-P
        css = re.sub( r'\s*/\*\s*\*/', "$$HACK1$$", css ) # preserve IE<6 comment hack
        css = re.sub( r'/\*[\s\S]*?\*/', "", css )
        css = css.replace( "$$HACK1$$", '/**/' ) # preserve IE<6 comment hack

        # url() doesn't need quotes
        css = re.sub( r'url\((["\'])([^)]*)\1\)', r'url(\2)', css )

        # spaces may be safely collapsed as generated content will collapse them anyway
        css = re.sub( r'\s+', ' ', css )

        # shorten collapsable colors: #aabbcc to #abc
        css = re.sub( r'#([0-9a-f])\1([0-9a-f])\2([0-9a-f])\3(\s|;)', r'#\1\2\3\4', css )

        # fragment values can loose zeros
        css = re.sub( r':\s*0(\.\d+([cm]m|e[mx]|in|p[ctx]))\s*;', r':\1;', css )

        new_css = ""
        for rule in re.findall( r'([^{]+){([^}]*)}', css ):

            # we don't need spaces around operators
            selectors = [re.sub( r'(?<=[\[\(>+=])\s+|\s+(?=[=~^$*|>+\]\)])', r'', selector.strip() ) for selector in rule[0].split( ',' )]

            # order is important, but we still want to discard repetitions
            properties = {}
            porder = []
            for prop in re.findall( '(.*?):(.*?)(;|$)', rule[1] ):
                key = prop[0].strip().lower()
                if key not in porder: porder.append( key )
                properties[ key ] = prop[1].strip()

            # output rule if it contains any declarations
            if properties:
                new_css = new_css + "%s{%s}" % ( ','.join( selectors ), ''.join(['%s:%s;' % (key, properties[key]) for key in porder])[:-1] )

        return new_css
