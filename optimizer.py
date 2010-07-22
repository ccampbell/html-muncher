import math, sys, os

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

    def processArgs(self):
        # if we only pass in one argument let's assume we are running in single file mode
        if self.getArgCount() == 2:
            self.single_file_mode = True
            self.single_file_path = sys.argv[1]
            if not Util.fileExists(self.single_file_path):
                print "file does not exist at path: " + self.single_file_path
                sys.exit()

        # required arguments
        if self.single_file_mode is False:
            try:
                self.css_dir = sys.argv[1].rstrip("/")
                self.view_dir = sys.argv[2].rstrip("/")
            except IndexError:
                Optimizer.showUsage()
                sys.exit()

        # this is a hack and won't work in all situations
        if self.single_file_mode is False and self.view_dir.count('/') == self.css_dir.count('/'):
            self.relative_path = "../"

        # check for optional parameters
        for key, arg in enumerate(sys.argv):
            next = key + 1
            if arg == "--help":
                Optimizer.showUsage()
            elif arg == "--rewrite-css":
                config.rewrite_css = True
            elif arg == "--css-file":
                self.css_file = config.getArg(next)
            elif arg == "--view-ext":
                self.view_extension = config.getArg(next)


class Optimizer(object):
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
        sys.exit()

    def singleFileMode(self):
        return self.config.single_file_mode

    def setUpFiles(self):
        Util.unlink(self.config.getCssFile())
        Util.unlink(self.config.getCssMinFile())


class OptimizerSingleFile(Optimizer):
    def setUpFiles(self):
        ext = self.config.single_file_path.split(".").pop()
        self.config.single_file_opt_path = self.config.single_file_path.replace("." + ext, ".opt." + ext)
        Util.unlink(self.config.single_file_opt_path)


class Util:
    @staticmethod
    def fileExists(path):
        return os.path.isfile(path)

    @staticmethod
    def dump(obj):
        for attr in dir(obj):
            print "obj.%s = %s" % (attr, getattr(obj, attr))

    @staticmethod
    def unlink(path):
        if Util.fileExists(path):
            os.unlink(path)

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
