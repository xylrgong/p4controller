from enum import Enum


class Reverse(Enum):
    t_234 = '0'
    t_324 = '1'
    t_342 = '2'


dict_reverse = {'0': '234', '1': '324', '2': '342'}


pkt_reverse_t = Reverse.t_234.value  # default strategy is set to normal

switch_ip_table = {'1': '172.16.0.15',  # switch['1'] = '172.16.0.15'
                   '2': '172.16.0.25',
                   '3': '172.16.0.35',
                   '4': '192.168.123.14',
                   '5': '192.168.123.15',
                   '6': '192.168.123.16',
                   '7': '192.168.123.17',
                   '8': '192.168.123.18',
                   }

                   #  1    2    3    4    5    6    7    8
route_port_table = [['x', '1', '2', '3', 'x', 'x', 'x', 'x'], # 1
                    ['0', 'x', '1', 'x', 'x', 'x', 'x', 'x'], # 2
                    ['2', '1', 'x', 'x', 'x', 'x', 'x', '3'], # 3
                    ['0', 'x', 'x', 'x', '1', 'x', '2', 'x'], # 4
                    ['x', 'x', 'x', '0', 'x', '1', 'x', 'x'], # 5
                    ['x', 'x', 'x', 'x', '1', 'x', '0', 'x'], # 6
                    ['x', 'x', 'x', '0', 'x', '1', 'x', '2'], # 7
                    ['x', 'x', '1', 'x', 'x', 'x', '0', 'x'], # 8
                    ]

#route_port_table = [['x', '1', '2', '3', 'x', 'x', 'x', 'x'], # 1
#                    ['0', 'x', '1', 'x', 'x', 'x', 'x', 'x'], # 2
#                    ['2', '1', 'x', 'x', 'x', 'x', 'x', '3'], # 3
#                    ['0', 'x', 'x', 'x', '1', 'x', '2', 'x'], # 4
#                    ['x', 'x', 'x', '0', 'x', '1', 'x', 'x'], # 5
#                    ['x', 'x', 'x', 'x', '1', 'x', '0', 'x'], # 6
#                    ['x', 'x', 'x', '0', 'x', '1', 'x', '2'], # 7
#                    ['x', 'x', '1', 'x', 'x', 'x', '0', 'x'], # 8
#                    ]

dpdk_work_dir = {'1' : '/home/p4security1/dpdk-21.02/examples/pipeline/examples/',
                 '2' : '/home/p4s2/dpdk-21.02/examples/pipeline/examples/',
                 '3' : '/home/p4s3/dpdk-21.02/examples/pipeline/examples/',
                 '4' : '/home/pc-1/dpdk-21.02/examples/pipeline/examples/',
                 '5' : '/home/pc-1/dpdk-21.02/examples/pipeline/examples/',
                 '6' : '/home/pc-1/dpdk-21.02/examples/pipeline/examples/',
                 '7' : '/home/pc-1/dpdk-21.02/examples/pipeline/examples/',
                 '8' : '/home/pc-1/dpdk-21.02/examples/pipeline/examples/',
                 }

local_work_dir = '/home/gs/p4controller/'

dpdk_username = {'1': 'p4security1',
                 '2': 'p4s2',
                 '3': 'p4s3',
                 '4': 'pc-1',
                 '5': 'pc-1',
                 '6': 'pc-1',
                 '7': 'pc-1',
                 '8': 'pc-1',
                 }

dpdk_switch = ['1', '2', '3']
# real_switch = ['1', '2', '3']
# virtual_switch = ['4', '5', '6', '7', '8']
