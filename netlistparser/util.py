#!/usr/bin/python
# encoding: utf-8
import re

def getline(file):
    with open(file, 'r') as f:
        lastline = ''
        for nextline in f.readlines()[1:]:
            nextline = cleanline(nextline)
            if nextline == '':
                continue
            if nextline[0] == '+':
                lastline += ' ' + nextline[1:]
                lastline = cleanline(lastline)
            elif lastline[-2:] == '\\\\':
                lastline = lastline[:-2] + nextline
                lastline = cleanline(lastline)
            else:
                tmp, lastline = lastline, nextline
                if tmp == '' or tmp[:4] == '.sub' or tmp[:5] == '.ends' or tmp[:7] == '.global' or tmp[0] != '.':
                    yield tmp
                elif tmp == '.end' or tmp[:6] == '.alter' :
                    yield tmp
                    return
                else:
                    yield ''

# remove the comments and un-necessary space or tabs
def cleanline(line, raw = False):
    line = re.sub(r'\t', ' ', line).strip()
    line = re.sub(r'\^M$', '', line)
    line = re.sub(r'^[\*\$].*$', '', line)
    line = re.sub(r'\ \$.*$', '', line)
    line = re.sub(r'=', ' = ', line)
    line = re.sub(r'\ +', ' ', line).strip()
    if not raw:
        line = line.lower()
    return line

def gettokenlist(line):
    tokens = line.split(' ')
    return_list = []
    for i in range(len(tokens)):
        if tokens[i] == '=':
            return_list.pop()
            break
        return_list.append(tokens[i])
    return return_list
    
