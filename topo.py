import networkx as nx
from setting import in_port1
from setting import in_port2
from setting import egress_sw1
from setting import egress_sw2


def get_all_paths():
    nodes = load_nodes()
    links, ports = load_links_and_ports()
    G = create_graph(nodes, links)
    paths = retrieve_paths(nodes, G)
    return paths, ports


def load_nodes():
    nodes = []
    with open('.nodes', 'r') as fp:
        lines = fp.read().splitlines()
        for line in lines:
            if line:
                nodes.append(line)
    return nodes


def load_links_and_ports():
    links = []
    ports = {}
    with open('.links', 'r') as fp:
        lines = fp.read().splitlines()
        for line in lines:
            if line:
                line_list = line.split(' ')
                link = (line_list[0], line_list[1])
                reverse_link = (line_list[1], line_list[0])
                links.append(link)
                ports[link] = (line_list[2], line_list[3])
                ports[reverse_link] = (line_list[3], line_list[2])

    return links, ports


def create_graph(nodes, links):
    G = nx.Graph()
    G.add_nodes_from(nodes)
    for link in links:
        src = link[0]
        dst = link[1]
        G.add_edge(src, dst)
    return G


def retrieve_paths(nodes, G):
    paths = {}
    for src in nodes:
        for dst in nodes:
            if src != dst:
                all_paths = nx.all_simple_paths(G, src, dst)
                paths[(src, dst)] = []
                for path in all_paths:
                    paths[(src, dst)].append(path)
    return paths


def generate_ports(path, ports):
    ports_list = []
    ports_list.append(in_port1)
    for i in range(len(path) - 1):
        ports_pair = ports[(path[i], path[i + 1])]
        ports_list.append(ports_pair[0])
        ports_list.append(ports_pair[1])
    ports_list.append(in_port2)
    return ports_list


def get_all_egress_paths():
    paths, _ = get_all_paths()
    return paths[(egress_sw1, egress_sw2)]
