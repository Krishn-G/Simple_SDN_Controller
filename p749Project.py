import heapq, time, math
from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from jnpr.junos.utils.config import Config
from lxml import etree

d=Device(host='192.168.1.22',user='labuser',password='Labuser')
d2=Device(host='192.168.1.23',user='labuser',password='Labuser')
d3=Device(host='192.168.1.24',user='labuser',password='Labuser')
d4=Device(host='192.168.1.25',user='labuser',password='Labuser')

# Variables

dlist = [d,d2,d3,d4]
vt = [[64] * len(dlist) for _ in range(len(dlist))] # Collection of routing vectors
ind_t = [] # list of router names as found at routers
ddlist = {}
if_on = ['ge-0/0/1','ge-0/0/2','ge-0/0/3','ge-0/0/4','ge-0/0/5']
base_address = '172.16.'
sns = '/30' #subnet size

try:
	for dev in dlist:
		dev.open()
		dev.bind(conf=Config)
		dev.conf.load(template_path = '749ifyfwfp.conf', template_vars = {'if_config':if_on},merge = True)
		dev.conf.commit()
		name = dev.rpc.get_system_information() # will make vector of names aligned with dlist
		rname = name.xpath('host-name/text()')[0].replace("'","") # router name
		ind_t.append(rname)
		ddlist[rname] = {'local_addresses':[],'if_config':{},'neighbors':{}}
	time.sleep(3)
	b = 0 # current dev tracker, selects from ind_t current router
	ipt = 0 # ip tracker
	for dev in dlist:
		s = dev.rpc.get_lldp_neighbors_information()
		lsn = ind_t[b]
		for e in s:
			if e.xpath('lldp-local-interface/text()')[0] != 'ge-0/0/0.0':
				lif = e.xpath('lldp-local-interface/text()')[0] # local interface
				esn = e.xpath('lldp-remote-system-name/text()')[0] # external system name
				eif = e.xpath('lldp-remote-port-description/text()')[0] # external interface
				s3 = d.rpc.get_interface_information(interface_name=lif,brief = True) # rpc response 3
				lsp = s3.xpath('physical-interface/speed')
				c = 0
				for ent in ind_t:
					if esn == ent:
						break
					else:
						c += 1
				if b < c:
					al = base_address + str(math.floor(ipt/256) + 1) + "." + str((ipt + 1)%256) + sns
					ae = base_address + str(math.floor(ipt/256) + 1) + "." + str((ipt + 2)%256) + sns
					ddlist[lsn]['if_config'][lif] = al
					ddlist[esn]['if_config'][eif] = ae
					ddlist[lsn]['neighbors'][esn] = ae
					ipt += 4
				else:
					ddlist[lsn]['neighbors'][esn] = ddlist[esn]['if_config'][eif]	
				print('Local SysName: ', lsn)
				print('Local if: ', lif)
				print('External SysName: ',esn)
				print('External if: ',eif)
				print('Link Speed: ',lsp)
				vt[b][c] = 1
			print('\n')
		b += 1
except ConnectError as err:
	print('\n Error: ' + repr(err))
finally:
	for dev in dlist:
		dev.close()

print('ind_t: ',ind_t)
print('VT: ')
for i in range(len(vt)):
	print(ind_t[i],vt[i])
for k,v in ddlist.items():
	print(k,v)
