import numpy as np
from scipy.optimize import linprog
from coef import generate_c_coefficient
from coef import generate_ub_coefficient
from coef import generate_eq_coefficient
from coef import generate_opti_c_coefficient
from coef import generate_opti_ub_coefficient
from coef import generate_opti_eq_coefficient
from coef import generate_opti_bounds
from coef import generate_bounds
from coef import get_all_path_num
from coef import get_all_links
from coef import get_flow_path_num
from topo import get_all_paths
from topo import generate_ports
from setting import max_bandwidth
from util import *


flow_table = []


# main function
def schedule_flows(flow_data):
    flow_table.append(flow_data)
    data = allocate_paths_and_bandwidth()
    print(data)
    return data


def allocate_paths_and_bandwidth():
    avail_paths, ports = get_all_paths()

    all_paths = {}
    all_volumes = {}
    all_delay = {}
    for flow in flow_table:
        retrieve_paths_and_volume_of_flow(avail_paths, all_paths, all_volumes, all_delay, flow)

    data = resource_utilization_optimize(all_paths, all_volumes, all_delay, ports)
    return data


def resource_utilization_optimize(all_paths, all_volumes, all_delay, ports):
    # implementation of optimize algorithm
    flow_num = len(all_paths)
    path_num = get_all_path_num(all_paths)
    path_flow_num = get_flow_path_num(all_paths)
    all_links = get_all_links(all_paths)

    result = continuous_model_optimize(flow_num, path_num, all_links, all_paths, all_volumes, all_delay)

    if result.success:
        path_indexs = choose_path(result.x, flow_num, path_flow_num)
        ret = allocate_bandwidth(all_volumes, all_links, all_paths, path_indexs, flow_num, all_delay)

    status = "failed"
    if result.success and ret.success:
        status = "success"

    data = {}
    flow_count = 0
    data['status'] = status
    if status == 'success':
        data.setdefault("items", [])
        for flow, path in all_paths.items():
            item = {}
            item['src_mac'] = flow[0]
            item['dst_mac'] = flow[1]
            select_path = path[path_indexs[flow_count]]
            item['path'] = select_path
            item['ports'] = generate_ports(select_path, ports)
            flow_count += 1
            data['items'].append(item)
    return data


def continuous_model_optimize(flow_num, path_num, all_links, all_paths, all_volumes, all_delay):
    c_coef = generate_c_coefficient(flow_num, path_num)
    c = np.array(c_coef)

    ub_coef = generate_ub_coefficient(all_links, all_paths, all_volumes, flow_num)
    A_ub = np.array(ub_coef)  # <=
    b_ub = np.array([float(max_bandwidth) for _ in range(len(all_links))])

    eq_coef = generate_eq_coefficient(all_paths, flow_num, path_num)
    A_eq = np.array(eq_coef)  # ==
    b_eq = np.array([0.0 for _ in range(flow_num)])

    bounds = generate_bounds(flow_num, path_num, all_delay)  # range for every variable
    result = linprog(-c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                     bounds=bounds)
    return result


def choose_path(result_x, flow_num, flow_path_num):
    cursor = 0
    path_indexs = []
    for flow_index in range(flow_num):
        max_num = 0.0
        path_indexs.append(0)
        for path_index in range(flow_path_num[flow_index]):
            x = result_x[cursor] / float(result_x[- (flow_num - flow_index)])
            if x > max_num:
                max_num = x
                path_indexs[flow_index] = path_index
            cursor += 1
    return path_indexs


def allocate_bandwidth(all_volumes, all_links, all_paths, path_indexs, flow_num, all_delay):
    coef = generate_opti_c_coefficient(flow_num)
    c = np.array(coef)

    ub_coef = generate_opti_ub_coefficient(all_links, all_paths, path_indexs, flow_num)
    A_ub = np.array(ub_coef)  # <=
    b_ub = np.array([float(max_bandwidth) for _ in range(len(all_links))])

    eq_coef = generate_opti_eq_coefficient(all_volumes, flow_num)
    A_eq = np.array(eq_coef)  # ==
    b_eq = np.array([0.0 for _ in range(flow_num)])

    bounds = generate_opti_bounds(flow_num, all_delay)
    result = linprog(-c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds)

    return result



