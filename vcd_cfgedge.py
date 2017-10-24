#! /usr/bin/env python

"""
===================================================================================================
   Author:         Petr Nemec
   Description:    Create the edge
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



# Choose external network ---------------------------------------------------------------
extnets = myvcd.getextnetworks()
pprint(extnets.keys())

extnw = 'None'
failure = 0
while extnw == 'None' or extnw not in extnets.keys():
    extnw = raw_input("Choose an existing external network: ")
    failure += 1
    if failure > 3:
        print('Too many failures')
        sys.exit(1)




# Read the parameters of the external network from *.yml file ---------------------------
path = 'inputs/edge_' + env + '.yml'

# Read Edge parameters
with open(path, 'r') as f:
    edge_spec = f.read()

edge_data = yaml.load(edge_spec)


# add additional parameters taken from input dialog to directory
edge_data['extnetwork'] = extnets[extnw]



# Print configuration summary -----------------------------------------------------------
print('\n')
cprint('\nReview the edge to be created:', 'red')
print('  Organization:       %s' % org)
print('  vDC                 %s' % vdc)
print('  External network:   %s' % extnw)
print('  Name:               %s' % edge_data['name'])
print('  Gateway:            %s' % edge_data['Gateway'])
print('  Netmask:            %s' % edge_data['Netmask'])
print('  Pool End Address:   %s' % edge_data['IpAddress'])
print('\n')


agree = raw_input("Do you want to apply these changes? y/n[N]: " or 'N')


# Configure edge   ----------------------------------------------------------------------

# Proceed with updating configuration
if agree != "Y" and agree != "y":
    print("Script execution canceled")
    sys.exit(1)
else:
    # Define XML Body
    xml_edge = createbody("templates/edge.j2", edge_data)

    # Create edge
    print('Wait for tasks to be completed')
    print('Configuring edge - {0} ---------'.format(edge_data['name']))
    myvcd.create_edge(vdcs[vdc], xml_edge)







