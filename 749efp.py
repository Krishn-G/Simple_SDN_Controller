from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from jnpr.junos.utils.config import Config
d=Device(host='192.168.1.22',user='labuser',password='Labuser')
d2=Device(host='192.168.1.23',user='labuser',password='Labuser')

dlist = [d,d2]

try:
	for dev in dlist:
		dev.open()
		dev.bind(conf=Config)
		#r3 = {'ge-0/0/1': '172.16.1.1/30','ge-0/0/2':'172.16.2.1/30','ge-0/0/3':'172.16.3.1/30'}
		#r3f = {'if_config': r3}
		dev.conf.load(template_path = 'c749lldp.conf',  merge = True)
		dev.conf.commit()
		dev.close
	# to find the xml hierarchy for a show command, run below
	#s= d.display_xml_rpc('show lldp neighbors', format = 'text')	
	# output was <get-lldp-neighbors-information></get-...-information>
	d.open()
	s = d.rpc.get_lldp_neighbors_information()
	# output is an etree
	s2 = d.rpc.get_system_information()
	for e in s:	
		if e.xpath('lldp-local-interface/text()')[0] != 'ge-0/0/0.0':
			lsn = s2.xpath('host-name/text()')[0]
			lif = e.xpath('lldp-local-interface/text()')[0]
			esn = e.xpath('lldp-remote-system-name/text()')[0]
			eif = e.xpath('lldp-remote-port-description/text()')[0]
			s3 = d.rpc.get_interface_information(interface_name=lif,brief = True)
			lsp = s3.xpath('physical-interface/speed')
			print('Local SysName: ', lsn)
			print('Local if: ', lif)
			print('External SysName: ',esn)	
			print('External if: ',eif)
			print('Link Speed: ',lsp)
except ConnectError as err:
	print('\n Error: ' + repr(err))
finally:
	d.close()

