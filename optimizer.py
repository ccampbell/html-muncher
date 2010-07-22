import math

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
