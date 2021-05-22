from util import link_in_path


def generate_c_coefficient(flow_num, path_num):
    s_coef = [0.0 for _ in range(path_num)]
    f_coef = [1.0 for _ in range(flow_num)]
    coef = s_coef + f_coef
    return coef


def generate_opti_c_coefficient(flow_num):
    s_coef = [0.0 for _ in range(flow_num)]
    f_coef = [1.0 for _ in range(flow_num)]
    coef = s_coef + f_coef
    return coef


def generate_ub_coefficient(all_links, all_paths, all_volumes, flow_num):
    ub_coef = []
    for link in all_links:
        link_coef = []
        for flow, paths in all_paths.items():
            for path in paths:
                if link_in_path(link, path):
                    link_coef.append(float(all_volumes[flow]))
                else:
                    link_coef.append(0.0)
        ub_coef.append(link_coef)
        for i in range(flow_num):
            link_coef.append(0.0)
    return ub_coef


def generate_opti_ub_coefficient(all_links, all_paths, path_index, flow_num):
    ub_coef = []
    for link in all_links:
        link_coef = []
        flow_index = 0
        for flow, paths in all_paths.items():
            flow_coef = []
            for index, path in enumerate(paths):
                if link_in_path(link, path) and index == path_index[flow_index]:
                    flow_coef.append(1.0)
                else:
                    flow_coef.append(0.0)
            link_coef.append(sum(flow_coef))
            flow_index += 1

        ub_coef.append(link_coef)
        for i in range(flow_num):
            link_coef.append(0.0)

    return ub_coef


def generate_eq_coefficient(all_paths, flow_num, path_num):
    step = 0
    flow_count = 0
    eq_coef = []
    for paths in all_paths.values():
        flow_coef = [0.0 for _ in range(path_num + flow_num)]
        flow_paths_num = len(paths)
        for i in range(flow_paths_num):
            flow_coef[i + step] = 1.0
        step += flow_paths_num

        flow_index = - (flow_num - flow_count)
        flow_count += 1
        flow_coef[flow_index] = -1.0

        eq_coef.append(flow_coef)

    return eq_coef


def generate_opti_eq_coefficient(all_volumes, flow_num):
    vol = []
    for value in all_volumes.values():
        vol.append(value)
    eq_coef = []
    for i in range(flow_num):
        flow_coef = [0 for _ in range(2 * flow_num)]
        flow_coef[i] = 1
        flow_coef[i + flow_num] = -1 * vol[i]
        eq_coef.append(flow_coef)
    return eq_coef


def generate_bounds(flow_num, path_num, all_delay):
    bounds = []

    for _ in range(path_num):
        bounds.append((0, None))

    for delay in all_delay.values():
        bounds.append((1.0 / delay, None))

    return bounds


def generate_opti_bounds(flow_num, all_delay):
    bounds = []

    for _ in range(flow_num):
        bounds.append((0, None))
    for delay in all_delay.values():
        bounds.append((1.0 / delay, None))

    return bounds


def get_all_path_num(all_paths):
    all_paths_num = 0
    for value in all_paths.values():
        all_paths_num += len(value)
    return all_paths_num


def get_all_links(all_paths):
    all_links = []
    for paths in all_paths.values():
        for path in paths:
            for i in range(len(path) - 1):
                link = (path[i], path[i + 1])
                reverse_link = (path[i + 1], path[i])
                if link not in all_links and reverse_link not in all_links:
                    all_links.append(link)
    return all_links


def get_flow_path_num(all_paths):
    flow_path_num = []
    for value in all_paths.values():
        flow_path_num.append(len(value))
    return flow_path_num
