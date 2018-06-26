#! /usr/bin/env python

"""
=================================================================================================================
   Author:          Petr Nemec
   Description:     To switchover ORG Networks.
                    VMs to be switched over are read from the input/vm.yaml
                    VMs are switched over in a loop. Task status is checked regularly each 200ms.
                    IP addresses are changed to <IpAddressAllocationMode>MANUAL</IpAddressAllocationMode>
                    There's one limitation - the network card being switched must be the primary one

                    Python 2.7

   Date:            2018-06-26
=================================================================================================================
"""

from vcd import vCD
from vcd import createbody
from vcd import credentials
from vcd import seldc
import sys
import yaml

from termcolor import cprint
from prettytable import PrettyTable

import time
import pyprind


# Select the vCD to be modified
inputs = 'inputs/vcd_' + seldc(sys.argv[1:]) + '.yml'


# Load vCD credentials ------------------------------------------------------------------
cred = credentials(inputs)

myvcd = vCD(*cred)
myvcd.gettoken()


# Choose organization -------------------------------------------------------------------
orgs = myvcd.getorgs()
cprint('\nThe Organizations available in the vDC', 'yellow')
# pprint(orgs.keys())
orgs_output = PrettyTable(['Organization'])
for org in orgs.keys():
    orgs_output.add_row([org])
print(orgs_output)


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

vdc_output = PrettyTable(['Organization VDC'])
for vdc in vdcs.keys():
    vdc_output.add_row([vdc])
print(vdc_output)


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


# Load VMs from a yaml file -------------------------------------------------------------
with open('inputs/vm.yml', 'r') as infile:
    compl_VMs = yaml.load(infile)


cprint('\nThese are the VMs to be updated with new Org VDC Network', 'yellow')
vm_output = PrettyTable(['VM name', 'adapter', 'IP address', 'MAC address', 'network', 'primary'])
for vm in compl_VMs:
    for adapter in compl_VMs[vm]['adapters'].keys():
        vm_output.add_row([vm,
                           adapter,
                           compl_VMs[vm]['adapters'][adapter]['ip_addr'],
                           compl_VMs[vm]['adapters'][adapter]['mac'],
                           compl_VMs[vm]['adapters'][adapter]['org_nw'],
                           compl_VMs[vm]['adapters'][adapter]['primary_nw']])
print(vm_output)


# Review the VMs connected to the switched network work card ----------------------------
agree = raw_input("Do you want to continue? y/n[N]: " or 'N')

# Proceed with updating configuration
if agree != "Y" and agree != "y":
    print("Script execution canceled")
    sys.exit(1)


# Switch VM's network card --------------------------------------------------------------

# Proceed with updating configuration
if agree != "Y" and agree != "y":
    print("Script execution canceled")
    sys.exit(1)
else:
    n = len(compl_VMs.keys())
    bar = pyprind.ProgBar(n, monitor=True, bar_char='#')
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
        cprint('\nUpdating the VM {0} {1}'.format(vm, compl_VMs[vm]['adapters']['0']['ip_addr']), 'yellow')
        # Update primary network adapter '0' with new network
        compl_VMs[vm]['adapters']['0']['org_nw'] = new_vdcnet

        # Generate xml body
        xml_body = createbody('templates/nwconnectionsection.j2', compl_VMs[vm])
        print(xml_body)

        bar.update()
        # Update current networkCards section with new Org Network
        task_href = myvcd.vm_update_nwconnectsection(compl_VMs[vm]['uuid'], xml_body)

        i = 0
        while myvcd.get_task_status(task_href) != 'success':
            time.sleep(0.2)
            i += 1
            print(i)
            if i > 50:
                break

    # Print the statistics how long the iteration took
    print(bar)

    # Print the list of VMs and their IP addresses --------------------------------------------
    cprint('\nIdentifying the IP addresses after the switchover', 'yellow')
    VMs_w_ip_afterswithover = {}
    VM_output = PrettyTable(['VM name', 'old IP', 'old network', 'new IP', 'new network'])
    for vm in compl_VMs:
        VMs_w_ip_afterswithover[vm] = {'uuid': compl_VMs[vm]['uuid']}
        nwinfo = myvcd.getvapp_vm_networkcards(compl_VMs[vm]['uuid'])
        VMs_w_ip_afterswithover[vm].update(nwinfo)
        VM_output.add_row([vm,
                           compl_VMs[vm]['adapters']['0']['ip_addr'],
                           old_vdcnet,
                           VMs_w_ip_afterswithover[vm]['adapters']['0']['ip_addr'],
                           VMs_w_ip_afterswithover[vm]['adapters']['0']['org_nw']])
    cprint('Detailed network information after switchower', 'yellow')
    print(VM_output)

    cprint('\nTask completed', 'green')