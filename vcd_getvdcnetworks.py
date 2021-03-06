#! /usr/bin/env python

"""
===================================================================================================
   Author:         Petr Nemec
   Description:    Get the vDC networks from all organizations
   Date:           2017-10-23
===================================================================================================
"""

from vcd import vCD
from vcd import credentials
from vcd import seldc
import sys

from pprint import pprint

# Select the vCD
inputs = 'inputs/vcd_' + seldc(sys.argv[1:]) + '.yml'


# vCD credentials
cred = credentials(inputs)
myvcd = vCD(*cred)


# List all external networks
myvcd.gettoken()
pprint(myvcd.getedges())


# Get all organizations
print('Retrieving organisation list -------')
orgs = myvcd.getorgs()
pprint(orgs)


# Get vDCs
print('Retrieving vDCs --------------------')
# Get all vDCs
vdc_dir = {}
for org in orgs:
    vdc_dir[org] = myvcd.getvdcs(orgs[org])
print('vDCs summary --------------------')
pprint(vdc_dir)



# Get all vDC networks from all organisations
print('Retrieving vDC Networks -------------')
vdcnets = {}
for org in vdc_dir:
    for vdc in vdc_dir[org].values():
        vdcnets.update(myvcd.getvdcnetworks(vdc))
pprint(vdcnets)
