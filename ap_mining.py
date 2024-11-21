import collections
import json

from graph import Graph
from graph import VACANT_GRAPH_ID

# 数据目录路径
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
    fre2_patterns_index = collections.defaultdict(list)

    for key_edge1, edge_list1 in fre1_patterns_index.items():
        name_v1, name_v2, amt_e1, strategy_name_e1, buscode_e1 = key_edge1
        for vid1, vid2 in edge_list1:
            v2 = fre1_subgraph.vertices[vid2]
            for vid3, edge_list2 in v2.edges.items():
                if vid3 == vid1:
                    continue
                for edge2 in edge_list2:
                    

