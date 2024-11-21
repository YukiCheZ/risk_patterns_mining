import collections
import itertools
import json
from my_graph import Graph
from my_graph import VACANT_GRAPH_ID
from my_graph import AUTO_EDGE_ID

# 数据目录路径
data_dir = "./data/"

# 将点类型的 name 字段映射为整数
name_mapping = {'Jobs': 0, 'Mike': 1, 'John': 2}
v_type_mapping = {'account': 0, 'card': 1}

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
        return -1

def convert_amt_to_int(value):
    try:
        return int(float(value))
    except ValueError:
        return 0

def map_card_id(value):
    return int(value) + card_id_offset

# 直接从文件中读取数据并构建图
def construct_graph(data_dir):
    graph = Graph()

    # 读取并处理 account 文件
    try:
        with open(data_dir + "account", "r") as file:
            for line in file:
                id_str, name = line.strip().split(",")[:2]
                vid = int(id_str)
                name_int = map_name(name)
                graph.add_vertex(vid, {'type' : v_type_mapping['account'], 'name': name_int})
                # graph.add_vertex(vid, {'name': name_int})
    except Exception as e:
        print(f"Error reading account file: {e}")

    # 读取并处理 card 文件
    try:
        with open(data_dir + "card", "r") as file:
            for line in file:
                id_str, name = line.strip().split(",")[:2]
                vid = map_card_id(id_str)
                name_int = map_name(name)
                graph.add_vertex(vid, {'type' :  v_type_mapping['card'], 'name': name_int})
                # graph.add_vertex(vid, {'name': name_int})
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
                    eid=None,  # 自动生成边ID
                    frm=source_id,
                    to=target_id,
                    attributes={'amt': amt, 'strategy_name': strategy_name, 'buscode': buscode}
                )
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
                    eid=None,  # 自动生成边ID
                    frm=source_id,
                    to=target_id,
                    attributes={'amt': amt, 'strategy_name': strategy_name, 'buscode': buscode}
                )
    except Exception as e:
        print(f"Error reading account_to_card file: {e}")

    print("Graph construction completed.")
    return graph


def pruning_1edge_frequent_subgraph(min_support):
    """Generate frequent subgraphs with one edge."""
    g = construct_graph(data_dir)
    subgraph = Graph(eid_auto_increment=False)
    for key, edge_list in g.edge_attribute_index.items():
        if(len(edge_list) >= min_support):
            for frm, to, eid in edge_list:
                frm_attrs = g.vertices[frm].attributes
                to_attrs = g.vertices[to].attributes
                edge_attributes = dict(key[0])
                subgraph.add_vertex(frm, frm_attrs)
                subgraph.add_vertex(to, to_attrs)
                subgraph.add_edge(eid, frm, to, edge_attributes)
    print("1 edge frequent subgraph generation completed.")

    return subgraph


def pruning_2edge_frequent_subgraph(sub_1e_g, min_support):
    """Generate frequent subgraphs with two edges."""
    sub_2e_patterns = collections.defaultdict(list)

    for key1, edge_list in sub_1e_g.edge_attribute_index.items():
        for frm1, to1, eid1 in edge_list:
            vertex_to1 = sub_1e_g.vertices[to1]
            for to2, edge_list2 in vertex_to1.edges.items():
                if to2 == frm1:
                    continue
                for edge2 in edge_list2:
                    key2 = (tuple(edge2.attributes.items()), 
                            tuple(vertex_to1.attributes.items()), 
                            tuple(sub_1e_g.vertices[to2].attributes.items()))
                    if key1 == key2:
                        continue
                    new_key = (key1, key2)
                    sub_2e_patterns[new_key].append((eid1, edge2.eid, frm1, to1, to2))
        
    frequent_sub_2e_patterns = {
        k: v for k, v in sub_2e_patterns.items() if len(v) >= min_support
    }

    print("2 edge frequent patterns generation completed.")
    return frequent_sub_2e_patterns


def pruning_3edge_frequent_subgraph(sub_1e_g, sub_2e_patterns, min_support):
    # 用于存储两种模式的三条边候选模式及其支持度
    sub_3e_patterns_mode1 = collections.defaultdict(int)
    sub_3e_patterns_mode2 = collections.defaultdict(int)

    for (key1, key2), edge_list in sub_2e_patterns.items():

        for eid1, eid2, vid1, vid2, vid3 in edge_list:
            v3 = sub_1e_g.vertices[vid3]
            for vid4, edge_list_right in v3.edges.items():
                if vid4 == vid2:
                    continue
                for edge3 in edge_list_right:
                    key3 = (tuple(edge3.attributes.items()), 
                            tuple(v3.attributes.items()), 
                            tuple(sub_1e_g.vertices[vid4].attributes.items()))
                    if (key2, key3) not in sub_2e_patterns.keys() or key1 == key3:
                        continue
                    new_key = (key1, key2, key3)
                    if vid4 != vid1:
                        sub_3e_patterns_mode1[new_key] += 1
                    else:
                        if (key3, key1) not in sub_2e_patterns.keys():
                            continue
                        sub_3e_patterns_mode2[new_key] += 1
        
    # Step 4: 返回满足支持度的模式
    frequent_sub_3e_patterns_mode1 = {
        k: v for k, v in sub_3e_patterns_mode1.items() if v >= min_support
    }
    frequent_sub_3e_patterns_mode2 = {
        k: v for k, v in sub_3e_patterns_mode2.items() if v >= min_support
    }

    return frequent_sub_3e_patterns_mode1, frequent_sub_3e_patterns_mode2


def generate_result_json(frequent_sub_3e_patterns_mode1, frequent_sub_3e_patterns_mode2):
    result = []

    for key, support in frequent_sub_3e_patterns_mode1.items():
        nodes = []
        edges = []
        key1, key2, key3 = key
        edge1_attrs, vertex1_attrs, vertex2_attrs = key1
        edge2_attrs, _, vertex3_attrs = key2
        edge3_attrs, _, vertex4_attrs = key3
        v1_att = dict(vertex1_attrs)
        v2_att = dict(vertex2_attrs)
        v3_att = dict(vertex3_attrs)
        v4_att = dict(vertex4_attrs)
        e1_att = dict(edge1_attrs)
        e2_att = dict(edge2_attrs)
        e3_att = dict(edge3_attrs)
        nodes.append({
            "node_id": "0",
            "name": decode_name(v1_att['name'])
        })
        nodes.append({
            "node_id": "1",
            "name": decode_name(v2_att['name'])
        })
        nodes.append({
            "node_id": "2",
            "name": decode_name(v3_att['name'])
        })
        nodes.append({
            "node_id": "3",
            "name": decode_name(v4_att['name'])
        })
        edges.append({
            "source_node_id": "0",
            "target_node_id": "1",
            "amt": str(e1_att['amt']),
            "strategy_name": str(e1_att['strategy_name']),
            "buscode": str(e1_att['buscode'])
        })
        edges.append({
            "source_node_id": "1",
            "target_node_id": "2",
            "amt": str(e2_att['amt']),
            "strategy_name": str(e2_att['strategy_name']),
            "buscode": str(e2_att['buscode'])
        })
        edges.append({
            "source_node_id": "2",
            "target_node_id": "3",
            "amt": str(e3_att['amt']),
            "strategy_name": str(e3_att['strategy_name']),
            "buscode": str(e3_att['buscode'])
        })
        result.append({
            "frequency": support,
            "nodes": nodes,
            "edges": edges
        })


    for key, support in frequent_sub_3e_patterns_mode2.items():
        nodes = []
        edges = []
        key1, key2, key3 = key
        edge1_attrs, vertex1_attrs, vertex2_attrs = key1
        edge2_attrs, _, vertex3_attrs = key2
        edge3_attrs, _, _ = key3
        v1_att = dict(vertex1_attrs)
        v2_att = dict(vertex2_attrs)
        v3_att = dict(vertex3_attrs)
        e1_att = dict(edge1_attrs)
        e2_att = dict(edge2_attrs)
        e3_att = dict(edge3_attrs)
        nodes.append({
            "node_id": "0",
            "name": decode_name(v1_att['name'])
        })
        nodes.append({
            "node_id": "1",
            "name": decode_name(v2_att['name'])
        })
        nodes.append({
            "node_id": "2",
            "name": decode_name(v3_att['name'])
        })
        edges.append({
            "source_node_id": "0",
            "target_node_id": "1",
            "amt": str(e1_att['amt']),
            "strategy_name": str(e1_att['strategy_name']),
            "buscode": str(e1_att['buscode'])
        })
        edges.append({
            "source_node_id": "1",
            "target_node_id": "2",
            "amt": str(e2_att['amt']),
            "strategy_name": str(e2_att['strategy_name']),
            "buscode": str(e2_att['buscode'])
        })
        edges.append({
            "source_node_id": "2",
            "target_node_id": "0",
            "amt": str(e3_att['amt']),
            "strategy_name": str(e3_att['strategy_name']),
            "buscode": str(e3_att['buscode'])
        })
        result.append({
            "frequency": support,
            "nodes": nodes,
            "edges": edges
        })

    with open("result.json", "w") as file:
        json.dump(result, file, indent=2)

    print("Result JSON generation completed.")

sub_1e_g = pruning_1edge_frequent_subgraph(10000)
fre_sub_2e_patterns = pruning_2edge_frequent_subgraph(sub_1e_g, 10000)
fre_sub_3e_patterns_mode1, fre_sub_3e_patterns_mode2 = pruning_3edge_frequent_subgraph(sub_1e_g, fre_sub_2e_patterns, 10000)
print(f"Number of frequent 3-edge subgraphs mode1: {len(fre_sub_3e_patterns_mode1)}")
print(f"Number of frequent 3-edge subgraphs mode2: {len(fre_sub_3e_patterns_mode2)}")
generate_result_json(fre_sub_3e_patterns_mode1, fre_sub_3e_patterns_mode2)
