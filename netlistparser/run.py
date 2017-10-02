#!/usr/bin/python
# coding: utf-8

"""
parser all cases in circuit_classification_dataset
"""

import os, sys, pdb

ampPath='../../circuit_classification_dataset/amp_cases/'
p_ampPath='../../circuit_classification_dataset/parsered_cases/amp_cases/'
nonampPath='../../circuit_classification_dataset/nonamp_cases/'
p_nonampPath='../../circuit_classification_dataset/parsered_cases/nonamp_cases/'

ampFiles=[]
nonampFiles=[]
ampFiles=[f for f in os.listdir(ampPath)]
nonampFiles=[f for f in os.listdir(nonampPath)]

for file in ampFiles:
    name=file.split('.')[0]
    os.system('python parser.py '+ampPath+file+' '+p_ampPath+name+'.out')
for file in nonampFiles:
    name=file.split('.')[0]
    os.system('python parser.py '+nonampPath+file+' '+p_nonampPath+name+'.out')
