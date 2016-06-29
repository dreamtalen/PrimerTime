import re
import time

def find_path(graph, start, end, reg_list=[], path=[]):
    path = path + [start]
    if start == end:
        return path
    if not graph.has_key(start):
        return None
    for node in graph[start]:
        if node not in path and node not in reg_list:
            newpath = find_path(graph, node, end, reg_list, path)
            if newpath: return newpath
    return None

def find_all_paths(graph, start, end, reg_list=[], path=[]):
    path = path + [start]
    if start == end:
        return [path]
    if not graph.has_key(start):
        return []
    paths = []
    for node in graph[start]:
        if (node not in path and node not in reg_list) or node == end :
            newpaths = find_all_paths(graph, node, end, reg_list, path)
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

if __name__ == '__main__':

    design_input_dict, design_output_dict, design_timing_dict = lib_parser('7lib.v')

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
    with open("7full.ast") as f:
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
                    module_wire_dict[this_module].remove(this_net)
                    del module_port_arg_dict[this_module][this_net]
                    new_net_name = this_net+'_index_'+str(name)
                    module_wire_dict[this_module].append(new_net_name)
                    module_port_arg_dict[this_module][new_net_name] = this_portarg
    # print module_wire_dict
    for k, v in module_wire_dict.items():
        module_list.append(k)
        wire_list+=v
    wire_list = list(set(wire_list))
    # print module_list
    # print wire_list
    wire_module_dict = {wire:[] for wire in wire_list}
    for module in module_list:
        for w in module_wire_dict[module]:
            wire_module_dict[w].append(module)
    # print wire_module_dict
    # print module_port_arg_dict
    graph = {}
    start_end_wire_dict = {}
    #undirected graph
    # for module in module_list:
    #     connected_module_list = []
    #     for net in module_wire_dict[module]:
    #         for connected_module in wire_module_dict[net]:
    #             connected_module_list.append(connected_module)
    #     connected_module_list = list(set(connected_module_list))
    #     connected_module_list.remove(module)
    #     graph[module] = connected_module_list

    for wire in wire_list:
        all_m_list = wire_module_dict[wire]
        input_m_list = [m for m in all_m_list if module_port_arg_dict[m][wire] in design_input_dict[module_design_dict[m]]]
        output_m_list = [m for m in all_m_list if module_port_arg_dict[m][wire] in design_output_dict[module_design_dict[m]]]
        if input_m_list and output_m_list:
            for input in input_m_list:
                for output in output_m_list:
                    if output in graph.keys():
                        graph[output].append(input)
                    else:
                        graph[output] = [input]
                    if output in start_end_wire_dict.keys():
                        start_end_wire_dict[output].update({input:wire})
                    else:
                        start_end_wire_dict.update({output:{input:wire}})
    # print graph
    # print start_end_wire_dict
    raw_input_wire_list = []
    for raw_input in raw_input_list:
        regex = raw_input+'_index_'
        for wire in wire_list:
            if wire == raw_input:
                raw_input_wire_list.append(wire)
            elif regex in wire:
                raw_input_wire_list.append(wire)
    raw_input_module_list = []
    for raw_input_wire in raw_input_wire_list:
        raw_input_module_list += wire_module_dict[raw_input_wire]
    raw_input_module_list = list(set(raw_input_module_list))

    raw_output_wire_list = []
    for raw_output in raw_output_list:
        regex = raw_output+'_index'
        for wire in wire_list:
            if wire == raw_output:
                raw_output_wire_list.append(wire)
            elif regex in wire:
                raw_output_wire_list.append(wire)
    raw_output_module_list = []
    for raw_output_wire in raw_output_wire_list:
        raw_output_module_list += wire_module_dict[raw_output_wire]
    raw_output_module_list = list(set(raw_output_module_list))

    reg_module_list = [ m for m in module_list if module_design_dict[m] == 'DFQD1']

    print raw_input_module_list
    print raw_output_module_list
    print reg_module_list


    #input -> reg D
    print '#input -> reg D'
    for startpoint in raw_input_module_list:
        for endpoint in reg_module_list:
            if startpoint != endpoint:
                paths = find_all_paths(graph, startpoint, endpoint)
                if paths:
                    print startpoint,'->',endpoint,paths
    #reg clk -> reg D
    print '#reg clk -> reg D'
    for startpoint in reg_module_list:
        for endpoint in reg_module_list:
            if startpoint != endpoint:
                paths = find_all_paths(graph, startpoint, endpoint)
                if paths:
                    print startpoint,'->',endpoint,paths
    #reg clk -> output
    print '#reg clk -> output'
    for startpoint in reg_module_list:
        for endpoint in raw_output_module_list:
            if startpoint != endpoint:
                paths = find_all_paths(graph, startpoint, endpoint, reg_list=reg_module_list)
                if paths:
                    print startpoint,'->',endpoint,paths
    #input -> output
    print '#input -> output'
    for startpoint in raw_input_module_list:
        for endpoint in raw_output_module_list:
            if startpoint != endpoint:
                paths = find_all_paths(graph, startpoint, endpoint, reg_list=reg_module_list)
                if paths:
                    print startpoint,'->',endpoint,paths
