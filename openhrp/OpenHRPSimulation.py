#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''openhrp

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
import pickle
import progressbar
from optparse import OptionParser, OptionError
from xml.dom.minidom import parse
from omniORB import CORBA
import CosNaming
import OpenHRP
from utils import transtoangle, angletotrans
from SimulationItem import *
from ModelItem import *
from CollisionPairItem import *

class OpenHRPSimulation:
    def __init__(self):
        self.simulationitem = []
        self.modelitem = []
        self.collisionpairitem = []
        self.orb = None
        self.ns = None
        self.sim = None
        
        # initialize CORBA
        self.orb = CORBA.ORB_init(sys.argv, CORBA.ORB_ID)

        # find CORBA name server
        nsobj = self.orb.resolve_initial_references("NameService")
        self.ns = nsobj._narrow(CosNaming.NamingContext)
        
        # find simulator service from the name server
        try:
            obj = self.ns.resolve([CosNaming.NameComponent("DynamicsSimulator","")])
            self.sim = obj._narrow(OpenHRP.DynamicsSimulator)
        except CosNaming.NamingContext.NotFound:
            pass

    def createsimulator(self):
        # find dyamics simulator factory service from the name server
        try:
            obj = self.ns.resolve([CosNaming.NameComponent("DynamicsSimulatorFactory","")])
            simfactory = obj._narrow(OpenHRP.DynamicsSimulatorFactory)
        except CosNaming.NamingContext.NotFound:
            print >> sys.stderr, "Cannot find DynamicsSimulatorFactory."
            sys.exit(1)
        self.sim = simfactory.create()
        # bind simulator service to the name server
        self.ns.bind([CosNaming.NameComponent("DynamicsSimulator","")], self.sim)

    def init(self):
        if self.sim is not None:
            self.ns.unbind([CosNaming.NameComponent("DynamicsSimulator","")])
            try:
                self.sim.destroy()
            except CORBA.TRANSIENT:
                pass
        self.createsimulator()
    
    def load(self, fname):
        # find model loader service
        obj = self.ns.resolve([CosNaming.NameComponent("ModelLoader","")])
        modelloader = obj._narrow(OpenHRP.ModelLoader)

        # parse items in project file
        doc = parse(fname)
        for d in doc.getElementsByTagName('item'):
            t = d.getAttribute('class')
            if t == 'com.generalrobotix.ui.item.GrxSimulationItem':
                self.simulationitem.append(SimulationItem().parse(d))
            elif t == 'com.generalrobotix.ui.item.GrxModelItem':
                self.modelitem.append(ModelItem().parse(d, fname))
            elif t == 'com.generalrobotix.ui.item.GrxCollisionPairItem':
                self.collisionpairitem.append(CollisionPairItem().parse(d))

        if len(self.simulationitem) == 0:
            return 1

        # load models to dynamic simulator
        for m in self.modelitem:
            m.attachmodel(self.sim, modelloader)

        # set simulation parameters
        self.simulationitem[0].attach(self.sim)

        # set angles to models
        for m in self.modelitem:
            m.attachangles(self.sim)
        self.sim.calcWorldForwardKinematics()

        # set collision pairs
        for p in self.collisionpairitem:
            p.attach(self.sim)

        return 0
        
    def run(self, endtime, logfile = None):
        meter = progressbar.ProgressBar(maxval=endtime)
        self.sim.initSimulation()
        if logfile:
            f = open(logfile, 'wb')
            p = pickle.Pickler(f, -1)
        while True:
            # update dynamics simulator
            self.sim.stepSimulation()
            state = self.sim.getWorldState()
            # store current state to log
            if logfile:
                p.dump(state)
            # quit when end time has reached
            if (state.time > endtime):
                break
            meter.update(state.time)
        if logfile:
            del p
            f.close()
        meter.finish()
        return 0

    def view(self, logfile):
        obj = self.ns.resolve([CosNaming.NameComponent("OnlineViewer","")])
        viewer = obj._narrow(OpenHRP.OnlineViewer)
        f = open(logfile, 'rb')
        p = pickle.Unpickler(f)
        while True:
            state = p.load()
            viewer.update(state)
        del p
        f.close()
        return 0

def main():
    usage = '''Usage: %prog [options]
Control simulation from command line.'''
    #parser = OptionParser(usage=usage, version=OPENHRP_VERSION)
    parser = OptionParser(usage=usage)
    parser.add_option('-p', '--project', dest='projectfile', metavar='FILE', help='load project from FILE')
    parser.add_option('-r', '--run', dest='run', metavar='TIME',
                      help='run simulation for specified time period')
    parser.add_option('-l', '--log', dest='logfile', metavar='FILE', help='save log to FILE')
#    parser.add_option('-t', '--testfunc', dest='testfunc', metavar='FILE',
#                      help='test function (in python script) to detect success or failure')
    parser.add_option('-v', '--view', dest='viewfile', metavar='FILE',
                      help='load log from FILE and send to viewer service')

    # testfunc(sim, final=False)
    #    sim.getWorldState()
    #    return 1, 0, -1 (0 means continue, otherwise stop)

    try:
        options, args = parser.parse_args()
    except OptionError, e:
        print >>sys.stderr, 'OptionError: ', e
        return 1

    sim = OpenHRPSimulation()
    ret = 0
    if options.projectfile:
        sim.init()
        ret = sim.load(options.projectfile)
    if options.run:
        ret = sim.run(float(options.run), options.logfile)
    if options.viewfile:
        ret = sim.view(options.viewfile)
    return ret

if __name__=='__main__':
    sys.exit(main())
