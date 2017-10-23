#! /usr/bin/env python

"""
===================================================================================================
   Author:         Petr Nemec
   Description:    Get the list of external networks
   Date:           2017-10-23
===================================================================================================
"""

from vcd import vCD
from vcd import credentials
from vcd import seldc
import sys

# Select the vCD to be modified
inputs = 'inputs/vcd_' + seldc(sys.argv[1:]) + '.yml'


# vCD credentials
cred = credentials(inputs)
myvcd = vCD(*cred)


# List all external networks
myvcd.gettoken()
myvcd.getextnetworks()
