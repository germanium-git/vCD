"""
===================================================================================================
   Author:         Petr Nemec
   Description:    NSX Class definition
   Date:           2017-10-04
===================================================================================================
"""

import requests
from pprint import pprint
from jinja2 import Template
import yaml
import getpass
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import xml.etree.ElementTree as ET
import xmltodict
import re

import sys
import getopt

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from os import listdir
from os.path import isfile, join


# Specify the inventory folder
mypath = 'inputs'

def getiventories(mypath):
    """
    :param argv: Path to inventory files
    :return:     list of inventories
    """

    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    inv_list = []
    for file in onlyfiles:
        inv_list.append(file.split('_')[-1][:-4])
    return inv_list


def seldc(argv):
    """
    :param argv: Command line argumets
    :return:     Name of the inventory file
    """
    inp = ''
    try:
        opts, args = getopt.getopt(argv,"hi:")
    except getopt.GetoptError:
        print 'Use this script with the parameter e.g.:'
        print 'python <script>.py -i <DC>'
        print 'python <script>.py -h for more information'
        sys.exit()
    for opt, arg in opts:
        if opt == '-h':
            print 'Use this script with inventory parameter'
            print(' -i myvmware - for MyVMware lab ')
            sys.exit()
        elif opt in ("-i"):
            if arg in getiventories(mypath):
                inp = arg
            else:
                print('Invalid argument')
                print('Only these inventories are valid: ', getiventories(mypath))
                sys.exit()
    if not(opts):
        print 'Use this script with the parameter e.g.:'
        print 'python <script>.py -i <DC>'
        print 'python <script>.py -h for more information'
        sys.exit()
    return inp


def credentials(inputfile):
    """
    :param:	    path to an inventory file
    :return:    tuple with (ip, account, password)
    """
    # Import credentials from YAML file
    with open(inputfile, 'r') as f:
        s = f.read()

    # Read the directory of credentials from file
    vcd_cred = yaml.load(s)

    vcd_ip = raw_input("vCD IP [%s]: " % vcd_cred['vcd_ip']) or vcd_cred['vcd_ip']
    account = raw_input("Account [%s]: " % vcd_cred['account']) or vcd_cred['account']
    if 'passw' in vcd_cred:
        passw = getpass.getpass(prompt='Use the stored password or enter new one: ', stream=None) or vcd_cred['passw']
    else:
        passw = 'None'
        while passw == 'None' or passw == '':
            passw = getpass.getpass(prompt='Password: ', stream=None)

    return vcd_ip, account, passw



def createbody(template, vars):
    """
    :param:	    path to a Jinja2 template file and directory of variables
    :return:    The output rendered from the template
    """
    # CREATE Body with Jinja2 template
    with open(template) as f:
        s = f.read()
    template = Template(s)

    # Define XML Body - Global Routing > router ID
    xml_body = template.render(vars)

    return xml_body



class vCD:

    def __init__(self, vcd_ip, login, pswd):
        self.vcd_ip = vcd_ip
        self.login = login
        self.pswd = pswd
        self.headers = {'Content-Type': 'application/vnd.vmware.vcloud.orgVdcNetwork+xml',
                        'Accept': "application/*;version=9.0",
                        'x-vcloud-authorization': 'None'}


    def gettoken(self):
        """
        :param:
        :return:    token
        """
        print('Updating authentication token -----------')
        try:
            r = requests.post('https://' + self.vcd_ip + '/api/sessions', auth=(self.login, self.pswd),
                             verify=False, headers=self.headers)

            pprint(r)

            token = r.headers['x-vcloud-authorization']
            self.headers.update({'x-vcloud-authorization': token})

        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))



    def getextnetworks(self):
        """
        :param:
        :return:
        """
        extnets = {}
        print('Retrieving the list of external networks -----------')
        try:
            extnw_list = requests.get('https://' + self.vcd_ip + '/api/admin/extension/externalNetworkReferences',
                             verify=False, headers=self.headers)

            root = ET.fromstring(extnw_list.text)
            for child in root:
                #print (child.tag, child.attrib)
                if re.search('ExternalNetworkReference', child.tag):
                    #print('\n')
                    #print edgeGateway name
                    extnets[child.attrib['name']] = child.attrib['href'].split('/')[-1]


        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))

        return extnets


    def getedges(self):
        """
        :param:
        :return:    directory of edges
        """
        print('Retrieving the list of edges -----------')
        edges = {}
        try:
            edge_list = requests.get('https://' + self.vcd_ip + '/api/query?type=edgeGateway&format=records',
                             verify=False, headers=self.headers)

            root = ET.fromstring(edge_list.text)
            for child in root:
                #print (child.tag, child.attrib)
                if re.search('EdgeGatewayRecord', child.tag):
                    #print('\n')
                    edges[child.attrib['name']] = {'vdc': child.attrib['vdc'].split('/')[-1],
                                                   'uuid': child.attrib['href'].split('/')[-1]}
                    # print vDC
                    #print child.attrib['vdc'].split('/')[-1]
                    # print edgeGateway href
                    #print child.attrib['href'].split('/')[-1]


        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))

        return edges


    def getorgs(self):
        """
        :param:
        :return:    organisations
        """
        orgs = {}
        try:
            org_list = requests.get('https://' + self.vcd_ip + '/api/org',
                             verify=False, headers=self.headers)

            root = ET.fromstring(org_list.text)
            for child in root:
                #print (child.tag, child.attrib)
                if re.search('Org', child.tag):
                    #print('\n')
                    #print child.attrib['name']
                    orgs[child.attrib['href'].split('/')[-1]] = child.attrib['name']


        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))

        return orgs


    def getvdcs(self, org):
        """
        :param:
        :return:    vDCs
        """
        vdcs = {}

        try:
            orgcontent = requests.get('https://' + self.vcd_ip + '/api/org/' + org,
                             verify=False, headers=self.headers)

            print(org + ' ----------------------------------------')
            #pprint(orgcontent.text)
            root = ET.fromstring(orgcontent.text.encode('utf-8'))

            for child in root:
                #print (child.tag, child.attrib)
                #print (child.tag)

                if re.search('Link', child.tag):
                    #print('\n')
                    if re.search('/api/vdc/', child.attrib['href']):
                        vdcs[child.attrib['name']] = child.attrib['href'].split('/')[-1]


        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))

        return vdcs


    def getvdcnetworks(self, vdc):
        """
        :param:
        :return:    vdc networks
        """
        vdcnetworks = {}
        try:
            vdc_list = requests.get('https://' + self.vcd_ip + '/api/admin/vdc/' + vdc + '/networks',
                             verify=False, headers=self.headers)

            root = ET.fromstring(vdc_list.text)
            for child in root:
                #print (child.tag, child.attrib)
                if re.search('OrgVdcNetworkRecord', child.tag):
                    #print('\n')
                    vdcnetworks[child.attrib['name']] = {'edge': child.attrib['connectedTo'],
                                                         'netmask': child.attrib['netmask'],
                                                         'gateway': child.attrib['defaultGateway'],
                                                         'uuid': child.attrib['href'].split('/')[-1], 'vdc': vdc}


        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))

        return vdcnetworks



    def getvcenter(self):
        """
        :param:
        :return:    vcenter uuid
        """
        vcenter = {}
        try:
            vimServerReferences = requests.get('https://' + self.vcd_ip + '/api/admin/extension/vimServerReferences',
                             verify=False, headers=self.headers)

            root = ET.fromstring(vimServerReferences.text)
            for child in root:
                #print (child.tag, child.attrib)
                if re.search('VimServerReference', child.tag):
                    if re.search('api/admin/extension/vimServer/', child.attrib['href']):
                        vcenter['VimServerReference'] = child.attrib['href'].split('/')[-1]
                        vcenter['name'] = child.attrib['name']


        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))

        return vcenter


    def getportgroups(self, VimServerReference):
        """
        :param:
        :return:    vdc networks
        """
        pgroups = {}
        try:
            networks = requests.get('https://' + self.vcd_ip + '/api/admin/extension/vimServer/'
                                    + VimServerReference + '/networks', verify=False, headers=self.headers)


            netw_dir = xmltodict.parse(networks.text)
            #print(netw_dir)


        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))

        return netw_dir



    def create_extnetwork(self, vdc, cfg):
        """
        :param:     xml body & vDC
        :return:
        """
        self.headers.update({'Content-Type': 'application/vnd.vmware.vcloud.orgVdcNetwork+xml'})

        try:
            r = requests.post('https://' + self.vcd_ip + 'api/admin/vdc/' + vdc + '/networks', data=cfg,
                             verify=False, headers=self.headers)

            print(r)

        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))




