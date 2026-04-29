import ipaddress
import pprint
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectError

#=====================================================================================

def Define_IP(matrix, base_subnet = "172.16.1.0/24"):
    subnets = list(ipaddress.ip_network(base_subnet).subnets(new_prefix=30))        #Creates /30 subnets from the /24

    Router_IPs = {}                                                                 #Dictionary to store router IP addresses
    
    subnet_id = 0
    n_routers = len(matrix)

    for i in range(n_routers):                                                      #Iterating only through upper triangle to avoid double links
        for j in range(i+1, n_routers):
            link = matrix[i][j]

            if link != None:
                if (subnet_id >= len(subnets)):
                    raise ValueError("Not enough subnets to assign IP addresses to all routers")
            
                sub = subnets[subnet_id]
                hosts = list(sub.hosts())

                rx_int = link[0]
                rx_ip = f"{hosts[0]}/30"
                ry_int = link[1]
                ry_ip = f"{hosts[1]}/30"

                for r_id, r_int, r_ip in [(i, rx_int, rx_ip), (j, ry_int, ry_ip)]:
                    if r_id not in Router_IPs:
                        Router_IPs[r_id] = {}
                    Router_IPs[r_id][r_int] = r_ip
                
                subnet_id += 1
    
    return Router_IPs

def Assign_IP(Router_IPs, dlist):
    for r_id, r_ints in Router_IPs.items():
        if r_id > len(dlist):
            raise ValueError("Not enough devices to assign IP addresses to all routers")
        
        d = dlist[r_id]
        try:
            d.open()
            d.bind(conf=Config)
            d.conf.load(template_path = 'Config_Files/IP_Assignment.conf', template_vars = {'r_ints': r_ints},  merge = True)
            d.conf.commit()
            d.close()
        
        except ConnectError:
            raise ConnectError("Unable to connect to device")
        finally:
            d.close()


#=====================================================================================

if __name__ == "__main__":
    example_matrix = [[None for _ in range(3)] for _ in range(3)]
    example_matrix[0][1] = ("ge-0/0/0", "ge-0/0/0", 10) # Link R0-R1
    example_matrix[1][2] = ("ge-0/0/1", "ge-0/0/0", 15) # Link R1-R2
    configs = Define_IP(example_matrix)
    pprint.pprint(configs)