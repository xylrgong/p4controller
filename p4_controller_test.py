# -*- coding: utf-8 -*-
from flask import Flask,  request, Response
from binascii import hexlify
from scp import SCPClient
import socket
import time
import flow_trans
import paramiko
from logger import *
from setup import *
from file_handler import file_handler_route, file_handler_reverse


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
        log.logger.error("Cannot find file " + filename + ' at' + local_file)
        return 'Error'
    log.logger.info('File ' + filename + ' successfully send to: ' + ip)
    ssh_client.close()
    return 'OK'


def dpdk_reverse_commands_handler(switch, ip, order_o, order_n): # choose reverse file for dpdk switch
    print('/*********** DPDK switch **********/')
    print('switch:', switch)
    print('Strategy running is: ', order_o, ' Now switch to: ', order_n)
    table_filename_at_dir = 'mac_table_' + switch + '.txt'
    table_filename = 'mac_table.txt'
    table_dir = 'mac_table_local/'
    status = file_handler_reverse(log=log, table_dir=table_dir,
                                  table_name=table_filename_at_dir,
                                  order_n=order_n)
    '''
    status can be:
    1. 'Not existing': which is a warning level log, suggesting no route has passed this switch, we will create a file
    2. 'OK': reverse mac_table is correctly written.
    '''
    if status == 'OK':
        res = scpClient(ip=ip, filename=table_filename,
                        local_path=local_work_dir, remote_path=dpdk_work_dir[switch],
                        username=dpdk_username[switch], password=dpdk_psw[switch])
        return res
    elif status == 'Not existing':
        return status


def mac_form_handler(macAddr):  # transfer mac form from '00:00:00:00:00:10' to '000000000010'
    return macAddr.replace(':', '')


app = Flask(__name__)


@app.route('/det_switch', methods=['POST'])
def change_det_state():
    global det_switch
    req = request.form.get("switch", type=str)
    if req == 'on' and not det_switch:
        det_switch = True
        log.logger.info('Change detNet switch to ON')
    elif req == 'off' and det_switch:
        det_switch = False
        log.logger.info('Change detNet switch to OFF')
    else:
        log.logger.info('detNet switch not change')
    return Response(status=200)


@app.route('/strategy', methods=['POST'])
def packet_reverse():  #
    global pkt_reverse_t
    pkt_reverse_t_n = request.form.get("type", type=str)  # get reverse type from controller
    order_o = dict_reverse[pkt_reverse_t]
    order_n = dict_reverse[pkt_reverse_t_n]
    if pkt_reverse_t_n == pkt_reverse_t:
        log.logger.warning('Strategy not change!')
        return 'Bad Request'
    # for dpdk switches:

    for switch in dpdk_switch:
        res = dpdk_reverse_commands_handler(switch=switch, ip=switch_ip_table[switch], order_o=order_o, order_n=order_n)
        if res == 'OK':
            info = "Change strategy from " + order_o + " to " + order_n + " for switch " + switch
            log.logger.info(info)
        elif res == 'Not existing':
            print("strategy not change for switch:" + switch + " for file not existing")
    pkt_reverse_t = pkt_reverse_t_n
    return 'OK'


@app.route('/route', methods=['POST'])
def packet_route():
    global pkt_reverse_t
    global det_switch
    order = dict_reverse[pkt_reverse_t]
    print("Reverse strategy now is:", order)
    edge_switch_min = '1'  # edge switch connected with host at port 0
    edge_switch_max = len(route_port_table)  # edge switch connected with host at port 0

    pkt_route = request.form # get route from controller. get src/dst mac and ip
    if not det_switch:
        log.logger.warning('detNet switch is off but get a route flow')
        return 'detNet not open'
    print("get raw data")
    print(pkt_route)
    src_mac = pkt_route['src_mac']
    dst_mac = pkt_route['dst_mac']
    bw = float(pkt_route['bw'])
    delay = float(pkt_route['delay'])  # generate flow_data
    flow_data = {"src": src_mac, "dst": dst_mac, "bandwidth": bw, "delay": delay}
    # print("Get flow data:", flow_data)
    # switch to calculate by flow_trans!!!
    flow = flow_trans.schedule_flows(flow_data)
    # print("Get flow:", flow)
    # flow = {'status': 'success', 'items': [{'src_mac': 'a0:36:9f:a9:5b:6f', 'dst_mac': '08:00:27:87:aa:b8', 'path': ['1',  '3'], 'ports': ['-1', '5', '6', '7', '8', '-1']}]}
    # flow = {'status': 'success', 'items': [{'src_mac': '00:f1:f3:1a:0a:93', 'dst_mac': '00:f1:f3:1a:cc:c1', 'path': ['1', '4', '5', '6', '7', '8', '3'], 'ports': ['-1', '5', '6', '7', '8', '-1']}]}
    # flow = {'status': 'success', 'items': [{'src_mac': '00:f1:f3:19:37:81', 'dst_mac': '00:f1:f3:19:37:39', 'path': ['1', '7', '6'], 'ports': ['-1', '5', '6', '7', '8', '-1']}]}
    status = flow['status']
    if status == 'failed':
        log.logger.error('Flow status is \'failed\', route update failed')
        return 'Bad flow'
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
            m = int(path[i])       # eg, h1----s1----s2----s3----s4, and m means from s1 to s2(further switch)
            n = int(path[i + 1])   # eg, in this case, n means from s1 to h1
            port_m2n = route_port_table[m][n]   # port_m2n means port from s1 to further switch
            port_n2m = '0'      # port_n2m means port from s1 to h1
        elif i == path_len - 1:  # we assume when i is path_len-1, it must be the edge_switch_max(s4 in this case) connected to host at port 0
            m = int(path[i - 1])
            n = int(path[i])
            '''
            !!!!!!!!!!!!!!!!!!!!!!!!!s
            '''
            port_m2n = '0'      # we assume s4 to h4 through port 0
            port_n2m = route_port_table[n][m]
        else:
            l = int(path[i - 1])   # l means the former node, in this case, when i = 1, s = '3', l means switch '1'
            m = int(path[i])    # m means switch '3'
            n = int(path[i + 1])  # n means switch 4
            port_m2n = route_port_table[m][n]  # for s3->s4 lookup in route_port_table[2][3]
            port_n2m = route_port_table[m][l]  # for s3->s1 lookup in route_port_table[2][0]
        tmp_mac_port = {dst_mac_write_dpdk: port_m2n, src_mac_write_dpdk: port_n2m}
        switch = path[i]  # switch = '1' or '3' or '4'
        switch_ip = switch_ip_table[switch]
        if switch in dpdk_switch:  # deploy flow table to DPDK switch
            print('/*********** DPDK switch **********/')
            print('switch:', switch)
            table_name_at_dir = 'mac_table_' + switch + '.txt'
            table_name = 'mac_table.txt'
            table_dir = 'mac_table_local/'
            file_handler_route(log=log, table_dir=table_dir, table_name=table_name_at_dir,
                               src_mac=src_mac_write_dpdk, src_mac_p=port_n2m,
                               dst_mac=dst_mac_write_dpdk, dst_mac_p=port_m2n,
                               order=order)

            res = scpClient(ip=switch_ip, filename=table_name, local_path=local_work_dir,
                            remote_path=dpdk_work_dir[switch],
                            username=dpdk_username[switch], password=dpdk_psw[switch])
            if res == 'OK':
                log.logger.info("flow table for switch:" + switch + " update successfully!")
                log.logger.info("switch " + switch + " flow table:" + 'match ' + src_mac_write_dpdk + ' order ' + order + ' port ' + port_n2m)
                log.logger.info("switch " + switch + " flow table:" + 'match ' + dst_mac_write_dpdk + ' order ' + order + ' port ' + port_m2n)
            elif res == 'Error':
                log.logger.error("Unable to update flow table for switch:", switch)
    return 'OK'


if __name__ == '__main__':
    log = Logger('log/all.log', level='debug')
    default_mac_table_loc = '/home/gs/p4controller/default_table_local/'
    for switch in dpdk_switch:
        file_name = 'mac_table_' + switch + '.txt'
        status = scpClient(ip=switch_ip_table[switch], local_path=default_mac_table_loc,
                           remote_path=dpdk_work_dir[switch] + 'mac_table.txt', filename=file_name,
                           username=dpdk_username[switch],
                           password=dpdk_psw[switch])
        scpClient(ip='localhost', local_path=default_mac_table_loc,
                  remote_path='/home/gs/p4controller/mac_table_local/', filename=file_name,
                  username='gs',
                  password='123456')
        if status == 'OK':
            log.logger.info('Initialize mac table to switch ' + switch + ' with return status:' + status)
        elif status == 'Error':
            log.logger.error('Initialize mac table to switch ' + switch + ' failed')
    app.run(host='0.0.0.0', port=2021, debug=True)
