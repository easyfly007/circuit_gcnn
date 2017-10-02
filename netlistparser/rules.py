#!/usr/bin/python
# encoding: utf-8
import re
from util import cleanline, gettokenlist
class Rule:
    """
    base class
    """
    def action(self, block, handler):
        handler.start(self.type)
        handler.feed(block)
        handler.end(self.type)
        return True

class CmdGlobalRule(Rule):
    def condition(self, line, flaglist):
        if line.split(' ')[0] in ['.global', '.GLOBAL']:
            return True
        return False   
    def action(self, line, handler):
        handler.add_cmdGlobal(line) 

class StartSubcktRule(Rule):
	def action(self, line, handler):
		handler.start_subckt(line)
	def condition(self, line, flaglist):
		if line.split(' ')[0] in ['.subckt', '.sub'] and not flaglist['subckt']:
			flaglist['subckt'] = True
			return True
		return False

class EndSubcktRule(Rule):
	def action(self, line, handler):
		handler.end('subckt')
	def condition(self, line, flaglist):
		if line.split(' ')[0] in ['.ends', '.endsub'] and flaglist['subckt']:
			flaglist['subckt'] = False
			return True
		return False

class Terminal2ElementRule(Rule):
    def action(self, line, handler):
        tokens = line.split(' ')
        elem = {}
        elem['name'] = tokens[0]
        elem['type'] = self.getElemType()
        elem['nodes'] = tokens[1:3]
        handler.add('instance', elem)

class Terminal3ElementRule(Rule):
    def action(self, line, handler):
        tokens = line.split(' ')
        elem = {}
        elem['name'] = tokens[0]
        elem['type'] = self.getElemType()
        elem['nodes'] = tokens[1:4]
        handler.add('instance', elem)

class Terminal4ElementRule(Rule):
    def action(self, line, handler):
        line = cleanline(line)
        tokens = line.split(' ')
        elem = {}
        elem['name'] = tokens[0]
        elem['type'] = self.getElemType()
        elem['nodes'] = tokens[1:5]
        handler.add('instance', elem)

class XinsRule(Rule):
	def condition(self, line, flaglist):
		return line[0] in ['x', 'X']
	def getElemType(self):
		return 'x'
	def action(self, line, handler):
		tokens = gettokenlist(line)
		elem = {}
		elem['name'] = tokens[0]
		elem['type'] = self.getElemType()
		elem['nodes'] = []
		for token in tokens[1:]:
			if token == '=':
				elem['nodes'].pop()
				break
			elem['nodes'].append(token)
		elem['subckt'] = elem['nodes'].pop()
		handler.add('instance',elem)

class ResRule(Terminal2ElementRule):
    def condition(self, line, flaglist):
        return line[0] in ['r', 'R']
    def getElemType(self):
        return 'res'

class VsrcRule(Terminal2ElementRule):
    def condition(self, line, flaglist):
        return line[0] in ['v', 'V']
    def getElemType(self):
        return 'vsrc'

class VcvsRule(Terminal2ElementRule):
    # E element
    def condition(self, line, flaglist):
        return line[0] in ['e', 'E']
    def getElemType(self):
        return 'vcvs'

class IsrcRule(Terminal2ElementRule):
    def condition(self, line, flaglist):
        return line[0] in ['i', 'I']
    def getElemType(self):
        return 'isrc'

class CapRule(Terminal2ElementRule):
    def condition(self, line, flaglist):
        return line[0] in ['c', 'C']
    def getElemType(self):
        return 'cap'

class IndRule(Terminal2ElementRule):
    def condition(self, line, flaglist):
        return line[0] in ['l', 'L']
    def getElemType(self):
        return 'ind'

class BjtRule(Terminal3ElementRule):
    def condition(self, line, flaglist):
        return line[0] in ['q', 'Q']
    def getElemType(self):
        return 'bjt'

class MosfetRule(Terminal4ElementRule):
    def condition(self, line, flaglist):
        return line[0] in ['m', 'M']
    def getElemType(self):
        return 'mos'

class DiodeRule(Terminal2ElementRule):
    def condition(self, line, flaglist):
        return line[0] in ['d', 'D']
    def getElemType(self):
        return 'diode'
