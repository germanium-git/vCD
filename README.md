**vCD**
--------

There're some Python scripts simplifying the operations tasks on VMware vCloud Director.
* Create an external network
* Create Edge
* Create VDC Network


### Dependencies
These are the python modules needed to run the scrips. Install those by using pip
* jinja2
* yaml
* reqests
* termcolor


### How to use this project
##### Inventory files
All scripts in this repository are ready-to-use. All input parameters including the credentials to authenticate with vCD are specified by *.yaml files stored in the input folder. The password is stored there as an optional parameter which can be omitted. The password can always be passed as the input parameter at the beginning of script execution.
Update the variables in the file inputs/vcd_mylab.yml and rename it to some other name consisting of two parts such as all files defining variables inputs/\*_mylab.yml.
Note the "mylab" part between underscore and .yml will be used as the argument for specifying the NSX manager. There's the argument -i put when script is being executed. In case of using for instance *_mylab.yml convention the scrips will be executed with -i mylab parameter.

##### vcd_getedges.py

```sh
$ ./vcd_getedges.py -i mylab
```

It provides an information about the edges configured in vCD.

##### vcd_getextnetworks.py

```sh
$ ./cd_getextnetworks.py -i myvmware
```
It provides an information about all external networks configured in vCD.

##### vcd_getvdcnetworks.py

```sh.
$ ./vcd_getvdcnetworks.py -i myvmware
```
It provides an information about all vDC networks from all organizations configured in vCD.

##### vcd_getvimServer.py

```sh.
$ ./vcd_getvimServer.py -i myvmware
```
This is an auxiliary script to get vimServer id by which the vCenter is referenced to. This information is needed to carry out other REST API calls.

##### vcd_cfgedge.py

```sh.
$ ./vcd_cfgedge.py -i myvmware
```
It will deploy new edge based on the information stored in inputs/edge_mylab.yml. The organization, vDC and the external network are chosen within the input dialog.


##### vcd_cfgextnetwork.py

```sh.
$ ./vcd_cfgextnetwork.py -i myvmware
```
It will deploy new external network on the information stored in inputs/extnet_mylab.yml. The ID of the distributed port group the external network will reference to must be known before executing the script.
The dvportgroup-id may be identified by using the scripts from https://github.com/germanium-git/pyVMware


##### vcd_cfgvdcnetwork.py

```sh.
$ ./vcd_cfgvdcnetwork.py -i myvmware
```
It will deploy new vDC network as a routed network connected to an existing edge. The parameters are stored in inputs/vdcnet_mylab.yml.
The organization, vDC and the edge are chosen within the input dialog.







