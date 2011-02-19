# from pyquery import PyQuery as pq
from muncher import Muncher
from util import Util
from varfactory import VarFactory

class ChainReducer(object):
    def __init__(self, config):
        """constructor

        Arguments:
        config -- Config object

        Returns:
        void

        """
        self.config = config
        self.chains = {}

    def findChains(self):
        for selector in self.getAllCssSelectors():
            self.addChain(selector)

        for selector in self.getAllJsSelectors():
            self.addChain(selector)

    def addChain(self, chain):
        if ":" in chain:
            return
        chains = chain.split(",")
        for chain in chains:
            bits = chain.split(" ")

            if len(bits) > 1 and chain not in self.chains:
                self.chains[chain] = "." + VarFactory.getNext("class")

    def getCssBlocks(self):
        css_blocks = []
        for file in self.config.getOptimizedViewFiles():
            css = Util.fileGetContents(file)
            blocks = Muncher.getCssBlocks(css)
            for block in blocks:
                css_blocks.append(block)

        return css_blocks

    def getAllJsSelectors(self):
        js_selectors = []
        for file in self.config.getOptimizedViewFiles():
            js = Util.fileGetContents(file)
            selectors = Muncher.getJsSelectors(js)
            for selector in selectors:
                js_selectors.append(selector[3])

        return js_selectors

    def getAllCssSelectors(self):
        css_selectors = []
        for block in self.getCssBlocks():
            lines = block.split("\n")
            for line in lines:
                if "{" in line:
                    css_selectors.append(line.lstrip(" ").rstrip("{").rstrip(" "))

        return css_selectors

    def replaceViews(self):
        for file in self.config.getOptimizedViewFiles():
            html = Util.fileGetContents(file)
            new_html = self.updateClasses(html)
            Util.filePutContents(file, new_html)

    def updateClasses(self, html):
        d = pq(html)
        for key, value in self.chains.items():
            d(key).addClass(value.replace(".", ""))
        return d.html()

    def run(self):
        print "only single file mode at moment"
        pass

class ChainReducerSingleFile(ChainReducer):
    def replaceCssAndJavascript(self):
        contents = Util.fileGetContents(self.config.single_file_opt_path)
        for key, value in self.chains.items():
            contents = contents.replace(key + " {", value + " {")
            contents = contents.replace("(\"" + key + "\")", "(\"" + value + "\")")
            contents = contents.replace("('" + key + "')", "('" + value + "')")

        Util.filePutContents(self.config.single_file_opt_path, contents)

    def run(self):
        print "reducer is mad buggy ... skipping for now"
        # self.findChains()
        # self.replaceCssAndJavascript()
        # self.replaceViews()

