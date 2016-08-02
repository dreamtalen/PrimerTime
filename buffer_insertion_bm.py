import time
from pulp import *
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
    design_input_dict, design_output_dict, design_timing_dict = lib_parser('BM_lib.v')
    module_wire_dict, module_port_arg_dict, module_design_dict, module_list, wire_list, raw_input_list, raw_output_list = ast_parser("c432_netlist.AST")
    port_list = []
    port_wire_dict = {}
    port_design_dict = {}
    port_attr_dict = {}
    port_origin_name_dict = {}
    directed_graph = {}
    module_port_dict = {}
    edge_attr_dict = {}
    edge_delay_dict = {}
    path_latency_dict = {}

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
    for raw_input in raw_input_list:
        regex = raw_input+'_index_'
        for wire in wire_list:
            if wire == raw_input:
                raw_input_wire_list.append(wire)
            elif regex in wire:
                raw_input_wire_list.append(wire)
    # raw_input_wire_list.remove('clock')
    # raw_input_wire_list.remove('reset')

    raw_output_wire_list = []
    for raw_output in raw_output_list:
        regex = raw_output+'_index'
        for wire in wire_list:
            if wire == raw_output:
                raw_output_wire_list.append(wire)
            elif regex in wire:
                raw_output_wire_list.append(wire)

    raw_input_port_list = [port for port in port_list if port_wire_dict[port] in raw_input_wire_list and port_attr_dict[port] == 'input']
    raw_output_port_list = [port for port in port_list if port_wire_dict[port] in raw_output_wire_list and port_attr_dict[port] == 'output']
    clock_port_list = [port for port in port_list if port_wire_dict[port] == 'clock']
    reset_port_list = [port for port in port_list if port_wire_dict[port] == 'reset']
    D_port_list = [port for port in port_list if port_origin_name_dict[port] == 'D']

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

    path_start_port_list = list(set(raw_input_port_list) | set(clock_port_list))
    path_end_port_list = list(set(D_port_list) | set(raw_output_port_list))
    for start_port in path_start_port_list:
        for end_port in path_end_port_list:
            paths = find_all_paths(directed_graph, start_port, end_port, D_port_list)
            if paths:
                for path in paths:
                    path_name = '->'.join(path)
                    path_latency_dict[path_name] = 0.0
                    for index, port in enumerate(path):
                        if index != len(path) - 1:
                            edge_name = port+'=>'+path[index+1]
                            path_latency_dict[path_name] += edge_delay_dict[edge_name]

    # print path_latency_dict

    path_list = path_latency_dict.keys()
    outer_edge_list = [edge for edge in edge_delay_dict.keys() if edge_attr_dict[edge] == 'outer']
    inner_edge_list = [edge for edge in edge_delay_dict.keys() if edge_attr_dict[edge] == 'inner']
    high_bound = max(path_latency_dict.values())
    low_bound = high_bound/3

    print high_bound
    print min(path_latency_dict.values())
    # continuous_insertion(outer_edge_list, path_list, edge_attr_dict, edge_delay_dict, high_bound, path_latency_dict)
    discrete_insertion(outer_edge_list, path_list, edge_attr_dict, edge_delay_dict, high_bound, low_bound, path_latency_dict)

def discrete_insertion(outer_edge_list, path_list, edge_attr_dict, edge_delay_dict, high_bound, low_bound, path_latency_dict):
    ###RVT
    buffer_kinds = ['BUFFD0', 'BUFFD1', 'INVD0', 'INVD1', 'ND2D0', 'ND2D1', 'NR2D0', 'NR2D1']
    buffer_delay_dict = {'BUFFD0':0.02229, 'BUFFD1':0.02261, 'INVD0':0.009212, 'INVD1':0.007224, 'ND2D0':0.01299, 'ND2D1':0.01049, 'NR2D0':0.01514, 'NR2D1':0.01202}
    buffer_area_dict = {'BUFFD0':1.44, 'BUFFD1':1.44, 'INVD0':1.08, 'INVD1':1.08, 'ND2D0':1.44, 'ND2D1':1.44, 'NR2D0':1.44, 'NR2D1':1.44}
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

    for path in path_list:
        port_list = path.split('->')
        inner_edges = []
        outer_edges = []
        for index, port in enumerate(port_list):
            if index != len(port_list) - 1:
                edge_name = port+'=>'+port_list[index+1]
                if edge_attr_dict[edge_name] == 'inner':
                    inner_edges.append(edge_name)
                elif edge_attr_dict[edge_name] == 'outer':
                    outer_edges.append(edge_name)
                else:
                    print 'wrong edge:', edge_name
        inner_delay = sum(edge_delay_dict[e] for e in inner_edges)
        max_outer_delay = 5.0
        # max_outer_delay = high_bound - inner_delay
        min_outer_delay = low_bound - inner_delay
        path_buffer_list = []
        for edge in outer_edges:
            path_buffer_list += outer_edge_buffer_dict[edge]

        prob += lpSum(buffer_delay_dict[buffer_kind_dict[i]]*buffer_vars[i] for i in path_buffer_list) <= max_outer_delay
        prob += lpSum(buffer_delay_dict[buffer_kind_dict[i]]*buffer_vars[i] for i in path_buffer_list) >= min_outer_delay

    prob.writeLP("BufferInsertion.lp")

    prob.solve()

    print "Status:", LpStatus[prob.status]

    print "Total area cost", value(prob.objective)

    for v in prob.variables():
        buffer_name = vars_buffer_dict[v.name]
        buffer_number_dict[buffer_name] = v.varValue

    for outer_edge in outer_edge_list:
        edge_delay_dict[outer_edge] = sum(buffer_number_dict[b]*buffer_delay_dict[buffer_kind_dict[b]] for b in outer_edge_buffer_dict[outer_edge])

    path_latency_dict_final = {}
    for path in path_list:
        port_list = path.split('->')
        new_latency = 0.0
        for index, port in enumerate(port_list):
            if index != len(port_list) - 1:
                edge_name = port+'=>'+port_list[index+1]
                new_latency += edge_delay_dict[edge_name]
        path_latency_dict_final[path] = new_latency
        # if new_latency != path_latency_dict[path]:
            # print path, new_latency, path_latency_dict[path]
    print "Before buffer insertion"
    print "Max path delay", max(path_latency_dict.values())
    print "Min path delay", min(path_latency_dict.values())
    print "After buffer insertion"
    print "Max path delay", max(path_latency_dict_final.values())
    print "Min path delay", min(path_latency_dict_final.values())

def continuous_insertion(outer_edge_list, path_list, edge_attr_dict, edge_delay_dict, high_bound, path_latency_dict):
    prob = LpProblem("Buffer Insertion", LpMinimize)
    outer_edge_vars = LpVariable.dicts("OutEdge", outer_edge_list, 0)
    vars_edge_dict = {str(outer_edge_vars[i]):i for i in outer_edge_list}
    prob += lpSum([outer_edge_vars[i] for i in outer_edge_list])
    for path in path_list:
        port_list = path.split('->')
        inner_edges = []
        outer_edges = []
        for index, port in enumerate(port_list):
            if index != len(port_list) - 1:
                edge_name = port+'=>'+port_list[index+1]
                if edge_attr_dict[edge_name] == 'inner':
                    inner_edges.append(edge_name)
                elif edge_attr_dict[edge_name] == 'outer':
                    outer_edges.append(edge_name)
                else:
                    print 'wrong edge:', edge_name
        inner_delay = sum(edge_delay_dict[e] for e in inner_edges)
        max_outer_delay = high_bound - inner_delay
        min_outer_delay = 4.0 - inner_delay

        prob += lpSum(outer_edge_vars[i] for i in outer_edges) <= max_outer_delay
        prob += lpSum(outer_edge_vars[i] for i in outer_edges) >= min_outer_delay


    prob.writeLP("BufferInsertion.lp")

    prob.solve()

    print "Status:", LpStatus[prob.status]


    for v in prob.variables():
        edge_name = vars_edge_dict[v.name]
        edge_delay_dict[edge_name] = v.varValue

    print "Total Button delay", value(prob.objective)

    path_latency_dict_final = {}
    for path in path_list:
        port_list = path.split('->')
        new_latency = 0.0
        for index, port in enumerate(port_list):
            if index != len(port_list) - 1:
                edge_name = port+'=>'+port_list[index+1]
                new_latency += edge_delay_dict[edge_name]
        path_latency_dict_final[path] = new_latency
        # if new_latency != path_latency_dict[path]:
            # print path, new_latency, path_latency_dict[path]
    print "Before buffer insertion"
    print "Max path delay", max(path_latency_dict.values())
    print "Min path delay", min(path_latency_dict.values())
    print "After buffer insertion"
    print "Max path delay", max(path_latency_dict_final.values())
    print "Min path delay", min(path_latency_dict_final.values())

if __name__ == '__main__':
    main_progress()