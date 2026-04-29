from jnpr.junos import Device

cost = 1
d1=Device(host='192.168.1.26',user='labuser',password='Labuser')
d2=Device(host='192.168.1.27',user='labuser',password='Labuser')
dlist = [d1,d2]

#=====================================================================================

def Topology(dlist):
    n_routers= len(dlist)
    matrix = [[None for _ in range(n_routers)] for _ in range(n_routers)]

    id_name = {}
    name_id = {}

    for i, d in enumerate(dlist):
        d.open()
        r_info = d.rpc.get_system_information()
        r_host = r_info.xpath('host-name/text()')[0].strip()
        id_name[i] = r_host
        name_id[r_host] = i
        d.close()
        
    for i in range(n_routers):
        d = dlist[i]
        d.open()
        lldp_info = d.rpc.get_lldp_neighbors_information()

        for neighbor in lldp_info:
            local_if = neighbor.xpath('lldp-local-interface/text()')[0]
            if (local_if.startswith('ge-0/0/0')):
                continue
            
            remot_host = neighbor.xpath('lldp-remote-system-name/text()')[0]
            remot_if = neighbor.xpath('lldp-remote-port-description/text()')[0]

            if (remot_host in name_id):
                j = name_id[remot_host]
                matrix[i][j] = (local_if, remot_if, cost)
    
        d.close()
    
    return matrix


#=====================================================================================

if __name__ == "__main__":
    matrix = Topology(dlist)
    print(matrix)