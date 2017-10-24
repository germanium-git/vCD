#! /usr/bin/env python

"""
===================================================================================================
   Author:         Petr Nemec
   Description:    Create vDC network
   Date:           2017-10-23
===================================================================================================
"""

from vcd import vCD
from vcd import credentials
from vcd import seldc
from vcd import createbody
import sys

import yaml
from termcolor import cprint
from pprint import pprint



# Select the vCD to be modified
env = seldc(sys.argv[1:])
inputs = 'inputs/vcd_' + env + '.yml'


# Load vCD credentials ---------------------------------------------------
cred = credentials(inputs)
myvcd = vCD(*cred)
myvcd.gettoken()


# Choose organization -------------------------------------------------------------------
orgs = myvcd.getorgs()
pprint(orgs.keys())


org = 'None'
failure = 0
while org == 'None' or org not in orgs:
    org = raw_input("Choose an existing organization: ")
    failure += 1
    if failure > 3:
        print('Too many failures')
        sys.exit(1)


# Choose vDC ----------------------------------------------------------------------------
vdcs = myvcd.getvdcs(orgs[org])
pprint(vdcs.keys())

vdc = 'None'
failure = 0
while vdc == 'None' or vdc not in vdcs:
    vdc = raw_input("Choose an existing vDC: ")
    failure += 1
    if failure > 3:
        print('Too many failures')
        sys.exit(1)



# Choose edge ---------------------------------------------------------------------------
alledges = myvcd.getedges()
pprint(alledges)
orgedges = {}

print(vdcs.values())

for edge in alledges:
    # Test if the edge belongs to one of the organisation's vDC
    print alledges[edge]['vdc']
    if alledges[edge]['vdc'] in vdcs.values():
        # Crete a subset of edges belonging to the organisation
        orgedges[edge] = alledges[edge]['uuid']

pprint(orgedges.keys())

edge = 'None'
failure = 0
while edge == 'None' or edge not in orgedges.keys():
    edge = raw_input("Choose an existing edge: ")
    failure += 1
    if failure > 3:
        print('Too many failures')
        sys.exit(1)




# Read the parameters of the vdc network from *.yml file ---------------------------
path = 'inputs/vdcnet_' + env + '.yml'

# Read Edge parameters
with open(path, 'r') as f:
    edge_spec = f.read()

vdc_data = yaml.load(edge_spec)


# add additional parameters taken from input dialog to directory
vdc_data['edge'] = orgedges[edge]


# Print configuration summary -----------------------------------------------------------
print('\n')
cprint('\nReview the edge to be created:', 'red')
print('  Organization:       %s' % org)
print('  Edge                %s' % edge)
print('  Name:               %s' % vdc_data['name'])
print('  Description:        %s' % vdc_data['Description'])
print('  Gateway:            %s' % vdc_data['Gateway'])
print('  Netmask:            %s' % vdc_data['Netmask'])
print('  Pool Start Address: %s' % vdc_data['StartAddress'])
print('  Pool End Address:   %s' % vdc_data['EndAddress'])
print('\n')


agree = raw_input("Do you want to apply these changes? y/n[N]: " or 'N')


# Configure edge   ----------------------------------------------------------------------

# Proceed with updating configuration
if agree != "Y" and agree != "y":
    print("Script execution canceled")
    sys.exit(1)
else:
    # Define XML Body
    xml_vdcnet = createbody("templates/edge.j2", vdc_data)

    # Create edge
    print('Wait for tasks to be completed')
    print('Configuring vDC network - {0} ---------'.format(vdc_data['name']))
    myvcd.create_vdcnetwork(vdcs[vdc], xml_vdcnet)







