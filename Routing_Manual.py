import networkx as nx
from jnpr.junos.exception import ConnectError
from jnpr.junos.utils.config import Config

#=====================================================================================

def Dijkstra(matrix, start_node, target_node):
    '''
    matrix[i][j] = (local_intf, remote_intf, cost)
    Returns a list of node indices representing the shortest path
    '''
    n = len(matrix)
    distances = {node: float('inf') for node in range(n)}
    prev_nodes = {node: None for node in range(n)}
    distances[start_node] = 0
    unvisited = set(range(n))

    while unvisited:
        curr_node = min(unvisited, key=lambda node:distances[node])
        if distances[curr_node] == float('inf') or curr_node == target_node:
            break
        unvisited.remove(curr_node)

        for neighbor in range(n):
            link = matrix[curr_node][neighbor]
            if link != None:
                cost = link[2]
                new_dist = distances[curr_node] + cost

                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    prev_nodes[neighbor] = curr_node

    path = []
    curr_node = target_node
    while curr_node is not None:
        path.insert(0, curr_node)
        curr_node = prev_nodes[curr_node]

    return path if (path and path[0] == start_node) else [] 


def Next_Hops(matrix, Router_IPs, all_routes):
    '''
    matrix: Adjacency matrix for all the routers w/ (intf, neigh_intf, cost)
    Router_IPs: /30 addresses assigned to interfaces
    all_routes: Dict with cust_routes at each router {r0: [prefixes...]}
    '''
    next_hops = {}
    
    for target_router, prefixes in all_routes.items():
        for prefix in prefixes:
            
            for source_router in range(len(matrix)):
                if source_router ==  target_router:
                    continue

                path = Dijkstra(matrix, source_router, target_router)

                if len(path) > 1:
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