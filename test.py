from flow_trans import schedule_flows
from shortest_path import default_strategy
from flow_trans import clean_flow_table as clean_opti_flow_table
from shortest_path import clean_flow_table as clean_default_flow_table

test_flows = [
    {"src": "2c:53:4a:07:b3:6e",
     "dst": "2c:53:4a:07:b3:ad",
     "bandwidth": 400, "delay": 10},
    {"src": "2c:53:4a:07:b3:6c",
     "dst": "2c:53:4a:07:b3:af",
     "bandwidth": 700, "delay": 10},
    {"src": "2c:53:4a:07:b3:ad",
     "dst": "2c:53:4a:07:b3:af",
     "bandwidth": 300, "delay": 10},

]

# 转化策略前需要清空一次
clean_default_flow_table()
clean_opti_flow_table()

for flow in test_flows:
    print('opt:')
    ret = schedule_flows(flow)
    # print(ret)
    print('default:')
    ret = default_strategy(flow)
    # print(ret)
    input()

"""
from flow_trans import schedule_flows
from shortest_path import default_strategy
from flow_trans import clean_flow_table as clean_opti_flow_table
from shortest_path import clean_flow_table as clean_default_flow_table

# 转化策略前需要清空一次（开关打开前，调用默认前）
clean_default_flow_table()
clean_opti_flow_table()

# 带宽优化的策略
ret = schedule_flows(flow)
# 最短路径策略
ret = default_strategy(flow)

"""
