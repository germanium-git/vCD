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

from pprint import pprint

# Select the vCD to be modified
inputs = 'inputs/vcd_' + seldc(sys.argv[1:]) + '.yml'


extnw_data = {}

"""
# Choose organization -----------------------------------------------------
orgs = myvcd.getorgs()
org = 'None'
while org == 'None' or org not in orgs:
    org = raw_input("Organization: ")


org = 'None'
failure = 0
while org == 'None' or org not in orgs:
    org = raw_input("Organization: ")
    failure += 1
    if failure > 3:
        print('Too many failures')
        sys.exit(1)

extnw_data['organization'] = org

"""

# Choose dvportgroup -----------------------------------------------------
dvportgroups = myvcd.getportgroups()
dvpgroup = 'None'
failure = 0
while dvpgroup == 'None' or dvpgroup not in dvportgroups:
    dvpgroup = raw_input("dvportgroup: ")
    failure += 1
    if failure > 3:
        print('Too many failures')
        sys.exit(1)

extnw_data['organization'] = org


VimServerReference


# vCD credentials
cred = credentials(inputs)
myvcd = vCD(*cred)


# List all external networks
myvcd.gettoken()
pprint(myvcd.getextnetworks())
