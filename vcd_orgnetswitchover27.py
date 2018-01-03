#! /usr/bin/env python

"""
===================================================================================================
   Author:          Petr Nemec
   Description:     To switchover ORG Networks - Work in progress
                    There's one limitation - the network card being switched must be the primary one

   Date:            2018-01-01
===================================================================================================
"""

from vcd import vCD
from vcd import createbody
from vcd import credentials
from vcd import seldc
import sys

from termcolor import cprint
from pprint import pprint

import time


# Select the vCD to be modified
inputs = 'inputs/vcd_' + seldc(sys.argv[1:]) + '.yml'


# Load vCD credentials ------------------------------------------------------------------
cred = credentials(inputs)

myvcd = vCD(*cred)
myvcd.gettoken()


# Choose organization -------------------------------------------------------------------
orgs = myvcd.getorgs()
cprint('\nThe Organizations available in the vDC', 'yellow')
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



# Identify Organizations's vDC ----------------------------------------------------------
vdcs = myvcd.getvdcs(orgs[org])
print('\n')
cprint('\nThe Virtual Data Centers available in the organization %s' % org, 'yellow')
print(vdcs.keys())




# Identify Organizations's vApps ----------------------------------------------------------
cprint('\nThese are the vApps in the organization %s' % org, 'yellow')
vapps = {}
print('\n')
for vdc in vdcs:
    vdc_vapps = myvcd.getvapp(vdcs[vdc])
    vapps.update(vdc_vapps)



# Get the list of VMs included in the vApps ---------------------------------------------
cprint('\nRetrieving the list of all VMs in the organization %s' % org, 'yellow')
VMs = {}
for vapp in vapps:
    vapp_vms = myvcd.getvapp_vms(vapps[vapp])
    # Update the dictionary of VMs with vApp to which the VM belongs to
    for vm in vapp_vms:
        VMs[vm] = {'uuid': vapp_vms[vm], 'vapp': vapp}



# Get the list of VMs and their IP addresses --------------------------------------------
cprint('\nIdentifying the IP addresses & network cards of all VMs', 'yellow')
VMs_w_ip = {}
for vm in VMs:
    VMs_w_ip[vm] = {'uuid': VMs[vm]['uuid']}
    nwinfo = myvcd.getvapp_vm_networkcards(VMs[vm]['uuid'])
    VMs_w_ip[vm].update(nwinfo)



# Get the list of all Org Vdc Networks --------------------------------------------------
cprint('\nIdentifying the Org VDC Networks', 'yellow')
orgnets = {}
for vdc in vdcs:
    vdcnets = myvcd.getvdcnetworks(vdcs[vdc])
    orgnets.update(vdcnets)
cprint('\nThese are the Org VDC Networks available in the organization %s' % org, 'yellow')
print(orgnets.keys())



# Choose existing Org Network (old network) ---------------------------------------------
old_vdcnet = 'None'
failure = 0
while old_vdcnet == 'None' or old_vdcnet not in orgnets:
    old_vdcnet = raw_input("Choose the existing Org Network to be switched onto new Org Network: ")
    failure += 1
    if failure > 3:
        print('Too many failures')
        sys.exit(1)



# Choose new Org Network ----------------------------------------------------------------
new_vdcnet = 'None'
failure = 0
while new_vdcnet == 'None' or new_vdcnet not in orgnets:
    new_vdcnet = raw_input("Choose the new Org Network to be switched to: ")
    failure += 1
    if failure > 3:
        print('Too many failures')
        sys.exit(1)



# Identifying the VMs connected to the Old Network --------------------------------------
compl_VMs = {}
for vm in VMs_w_ip:
    vm_compliant = False
    for key in VMs_w_ip[vm]['adapters'].keys():
        if VMs_w_ip[vm]['adapters'][key]['org_nw'] == old_vdcnet:
            vm_compliant = True
    if vm_compliant:
        compl_VMs[vm] = (VMs_w_ip[vm])

cprint('\nThese are the VMs to be updated with new Org VDC Network', 'yellow')
pprint(compl_VMs)


# Identify the vApps the compliant VMs are member of ------------------------------------
app_list = []
for vm in compl_VMs:
    app_list.append(VMs[vm]['vapp'])

app_list = set(app_list)

cprint('\nThese are the vApps to be updated with new Org VDC Network', 'yellow')
pprint(app_list)



# Add new Org Network to the vApp -------------------------------------------------------
for vapp in app_list:
    # Retrieve current networkConfigSection
    current_config = myvcd.vapp_get_networks(vapps[vapp])
    # Create new body (append new network
    nw_cfg = {'org_nw_name': new_vdcnet, 'org_nw_id': orgnets[new_vdcnet]['uuid']}
    new_config = createbody('templates/nwconfig.j2', nw_cfg)

    # Replace the ending </NetworkConfigSection> tag from current config with new config
    updated_config = current_config.replace("</NetworkConfigSection>", new_config)

    # Add new network to vApp
    print('\nAdding the New Org network {} to the vApp: {}'.format(new_vdcnet, vapp))
    myvcd.vapp_add_network(vapps[vapp], updated_config)


# Switch VM's network card --------------------------------------------------------------
for vm in compl_VMs:
    # Render networkCards section
    """
    # This section would be needed only if the non-primary network card is to be modified
    for adapter in compl_VMs[vm]['adapters']:
        if compl_VMs[vm]['adapters'][adapter]['primary_nw'] == 'true':
            primary_adapter = compl_VMs[vm]['adapters'][adapter]

        compl_VMs[vm].update({'prim_nw_conn_index': primary_adapter})

    pprint(compl_VMs[vm])
    """
    print('\nUpdating the VM {}'.format(vm))
    # Update primary network adapter '0' with new network
    compl_VMs[vm]['adapters']['0']['org_nw'] = new_vdcnet

    # Generate xml body
    xml_body = createbody('templates/nwconnectionsection.j2', compl_VMs[vm])
    # print(xml_body)

    # Let it wait for a few seconds so as not to get script failed
    time.sleep(5)

    # Update current networkCards section with new Org Network
    myvcd.vm_update_nwconnectsection(compl_VMs[vm]['uuid'], xml_body)

cprint('\nTask completed', 'green')
