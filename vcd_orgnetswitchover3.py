#! /usr/bin/env python

"""
===================================================================================================
   Author:         Petr Nemec
   Description:    To switchover ORG Networks - Work in progress
   Date:           2018-01-01
===================================================================================================
"""

from vcd import vCD
from vcd import createbody
from vcd import credentials
from vcd import seldc
import sys

from termcolor import cprint
from pprint import pprint

# Select the vCD to be modified
inputs = 'inputs/vcd_' + seldc(sys.argv[1:]) + '.yml'
# Uncomment for testing purposes
# inputs = 'inputs/vcd_mylab.yml'


# Load vCD credentials ------------------------------------------------------------------
cred = credentials(inputs)
# cred = ('10.20.30.40', 'administrator@system', 'Password1234')



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
    org = input("Choose an existing organization: ")
    failure += 1
    if failure > 3:
        print('Too many failures')
        sys.exit(1)



# Identify Organizations's vDC ----------------------------------------------------------
vdcs = myvcd.getvdcs(orgs[org])
print('\n')
cprint('\nThese are the Virtual Data Centers available in the organization %s' % org, 'yellow')
print(vdcs.keys())




# Choose Organizations's vApps ----------------------------------------------------------
vapps = {}
print('\n')
for vdc in vdcs:
    vdc_vapps = myvcd.getvapp(vdcs[vdc])
    vapps.update(vdc_vapps)

cprint('\nThese are the vApps in the organization %s' % org, 'yellow')
print(vapps.keys())



# Get the list of VMs included in the vApps ---------------------------------------------
VMs = {}
for vapp in vapps:
    vapp_vms = myvcd.getvapp_vms(vapps[vapp])
    for vm in vapp_vms:
        """
        print(vapp_vms[vm])
        print(vm)
        print(VMs)
        """
        VMs[vm] = {'uuid': vapp_vms[vm], 'vapp': vapp}

print('\n')
cprint('\nThese are the VMs in the organization %s' % org, 'yellow')
pprint(VMs)



# Get the list of VMs and their IPs -----------------------------------------------------
VMs_w_ip = {}
print('\n')
for vm in VMs:
    VMs_w_ip[vm] = {'uuid': VMs[vm]['uuid']}
    nwinfo = myvcd.getvapp_vm_networkcards(VMs[vm]['uuid'])
    VMs_w_ip[vm].update(nwinfo)


print('\n')
cprint('\nList of the VMs updated with IP addresses & nw info', 'yellow')
pprint(VMs_w_ip)


# Get the list of all Org Vdc Networks --------------------------------------------------
orgnets = {}
for vdc in vdcs:
    vdcnets = myvcd.getvdcnetworks(vdcs[vdc])
    orgnets.update(vdcnets)
print('\n')
cprint('\nThese Org VDC Networks are available in the organization %s' % org, 'yellow')
print(orgnets.keys())


old_vdcnet = 'None'
failure = 0
while old_vdcnet == 'None' or old_vdcnet not in orgnets:
    old_vdcnet = input("Choose the existing Org Network to be switched onto new Org Network: ")
    failure += 1
    if failure > 3:
        print('Too many failures')
        sys.exit(1)



# Check which VMs are connected to the Old Network --------------------------------------
compl_VMs = {}
for vm in VMs_w_ip:
    vm_compliant = False
    for key in VMs_w_ip[vm].keys():
        if key.startswith("Network adapter"):
            if VMs_w_ip[vm][key]['org_nw'] == old_vdcnet:
                vm_compliant = True
    if vm_compliant:
        compl_VMs[vm] = (VMs_w_ip[vm])


pprint(compl_VMs)


# Identify the vApps the compliant VMs are member of ------------------------------------

app_list = []
for vm in compl_VMs:
    app_list.append(VMs[vm]['vapp'])

app_list = set(app_list)

cprint('\nThese are the vApps to be updated with new Org VDC Network', 'yellow')
pprint(app_list)



# Add new Org Network to the vApp -------------------------------------------------------

cprint('\nThese are the Org VDC Networks available in the organization %s' % org, 'yellow')
print(orgnets.keys())
new_vdcnet = 'None'
failure = 0
while new_vdcnet == 'None' or new_vdcnet not in orgnets:
    new_vdcnet = input("Choose the new Org Network to be switched to: ")
    failure += 1
    if failure > 3:
        print('Too many failures')
        sys.exit(1)



for vapp in app_list:
    # Retrieve current networkConfigSection
    current_config = myvcd.vapp_get_networks(vapps[vapp])
    # Create new body (append new network
    nw_cfg = {'org_nw_name': new_vdcnet, 'org_nw_id': orgnets[new_vdcnet]}
    new_config = createbody('templates/nwconfig.j2', nw_cfg)

    # Replace the ending </NetworkConfigSection> tag from current config with new config
    updated_config = current_config.replace("</NetworkConfigSection>", new_config)
    print(updated_config)

    # Add new network to vApp
    myvcd.vapp_add_network(vapps[vapp], updated_config)


# Switch VM network card ----------------------------------------------------------------

for vm in compl_VMs:
    # Read current networkCards section
    # Update current networkCards section with new Org Network



    

