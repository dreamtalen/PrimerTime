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
                edge_name = start_port+'=>'+end_port
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
                edge_name = start_port+'=>'+end_port
                edge_attr_dict[edge_name] = 'outer'
                edge_delay_dict[edge_name] = 0.0

    # print directed_graph

    path_start_port_list = list(set(module_input_port_list)|set(DFF_CK_port_list))
    path_end_port_list = list(set(D_port_list)|set(module_output_port_list))
    # path_start_port_list = ['DFF_948_dff_org_port_CP']
    # path_end_port_list = ['DFF_413_dff_org_port_D']

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
                            for index, port in enumerate(path):
                                if index != len(path) - 1:
                                    edge_name = port+'=>'+path[index+1]
                                    path_latency_dict[path_name] += edge_delay_dict[edge_name]
                            part_path_list.append(path_name)
                            print path_name
                        # print start_port, end_port, path_num
        part_path_list_list.append(part_path_list)
        print len(part_path_list)
    # print path_latency_dict

    path_list = path_latency_dict.keys()
    outer_edge_list = [edge for edge in edge_delay_dict.keys() if edge_attr_dict[edge] == 'outer']
    inner_edge_list = [edge for edge in edge_delay_dict.keys() if edge_attr_dict[edge] == 'inner']
    high_bound = max(path_latency_dict.values())
    low_bound = high_bound/3

    ###critical paths
    # for key, value in path_latency_dict.items():
    #     if value == high_bound: print key

    print high_bound
    print min(path_latency_dict.values())
    print len(path_list)


if __name__ == '__main__':
    main_progress()