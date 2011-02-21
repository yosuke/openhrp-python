#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''openhrp.py

Copyright (C) 2010
    Yosuke Matsusaka
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt
'''

import os
import sys
_openhrp_idl_path = os.path.join(os.path.dirname(__file__), 'idl')
if _openhrp_idl_path not in sys.path:
    sys.path.append(_openhrp_idl_path)

import OpenHRP
from utils import transtoangle, angletotrans

class ModelItem:
    def __init__(self):
        self.name = None
        self.url = None
        self.angle = {}
        self.transition = {}
        self.rotation = {}
        self.sim = None
    
    def parse(self, d, fname = None):
        '''Parse XML object for object model'''
        self.name = str(d.getAttribute('name'))
        self.url = str(d.getAttribute('url'))
        if fname:
            self.url = os.path.abspath(self.url.replace('$(PROJECT_DIR)', os.path.dirname(fname)))
        for p in d.getElementsByTagName('property'):
            t = str(p.getAttribute('name'))
            if t.count('.') == 1:
                (joint, type) = t.split('.')
                if type == 'angle':
                    self.angle[joint] = float(p.getAttribute('value').strip())
                elif type == 'transition':
                    self.transition[joint] = [float(v) for v in p.getAttribute('value').strip().split(' ')]
                elif type == 'rotation':
                    self.rotation[joint] = [float(v) for v in p.getAttribute('value').strip().split(' ')]
        return self

    def attachmodel(self, sim, modelloader):
        '''Attach object model to the dynamics simulator'''
        self.sim = sim
        # load model from file
        mm = modelloader.loadBodyInfo(self.url)
        # initialize dynamics simulator
        self.sim.registerCharacter(self.name, mm)

    def attachangles(self, sim):
        '''Attach object angles to the dynamics simulator'''
        self.sim = sim
        for n, v in self.angle.iteritems():
            self.sim.setCharacterLinkData(self.name, n, OpenHRP.DynamicsSimulator.JOINT_VALUE, [v])
        for n in list(set(self.transition.keys() + self.rotation.keys())):
            t = self.transition.get(n)
            if t is None:
                t = [0, 0, 0]
            r = self.rotation.get(n)
            if t is None:
                r = [1,0,0,0,1,0,0,0,1]
            else:
                r = angletotrans(r)
            self.sim.setCharacterLinkData(self.name, n, OpenHRP.DynamicsSimulator.ABS_TRANSFORM, t + r)


