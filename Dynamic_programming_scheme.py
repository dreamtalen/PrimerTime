import time
import random
import itertools
from pulp import *
import argparse
parser = argparse.ArgumentParser()

parser.add_argument('file')

args = parser.parse_args()

input_file = args.file


def find_all_paths(graph, start, end, D_port_list=[], path=[]):
    path = path + [start]
    if start == end:
        return [path]
    if not graph.has_key(start):
        return []
    paths = []
    for node in graph[start]:
        if (node not in path and node not in D_port_list) or node == end :
            newpaths = find_all_paths(graph, node, end, D_port_list, path)
            for newpath in newpaths:
                paths.append(newpath)
    return paths

def lib_parser(filename):
    design_name = ''
    design_input_dict = {}
    design_output_dict = {}
    design_timing_dict = {}
    with open(filename) as f:
        for line in f.readlines():
            if line.strip():
                type, content = line.strip().split(' ', 1)
                if type == 'module':
                    design_name, port_list = content.strip().split(' ', 1)
                    design_timing_dict[design_name] = {}
                if type == 'input' and design_name:
                    input_list = content.strip().split(',')
                    design_input_dict[design_name] = [k.strip() for k in input_list]
                if type == 'output' and design_name:
                    output_list = content.strip().split(',')
                    design_output_dict[design_name] = [k.strip() for k in output_list]
                if type == 'timing' and design_name:
                    path, time = content.strip().split(',', 1)
                    input, output = path.split()
                    if input in design_timing_dict[design_name].keys():
                        design_timing_dict[design_name][input][output] = float(time)
                    else:
                        design_timing_dict[design_name][input]= {output: float(time)}
    return design_input_dict, design_output_dict, design_timing_dict

def ast_parser(filename):
    module_wire_dict = {}
    module_port_arg_dict = {}
    module_design_dict = {}
    module_list = []
    wire_list = []
    raw_input_list = []
    raw_output_list = []
    this_module = ''
    this_net = ''
    this_portarg = ''

    with open(filename) as f:
        for line in f.readlines():
            if line:
                content_list = line.strip().split()
                type = content_list[0]
                name = content_list[1]
                if type == 'input':
                    raw_input_list.append(name)
                if type == 'output':
                    raw_output_list.append(name)
                if type == 'module':
                    this_module = name
                    module_design_dict[this_module] = content_list[2]
                    module_wire_dict[this_module] = []
                    module_port_arg_dict[this_module] = {}
                if type == 'PortArg':
                    this_portarg = name
                if type == 'port' and this_module:
                    module_wire_dict[this_module].append(name)
                    this_net = name
                    module_port_arg_dict[this_module][this_net] = this_portarg
                if type == 'width' and this_net:
                    if this_net in module_wire_dict[this_module]:
                        module_wire_dict[this_module].remove(this_net)
                        del module_port_arg_dict[this_module][this_net]
                        new_net_name = this_net+'_index_'+str(name)
                        module_wire_dict[this_module].append(new_net_name)
                        module_port_arg_dict[this_module][new_net_name] = this_portarg
                    ##solve INVD1 U76 ( .I(1'b1), .ZN(data_out[12]) );
                    else:
                        wire_name = 'VDD'
                        module_wire_dict[this_module].append(wire_name)
                        module_port_arg_dict[this_module][wire_name] = this_portarg
    for k, v in module_wire_dict.items():
        module_list.append(k)
        wire_list+=v
    wire_list = list(set(wire_list))
    return module_wire_dict, module_port_arg_dict, module_design_dict, module_list, wire_list, raw_input_list, raw_output_list

def main_progress():
    design_input_dict, design_output_dict, design_timing_dict = lib_parser('LV_lib.v') #BM_lib.v
    module_wire_dict, module_port_arg_dict, module_design_dict, module_list, wire_list, raw_input_list, raw_output_list = ast_parser(input_file)
    port_list = []
    port_wire_dict = {}
    port_design_dict = {}
    port_attr_dict = {}
    port_origin_name_dict = {}
    port_module_dict = {}
    directed_graph = {}
    module_port_dict = {}
    edge_attr_dict = {}
    edge_delay_dict = {}
    path_latency_dict = {}
    path_outeredge_dict = {}


    a_list = []
    for m in module_list:
        if module_design_dict[m] not in design_input_dict.keys():
            # print module_design_dict[m], m
            a_list.append(module_design_dict[m])
    if set(a_list):
        print set(a_list)
        time.sleep(100)

    for m in module_list:
        module_port_dict[m] = []
        for wire, port in module_port_arg_dict[m].items():
            port_name = m+'_port_'+port
            port_list.append(port_name)
            port_wire_dict[port_name] = wire
            port_design_dict[port_name] = module_design_dict[m]

            if port in design_input_dict[module_design_dict[m]]:
                port_attr_dict[port_name] = 'input'
            elif port in design_output_dict[module_design_dict[m]]:
                port_attr_dict[port_name] = 'output'
            else:
                print 'error', port_name
            port_origin_name_dict[port_name] = port
            module_port_dict[m].append(port_name)
            port_module_dict[port_name] = m
        m_input_port_list = [p for p in module_port_dict[m] if port_attr_dict[p] == 'input']
        m_output_port_list = [p for p in module_port_dict[m] if port_attr_dict[p] == 'output']
        for start_port in m_input_port_list:
            for end_port in m_output_port_list:
                if directed_graph.has_key(start_port):
                    directed_graph[start_port].append(end_port)
                else:
                    directed_graph[start_port] = [end_port,]
                edge_name = start_port+'->'+end_port
                edge_attr_dict[edge_name] = 'inner'
                edge_delay_dict[edge_name] = design_timing_dict[module_design_dict[m]][port_origin_name_dict[start_port]][port_origin_name_dict[end_port]]

    raw_input_wire_list = []
    # print raw_input_list
    for raw_input in raw_input_list:
        regex = raw_input+'_index_'
        for wire in wire_list:
            if wire == raw_input:
                raw_input_wire_list.append(wire)
            elif regex in wire:
                raw_input_wire_list.append(wire)
    # print raw_input_wire_list
    # raw_input_wire_list.remove('clock')
    # raw_input_wire_list.remove('reset')
    module_input_port_list = []
    for w in raw_input_wire_list:
        if w not in ['GND', 'VDD', 'CK', 'clk']:
            new_port = 'module_port_'+w
            port_list.append(new_port)
            port_attr_dict[new_port] = 'output' #The top module input port seems like a output port to the next module
            port_wire_dict[new_port] = w
            module_input_port_list.append(new_port)
            port_origin_name_dict[new_port] = new_port
            port_module_dict[new_port] = 'TOP_INPUT'

    # print module_input_port_list

    raw_output_wire_list = []
    for raw_output in raw_output_list:
        regex = raw_output+'_index'
        for wire in wire_list:
            if wire == raw_output:
                raw_output_wire_list.append(wire)
            elif regex in wire:
                raw_output_wire_list.append(wire)
    # print raw_output_list
    # print raw_output_wire_list
    module_output_port_list = []
    for w in raw_output_wire_list:
        new_port = 'module_port_'+w
        port_list.append(new_port)
        port_attr_dict[new_port] = 'input' #The top module output port seems like a input port to the previous module
        port_wire_dict[new_port] = w
        module_output_port_list.append(new_port)
        port_origin_name_dict[new_port] = new_port
        port_module_dict[new_port] = 'TOP_OUTPUT'


    # print module_output_port_list

    # time.sleep(10)
    raw_input_port_list = [port for port in port_list if port_wire_dict[port] in raw_input_wire_list and port_attr_dict[port] == 'input']
    raw_output_port_list = [port for port in port_list if port_wire_dict[port] in raw_output_wire_list and port_attr_dict[port] == 'output']
    clock_port_list = [port for port in port_list if port_wire_dict[port] == 'clock']
    reset_port_list = [port for port in port_list if port_wire_dict[port] == 'reset']
    D_port_list = [port for port in port_list if port_origin_name_dict[port] == 'D' and port_design_dict[port] == 'DFQD1']
    DFF_CK_port_list = [port for port in port_list if port_origin_name_dict[port] == 'CP' and port_design_dict[port] == 'DFQD1']

    output_port_list = [p for p in port_list if port_attr_dict[p] == 'output']
    input_port_list = [p for p in port_list if port_attr_dict[p] == 'input']
    for start_port in output_port_list:
        wire = port_wire_dict[start_port]
        for end_port in input_port_list:
            if port_wire_dict[end_port] == wire:
                if directed_graph.has_key(start_port):
                    directed_graph[start_port].append(end_port)
                else:
                    directed_graph[start_port] = [end_port,]
                edge_name = start_port+'->'+end_port
                edge_attr_dict[edge_name] = 'outer'
                edge_delay_dict[edge_name] = 0.0

    # print directed_graph

    path_start_port_list = list(set(module_input_port_list)|set(DFF_CK_port_list))
    path_end_port_list = list(set(D_port_list)|set(module_output_port_list))
    # path_start_port_list = list(set(DFF_CK_port_list))
    # path_end_port_list = list(set(D_port_list))

    path_num = 0

    startportlist_list = [path_start_port_list]
    endportlist_list = [path_end_port_list]

    part_path_list_list = []
    for path_start_port_list, path_end_port_list in zip(startportlist_list, endportlist_list):
        part_path_list = []
        for start_port in path_start_port_list:
            for end_port in path_end_port_list:
                if port_module_dict[start_port] != port_module_dict[end_port]:
                    paths = find_all_paths(directed_graph, start_port, end_port, D_port_list)
                    if paths:
                        for path in paths:
                            path_num+=1
                            path_name = '->'.join(path)
                            path_latency_dict[path_name] = 0.0
                            path_outeredge_dict[path_name] = []
                            for index, port in enumerate(path):
                                if index != len(path) - 1:
                                    edge_name = port+'->'+path[index+1]
                                    path_latency_dict[path_name] += edge_delay_dict[edge_name]
                                    if edge_attr_dict[edge_name] == 'outer':
                                        path_outeredge_dict[path_name].append(edge_name)
                            part_path_list.append(path_name)
                        print start_port, end_port, path_num
        part_path_list_list.append(part_path_list)
        print len(part_path_list)
    # print path_latency_dict

    path_list = path_latency_dict.keys()
    outer_edge_list = [edge for edge in edge_delay_dict.keys() if edge_attr_dict[edge] == 'outer']
    inner_edge_list = [edge for edge in edge_delay_dict.keys() if edge_attr_dict[edge] == 'inner']
    high_bound = max(path_latency_dict.values())
    low_bound = high_bound/3


    print high_bound
    print min(path_latency_dict.values())
    print len(path_list)

    edge_delay_dict_bak = dict.copy(edge_delay_dict)
    path_latency_dict_bak = dict.copy(path_latency_dict)

    ######## Original version
    buffer_kinds = ['INVD0', 'BUFFD0', 'DEL1','DEL0']
    buffer_delay_dict = {'INVD0':0.643122, 'BUFFD0':1.396066, 'DEL0':9.4457185, 'DEL1':17.2656825}
    buffer_area_dict = {'INVD0':1.08, 'BUFFD0':1.44, 'DEL0':4.68,'DEL1':6.12}

    outeredge_path_dict = {outer_edge:[] for outer_edge in outer_edge_list}
    for k, v in path_outeredge_dict.items():
        for outeredge in v:
            outeredge_path_dict[outeredge].append(k)
    edge_delay_dict, path_latency_dict = greedy_mostpathsharing_first(buffer_kinds, buffer_delay_dict, buffer_area_dict, outer_edge_list, path_list, edge_attr_dict, edge_delay_dict, high_bound, low_bound, path_latency_dict, path_outeredge_dict, outeredge_path_dict)

def greedy_assign_buffer_onlyhighbound(d_slack, d_desired, buffer_kinds, buffer_delay_dict, buffer_area_dict):
    upper_bound = d_slack
    sorted_buffer_list = sorted(buffer_kinds, key=lambda x:buffer_delay_dict[x], reverse=True)
    buffer_number_dict = {}
    delay_result = 0
    for buffer in sorted_buffer_list:
        buffer_delay = buffer_delay_dict[buffer]
        if buffer_delay > upper_bound - delay_result:
            buffer_number_dict[buffer] = 0
        else:
            max_num = int((upper_bound - delay_result)/buffer_delay)
            buffer_number_dict[buffer] = max_num
            delay_result += max_num * buffer_delay
    print buffer_number_dict
    return sum(buffer_number_dict[x]*buffer_delay_dict[x] for x in buffer_kinds)

def DP_assign_buffer_onlyhighbound(d_slack, d_desired, buffer_kinds, buffer_delay_dict, buffer_area_dict):
    sorted_buffer_list = sorted(buffer_kinds, key=lambda x:buffer_delay_dict[x])
    cache_dict = {}
    buffer_list = dp_max_delay_highbound_only(sorted_buffer_list, d_slack, cache_dict, buffer_delay_dict)
    return sum(buffer_delay_dict[i] for i in buffer_list), sum(buffer_area_dict[i] for i in buffer_list)

def dp_max_delay_highbound_only(buffer_list, high_bound, cache_dict, buffer_delay_dict):
    if buffer_delay_dict[buffer_list[0]] > high_bound: return []
    if high_bound in cache_dict:
        # print 'cache hit'
        return cache_dict[high_bound]
    else:
        result = max([dp_max_delay_highbound_only(buffer_list, high_bound - buffer_delay_dict[n], cache_dict, buffer_delay_dict) +[n] for n in buffer_list if buffer_delay_dict[n] < high_bound], key=lambda x: sum(buffer_delay_dict[i] for i in x))
        cache_dict[high_bound] = result
        return result

def DP_assign_buffer_bothbound(d_slack, d_desired, buffer_kinds, buffer_delay_dict, buffer_area_dict):
    sorted_buffer_list = sorted(buffer_kinds, key=lambda x:buffer_delay_dict[x])
    cache_dict = {}
    buffer_list = dp_min_area_bothbound(sorted_buffer_list, d_slack, d_desired, buffer_delay_dict, buffer_area_dict, cache_dict)
    # print buffer_list, sum(buffer_area_dict[i] for i in buffer_list), sum(buffer_delay_dict[i] for i in buffer_list)
    return sum(buffer_delay_dict[i] for i in buffer_list), sum(buffer_area_dict[i] for i in buffer_list)

def dp_min_area_bothbound(buffer_list, high_bound, low_bound, buffer_delay_dict, buffer_area_dict, cache_dict):
    # if low_bound <= buffer_delay_dict[buffer_list[0]] <= high_bound: return [buffer_list[0]]
    if low_bound <= 0: return []
    if buffer_delay_dict[buffer_list[0]] > high_bound: return []
    if high_bound in cache_dict:
        # print 'cache hit'
        return cache_dict[high_bound]
    else:
        # print high_bound, low_bound, cache_dict
        result_list =[dp_min_area_bothbound(buffer_list, high_bound - buffer_delay_dict[n], low_bound - buffer_delay_dict[n], buffer_delay_dict, buffer_area_dict, cache_dict)+[n] for n in buffer_list if buffer_delay_dict[n] < high_bound]
        result = min(result_list, key=lambda x: sum(buffer_area_dict[i] for i in x))
        # print result_list, high_bound, low_bound, result
        cache_dict [high_bound] = result
        return result
    # return min(d_slack, d_desired)

def greedy_mostpathsharing_first(buffer_kinds, buffer_delay_dict, buffer_area_dict, outer_edge_list, path_list, edge_attr_dict, edge_delay_dict, high_bound, low_bound, path_latency_dict, path_outeredge_dict, outeredge_path_dict):
    added_area = 0.0
    short_path_list = [path for path in path_list if path_latency_dict[path] < low_bound]
    print len(short_path_list)
    outeredge_shortpath_dict = {k:[p for p in v if path_latency_dict[p] < low_bound] for k,v in outeredge_path_dict.items()}
    e = max(outer_edge_list, key=lambda k: len(outeredge_shortpath_dict[k]))
    start_time = time.time()
    while short_path_list:
        # print e, len(outeredge_shortpath_dict[e]), len(outeredge_path_dict[e])
        if len(outeredge_shortpath_dict[e]) > 0:
            d_slack = high_bound - path_latency_dict[max(outeredge_path_dict[e], key=lambda k: path_latency_dict[k])]
            d_desired = low_bound - path_latency_dict[min(outeredge_path_dict[e], key=lambda k: path_latency_dict[k])]
            # d = min(d_slack, d_desired)
            if d_slack <= d_desired:
                # d = greedy_assign_buffer_onlyhighbound(d_slack, d_desired, buffer_kinds, buffer_delay_dict, buffer_area_dict)
                d, area = DP_assign_buffer_onlyhighbound(d_slack, d_desired, buffer_kinds, buffer_delay_dict, buffer_area_dict)
            else:
                d, area = DP_assign_buffer_bothbound(d_slack, d_desired, buffer_kinds, buffer_delay_dict, buffer_area_dict)
            #update graph
            outer_edge_list.remove(e)
            added_area += area
            if d:
                deleted_shortpath_list = []
                for p in outeredge_path_dict[e]:

                    path_latency_dict[p] += d

                short_path_list = [path for path in path_list if path_latency_dict[path] < low_bound]
                outeredge_shortpath_dict = {k:[p for p in v if path_latency_dict[p] < low_bound] for k,v in outeredge_path_dict.items()}
                e = max(outer_edge_list, key=lambda k: len(outeredge_shortpath_dict[k]))
            else:
                e = max(outer_edge_list, key=lambda k: len(outeredge_shortpath_dict[k]))
            # print len(short_path_list)

    end_time = time.time()
    print "After buffer insertion"
    print "Max path delay", max(path_latency_dict[p] for p in path_list)
    print "Min path delay", min(path_latency_dict[p] for p in path_list)
    print "Used buffer area", added_area
    print "Execute time:", end_time - start_time
    return edge_delay_dict, path_latency_dict

def discrete_insertion(buffer_kinds, buffer_delay_dict, buffer_area_dict, outer_edge_list, path_list, edge_attr_dict, edge_delay_dict, high_bound, low_bound, path_latency_dict):

    all_buffer_list = []
    buffer_kind_dict = {}
    outer_edge_buffer_dict = {}
    buffer_number_dict = {}
    for buffer in buffer_kinds:
        for outer_edge in outer_edge_list:
            buffer_name = outer_edge+'_'+buffer
            all_buffer_list.append(buffer_name)
            buffer_kind_dict[buffer_name] = buffer
            if outer_edge_buffer_dict.has_key(outer_edge):
                outer_edge_buffer_dict[outer_edge].append(buffer_name)
            else:
                outer_edge_buffer_dict[outer_edge] = [buffer_name,]


    prob = LpProblem("Buffer Insertion", LpMinimize)
    buffer_vars = LpVariable.dicts("Buffer", all_buffer_list, 0, None, LpInteger)
    vars_buffer_dict = {str(buffer_vars[i]):i for i in all_buffer_list}

    prob += lpSum([buffer_area_dict[buffer_kind_dict[i]]*buffer_vars[i] for i in all_buffer_list])

    # for path in random.sample(path_list, len(path_list)/4):
    for path in path_list:
        port_list = path.split('->')
        inner_edges = []
        outer_edges = []
        for index, port in enumerate(port_list):
            if index != len(port_list) - 1:
                edge_name = port+'->'+port_list[index+1]
                if edge_attr_dict[edge_name] == 'inner':
                    inner_edges.append(edge_name)
                elif edge_attr_dict[edge_name] == 'outer':
                    outer_edges.append(edge_name)
                else:
                    print 'wrong edge:', edge_name
        initial_delay = sum(edge_delay_dict[e] for e in inner_edges)
        initial_delay += sum(edge_delay_dict[e] for e in outer_edges)
        # max_outer_delay = 5.0
        high_bound = high_bound
        low_bound = low_bound
        max_outer_delay = high_bound - initial_delay
        min_outer_delay = low_bound - initial_delay
        path_buffer_list = []
        for edge in outer_edges:
            path_buffer_list += outer_edge_buffer_dict[edge]

        prob += lpSum(buffer_delay_dict[buffer_kind_dict[i]]*buffer_vars[i] for i in path_buffer_list) <= max_outer_delay
        prob += lpSum(buffer_delay_dict[buffer_kind_dict[i]]*buffer_vars[i] for i in path_buffer_list) >= min_outer_delay



    prob.writeLP("BufferInsertion.lp")

    start_time = time.time()
    prob.solve()
    end_time = time.time()
    print "Execute time:", end_time - start_time

    print "Status:", LpStatus[prob.status]

    if LpStatus[prob.status] != 'Optimal':
        print 'Failed'
        return edge_delay_dict, path_latency_dict

    print "Total area cost", value(prob.objective)

    print "Constraints number", prob.numConstraints()
    print "Variable number", prob.numVariables()

    buffer_count_dict = {}
    for v in prob.variables():
        if v.name != '__dummy':
            buffer_name = vars_buffer_dict[v.name]
            buffer_number_dict[buffer_name] = v.varValue
            buffer_kind = buffer_kind_dict[buffer_name]
            if buffer_count_dict.has_key(buffer_kind):
                buffer_count_dict[buffer_kind] += v.varValue
            else:
                buffer_count_dict[buffer_kind] = v.varValue

    for k,v in buffer_count_dict.items():
        if v:
            print k,v

    for outer_edge in outer_edge_list:
        edge_delay_dict[outer_edge] += sum(buffer_number_dict[b]*buffer_delay_dict[buffer_kind_dict[b]] for b in outer_edge_buffer_dict[outer_edge])

    print "Before buffer insertion"
    print "Max path delay", max(path_latency_dict[p] for p in path_list)
    print "Min path delay", min(path_latency_dict[p] for p in path_list)

    for path in path_list:
        port_list = path.split('->')
        new_latency = 0.0
        for index, port in enumerate(port_list):
            if index != len(port_list) - 1:
                edge_name = port+'->'+port_list[index+1]
                new_latency += edge_delay_dict[edge_name]
        path_latency_dict[path] = new_latency
        # if new_latency == 0.09387:
        #     print path
        # if new_latency != path_latency_dict[path]:
            # print path, new_latency, path_latency_dict[path]

    print "After buffer insertion"
    print "Max path delay", max(path_latency_dict[p] for p in path_list)
    print "Min path delay", min(path_latency_dict[p] for p in path_list)

    print "\n"

    return edge_delay_dict, path_latency_dict, value(prob.objective), end_time-start_time

if __name__ == '__main__':
    main_progress()