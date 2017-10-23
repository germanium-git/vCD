#! /usr/bin/env python

"""
===================================================================================================
   Author:         Petr Nemec
   Description:    Get the vCenter UUID - vimServerReferences
   Date:           2017-10-23
===================================================================================================
"""

from vcd import vCD
from vcd import credentials
from vcd import seldc
import sys

from pprint import pprint

# Select the vCD to be modified
inputs = 'inputs/vcd_' + seldc(sys.argv[1:]) + '.yml'


# vCD credentials
cred = credentials(inputs)
myvcd = vCD(*cred)


# Get vCenter UUID
myvcd.gettoken()
VimServerReference = myvcd.getvcenter()

myvcd.getportgroups(VimServerReference)


