from topo import get_all_paths
from setting import mac_to_edge
from setting import INF
from util import print_log_info

flow_table = []


# 最短路径策略,每条流都会返回最短路径
def default_strategy(flow_data):
    data = {'status': 'success', 'items': []}
    if is_override_flow(flow_data):
        override_table_with_new_flow(flow_data)
    else:
        flow_table.append(flow_data)

    paths, _ = get_all_paths()

    for flow in flow_table:
        item = {'src_mac': flow['src'], 'dst_mac': flow['dst']}
        ingress = mac_to_edge[flow['src']]
        egress = mac_to_edge[flow['dst']]
        flow_paths = paths[(ingress, egress)]
        min_len = INF

        for path in flow_paths:
            if len(path) < min_len:
                min_len = len(path)
                shortest_path = path
        item['path'] = shortest_path
        data['items'].append(item)
    print_log_info(data)
    return data


def is_override_flow(flow_data):
    for flow in flow_table:
        if flow_data['src'] == flow['src'] and flow_data['dst'] == flow['dst']:
            return True
    return False


def override_table_with_new_flow(flow_data):
    override_index = -1
    for index, flow in enumerate(flow_table):
        if flow_data['src'] == flow['src'] and flow_data['dst'] == flow['dst']:
            override_index = index

    flow_table.pop(override_index)
    flow_table.append(flow_data)


def clean_flow_table():
    global flow_table
    flow_table = []
