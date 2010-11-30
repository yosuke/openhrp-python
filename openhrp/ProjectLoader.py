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

import traceback
import math
from optparse import OptionParser, OptionError
from xml.dom.minidom import parse
from omniORB import CORBA
import CosNaming
import OpenHRP
from utils import transtoangle, angletotrans

class SimulationItem:
    def __init__(self):
        self.name = None
        self.integrate = False
        self.viewsimulate = False
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
        self.sim.init(self.timeSep, self.integrate, self.viewsimulation)
        self.sim.setGVector([0, 0, self.gravity])

class ModelItem:
    def __init__(self):
        self.name = None
        self.url = None
        self.angle = {}
        self.transition = {}
        self.rotation = {}
        self.sim = Noe
    
    def parse(self, d):
        '''Parse XML object for object model'''
        self.name = d.getAttribute('name')
        self.url = d.getAttribute('url')
        for p in d.getElementsByTagName('property'):
            t = p.getAttribute('name')
            if t.count('.') == 1:
                (joint, type) = t.split('.')
                if type == 'angle':
                    self.angle[joint] = float(p.getAttribute('value'))
                elif type == 'transition':
                    self.transition[joint] = [float(v) for v in p.getAttribute('value').split(' ')]
                elif type == 'rotation':
                    self.rotation[joint] = [float(v) for v in p.getAttribute('value').split(' ')]
        return self

    def attach(self, sim, modelloader):
        '''Attach object model to the dynamics simulator'''
        self.sim = sim
        # load model from file
        mm = modelloader.loadBodyInfo(m.url)
        # initialize dynamics simulator
        self.sim.registerCharacter(self.name, mm)
        # set angles
        for n, v in self.angles.iteritem():
            self.sim.setCharacterLinkData(m.name, n, OpenHRP.DynamicsSimulator.JOINT_VALUE, v)
        # set transition
        for n, v in self.transition.iteritem():
            self.sim.setCharacterLinkData(m.name, n, OpenHRP.DynamicsSimulator.ABS_TRANSFORM, v)
        # set rotation
        for n, v in self.rotation.iteritem():
            self.sim.setCharacterLinkData(m.name, n, OpenHRP.DynamicsSimulator.ABS_TRANSFORM, angletotrans(v))

class CollisionPairItem:
    def __init__(self):
        self.name = None
        self.objectName1 = None
        self.objectName2 = None
        self.jointName1 = None
        self.jointName2 = None
        self.springDamperModel = False
        self.springConstant = []
        self.staticFriction = 0.5
        self.slidingFriction = 0.0
        self.damperConstant = []
        self.sim = None
    
    def parse(self, d):
        '''Parse XML object for collision pair'''
        self.name = d.getAttribute('name')
        for p in d.getElementsByTagName('property'):
            t = p.getAttribute('name')
            if type == 'objectName1':
                self.objectName1 = p.getAttribute('value')
            elif type == 'objectName2':
                self.objectName2 = p.getAttribute('value')
            elif type == 'jointName1':
                self.jointName1 = p.getAttribute('value')
            elif type == 'jointName2':
                self.jointName2 = p.getAttribute('value')
            elif type == 'springDamperModel':
                self.springDamperModel = (p.getAttribute('value') == 'true')
            elif type == 'springConstant':
                self.springConstant = [float(v) for v in p.getAttribute('value').split(' ')]
            elif type == 'staticFriction':
                self.staticFriction = float(p.getAttribute('value'))
            elif type == 'slidingFriction':
                self.slidingFriction = float(p.getAttribute('value'))
            elif type == 'damperConstant':
                self.damperConstant = [float(v) for v in p.getAttribute('value').split(' ')]
        return self

    def attach(self, sim):
        '''Attach collision pair to the dynamic simulator'''
        self.sim = sim
        self.sim.registerCollisionCheckPair(self.objectName1, self.jointName1, self.objectName2, self.jointName2)

class OpenHRPSimulation:
    def __init__(self, orb):
        self.simulationitem = []
        self.modelitem = []
        
        # find CORBA name server
        nsobj = orb.resolve_initial_references("NameService")
        self.ns = nsobj._narrow(CosNaming.NamingContext)
        
        # find simulator factory component from the name server
        obj = self.ns.resolve([CosNaming.NameComponent("DynamicsSimulatorFactory","")])
        self.simfactory = obj._narrow(OpenHRP.DynamicsSimulatorFactory)
        self.sim = self.simfactory.create()

        obj = self.ns.resolve([CosNaming.NameComponent("ModelLoader","")])
        self.modelloader = obj._narrow(OpenHRP.ModelLoader)

    def init(self):
        pass
    
    def load(self, fname):
        doc = parse(fname)
        for d in doc.getElementsByTagName('item'):
            t = d.getAttribute('class')
            if t == 'com.generalrobotix.ui.item.GrxSimulationItem':
                self.simulationitem.append(SimulationItem().parse(d))
            elif t == 'com.generalrobotix.ui.item.GrxModelItem':
                self.modelitem.append(ModelItem().parse(d))
            elif t == 'com.generalrobotix.ui.item.GrxCollisionPairItem':
                self.collisionpairitem.append(CollisionPairItem().parse(d))

        # set simulation algorithms
        if len(self.simulationitem) == 0:
            return

        self.simulationitem[0].attach(self.sim)
        for m in self.modelitem:
            m.attach(self.sim, self.modelloader)

        # set collision pairs
        for p in self.collisionpairitem:
            p.attach(self.sim)

        self.sim.calcWorldForwardKinematics()
        self.sim.initSimulation()
        
    def run(self):
        pass

def main():
    usage = '''Usage: %prog [options]
Control simulation from command line.'''
    parser = OptionParser(usage=usage, version=RTSH_VERSION)
    parser.add_option('-v', '--view', dest='view', action='store_true',
                      default=False, help='Show current simulation by connecting to the viewer. [Default: %default]')
    parser.add_option('-l', '--load [filename]', dest='load', action='store_true',
                      default=False, help='Load project file. [Default: %default]')
    parser.add_option('-r', '--run [endtime]', dest='run', action='store_true',
                      default=False, help='Run dynamic simulation. [Default: %default]')
    parser.add_option('-o', '--output [filename]', dest='output', action='store_true',
                      default=False, help='Save log to file. [Default: %default]')
    parser.add_option('-m', '--outputvrml [filename]', dest='outputvrml', action='store_true',
                      default=False, help='Save log to vrml file. [Default: %default]')
    parser.add_option('-t', '--testfunc [filename]', dest='testfunc', action='store_true',
                      default=False, help='Test function (in python script) to detect success or failure. [Default: %default]')

    # testfunc(sim, final=False)
    #    sim.getWorldState()
    #    return 1, 0, -1 (0 means continue, otherwise stop)

    try:
        options, args = parser.parse_args()
    except OptionError, e:
        print >>sys.stderr, 'OptionError: ', e
        return 1

    if not args:
        print >>sys.stderr, usage
        return 1

    sim = OpenHRPSimulator()
    ret = 0
    if options.load:
        sim.init()
        ret = sim.load(options.filename)
    if options.run:
        sim.test()
        ret = sim.run(options.output, options.testfunc)
    return ret
