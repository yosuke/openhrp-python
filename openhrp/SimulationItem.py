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

class SimulationItem:
    def __init__(self):
        self.name = None
        self.integrate = False
        self.viewsimulate = OpenHRP.DynamicsSimulator.DISABLE_SENSOR
        self.totalTime = 0
        self.timeSep = 0.001
        self.gravity = 9.8
        self.method = OpenHRP.DynamicsSimulator.EULER
        self.sim = None
    
    def parse(self, d):
        '''Parse XML object for simulation parameters'''
        self.name = d.getAttribute('name')
        for p in d.getElementsByTagName('property'):
            t = p.getAttribute('name')
            if t == 'integrate':
                self.integrate = (p.getAttribute('value') == 'true')
            elif t == 'viewsimulate':
                if p.getAttribute('value') == 'true':
                    self.viewsimulate = OpenHRP.DynamicsSimulator.ENABLE_SENSOR
            elif t == 'totalTime':
                self.totalTime = float(p.getAttribute('value'))
            elif t == 'timeSep':
                self.timeSep = float(p.getAttribute('value'))
            elif t == 'gravity':
                self.gravity = float(p.getAttribute('value'))
            elif t == 'method':
                if p.getAttribute('value') == 'RUNGE_KUTTA':
                    self.method = OpenHRP.DynamicsSimulator.RUNGE_KUTTA
        return self
    
    def attach(self, sim):
        '''Attach simulation parameters to the dynamics simulator'''
        self.sim = sim
        #self.sim.init(self.timeSep, self.method, self.viewsimulate)
        self.sim.init(self.timeSep, self.method, OpenHRP.DynamicsSimulator.DISABLE_SENSOR)
        self.sim.setGVector([0, 0, self.gravity])

