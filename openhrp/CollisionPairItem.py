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

class CollisionPairItem:
    def __init__(self):
        self.name = None
        self.objectName1 = ''
        self.objectName2 = ''
        self.jointName1 = ''
        self.jointName2 = ''
        self.springDamperModel = False
        self.springConstant = [0, 0, 0, 0, 0, 0]
        self.staticFriction = 0.5
        self.slidingFriction = 0.0
        self.damperConstant = [0, 0, 0, 0, 0, 0]
        self.sim = None
    
    def parse(self, d):
        '''Parse XML object for collision pair'''
        self.name = str(d.getAttribute('name'))
        for p in d.getElementsByTagName('property'):
            t = p.getAttribute('name')
            v = str(p.getAttribute('value'))
            if t == 'objectName1':
                self.objectName1 = v
            elif t == 'objectName2':
                self.objectName2 = v
            elif t == 'jointName1':
                self.jointName1 = v
            elif t == 'jointName2':
                self.jointName2 = v
            elif t == 'springDamperModel':
                self.springDamperModel = (v == 'true')
            elif t == 'springConstant':
                self.springConstant = [float(vi) for vi in v.split(' ')]
            elif t == 'staticFriction':
                self.staticFriction = float(v)
            elif t == 'slidingFriction':
                self.slidingFriction = float(v)
            elif t == 'damperConstant':
                self.damperConstant = [float(vi) for vi in v.split(' ')]
            else:
                print >>sys.stderr, 'cannot parse collision pair type: %s = %s' % (t, v)
        return self

    def attach(self, sim):
        '''Attach collision pair to the dynamic simulator'''
        self.sim = sim
        self.sim.registerCollisionCheckPair(self.objectName1, self.jointName1, self.objectName2, self.jointName2, self.staticFriction, self.slidingFriction, self.springConstant, self.damperConstant, 0.01)


