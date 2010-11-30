#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''openhrp-python

Copyright (C) 2010
    Yosuke Matsusaka
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

Utility functions for arithmetic operation.
'''

import math

def transtoangle(t):
    (m00, m01, m02, m10, m11, m12, m20, m21, m22) = t

    cos = (m00 + m11 + m22 - 1.0)*0.5;
    x = m21 - m12;
    y = m02 - m20;
    z = m10 - m01;
    sin = 0.5*math.sqrt(x*x + y*y + z*z);
    angle = math.atan2(sin, cos);

    return [angle, x, y, z]

def angletotrans(a):
    (angle, x, y, z) = a
    
    magnitude = math.sqrt(x*x + y*y + z*z);
    if magnitude == 0:
        return None
    x = x / magnitude;
    y = y / magnitude;
    z = z / magnitude;

    c = math.cos(angle)
    s = math.sin(angle)
    t = 1.0 - c
    m00 = c + x*x*t
    m11 = c + y*y*t
    m22 = c + z*z*t

    tmp1 = x*y*t
    tmp2 = z*s
    m10 = tmp1 + tmp2
    m01 = tmp1 - tmp2
    
    tmp1 = x*z*t
    tmp2 = y*s
    m20 = tmp1 - tmp2
    m02 = tmp1 + tmp2
    
    tmp1 = y*z*t
    tmp2 = x*s
    m21 = tmp1 + tmp2
    m12 = tmp1 - tmp2
    
    return [m00, m01, m02, m10, m11, m12, m20, m21, m22]

