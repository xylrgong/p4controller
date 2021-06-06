import time
import p4_controller_test


def mac_form_handler(macAddr):  # transfer mac form from '00:00:00:00:00:10' to '0x000000000010'
    return '0x' + macAddr.replace(':', '')


now = int(time.time())
timearray = time.localtime(now)
print(now)
print(timearray)
flow = {'status': 'success', 'items': [{'src_mac': 'a0:36:9f:a9:5b:6f', 'dst_mac': '08:00:27:87:aa:b8', 'path': ['1',  '3'], 'ports': ['-1', '5', '6', '7', '8', '-1']}]}
status = flow['status']
if status == 'failed':
    print('Route update failed')
elif status == 'success':
    route_and_path = flow['items'][-1]  # a dict contains 'src_mac', 'dst_mac' and 'path'
    dst_mac_write_dpdk = mac_form_handler(route_and_path['dst_mac'])  # get dst MAC as '0xaabbccddeeff'
    src_mac_write_dpdk = mac_form_handler(route_and_path['src_mac'])
    f1 = open('mac_table.txt', 'w')
    f1.write('match ' + dst_mac_write_dpdk + ' ' + 'order 234 port H(0)\n')
    f1.write('match ' + src_mac_write_dpdk + ' ' + 'order 234 port H(1)\n')
    f1.close()