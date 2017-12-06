#! /usr/bin/env python

"""
===================================================================================================
   Author:         Petr Nemec
   Description:    To switchover ORG Networks
   Date:           2017-10-23
===================================================================================================
"""

from vcd import vCD
from vcd import credentials
from vcd import seldc
import sys

from termcolor import cprint
from pprint import pprint

# Select the vCD to be modified
inputs = 'inputs/vcd_' + seldc(sys.argv[1:]) + '.yml'


# Load vCD credentials ---------------------------------------------------
cred = credentials(inputs)
myvcd = vCD(*cred)
myvcd.gettoken()


# Choose organization -------------------------------------------------------------------
orgs = myvcd.getorgs()
print('\n')
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
print('\n')
pprint(vdcs.keys())

vdc = 'None'
failure = 0
while vdc == 'None' or vdc not in vdcs:
    vdc = raw_input("Choose an existing vDC: ")
    failure += 1
    if failure > 3:
        print('Too many failures')
        sys.exit(1)


# Choose vApp ---------------------------------------------------------------------------
existing_vapps = myvcd.getvapp(vdcs[vdc])
print('\n')
pprint(existing_vapps.keys())
vapps = []
agree = 'Y'
failure = 0

while agree == "y" or agree == "Y":
    vapp = raw_input("Choose an existing vApp to be modified: ")
    if vapp not in vapps:
        failure += 1
        if failure > 3:
            print('Too many failures')
            sys.exit(1)
    vapps.append(vapp)
    agree = raw_input("Do you want to add more vApps? y/n[N]: " or 'N')

print('These vApps will be modified')
print(vapps)



# Choose the vDC Networks to be switched over -------------------------------------------
vdcnets = myvcd.getvdcnetworks(vdcs[vdc])
print('\n')
pprint(vdcnets.keys())


old_vdcnet = 'None'
failure = 0
while old_vdcnet == 'None' or old_vdcnet not in vdcnets:
    old_vdcnet = raw_input("Choose old Org Network: ")
    failure += 1
    if failure > 3:
        print('Too many failures')
        sys.exit(1)


new_vdcnet = 'None'
failure = 0
while new_vdcnet == 'None' or new_vdcnet not in vdcnets:
    new_vdcnet = raw_input("Choose new Org Network: ")
    failure += 1
    if failure > 3:
        print('Too many failures')
        sys.exit(1)



# Check that vApps contains the Old&New Org Networks ------------------------------------------------


# Get the list of VMs included in the vApps ---------------------------------------------------------

VMs = {}
for vapp in vapps:
    VMs.update(myvcd.getvapp_vms(existing_vapps[vapp]))
print('\n')
pprint(VMs)


# Get the list of VMs & IPs -------------------------------------------------------------

VMs_w_ip = {}
for vm in VMs:
    VMs_w_ip[vm] = VMs[vm]
    print vm
    print(myvcd.getvapp_vm_networkcards(VMs[vm])
    VMs_w_ip.update(myvcd.getvapp_vm_networkcards(VMs[vm]))


print('\n')
cprint('\nReview the VMs to be changed:', 'yellow')
pprint(VMs_w_ip)


# Print configuration summary -----------------------------------------------------------
print('\n')
cprint('\nReview the configuration changes:', 'red')
print('  Organization:       %s' % org)
print('  vDC                 %s' % vdc)
print('  vApps:              %s' % vapps)
print('  VMs:                %s' % VMs.keys())
print('  Old Org Network:    %s' % old_vdcnet)
print('  New Org Network:    %s' % new_vdcnet)
print('\n')


agree = raw_input("Do you want to apply these changes? y/n[N]: " or 'N')


# Configure edge   ----------------------------------------------------------------------
"""
# Proceed with updating configuration
if agree != "Y" and agree != "y":
    print("Script execution canceled")
    sys.exit(1)
else:
    for vm in VMs:
    # Define XML Body
    xml_edge = createbody("templates/edge.j2", edge_data)

    # Create edge
    print('Wait for tasks to be completed')
    print('Configuring edge - {0} ---------'.format(edge_data['name']))
    myvcd.create_edge(vdcs[vdc], xml_edge)

"""
