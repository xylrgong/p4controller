from setting import max_bandwidth
from setting import mac_to_edge
from setting import INF
from topo import load_links_and_ports
from topo import get_all_paths


def alter_path(flow_table):
    bandwidths = []
    chosen_paths = []

    paths, _ = get_all_paths()
    for flow in flow_table:
        bandwidth = flow['bandwidth']
        ingress = mac_to_edge[flow['src']]
        egress = mac_to_edge[flow['dst']]
        flow_paths = paths[(ingress, egress)]
        weights = get_paths_weight(flow_paths, chosen_paths, bandwidths)
        chosen_path = choose_path(weights, bandwidth)
        if chosen_path == -1:
            data = {'status': 'failed'}
            return data
        else:
            chosen_paths.append(flow_paths[chosen_path])
            bandwidths.append(bandwidth)

    return retrieve_paths(flow_table, chosen_paths)


def get_paths_weight(flow_paths, chosen_paths, bandwidths):
    links, _ = load_links_and_ports()
    links_weight = get_init_links_weight(links)

    count = 0
    for path in chosen_paths:
        for node_index in range(len(path[:-1])):
            src = path[node_index]
            dst = path[node_index + 1]
            link_index = get_index_of_link(src, dst, links)
            links_weight[link_index] -= bandwidths[count]
        count += 1

    return get_min_weight_in_path(flow_paths, links, links_weight)


def get_init_links_weight(links):
    return [max_bandwidth for _ in range(len(links))]


def get_index_of_link(src, dst, links):
    index = 0
    for v1, v2 in links:
        if v1 == src and v2 == dst \
                or v2 == src and v1 == dst:
            return index
        else:
            index += 1


def get_min_weight_in_path(paths, links, links_weight):
    path_weight = []

    for path in paths:
        min_weight = INF
        for node_index in range(len(path[:-1])):
            src = path[node_index]
            dst = path[node_index + 1]
            link_index = get_index_of_link(src, dst, links)
            cur_weight = links_weight[link_index]
            if cur_weight < min_weight:
                min_weight = cur_weight
        path_weight.append(min_weight)

    return path_weight


def choose_path(weights, bandwidth):
    indexed_weight = [(index, weight) for index, weight in enumerate(weights)]
    indexed_weight.sort(key=cmp)
    for index, weight in indexed_weight:
        if weight >= bandwidth:
            return index
    return -1


def cmp(elem):
    return elem[1]


def retrieve_paths(flow_table, chosen_paths):
    data = {}
    data['status'] = 'success'
    data.setdefault("items", [])

    flow_count = 0
    for flow in flow_table:
        item = {'src_mac': flow["src"], 'dst_mac': flow["dst"]}
        select_path = chosen_paths[flow_count]
        item['path'] = select_path
        flow_count += 1
        data['items'].append(item)

    else:
        pass

    return data


if __name__ == '__main__':
    # test data
    flow_table = [
        {"src": "01:00:5e:00:00:01",
         "dst": "01:00:5e:00:00:02",
         "bandwidth": 800, "delay": 10},
        {"src": "01:00:5e:00:00:01",
         "dst": "01:00:5e:00:00:03",
         "bandwidth": 80, "delay": 10},

   ]

    """
           {"src": "01:00:5e:00:00:03",
         "dst": "01:00:5e:00:00:02",
         "bandwidth": 300, "delay": 10},
        {"src": "01:00:5e:00:00:02",
         "dst": "01:00:5e:00:00:03",
         "bandwidth": 100, "delay": 10},
        {"src": "01:00:5e:00:00:02",
         "dst": "01:00:5e:00:00:01",
         "bandwidth": 150, "delay": 10},
        {"src": "01:00:5e:00:00:02",
         "dst": "01:00:5e:00:00:03",
         "bandwidth": 2000, "delay": 10},
        {"src": "01:00:5e:00:00:04",
         "dst": "01:00:5e:00:00:01",
         "bandwidth": 50, "delay": 10},
        {"src": "01:00:5e:00:00:04",
         "dst": "01:00:5e:00:00:03",
         "bandwidth": 2000, "delay": 10},

    """
    selected_path = alter_path(flow_table)
    if selected_path:
        print(selected_path)
    else:
        print('failed')

