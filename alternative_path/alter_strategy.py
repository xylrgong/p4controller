from setting import max_bandwidth
from setting import INF
from topo import load_links_and_ports


def alter_path(flow_table, paths):
    path_indexes = []
    bandwidths = []

    for flow in flow_table:
        bandwidth = flow['bandwidth']
        weights = get_paths_weight(paths, path_indexes, bandwidths)
        chosen_path = choose_path(weights, bandwidth)
        path_indexes.append(chosen_path)
        bandwidths.append(bandwidth)

    return retrieve_paths(flow_table, paths, path_indexes)


def get_paths_weight(paths, path_indexes, bandwidths):
    links, _ = load_links_and_ports()
    links_weight = get_init_links_weight(links)

    count = 0
    for index in path_indexes:
        path = paths[index]
        for node_index in range(len(path[:-1])):
            src = path[node_index]
            dst = path[node_index + 1]
            link_index = get_index_of_link(src, dst, links)
            links_weight[link_index] -= bandwidths[count]
        count += 1

    return get_min_weight_in_path(paths, links, links_weight)


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


def retrieve_paths(flow_table, paths, path_indexes):
    """
    selected_path = []
    for index in path_indexes:
        if index != -1:
            selected_path.append(paths[index])
        else:
            break
    """

    data = {}
    if path_indexes[-1] == -1:
        data['status'] = 'failed'
    else:
        data['status'] = 'success'

    if data['status'] == 'success':
        data.setdefault("items", [])
        flow_count = 0
        for flow in flow_table:
            item = {}
            item['src_mac'] = flow["src"]
            item['dst_mac'] = flow["dst"]
            select_path = paths[path_indexes[flow_count]]
            item['path'] = select_path
            flow_count += 1
            data['items'].append(item)

    else:
        pass

    return data


if __name__ == '__main__':
    # test data
    flow_table = [
        {"src": "00:00:00:00:00:10",
         "dst": "00:00:00:00:00:20",
         "bandwidth": 400, "delay": 10},
        {"src": "00:00:00:00:00:10",
         "dst": "00:00:00:00:00:30",
         "bandwidth": 350, "delay": 10},
        {"src": "00:00:00:00:00:10",
         "dst": "00:00:00:00:00:40",
         "bandwidth": 300, "delay": 10},
        {"src": "00:00:00:00:00:10",
         "dst": "00:00:00:00:00:50",
         "bandwidth": 50, "delay": 10},

    ]
    """
            
        {"src": "00:00:00:00:00:10",
         "dst": "00:00:00:00:00:60",
         "bandwidth": 300, "delay": 10},
    """
    paths = [
        ['1', '3'],
        ['1', '2', '3'],
        ['1', '4', '5', '6', '7', '8', '3'],
        ['1', '4', '7', '8', '3'],
    ]
    selected_path = alter_path(flow_table, paths)
    if selected_path:
        print(selected_path)
    else:
        print('failed')

