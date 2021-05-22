from flow_trans import schedule_flows

test_flows = [
    {"src": "00:00:00:00:00:10",
     "dst": "00:00:00:00:00:20",
     "bandwidth": 75000, "delay": 10},
    {"src": "00:00:00:00:00:10",
     "dst": "00:00:00:00:00:30",
     "bandwidth": 50000, "delay": 10},
    {"src": "00:00:00:00:00:10",
     "dst": "00:00:00:00:00:40",
     "bandwidth": 9500, "delay": 10},
    {"src": "00:00:00:00:00:10",
     "dst": "00:00:00:00:00:50",
     "bandwidth": 9000, "delay": 10},
    {"src": "00:00:00:00:00:10",
     "dst": "00:00:00:00:00:60",
     "bandwidth": 9000, "delay": 10},
    {"src": "00:00:00:00:00:10",
     "dst": "00:00:00:00:00:70",
     "bandwidth": 2000, "delay": 10},
    {"src": "00:00:00:00:00:10",
     "dst": "00:00:00:00:00:80",
     "bandwidth": 2000, "delay": 10},
]

for flow in test_flows:
    ret = schedule_flows(flow)
    input()
