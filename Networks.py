from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from lxml import etree

d1=Device(host='192.168.1.26',user='labuser',password='Labuser')
d2=Device(host='192.168.1.27',user='labuser',password='Labuser')
d3=Device(host='192.168.1.28',user='labuser',password='Labuser')
dlist = [d1, d2, d3]

#=====================================================================================

def Customer_Routes(dlist):
    """
    Connects to each router and get routes not associated with mgmt/underlay fabric
    """
    ignored_ifs = ['ge-0/0/0', 'ge=0/0/1', 'ge-0/0/2', 'ge-0/0/3', 'ge-0/0/4', 'ge-0/0/5']

    all_routes = {}

    for i, d in enumerate(dlist):
        external_routes = []

        try:
            d.open()
            route_info = d.rpc.get_route_information(table = 'inet.0')
            # routes = etree.tostring(route_info,pretty_print=True,encoding='unicode')
            # print(routes)

            for route in route_info.xpath('.//rt'):
                prefix = route.xpath('rt-destination/text()')[0]
                out_if = route.xpath('.//nh/via/text() | .//nh/nh-local-interface/text()')[0]

                if out_if:
                    if_name = out_if.split('.')[0]

                    if (if_name not in ignored_ifs):
                        external_routes.append(prefix)

            all_routes[i] = list(set(external_routes))
        
        except ConnectError:
            raise ConnectError("Unable to connect to device")
        finally:
            d.close()
    
    return all_routes


#=====================================================================================

if __name__ == "__main__":
    all_routes = Customer_Routes(dlist)
    print(all_routes)