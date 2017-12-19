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
cprint('\nThese are the organizations available in the vDC', 'yellow')
pprint(orgs.keys())


org = 'None'
failure = 0
print('\n')
while org == 'None' or org not in orgs:
    org = raw_input("Choose an existing organization: ")
    failure += 1
    if failure > 3:
        print('Too many failures')
        sys.exit(1)


# Choose vDC ----------------------------------------------------------------------------
vdcs = myvcd.getvdcs(orgs[org])
print('\n')
cprint('\nThese are the Virtual Data Centers available in the organizations %s' % org, 'yellow')
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
cprint('\nThese are the vApps in the Virtual Data Centers %s' % vdc, 'yellow')
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


# Get the list of VMs included in the vApps ---------------------------------------------------------

VMs = {}
for vapp in vapps:
    VMs.update(myvcd.getvapp_vms(existing_vapps[vapp]))
# print('\n')
# pprint(VMs)


# Get the list of VMs & IPs -------------------------------------------------------------

VMs_w_ip = {}
print('\n')
for vm in VMs:
    VMs_w_ip[vm] = {'uuid': VMs[vm]}
    # print vm
    nwinfo = myvcd.getvapp_vm_networkcards(VMs[vm])
    # print(nwinfo)
    VMs_w_ip[vm].update(nwinfo)


print('\n')
cprint('\nReview the VMs to be modified:', 'yellow')
pprint(VMs_w_ip)


# Choose the vDC Networks to be switched over -------------------------------------------
vdcnets = myvcd.getvdcnetworks(vdcs[vdc])
print('\n')
cprint('\nThese are the Org VDC Networks available in the %s' % vdc, 'yellow')
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


# Check that all VMs are connected to the Old Network -----------------------------------

incompl_VMs = []
for vm in VMs_w_ip:
    vm_compliant = False
    for key in VMs_w_ip[vm].keys():
        if key.startswith("Network adapter"):
            if VMs_w_ip[vm][key]['org_nw'] == old_vdcnet:
                vm_compliant = True
    if not vm_compliant:
        incompl_VMs.append(vm)

if len(incompl_VMs) > 0:
    cprint("\nThese VMs aren't assigned to the Org NW %s" % old_vdcnet, 'red')
    pprint(incompl_VMs)
    cprint("\nCan't proceed, exiting the script", 'red')
    sys.exit(1)



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
