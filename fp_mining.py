import collections
import json

from graph import Graph
from graph import VACANT_GRAPH_ID

data_dir = "./data/"

# 将点类型的 name 字段映射为整数
name_mapping = {'Jobs': 0, 'Mike': 1, 'John': 2}

card_id_offset = 800000

# 辅助函数
def map_name(value):
    return name_mapping.get(value, -1)

def decode_name(value):
    for k, v in name_mapping.items():
        if v == value:
            return k
    return "Unknown"

def extract_last_char_as_int(value):
    try:
        return int(str(value)[-1])
    except ValueError:
        print("Error extracting last character as int")
        return -1

def convert_amt_to_int(value):
    try:
        return int(float(value))
    except ValueError:
        print("Error converting value to int")
        return -1

def map_card_id(value):
    return int(value) + card_id_offset

# 直接从文件中读取数据并构建图
def construct_graph(data_dir):
    graph = Graph(gid=0)
    edge_attributes_index = collections.defaultdict(list)

    # 读取并处理 account 文件
    try:
        with open(data_dir + "account", "r") as file:
            for line in file:
                id_str, name = line.strip().split(",")[:2]
                vid = int(id_str)
                name_int = map_name(name)
                graph.add_vertex(vid, {'name': name_int})
    except Exception as e:
        print(f"Error reading account file: {e}")

    # 读取并处理 card 文件
    try:
        with open(data_dir + "card", "r") as file:
            for line in file:
                id_str, name = line.strip().split(",")[:2]
                vid = map_card_id(id_str)
                name_int = map_name(name)
                graph.add_vertex(vid, {'name': name_int})
    except Exception as e:
        print(f"Error reading card file: {e}")

    # 读取并处理 account_to_account 文件
    try:
        with open(data_dir + "account_to_account", "r") as file:
            for line in file:
                parts = line.strip().split(",")
                source_id = int(parts[0])
                target_id = int(parts[1])
                amt = convert_amt_to_int(parts[3])
                strategy_name = extract_last_char_as_int(parts[4])
                buscode = extract_last_char_as_int(parts[6])
                graph.add_edge(
                    frm=source_id,
                    to=target_id,
                    attributes={'amt': amt, 'strategy_name': strategy_name, 'buscode': buscode}
                )

                name_source = graph.vertices[source_id].attributes['name']
                name_target = graph.vertices[target_id].attributes['name']
                key = (name_source, name_target, amt, strategy_name, buscode)
                edge_attributes_index[key].append((source_id, target_id))
    except Exception as e:
        print(f"Error reading account_to_account file: {e}")

    # 读取并处理 account_to_card 文件
    try:
        with open(data_dir + "account_to_card", "r") as file:
            for line in file:
                parts = line.strip().split(",")
                source_id = int(parts[0])
                target_id = map_card_id(parts[1])
                amt = convert_amt_to_int(parts[3])
                strategy_name = extract_last_char_as_int(parts[4])
                buscode = extract_last_char_as_int(parts[6])
                graph.add_edge(
                    frm=source_id,
                    to=target_id,
                    attributes={'amt': amt, 'strategy_name': strategy_name, 'buscode': buscode}
                )

                name_source = graph.vertices[source_id].attributes['name']
                name_target = graph.vertices[target_id].attributes['name']
                key = (name_source, name_target, amt, strategy_name, buscode)
                edge_attributes_index[key].append((source_id, target_id))
    except Exception as e:
        print(f"Error reading account_to_card file: {e}")

    print("Graph construction completed.")
    print(f"Number of vertices of origin graph: {graph.get_num_vertices()}")
    print(f"Number of edges of origin graph: {graph.get_num_edges()}")
    print(f"Number of patterns in origin graph: {len(edge_attributes_index)}")

    return graph, edge_attributes_index


def pruning_1edge_frequent_subgraph(min_support):
    """Generate frequent subgraphs with one edge."""
    origin_graph, edge_attributes_index = construct_graph(data_dir)
    fre1_subgraph = Graph(gid=VACANT_GRAPH_ID)
    fre1_patterns_index = collections.defaultdict(list)

    for key, edge_list in edge_attributes_index.items():
        if len(edge_list) >= min_support:
            fre1_patterns_index[key] = edge_list
            name_source, name_target, amt, strategy_name, buscode = key
            for source_id, target_id in edge_list:
                fre1_subgraph.add_vertex(source_id, {'name': name_source})
                fre1_subgraph.add_vertex(target_id, {'name': name_target})
                fre1_subgraph.add_edge(
                    frm=source_id,
                    to=target_id,
                    attributes={'amt': amt, 'strategy_name': strategy_name, 'buscode': buscode}
                )
    
    print("1 edge frequent subgraph generation completed.")
    print(f"Number of vertices of frequent 1-edge subgraph: {fre1_subgraph.get_num_vertices()}")
    print(f"Number of edges of frequent 1-edge subgraph: {fre1_subgraph.get_num_edges()}")
    print(f"Number of frequent 1-edge patterns: {len(fre1_patterns_index)}")

    return fre1_subgraph, fre1_patterns_index


def pruning_2edge_frequent_subgraph(fre1_subgraph, fre1_patterns_index, min_support):
    """Generate frequent subgraphs with two edges."""
    sub_2e_patterns_index = collections.defaultdict(list)

    for key_edge1, edge_list1 in fre1_patterns_index.items():
        name_v1, name_v2, amt_e1, strategy_name_e1, buscode_e1 = key_edge1
        for vid1, vid2 in edge_list1:
            v2 = fre1_subgraph.vertices[vid2]
            for vid3, edge_list2 in v2.edges.items():
                if vid3 == vid1:
                    continue
                v3 = fre1_subgraph.vertices[vid3]
                for edge2 in edge_list2:
                    name_v3 = v3.attributes['name']
                    amt_e2 = edge2.attributes['amt']
                    strategy_name_e2 = edge2.attributes['strategy_name']
                    buscode_e2 = edge2.attributes['buscode']
                    key_edge2 = (name_v2, name_v3, amt_e2, strategy_name_e2, buscode_e2)
                    if key_edge1 == key_edge2:
                        continue
                    key = (name_v1, name_v2, name_v3, amt_e1, strategy_name_e1, buscode_e1, amt_e2, strategy_name_e2, buscode_e2)
                    sub_2e_patterns_index[key].append((vid1, vid2, vid3))

    fre2_patterns_index = {
        key: edge_list for key, edge_list in sub_2e_patterns_index.items() if len(edge_list) >= min_support
    }
    print("2 edge frequent subgraph generation completed.")
    print(f"Number of frequent 2-edge patterns: {len(fre2_patterns_index)}")
    return fre2_patterns_index


def pruning_3edge_frequent_subgraph(fre1_subgraph, fre2_patterns_index, min_support):
    sub_3e_patterns_mode1_index = collections.defaultdict(int)
    sub_3e_patterns_mode2_index = collections.defaultdict(int)

    for key_e_12, edge_list in fre2_patterns_index.items():
        name_v1, name_v2, name_v3, amt_e1, strategy_name_e1, buscode_e1, amt_e2, strategy_name_e2, buscode_e2 = key_e_12
        key_e_1 = (name_v1, name_v2, amt_e1, strategy_name_e1, buscode_e1)
        key_e_2 = (name_v2, name_v3, amt_e2, strategy_name_e2, buscode_e2)
        for vid1, vid2, vid3 in edge_list:
            v3 = fre1_subgraph.vertices[vid3]
            for vid4, edge_list2 in v3.edges.items():
                if vid4 == vid2:
                    continue
                v4 = fre1_subgraph.vertices[vid4]
                for edge3 in edge_list2:
                    name_v4 = v4.attributes['name']
                    amt_e3 = edge3.attributes['amt']
                    strategy_name_e3 = edge3.attributes['strategy_name']
                    buscode_e3 = edge3.attributes['buscode']
                    key_e_3 = (name_v3, name_v4, amt_e3, strategy_name_e3, buscode_e3)
                    key_e_23 = (name_v2, name_v3, name_v4, amt_e2, strategy_name_e2, buscode_e2, amt_e3, strategy_name_e3, buscode_e3)
                    if key_e_23 not in fre2_patterns_index.keys() or key_e_1 == key_e_3:
                        continue
                    key = (name_v1, name_v2, name_v3, name_v4, 
                           amt_e1, strategy_name_e1, buscode_e1, 
                           amt_e2, strategy_name_e2, buscode_e2, 
                           amt_e3, strategy_name_e3, buscode_e3)
                    if vid1 != vid4:
                        sub_3e_patterns_mode1_index[key] += 1
                    else:
                        key_e_31 = (name_v3, name_v1, name_v2, 
                                    amt_e3, strategy_name_e3, buscode_e3, 
                                    amt_e1, strategy_name_e1, buscode_e1)
                        if key_e_31 in fre2_patterns_index.keys():
                            sub_3e_patterns_mode2_index[key] += 1

    fre3_patterns_mode1_index = {
        key: count for key, count in sub_3e_patterns_mode1_index.items() if count >= min_support
    }

    fre3_patterns_mode2_index = {
        key: count for key, count in sub_3e_patterns_mode2_index.items() if count >= min_support
    }

    print("3 edge frequent subgraph generation completed.")
    print(f"Number of frequent 3-edge patterns (mode 1): {len(fre3_patterns_mode1_index)}")
    print(f"Number of frequent 3-edge patterns (mode 2): {len(fre3_patterns_mode2_index)}")

    return fre3_patterns_mode1_index, fre3_patterns_mode2_index


def generate_result_json(fre3_patterns_mode1_index, fre3_patterns_mode2_index):
    result = []

    for key, support in fre3_patterns_mode1_index.items():
        nodes = []
        edges = []
        name_v1, name_v2, name_v3, name_v4, amt_e1, strategy_name_e1, buscode_e1, amt_e2, strategy_name_e2, buscode_e2, amt_e3, strategy_name_e3, buscode_e3 = key
        nodes.append({
            "node_id": "0",
            "name": decode_name(name_v1)
        })
        nodes.append({
            "node_id": "1",
            "name": decode_name(name_v2)
        })
        nodes.append({
            "node_id": "2",
            "name": decode_name(name_v3)
        })
        nodes.append({
            "node_id": "3",
            "name": decode_name(name_v4)
        })
        edges.append({
            "source_node_id": "0",
            "target_node_id": "1",
            "amt": str(amt_e1),
            "strategy_name": str(strategy_name_e1),
            "buscode": str(buscode_e1)
        })
        edges.append({
            "source_node_id": "1",
            "target_node_id": "2",
            "amt": str(amt_e2),
            "strategy_name": str(strategy_name_e2),
            "buscode": str(buscode_e2)
        })
        edges.append({
            "source_node_id": "2",
            "target_node_id": "3",
            "amt": str(amt_e3),
            "strategy_name": str(strategy_name_e3),
            "buscode": str(buscode_e3)
        })
        result.append({
            "frequency": support,
            "nodes": nodes,
            "edges": edges
        })


    for key, support in fre3_patterns_mode2_index.items():
        nodes = []
        edges = []
        name_v1, name_v2, name_v3, name_v4, amt_e1, strategy_name_e1, buscode_e1, amt_e2, strategy_name_e2, buscode_e2, amt_e3, strategy_name_e3, buscode_e3 = key
        nodes.append({
            "node_id": "0",
            "name": decode_name(name_v1)
        })
        nodes.append({
            "node_id": "1",
            "name": decode_name(name_v2)
        })
        nodes.append({
            "node_id": "2",
            "name": decode_name(name_v3)
        })
        edges.append({
            "source_node_id": "0",
            "target_node_id": "1",
            "amt": str(amt_e1),
            "strategy_name": str(strategy_name_e1),
            "buscode": str(buscode_e1)
        })
        edges.append({
            "source_node_id": "1",
            "target_node_id": "2",
            "amt": str(amt_e2),
            "strategy_name": str(strategy_name_e2),
            "buscode": str(buscode_e2)
        })
        edges.append({
            "source_node_id": "2",
            "target_node_id": "0",
            "amt": str(amt_e3),
            "strategy_name": str(strategy_name_e3),
            "buscode": str(buscode_e3)
        })

    with open("result.json", "w") as file:
        json.dump(result, file, indent=2)

    print("Result JSON generation completed.")

fre1_subgraph, fre1_patterns_index = pruning_1edge_frequent_subgraph(10000)
fre2_patterns_index = pruning_2edge_frequent_subgraph(fre1_subgraph, fre1_patterns_index, 10000)
fre3_patterns_mode1_index, fre3_patterns_mode2_index = pruning_3edge_frequent_subgraph(fre1_subgraph, fre2_patterns_index, 10000)
generate_result_json(fre3_patterns_mode1_index, fre3_patterns_mode2_index)
