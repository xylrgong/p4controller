import copy


class FlowNode:
    def __init__(self, node, bandwidth):
        self.node = node
        self.bandwidth = bandwidth
        self.child = []
        self.parent = []


class LinkNode:
    def __init__(self, node, linkRemain):
        self.node = node
        self.linkRemain = linkRemain
        self.parent = []
        self.child = []


class UpdateTest:
    def __init__(self):
        self.list_segment_dst = []
        self.list_handle_by_controller = []

    def update(self, flow, bandwidth, link, path):
        # 移动之前的节点
        list_segment_src = []  # flow
        list_link_src = []  # link
        # 已经移动的节点列表

        # 存储所有的流节点
        for x in range(0, len(flow), 2):
            string = (flow[x], flow[x + 1])
            # list_segment_src：[SegmentNode]
            # SegmentNode:((f1_old, f1_new), 5M)
            list_segment_src.append(FlowNode(string, bandwidth[x]))  # (流节点, 流占用的带宽)

        # 存储所有的链路节点
        for key in link.keys():
            list_link_src.append(LinkNode(key, link.get(key)))  # (链路节点, 链路剩余带宽)

        for index in range(0, len(flow), 1):
            flow_link = path.get(flow[index])
            for link_index in range(0, len(flow_link) - 1, 1):
                # 创建linkNode并且指定链路
                tmp = (flow_link[link_index], flow_link[link_index + 1])
                node = LinkNode((), 0)
                # 找到path对应的链路节点
                for x in list_link_src:
                    if x.node == tmp and x.linkRemain == link.get(tmp):
                        node = x
                        break
                # old_link_node <- flow_node <- new_link_node
                # f 相关依赖
                if index % 2 == 0:
                    index_tmp = int(index / 2)
                    list_segment_src[index_tmp].child.append(node)
                    node.parent.append(list_segment_src[index_tmp])
                # f' 相关依赖
                else:
                    index_tmp = int((index - 1) / 2)
                    list_segment_src[index_tmp].parent.append(node)
                    node.child.append(list_segment_src[index_tmp])

        # 插入排序 按照流的带宽占用从大到小排序
        number = len(list_segment_src)
        for j in range(1, number):
            for i in range(j, 0, -1):
                if list_segment_src[i].bandwidth > list_segment_src[i - 1].bandwidth:
                    list_segment_src[i], list_segment_src[i - 1] = list_segment_src[i - 1], list_segment_src[i]
                else:
                    break

        self.remove_flow(list_segment_src)

    # 调用移动流的函数
    def remove_flow(self, list_segment_src):

        if len(list_segment_src) == 0:
            return

        length = len(list_segment_src)
        list_segment_src_tmp = copy.copy(list_segment_src)

        # 如果需要的带宽可以满足，则“移动”此流
        for segmentNode in list_segment_src:
            remove_flag = True
            for linkNode in segmentNode.parent:
                # 如果移动前后是同一条链路 则直接跳过
                if linkNode in segmentNode.child:
                    continue
                # 所需要的链路如果有任何一条不满足
                if segmentNode.bandwidth > linkNode.linkRemain:
                    remove_flag = False
            if remove_flag:
                # 如果可以移动，相应的父子节点剩余带宽重新赋值
                for linkNode_remove in segmentNode.parent:
                    linkNode_remove.linkRemain = round(linkNode_remove.linkRemain - segmentNode.bandwidth, 1)
                for linkNode_remove in segmentNode.child:
                    linkNode_remove.linkRemain = round(linkNode_remove.linkRemain + segmentNode.bandwidth, 1)
                list_segment_src_tmp.remove(segmentNode)
                self.list_segment_dst.append(segmentNode)
                break

        # 子图递归调用
        if len(list_segment_src_tmp) == length:
            # 解决死锁需要提交的节点
            node = self.unlock(list_segment_src_tmp)
            self.list_handle_by_controller.append(node)
            # print("node:", node.node)

            for linkNode_remove in node.parent:
                linkNode_remove.linkRemain -= node.bandwidth
            for linkNode_remove in node.child:
                linkNode_remove.linkRemain += node.bandwidth
            self.list_segment_dst.append(node)

            list_segment_src_tmp.remove(node)

            self.remove_flow(list_segment_src_tmp)

        else:
            self.remove_flow(list_segment_src_tmp)

    # 检测环路并且输出环路相关节点，list_segment_src中包含所有成环的节点
    def unlock(self, list_segment_src):
        if len(list_segment_src) == 0:
            return None
        r = len(list_segment_src)

        # graph = [len(list_segment_src)][len(list_segment_src)]
        graph = [[0] * len(list_segment_src) for i in range(len(list_segment_src))]

        # 创建邻接矩阵
        for i in range(len(list_segment_src)):
            for j in range(len(list_segment_src)):
                for linkNode_child in list_segment_src[i].child:
                    for linkNode_parent in list_segment_src[j].parent:
                        if linkNode_child == linkNode_parent:
                            graph[i][j] = 1
                            break
                    break

        # 调用深度搜索函数输出环中元素
        isDAG, stack = self.findcircle(graph)
        number = len(stack)

        # 将某个环的成环节点加入列表中
        circle = []
        for index in range(number):
            circle.append(list_segment_src[stack[index]])

        # 存放
        node_list = []
        flag = True

        for index in range(len(circle)):
            segment = circle[index]
            if index < number - 1:
                segment_next = circle[index + 1]
            else:
                segment_next = circle[0]

            for linkNode_child in segment.child:
                for linkNode_parent in segment_next.parent:
                    if linkNode_child == linkNode_parent:
                        if segment.bandwidth + linkNode_child.linkRemain < segment_next.bandwidth:
                            node_list.append(segment_next)
                            flag = False
                            break
                break

        if flag is True:
            # 排序找出占用带宽最小的节点
            for j in range(1, number):
                for i in range(j, 0, -1):
                    if circle[i].bandwidth < circle[i - 1].bandwidth:
                        circle[i], circle[i - 1] = circle[i - 1], circle[i]
                    # 如果占用带宽相同，选择释放链路较多的
                    elif circle[i].bandwidth == circle[i - 1].bandwidth:
                        if len(circle[i].child) > len(circle[i - 1].child):
                            circle[i], circle[i - 1] = circle[i - 1], circle[i]
                    else:
                        break
            return circle[0]
        else:
            number = len(node_list)
            for j in range(1, number):
                for i in range(j, 0, -1):
                    if node_list[i].bandwidth > node_list[i - 1].bandwidth:
                        node_list[i], node_list[i - 1] = node_list[i - 1], node_list[i]
                    # 如果占用带宽相同，选择释放链路较多的
                    elif node_list[i].bandwidth == node_list[i - 1].bandwidth:
                        if len(node_list[i].child) > len(node_list[i - 1].child):
                            node_list[i], node_list[i - 1] = node_list[i - 1], node_list[i]
                    else:
                        break
            return node_list[0]

    def findcircle(self, G):
        """
        color = 0 hasn't been visited
        color = -1 be visited once
        color = 1 has been dfs, all children of the spot has been visited
        """
        stack = []

        def dfs(G, i, color, is_DAG):
            if is_DAG == 0:
                pass
            else:
                r = len(G)
                color[i] = -1  # spot i has been visited
                stack.append(i)
                for j in range(r):
                    # 存在边
                    if G[i][j] != 0:
                        # 如果已经被访问过，则存在环
                        if color[j] == -1:
                            is_DAG = 0
                            break
                        # 没有访问过 递归
                        elif color[j] == 0:
                            is_DAG, color = dfs(G, j, color, is_DAG)
                color[i] = 1
            return is_DAG, color

        r = len(G)
        color = [0] * r  # the number of spots
        is_DAG = 1
        for i in range(r):
            if color[i] == 0:  # the spot i has not been visited
                is_DAG, color = dfs(G, i, color, is_DAG)  # DFS from spot i
                if is_DAG == 0:  # have circle
                    break

        return is_DAG, stack


# read the link & flow config; calc the path before and after when add a new flow;
def get_moved_flow(all_bandwidth, max_bandwidth, last_paths, new_paths):
    # 流的id和带宽
    flow = []
    bandwidth = []

    for i in range(len(all_bandwidth) - 1):
        flow.append('f{}_old'.format(i))
        flow.append('f{}_new'.format(i))
        bandwidth.append(all_bandwidth[i])
        bandwidth.append(all_bandwidth[i])

    # 总带宽
    link = {}
    with open('.links', 'r') as links:
        for line in links.readlines():
            src, dst, _, _ = [x for x in line.strip('\n').split(' ')]
            link[src, dst] = max_bandwidth
            link[dst, src] = max_bandwidth

    # 加入新流前后的流的路径
    flow_path_before = last_paths
    flow_path_after = new_paths
    # test data
    # flow_path_before = {0: [1, 2, 3, 5], 1: [1, 3, 5], 2: [1, 3, 5], 3: [1, 3, 5], 4: [1, 3, 5], 5: [1, 4, 3, 5]}
    # flow_path_after = {0: [1, 3, 5], 1: [1, 2, 3, 5], 2: [1, 2, 3, 5], 3: [1, 2, 3, 5], 4: [1, 4, 3, 5], 5: [1, 3, 5]}

    # 计算路径的剩余带宽
    for flow_id, path in flow_path_before.items():
        flow_bw = bandwidth[flow_id * 2]
        for i in range(len(path) - 1):
            src, dst = path[i], path[i + 1]
            link[src, dst] -= flow_bw
            link[dst, src] -= flow_bw

    # 计算传递给update函数的路径
    path = {}
    for flow_id in flow_path_before.keys():
        path['f{}_old'.format(flow_id)] = flow_path_before[flow_id]
        path['f{}_new'.format(flow_id)] = flow_path_after[flow_id]

    test = UpdateTest()
    test.update(flow, bandwidth, link, path)

    # 流的提交顺序; 需要临时由控制器转发的流
    flow_order = [int(x.node[0][1]) for x in test.list_segment_dst]
    flow_handled = [int(x.node[0][1]) for x in test.list_handle_by_controller]
    return flow_order, flow_handled


if __name__ == '__main__':
    flow_path_before, flow_path_after, flow_order, flow_handled = get_moved_flow('config/link', 'config/flow', 'config/flow2')
    print(flow_order)
    print(flow_handled)
    # # 用户输入移动前后的路径、每条流占用的带宽、各条链路剩余的带宽
    # flow = ['f1_old', 'f1_new', 'f2_old', 'f2_new', 'f3_old', 'f3_new',
    #         'f4_old', 'f4_new', 'f5_old', 'f5_new', 'f6_old', 'f6_new']
    # # 流占用的带宽
    # bandwidth = [0.5, 0.5, 0.2, 0.2, 0.3, 0.3, 0.4, 0.4, 0.7, 0.7, 0.5, 0.5]
    # # 链路剩余带宽
    # link = {(1, 2): 0.5, (2, 3): 0.5, (1, 3): 0, (1, 4): 0.5, (4, 3): 0.5,
    #         (2, 1): 0.5, (3, 2): 0.5, (3, 1): 0, (4, 1): 0.5, (3, 4): 0.5,
    #         (3, 5): 0, (5, 3): 0
    #         # (3, 5): 0.5, (5, 6): 0.5, (3, 6): 0, (3, 7): 0.5, (7, 6): 0.5,
    #         # (5, 3): 0.5, (6, 5): 0.5, (6, 3): 0, (7, 3): 0.5, (6, 7): 0.5,
    #         }
    #
    # path = {'f1_old': [1, 2, 3, 5], 'f1_new': [1, 3, 5],
    #         'f2_old': [1, 3, 5], 'f2_new': [1, 2, 3, 5],
    #         'f3_old': [1, 3, 5], 'f3_new': [1, 2, 3, 5],
    #         'f4_old': [1, 3, 5], 'f4_new': [1, 2, 3, 5],
    #         'f5_old': [1, 3, 5], 'f5_new': [1, 4, 3, 5],
    #         'f6_old': [1, 4, 3, 5], 'f6_new': [1, 3, 5]}
    #
    # # flow = ['f1_old', 'f1_new', 'f2_old', 'f2_new', 'f3_old', 'f3_new']
    # # bandwidth = [10, 10, 11, 11, 7, 7]
    # # link = {(1, 2): 5, (1, 3): 5, (1, 4): 3,
    # #         (2, 1): 5, (3, 1): 5, (4, 1): 3}
    # # path = {'f1_old': [1, 2], 'f1_new': [1, 3],
    # #         'f2_old': [1, 3], 'f2_new': [1, 4],
    # #         'f3_old': [1, 4], 'f3_new': [1, 2]}
    # test = UpdateTest()
    # test.update(flow, bandwidth, link, path)
