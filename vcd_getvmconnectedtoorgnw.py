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
#inputs = 'inputs/vcd_' + seldc(sys.argv[1:]) + '.yml'

inputs = 'inputs/vcd_lpr.yml'


# Load vCD credentials ------------------------------------------------------------------
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
    org = input("Choose an existing organization: ")
    failure += 1
    if failure > 3:
        print('Too many failures')
        sys.exit(1)



# Choose vDC ----------------------------------------------------------------------------
vdcs = myvcd.getvdcs(orgs[org])
print('\n')
cprint('\nThese are the Virtual Data Centers available in the organization %s' % org, 'yellow')
print(vdcs.keys())




# Choose vApp ---------------------------------------------------------------------------
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
    #VMs.update(myvcd.getvapp_vms(vapps[vapp]))
    vapp_vms = myvcd.getvapp_vms(vapps[vapp])
    for vm in vapp_vms:
        VMs[vm] = {'uuid': vapp_vms[vm], 'vapp': vapp}

    #VMs.update(vapp_vms)
print('\n')
cprint('\nThese are the VMs in the organization %s' % org, 'yellow')
pprint(VMs)



# Get the list of VMs and their IPs -----------------------------------------------------
VMs_w_ip = {}
print('\n')
for vm in VMs:
    VMs_w_ip[vm] = {'uuid': VMs[vm]}
    # print vm
    nwinfo = myvcd.getvapp_vm_networkcards(VMs[vm])
    # print(nwinfo)
    VMs_w_ip[vm].update(nwinfo)


print('\n')
cprint('\nThese are the VMs in the organization %s' % org, 'yellow')
pprint(VMs_w_ip)


# Get the list of Org Vdc Networks ------------------------------------------------------
orgnets = {}
for vdc in vdcs:
    vdcnets = myvcd.getvdcnetworks(vdcs[vdc])
    orgnets.update(vdcnets)
print('\n')
cprint('\nThese are the Org VDC Networks available in the organization %s' % org, 'yellow')
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




