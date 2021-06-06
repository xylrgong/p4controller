import time
from logger import *
import p4_controller_test


def mac_form_handler(macAddr):  # transfer mac form from '00:00:00:00:00:10' to '0x000000000010'
    return '0x' + macAddr.replace(':', '')


if __name__ == '__main__':
    log = Logger('all.log', level='debug')
    t1 = int(time.time())
    timearray = time.localtime(t1)
    print('time1:', t1)
    print(timearray)
    flow = {'status': 'success', 'items': [
        {'src_mac': 'a0:36:9f:a9:5b:6f', 'dst_mac': '08:00:27:87:aa:b8', 'path': ['1', '3'],
         'ports': ['-1', '5', '6', '7', '8', '-1']}]}
    status = flow['status']

    if status == 'failed':
        log.logger.error('Route update failed')
    elif status == 'success':
        switch = '1'
        route_and_path = flow['items'][-1]  # a dict contains 'src_mac', 'dst_mac' and 'path'
        dst_mac_write_dpdk = mac_form_handler(route_and_path['dst_mac'])  # get dst MAC as '0xaabbccddeeff'
        src_mac_write_dpdk = mac_form_handler(route_and_path['src_mac'])
        '''f1 = open('mac_table.txt', 'w')
        t2 = str(time.time()) + '\n'
        print("t2:", t2)
        f1.write(t2)
        f1.write('match ' + dst_mac_write_dpdk + ' ' + 'order 234 port 0\n')
        f1.write('match ' + src_mac_write_dpdk + ' ' + 'order 234 port 1\n')
        f1.close()
        log.logger.info('Route update success for switch:' + switch)'''
    order = ' 324 '
    f = open('mac_table.txt', 'r')
    mac_in_file = []
    t3 = str(time.time())
    print('t3:', t3)
    file_data = ''
    test_src_mac = '0xaabbccddeeff'
    test_dst_mac = '0x001122334455'
    test_src_mac_port = '2'
    test_dst_mac_port = '3'
    for line in f.readlines()[1:]:
        words = line.split()
        print(words)
        order_o = words[3]
        mac_o = words[1]
        mac_in_file.append(mac_o)
        order_o = ' ' + order_o + ' '
        if order != order_o:
            line = line.replace(order_o, order)
        file_data += line
    print("file_data:", file_data)
    print("words:", words)
    if test_dst_mac not in mac_in_file:
        add = 'match ' + test_dst_mac + ' ' + 'order' + order + 'port ' + test_dst_mac_port + '\n'
        file_data += add
    if test_src_mac not in mac_in_file:
        add = 'match ' + test_src_mac + ' ' + 'order' + order + 'port ' + test_src_mac_port + '\n'
        file_data += add
    with open('mac_table.txt', 'w') as f:
        f.write(t3)
        f.write('\n')
        f.write(file_data)
