import os
import time
import re
from logger import Logger

def file_handler_route(log, table_dir, table_name, src_mac, src_mac_p, dst_mac, dst_mac_p, order):
    if not os.path.exists(table_dir + table_name):
        log.logger.warning('Now deploy new route!, but ' + table_name + ' not existing, now create file for switch')
        f = open(table_dir + table_name, 'w', encoding='utf-8')
        f.close()
    f = open(table_dir + table_name, 'r')
    mac_in_file = []
    t = str(int(time.time()))
    print('t:', t)
    file_data = ''
    for line in f.readlines()[1:]:
        words = line.split()
        print(words)
        order_o = words[3]
        mac_o = words[1]
        port_o = words[5]
        mac_in_file.append(mac_o)
        if  order != order_o:
            pattr = 'order [0-9]+'
            repl = 'order ' + order
            line = re.sub(pattr, repl, line)
        if src_mac == mac_o:
            pattr = 'port [0-9]+'
            repl = 'port ' + src_mac_p
            line = re.sub(pattr, repl, line)
        if dst_mac == mac_o:
            pattr = 'port [0-9]+'
            repl = 'port ' + dst_mac_p
            line = re.sub(pattr, repl, line)
        file_data += line
        # print("file_data:", file_data)
    f.close()
    # print("words:", words)
    if src_mac not in mac_in_file:
        add = 'match ' + src_mac + ' ' + 'order ' + order + ' port ' + src_mac_p + '\n'
        file_data += add
    if dst_mac not in mac_in_file:
        add = 'match ' + dst_mac + ' ' + 'order ' + order + ' port ' + dst_mac_p + '\n'
        file_data += add
    with open(table_dir + table_name, 'w', encoding='utf-8') as f:
        f.write(t)
        f.write('\n')
        f.write(file_data)
        f.close()
    with open('mac_table.txt', 'w') as f:
        f.write(t)
        f.write('\n')
        f.write(file_data)
        f.close()


def file_handler_reverse(log, table_dir, table_name, order_n):
    if not os.path.exists(table_dir + table_name):
        log.logger.warning('Now deploy new strategy, but ' + table_name + ' not exist')
        return 'Not existing'
    with open(table_dir + table_name, 'r', encoding='utf-8') as f:
        t = str(int(time.time()))
        file_data = ''
        for line in f.readlines()[1:]:
            words = line.split()
            order_o = words[3]
            if order_n != order_o:
                pattr = 'order [0-9]+'
                repl = 'order ' + order_n
                line = re.sub(pattr, repl, line)
            file_data += line
        with open(table_dir + table_name, 'w', encoding='utf-8') as f:
            f.write(t)
            f.write('\n')
            f.write(file_data)
            f.close()
        with open('mac_table.txt', 'w') as f:
            f.write(t)
            f.write('\n')
            f.write(file_data)
            f.close()
    return 'OK'


if __name__ == '__main__':
    switch = '1'
    order = '432'
    table_dir = 'mac_table_local/'
    table_name = 'mac_table_' + switch + '.txt'
    test_src_mac = '0xaaaaaaaaaaaa'
    test_dst_mac = '0xbbbbbbbbbbbb'
    test_src_mac_port = '1'
    test_dst_mac_port = '2'
    file_handler_route(table_dir, table_name, src_mac=test_src_mac, src_mac_p= test_src_mac_port ,\
    dst_mac= test_dst_mac, dst_mac_p=test_dst_mac_port, order=order)
    #file_handler_reverse(table_dir, table_name, order)