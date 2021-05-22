from setting import egress_sw1
from setting import egress_sw2


def get_flow_str(flow):
    s = ','.join(map(str, flow))
    return s


def retrieve_paths_and_volume_of_flow(paths, all_paths, all_volumes, all_delay, flow):
    src, dst, vol, delay = parse_flow(flow)
    all_paths[(src, dst)] = paths[(egress_sw1, egress_sw2)]
    all_volumes[(src, dst)] = vol
    all_delay[(src, dst)] = delay


def parse_flow(flow):
    src = flow['src']
    dst = flow['dst']
    bw = flow['bandwidth']
    delay = flow['delay']
    vol = float(bw) * float(delay)
    return src, dst, vol, delay
