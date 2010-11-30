# -*- Python -*-
# -*- coding: utf-8 -*-

'''openhrp

Copyright (C) 2010
    Yosuke Matsusaka
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

Library for easy access to name servers running components, the components
themselves, and managers.

'''


# Add the IDL path to the Python path
import sys
import os
_openhrp_idl_path = os.path.join(os.path.dirname(__file__), 'idl')
if _openhrp_idl_path not in sys.path:
    sys.path.append(_openhrp_idl_path)
del _openhrp_idl_path
del os
del sys


OPENHRP_VERSION = '0.0.1'

# vim: tw=79
