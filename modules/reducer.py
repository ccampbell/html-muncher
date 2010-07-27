# from pyquery import PyQuery as pq
from optimizer import Optimizer
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

    def addChain(self, chain):
        if ":" in chain:
            return
        if chain not in self.chains:
            self.chains[chain] = "." + VarFactory.getNext("class")

    def findChains(self):
        css = Util.fileGetContents(self.config.single_file_opt_path)
        blocks = Optimizer.getCssBlocks(css)
        for block in blocks:
            lines = block.split("\n")
            for line in lines:
                if "{" in line:
                    self.addChain(line.lstrip(" ").rstrip("{").rstrip(" "))

    def run(self):
        pass

class ChainReducerSingleFile(ChainReducer):
    def run(self):
        self.findChains()
        print self.chains
