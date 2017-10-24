#! /usr/bin/env python

"""
===================================================================================================
   Author:         Petr Nemec
   Description:    Create the external network
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

# Load vCD credentials ---------------------------------------------------
cred = credentials(inputs)
myvcd = vCD(*cred)



# Retrieve vCenter VimServerReference ------------------------------------
myvcd.gettoken()
vcenter = myvcd.getvcenter()



# Choose dvportgroup -----------------------------------------------------
# Retrieve all portgroups
dvportgroups = myvcd.getportgroups(vcenter[VimServerReference])
dvpgroup = 'None'
failure = 0
while dvpgroup.isdigit == False or ('dvpgroup' + str(dvpgroup)) not in dvportgroups:
    dvpgroup = raw_input("Choose existing dvportgroup: ")
    failure += 1
    if failure > 3:
        print('Too many failures')
        sys.exit(1)



# Read the parameters of the external network from *.yml file ---------------
path = 'inputs/extnet_' + env + '.yml'

# Read PE parameters
with open(path, 'r') as f:
    extnw_spec = f.read()

# Read the directory of credentials from file
extnw_data = yaml.load(extnw_spec)


# add dvportgroup to directory
extnw_data['dvswitchpg'] = 'dvportgroup-' + str(dvportgroup)


# Print configuration summary ------------------------------------------------
print('\n')
cprint('\nReview the external network to be created:', 'red')
print('  Name:               %s' % extnw_data['name'])
print('  Gateway:            %s' % extnw_data['Gateway'])
print('  Netmask:            %s' % extnw_data['netmask'])
print('  Pool Start Address: %s' % extnw_data['StartAddress'])
print('  Pool End Address:   %s' % extnw_data['EndAddress'])
print('\n')


agree = raw_input("Do you want to apply these changes? y/n[N]: " or 'N')


# Configure external network   ------------------------------------------------

# Proceed with updating configuration
if agree != "Y" and agree != "y":
    print("Script execution canceled")
    sys.exit(1)
else:
    # Define XML Body
    xml_extnw = createbody("templates/extnetw.j2", extnw_data)

    # Create edge
    print('Wait for tasks to be completed')
    print('Configuring external network - {0} ---------'.format(extnw_data['name']))
    myvcd.create_extnetwork(xml_extnw)







