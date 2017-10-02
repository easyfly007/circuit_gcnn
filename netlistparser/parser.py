#!/usr/bin/python
# encoding: utf-8

import sys, re, sys, os
import logging

from handlers import *
from util import *
from rules import *

class Parser:
    """
    base class for parser
    """
    def __init__(self, handler):
        self.handler = handler
        self.rules = []
        self.filters = []

    def addRule(self, rule):
        self.rules.append(rule)

    def addFilter(self, pattern, name):
        def filter(block, handler):
            return re.sub(pattern, handler.sub(name), block)
        self.filters.append(filter)

    def merge(self, file):
        # preprocess for the .include commands
        # newfile = file +'.total'
        newfile = 'newfile.total'
        total_lines = self.handler.merge_file(file)
        with open(newfile, 'w') as f:
            for line in total_lines:
                f.write(line +'\n')
        return newfile

    def parse(self, file):

        for line in getline(file):
            if line == None or line == '':
                continue
            for rule in self.rules:
                if rule.condition(line, self.flaglist):
                    rule.action(line, self.handler)
                    break
    def flattern(self):
        self.handler.flattern()
    
    def dump(self, file, cktdir):
        self.handler.dump(file, cktdir)

class NetlistParser(Parser):
    def __init__(self, handler):
        Parser.__init__(self, handler)
        self.flaglist = {}
        self.flaglist['subckt'] = False

        self.addRule(ResRule())
        self.addRule(VsrcRule())
        self.addRule(CapRule())
        self.addRule(IndRule())
        self.addRule(IsrcRule())

        self.addRule(BjtRule())

        self.addRule(MosfetRule())

        self.addRule(DiodeRule())
        self.addRule(VcvsRule())

        self.addRule(XinsRule())

        self.addRule(CmdGlobalRule())
        self.addRule(StartSubcktRule())
        self.addRule(EndSubcktRule())
        


"""
main run
"""

if __name__ == '__main__':

    if len(sys.argv) < 3 or len(sys.argv) %2 == 0:
        print('error: correct syntax is >>> python parser.py inputfile outputfile '
              '[--log logfile] [--subckt cktdir]')
        exit()
    infile = sys.argv[1]
    if not os.path.exists(infile):
        print('error: input file \''+infile+'\' not exists')
        exit()
    outfile = sys.argv[2]
    if os.path.exists(outfile):
        print('warning: existing file \''+ outfile + '\' will be overwritten')

    argidx = 3
    logfile = '.log'
    cktdir = ''
    while argidx < len(sys.argv):
        if sys.argv[argidx] == '--log':
            logfile = sys.argv[argidx+1]
        if sys.argv[argidx] == '--subckt':
            cktdir = sys.argv[argidx+1]
        argidx += 1
 
    logging.basicConfig(level=logging.INFO,
                format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt = '%a, %d %b %Y %H:%M:%S',
                filename = logfile,
                filemode = 'w')
    # please using logging api to write message to log file, rather than print('')
    # logging.critical(), logging.error(), logging.warning(), logging.info(), logging.debug(), logging.notset()

    if cktdir:
        if not os.path.isdir(cktdir):
            print('error: directory \''+cktdir+'\' not exists')
            exit()
        if not os.path.isabs(cktdir):
            cktdir=os.path.abspath(cktdir)

    handler = NetlistHandler()
    parser = NetlistParser(handler)
    newfile = parser.merge(infile)
    parser.parse(newfile)
    os.remove(newfile)
    parser.flattern()
    parser.dump(outfile, cktdir)

    # for elem in handler.elementlist:
    #     print(elem)
    # for sub in handler.subcktlist:
    #     print(' for subckt ' + sub)
    #     for ins in handler.subcktlist[sub]:
    #         print('\t'+str(ins))

