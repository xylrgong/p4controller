from consistent_update.consistent_update import get_moved_flow


def get_submit_order(all_bandwidth, max_bandwidth, last_paths, new_paths):
    last_indexed_paths = {}
    new_indexed_paths = {}
    bandwidths = []
    for bandwidth in all_bandwidth.values():
        bandwidths.append(bandwidth)
    for i in range(len(last_paths)):
        last_indexed_paths[i] = last_paths[i]
        new_indexed_paths[i] = new_paths[i]
    flow_order, flow_handled = get_moved_flow(bandwidths, max_bandwidth, last_indexed_paths,
                                              new_indexed_paths)
    return flow_order, flow_handled
