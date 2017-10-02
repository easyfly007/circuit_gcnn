#!/usr/bin/python
# encoding: utf-8

import collections
import copy
import os
from util import cleanline, gettokenlist

class Handler:
    """
    base class for netlist handling
    """
    def callback(self, prefix, name, *args):
        method = getattr(self, prefix + name, None)
        if isinstance(method, collections.Callable): return method(*args)

    def start(self, name):
        self.callback('start_', name)

    def end(self, name):
        self.callback('end_', name)

    def add(self, name, element):
        self.callback('add_', name, element)

    def sub(self, name):
        def substitution(match):
            result = self.callback('sub_', name, match)
            if result is None: result = match.group(0)
            return result
        return substitution

class NetlistHandler(Handler):
    def __init__(self):
        self.elementlist = []
        self.globallist = []
        self.subcktlist = {}
        self.scope = self.elementlist
    def add_instance(self, instance):
        self.scope.append(instance)

    def start_subckt(self, line):
        tokens = gettokenlist(line)
        subname = tokens[1]
        assert subname not in self.subcktlist, 'subckt ' + subname + ' re-defined'
        self.subcktlist[subname] = []
        self.subcktlist[subname].append(tokens[2:])
        self.scope = self.subcktlist[subname]

    def end_subckt(self):
        self.scope = self.elementlist

    def add_cmdGlobal(self, line):
        tokens = gettokenlist(line)
        self.globallist += tokens[1:]

    def merge_file(self, file):
        def get_contents(file, modelscope = None):
            # file is now absolute path dir
            contents = []
            in_modelscope = None
            with open(file, 'r') as f:
                for line in f.readlines():
                    line = cleanline(line, raw = True)
                    if len(line) >0:
                        tokens = line.split(' ')
                        if tokens[0].lower() in ['.inc', '.include'] and tokens[1][0] in ['\'', '\"']:
                            if modelscope and in_modelscope != modelscope:
                                continue
                            incfile = tokens[1][1:-1]
                            if not os.path.isabs(incfile):
                                current_file_dir = os.path.split(file)[0]
                                incfile = os.path.join(current_file_dir, incfile)    
                            inc_contents = get_contents(incfile)
                                
                            contents.extend(inc_contents)
                        elif tokens[0].lower() in ['.lib',] and len(tokens) >= 2:
                            if tokens[1][0] in ['\'', '\"']:
                                if modelscope and in_modelscope != modelscope:
                                    continue
                                incfile = tokens[1][1:-1]
                                if not os.path.isabs(incfile):
                                    current_file_dir = os.path.split(file)[0]
                                    incfile = os.path.join(current_file_dir, incfile)  
                                if len(tokens) ==2:
                                    # .lib 'modelfile'
                                    inc_contents = get_contents(incfile)
                                    contents.extend(inc_contents)
                                elif len(tokens) == 3:
                                    # .lib "modelfile" tt
                                    modelname = tokens[2]
                                    inc_contents = get_contents(incfile, modelname.lower())
                                    contents.extend(inc_contents)
                            else:
                                # .lib tt
                                if modelscope:
                                    modelname = tokens[1]
                                    in_modelscope = modelname.lower()
                                    if in_modelscope == modelscope.lower():
                                        contents.append(line)
                                    else:
                                        pass     
                                else:
                                    contents.append(line)    
                        elif tokens[0].lower() in ['.endl']:
                            if in_modelscope == modelscope:
                                contents.append(line)
                            in_modelscope = None
                        else:
                            if modelscope:
                                if in_modelscope == modelscope:
                                    contents.append(line)
                                else:
                                    pass
                            else:
                                contents.append(line)
                    else:
                        contents.append('')    
            return contents
        if not os.path.isabs(file):
            file = os.path.join(os.getcwd(), file)
        return get_contents(file)

    def dump(self, file, cktdir):
        def name_cmp(elem1, elem2):
            if elem1['name'] > elem2['name']:
                return -1
            if elem1['name'] < elem2['name']:
                return 1
            return 0
        self.elementlist.sort(key=lambda elem: elem['name'])
        with open(file, 'w') as f:
            for elem in self.elementlist:
                f.write(elem['name'] + ': ')
                # f.write(elem['type'] +' ')
                f.write(' '.join(elem['nodes']))
                f.write('\n')

        if cktdir:
            lastSubckt = ''
            subcktlist = []
            subckt = []
            elementlistCopy = copy.deepcopy(self.elementlist)
            while len(elementlistCopy) > 0:
                i=0
                while i < len(elementlistCopy):
                    elem = elementlistCopy[i]
                    if elem['name'][0] != 'x':
                        elementlistCopy.remove(elem)
                        continue
                    subNames = elem['name'].split('.')
                    if lastSubckt == subNames[0] or lastSubckt == '':
                        subckt.append(dict(elem))
                    else:
                        subcktlist.append(list(subckt))
                        subckt=[dict(elem)]
                    lastSubckt = subNames[0]
                    elem['name'] = '.'.join(subNames[1:]) 
                    i += 1
                subcktlist.append(list(subckt))    

            for subckt in subcktlist:
                namedict={}
                cktname=subckt[0]['name'].split('.')[0]
                if cktname not in namedict:
                    namedict[cktname] = 0
                namedict[cktname] += 1
                with open(os.path.join(cktdir, cktname+'_'+str(namedict[cktname])+'.ckt'), 'w') as f:
                # with open(cktdir+'/'+cktname+'_'+str(namedict[cktname])+'.ckt', 'w') as f:
                    for elem in subckt:
                        f.write(elem['name'] + ': ')
                        f.write(' '.join(elem['nodes']))
                        f.write('\n')


    def flattern(self):
        #if len(self.elementlist) == 0 or len(self.subcktlist) == 0:
        #    return None
        i = 0
        while i < len(self.elementlist):
            xins = self.elementlist[i]
            if xins['type'] != 'x':
                i += 1
                for j in range(len(xins['nodes'])):
                    if xins['nodes'][j] in ['0', 'gnd', 'gnd!']:
                        xins['nodes'][j] = '0' 
                continue
            subname = xins['subckt']
            assert subname in self.subcktlist, 'xinstance ' + xins['name'] + ' definition ' + subname + ' not found in the netlist'
            subdef = self.subcktlist[subname] 
            assert len(subdef[0]) == len(xins['nodes']), 'xinstance ' + xins['name'] + ' port number not match, find '+ str(len(xins['nodes'])) + ', expect ' + str(len(subdef[0]))
            ports_mapping = {}
            for j in range(len(subdef[0])):
                ports_mapping[subdef[0][j]] = xins['nodes'][j]
            newsub = copy.deepcopy(subdef)
            for subins in newsub[1:]:
                # update internal instance name, using x1.mos1 
                subins['name'] = xins['name'] +'.'+subins['name']
                # update internal instance nodes, using real name or internal node name
                for j in range(len(subins['nodes'])):
                    subins_node = subins['nodes'][j]
                    if subins_node in ['gnd', '0', 'gnd!']: # global gnd node
                       subins['nodes'][j] = '0'
                    elif subins_node in self.globallist:
                       subins['nodes'][j] = subins_node
                    else:
                        if subins_node in ports_mapping:
                            subins['nodes'][j] = ports_mapping[subins['nodes'][j]]
                        else:
                            subins['nodes'][j] = xins['name'] + '.' + subins['nodes'][j]
            self.elementlist.remove(xins)
            self.elementlist.extend(newsub[1:])
