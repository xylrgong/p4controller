from setting import egress_sw1
from setting import egress_sw2
from setting import mac_to_edge
import operator


def get_flow_str(flow):
    s = ','.join(map(str, flow))
    return s


def retrieve_paths_and_volume_of_flow(paths, all_paths, all_volumes, all_delay, all_bandwidth, flow):
    src, dst, vol, delay, bw = parse_flow(flow)
    ingress = look_up_edge(src)
    egress = look_up_edge(dst)
    all_paths[(src, dst)] = paths[(ingress, egress)]
    all_volumes[(src, dst)] = vol
    all_delay[(src, dst)] = delay
    all_bandwidth[(src, dst)] = bw


def parse_flow(flow):
    src = flow['src']
    dst = flow['dst']
    bw = flow['bandwidth']
    delay = flow['delay']
    vol = float(bw) * float(delay)
    return src, dst, vol, delay, bw


def look_up_edge(mac):
    if mac not in mac_to_edge.keys():
        print('no mac info')
    else:
        return mac_to_edge[mac]


def link_in_path(link, path):
    for i in range(len(path) - 1):
        cur_link = (path[i], path[i + 1])
        cur_reverse_link = (path[i + 1], path[i])
        if operator.eq(cur_link, link) or operator.eq(cur_reverse_link, link):
            return True
    return False


def print_log_info(data):
    # log info
    print(data['status'])
    if data['status'] == 'success':
        for item in data['items']:
            print(item)
        print('*' * 140 + '\n')

