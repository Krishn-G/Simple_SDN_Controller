from jnpr.junos import Device
import LLDP_Setup

#=====================================================================================

d1=Device(host='192.168.1.24',user='labuser',password='Labuser')
d2=Device(host='192.168.1.25',user='labuser',password='Labuser')
dlist = [d1,d2]

if_s = ['ge-0/0/1', 'ge-0/0/2', 'ge-0/0/3', 'ge-0/0/4', 'ge-0/0/5']

#=====================================================================================

if __name__ == "__main__":

    LLDP_Setup(dlist, if_s)

