import networkx as nx

#=====================================================================================

def Next_Hops(matrix, Router_IPs, all_routes):
    '''
    matrix: Adjacency matrix for all the routers w/ (intf, neigh_intf, cost)
    Router_IPs: /30 addresses assigned to interfaces
    all_routes: Dict with cust_routes at each router {r0: [prefixes...]}
    '''
    G = nx.graph()
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if matrix[i][j] != None:
                G.add_edge(i, j, weight = matrix[i][j][2])
    
    next_hops = {}
    for target_router, prefixes in all_routes.items():
        for prefix in prefixes:
            
            for source_router in range(len(matrix)):
                if source_router ==  target_router:
                    continue

                path = nx.shortest_path(G, source = source_router, target = target_router, weight = 'weight')
                next_node = path[1]

                next_hop_if = matrix[next_node][source_router][0]
                next_hop_ip = Router_IPs[next_node][next_hop_if].split('/')[0]

                if source_router not in next_hops:
                    next_hops[source_router] = {}
                next_hops[source_router][prefix] = next_hop_ip 

    return next_hops

def Deploy_Routes(next_hop, dlist):
    for r_id, routes in next_hop.items():
        d = dlist[r_id]
        try:
            d.open()
            d.bind(conf=Config)
            d.conf.load(template_path = "Config_Files/Static_Routing.conf", template_vars = {'routes': routes}, merge = True)
            d.conf.commit()
            d.close()

        except ConnectError:
            raise ConnectError("Unable to connect to device")
        finally:
            d.close()


#=====================================================================================

if __name__ == '__main__':
    Next_Hops()