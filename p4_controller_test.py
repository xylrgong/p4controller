# -*- coding: utf-8 -*-
from flask import Flask, jsonify, render_template, request
from binascii import hexlify
from enum import Enum
from scp import SCPClient
import socket
import telnetlib
import time
import flow_trans
import json
import os
import time
import subprocess
import paramiko


class Reverse(Enum):
    t_234 = '0'
    t_342 = '1'
    t_324 = '2'


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

                #     1    2    3    4    5    6    7    8
route_port_table = [['x', '1', '2', '3', 'x', 'x', 'x', 'x'], # 1
                    ['0', 'x', '1', 'x', 'x', 'x', 'x', 'x'], # 2
                    ['2', '1', 'x', 'x', 'x', 'x', 'x', '3'], # 3
                    ['0', 'x', 'x', 'x', '1', 'x', '2', 'x'], # 4
                    ['x', 'x', 'x', '0', 'x', '1', 'x', 'x'], # 5
                    ['x', 'x', 'x', 'x', '1', 'x', '0', 'x'], # 6
                    ['x', 'x', 'x', '0', 'x', '1', 'x', '2'], # 7
                    ['x', 'x', '1', 'x', 'x', 'x', '0', 'x'], # 8
                    ]

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

dpdk_switch = ['1', '2', '3', '4', '5', '6', '7', '8']
# real_switch = ['1', '2', '3']
# virtual_switch = ['4', '5', '6', '7', '8']


def scpClient(ip, filename, local_path, remote_path, username, password): 
    port = 22
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh_client.connect(ip, port, username, password)
    scp_client = SCPClient(ssh_client.get_transport(), socket_timeout=15.0)
    local_file = local_path + filename   # local_path = '/home/p4s2/dpdk-21.02/examples/pipeline/examples/'
    try:
        scp_client.put(local_file, remote_path)
    except FileNotFoundError as e:
        print(e)
        print("Cannot find file " + filename)
        return
    print('File ', filename, ' successfully send to: ', ip)
    ssh_client.close()


def telnetClient(ip, port, filename):  # send reverse command to dpdk switches / reverse-dpdk
    try:
        tn = telnetlib.Telnet(ip, port)  # try to login
    except:
        return 'connection fail'
    # show = tn.read_very_eager().decode()  # show pipeline result
    print('Connected to switch@', ip)
    time.sleep(1)
    f = open(filename)
    commands = f.read()
    time.sleep(1)
    tn.write(commands.encode())  # encode to transfer str to byte-like
    result = tn.read_very_eager().decode()  # get pipeline result
    print(result)
    if 'Invalid' in result:        # print('unknown flow table\n')
        return result
    elif 'Wrong' in result:
        return result
    elif 'Unknown' in result:
        return result
    return 'OK'


def dpdk_reverse_commands_handler(switch, ip, pkt_reverse_t, pkt_reverse_t_n): # choose reverse file for dpdk switch
    print('/*********** DPDK switch **********/')
    print('switch:', switch)
    print('Strategy running is: ', str(pkt_reverse_t), ' Now switch to: ', pkt_reverse_t_n)
    pipeline_filename = 'pipeline_' + pkt_reverse_t_n + '.txt'
    ipv4_table_filename = 'tmp_flow_table_ipv4_s' + switch + '.txt'
    arp_table_filename = 'tmp_flow_table_arp_s' + switch + '.txt'
    f = open(pipeline_filename, 'w')
    f.write('thread 1 pipeline PIPELINE' + pkt_reverse_t_n + ' enable\n')
    f.write('thread 1 pipeline PIPELINE' + pkt_reverse_t + ' disable\n')
    f.write('pipeline PIPELINE' + pkt_reverse_t_n + ' table ipv4_lpm_0 update ./examples/' + ipv4_table_filename + ' none none\n')
    f.write('pipeline PIPELINE' + pkt_reverse_t_n + ' table arp_exact_0 update ./examples/' + arp_table_filename + ' none none\n')
    f.close()
    scpClient(ip=ip, filename=pipeline_filename, local_path=local_work_dir, remote_path=dpdk_work_dir[switch], username=dpdk_username[switch], password='123456')
    res = telnetClient(ip=switch_ip_table[switch], port=8086, filename=pipeline_filename)
    return res


def dec_to_hex(ip):   # transfer ip from dec to hex, eg, from 192.168.0.11 to 0xc0a80b
    packed_ip_addr = socket.inet_aton(ip)
    hexStr = hexlify(packed_ip_addr)
    return hexStr.decode()


def mac_form_handler(macAddr):  # transfer mac form from '00:00:00:00:00:10' to '0x000000000010'
    return '0x' + macAddr.replace(':', '')


app = Flask(__name__)


@app.route('/strategy', methods=['POST'])
def packet_reverse():  #
    global pkt_reverse_t
    pkt_reverse_t_n = request.form.get("type", type=str)  # get reverse type from controller
    if pkt_reverse_t_n == pkt_reverse_t:
        print('Strategy not change!')
        return 'Bad Request'
    # for dpdk switches:
    for switch in dpdk_switch:
        res = dpdk_reverse_commands_handler(switch=switch, ip=switch_ip_table[switch], pkt_reverse_t=pkt_reverse_t, pkt_reverse_t_n=pkt_reverse_t_n)
        if res == 'OK':
            print("Change strategy to " + pkt_reverse_t_n)
        else:
            print("Change strategy failed! " + res)
    pkt_reverse_t = pkt_reverse_t_n
    return 'OK'


@app.route('/route', methods=['POST'])
def packet_route():
    global pkt_reverse_t
    print("Reverse strategy now is:", pkt_reverse_t)
    edge_switch_min = '1'  # edge switch connected with host at port 0
    edge_switch_max = len(route_port_table)  # edge switch connected with host at port 0

    pkt_route = request.form # get route from controller. get src/dst mac and ip
    src_mac = pkt_route['src_mac']
    dst_mac = pkt_route['dst_mac']
    bw = float(pkt_route['bw'])
    delay = float(pkt_route['delay'])  # generate flow_data
    flow_data = {"src": src_mac, "dst": dst_mac, "bandwidth": bw, "delay": delay}
    # print("Get flow data:", flow_data)
    # switch to calculate by flow_trans!!!
    #flow = flow_trans.schedule_flows(flow_data)
    #print("Get flow:", flow)
    # flow = {'status': 'success', 'items': [{'src_mac': 'a0:36:9f:a9:5b:6f', 'dst_mac': '08:00:27:87:aa:b8', 'path': ['1',  '3'], 'ports': ['-1', '5', '6', '7', '8', '-1']}]}
    flow = {'status': 'success', 'items': [{'src_mac': '00:f1:f3:1a:0a:93', 'dst_mac': '00:f1:f3:1a:cc:c1', 'path': ['1',  '3'], 'ports': ['-1', '5', '6', '7', '8', '-1']}]}
    #flow = {'status': 'success', 'items': [{'src_mac': 'f0:2f:74:ad:b1:d1', 'dst_mac': 'f0:2f:74:ad:b1:30', 'path': ['1', '4', '5', '6', '7', '8', '3'], 'ports': ['-1', '5', '6', '7', '8', '-1']}]}

    '''
    flow can be like:
    flow = {'status': 'success', 'items': [{'src_mac': '00:00:00:00:00:10', 'dst_mac': '00:00:00:00:00:20', 'path': ['1', '3', '4'], 'ports': ['-1', '5', '6', '7', '8', '-1']}], 'order': [0, 1, 3, 2]}
    '''
    route_and_path = flow['items'][-1]  # a dict contains 'src_mac', 'dst_mac' and 'path'
    # order = flow['order']
    print("Route and path is:", route_and_path)
    dst_mac_write_dpdk = mac_form_handler(route_and_path['dst_mac']) # get dst MAC as '0xaabbccddeeff'
    src_mac_write_dpdk = mac_form_handler(route_and_path['src_mac'])
    path = route_and_path['path']  # get path as ['1,3,4'], which means s1->s3->s4
    path_len = len(path)  # for path s1->s3->s4, path_len is 3

    for i in range(path_len):
        if i == 0:  # we assume when i is 0, it must be the edge_switch_min(s1 in this case) connected to host at port 0.
            m = int(path[i]) - 1        # eg, h1----s1----s2----s3----s4, and m means from s1 to s2(further switch)
            n = int(path[i + 1]) - 1    # eg, in this case, n means from s1 to h1
            port_m2n = route_port_table[m][n]   # port_m2n means port from s1 to further switch
            port_n2m = '0'      # port_n2m means port from s1 to h1
        elif i == path_len - 1:  # we assume when i is path_len-1, it must be the edge_switch_max(s4 in this case) connected to host at port 0
            m = int(path[i - 1]) - 1
            n = int(path[i]) - 1
            '''
            !!!!!!!!!!!!!!!!!!!!!!!!!s
            '''
            port_m2n = '0'      # we assume s4 to h4 through port 0
            port_n2m = route_port_table[n][m]
        else:
            l = int(path[i - 1]) - 1    # l means the former node, in this case, when i = 1, s = '3', l means switch '1'
            m = int(path[i]) - 1  # m means switch '3'
            n = int(path[i + 1]) - 1  # n means switch 4
            port_m2n = route_port_table[m][n]  # for s3->s4 lookup in route_port_table[2][3]
            port_n2m = route_port_table[m][l]  # for s3->s1 lookup in route_port_table[2][0]
        switch = path[i]  # switch = '1' or '3' or '4'
        switch_ip = switch_ip_table[switch]
        if switch in dpdk_switch:  # deploy flow table to DPDK switch
            print('/*********** DPDK switch **********/')
            print('switch:', switch)
            ipv4_table_filename = 'tmp_flow_table_ipv4_s' + switch + '.txt'
            f1 = open(ipv4_table_filename, 'w')
            f1.write('match ' + dst_mac_write_dpdk + ' ' + 'action ipv4_forward port H(' + port_m2n + ')\n')
            f1.write('match ' + src_mac_write_dpdk + ' ' + 'action ipv4_forward port H(' + port_n2m + ')\n')
            f1.close()
            scpClient(ip=switch_ip, filename=ipv4_table_filename, local_path=local_work_dir, remote_path=dpdk_work_dir[switch], username=dpdk_username[switch], password='123456')
            print("flow_table ipv4 for switch" + switch + ": " + 'match ' + dst_mac_write_dpdk + ' ' + 'action ipv4_forward port H(' + port_m2n + ')')
            print("flow_table ipv4 for switch" + switch + ": " + 'match ' + src_mac_write_dpdk + ' ' + 'action ipv4_forward port H(' + port_n2m + ')')

            arp_table_filename = 'tmp_flow_table_arp_s' + switch + '.txt'
            f2 = open(arp_table_filename, 'w')
            f2.write('match ' + dst_mac_write_dpdk + ' ' + 'action arp_forward port H(' + port_m2n + ')\n')
            f2.write('match ' + src_mac_write_dpdk + ' ' + 'action arp_forward port H(' + port_n2m + ')\n')
            f2.write('match ' + '0xffffffffffff' + ' ' + 'action arp_forward port H(' + port_n2m + ')\n')
            f2.write('match ' + '0xffffffffffff' + ' ' + 'action arp_forward port H(' + port_m2n + ')\n')
            f2.close()
            scpClient(ip=switch_ip, filename=arp_table_filename, local_path=local_work_dir, remote_path=dpdk_work_dir[switch], username=dpdk_username[switch], password='123456')
            print("flow_table arp for switch" + switch + ": " + 'match 0xffffffffffff action arp_forward port H(' + port_m2n + ')')
            print("flow_table arp for switch" + switch + ": " + 'match 0xffffffffffff action arp_forward port H(' + port_n2m + ')')

            tmp_cmd_filename = 'tmp_cmd_s' + switch + '.txt'
            f3 = open(tmp_cmd_filename, 'w')
            f3.write('pipeline PIPELINE' + pkt_reverse_t + ' table ipv4_lpm_0 update ./examples/' + ipv4_table_filename + ' none none\n')
            f3.write('pipeline PIPELINE' + pkt_reverse_t + ' table arp_exact_0 update ./examples/' + arp_table_filename + ' none none\n')
            f3.close()
            scpClient(ip=switch_ip, filename=tmp_cmd_filename, local_path=local_work_dir, remote_path=dpdk_work_dir[switch], username=dpdk_username[switch], password='123456')

            res = telnetClient(ip=switch_ip, port=8086, filename=tmp_cmd_filename)
            if res == 'OK':
                print("flow table for switch:", switch, " update successfully!")
            else:
                print("Unable to update flow table!")
                print(res)
    return 'OK'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2021)
