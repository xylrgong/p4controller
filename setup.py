from enum import Enum


class Reverse(Enum):
    t_234 = '0'
    t_324 = '1'
    t_342 = '2'
    t_432 = '3'
    t_423 = '4'


det_switch = False

dict_reverse = {'0': '234', '1': '324', '2': '342', '3': '432', '4': '423'}

dpdk_psw = {'0': ' ',
            '1': '123456',
            '2': '123456',
            '3': '123456',
            '4': '123456',
            '5': '123456',
            '6': '123456',
            '7': '123456',
            }

pkt_reverse_t = Reverse.t_234.value  # default strategy is set to normal

switch_ip_table = {'0': '192.168.123.200',
                   '1': '192.168.123.201',  # switch['1'] = '172.16.0.15'
                   '2': '192.168.123.202',
                   '3': '192.168.123.203',
                   '4': '192.168.123.204',
                   '5': '192.168.123.205',
                   '6': '192.168.123.206',
                   '7': '192.168.123.207',
                   }

                   #  0    1    2    3    4    5    6    7
route_port_table = [['x', '1', '2', 'x', 'x', 'x', 'x', 'x'], # 0
                    ['1', 'x', 'x', 'x', 'x', '2', 'x', 'x'], # 1
                    ['2', 'x', 'x', '1', 'x', 'x', 'x', 'x'], # 2
                    ['x', 'x', '1', 'x', '2', 'x', '3', 'x'], # 3
                    ['x', 'x', 'x', '1', 'x', '2', 'x', 'x'], # 4
                    ['x', '2', 'x', 'x', '1', 'x', 'x', '3'], # 5
                    ['x', 'x', 'x', '1', 'x', 'x', 'x', '2'], # 6
                    ['x', 'x', 'x', 'x', 'x', '1', '2', 'x'], # 7
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

dpdk_work_dir = {'0': '/home/router/Projects/dpdk-21.05/examples/black_switch/',
                 '1': '/home/p4s1/dpdk-21.02/examples/black_switch/',
                 '2': '/home/p4s2/dpdk-21.02/examples/black_switch/',
                 '3': '/home/p4security1/dpdk-21.02/examples/black_switch/',
                 '4': '/home/p4s4/dpdk-21.02/examples/black_switch/',
                 '5': '/home/p4s5/dpdk-21.02/examples/black_switch/',
                 '6': '/home/p4s6/dpdk-21.02/examples/black_switch/',
                 '7': '/home/p4s7/dpdk-21.02/examples/black_switch/',
                 }

local_work_dir = '/home/gs/p4controller/'

dpdk_username = {'0': 'router',
                 '1': 'p4s1',
                 '2': 'p4s2',
                 '3': 'p4security1',
                 '4': 'p4s4',
                 '5': 'p4s5',
                 '6': 'p4s6',
                 '7': 'p4s7',
                 }

dpdk_switch = ['0', '1', '2', '3', '4', '5', '6', '7']
# real_switch = ['1', '2', '3']
# virtual_switch = ['4', '5', '6', '7', '8']
