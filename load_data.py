import pandas as pd
import networkx as nx
import gspan_mining as gSpan
import time 

data_dir = "./data/"

# 将点类型的 name 字段映射为整数
name_mapping = {'Jobs': 0, 'Mike': 1, 'John': 2}

def map_name(value):
    return name_mapping.get(value, -1)

# 将边类型的 strategy_name 和 buscode 字段的最后一个字符提取为整数
def extract_last_char_as_int(value):
    return int(str(value)[-1])

# 将边类型的 amt 字段提取为整数
def convert_amt_to_int(value):
    return int(float(value))

# 对点类型的id做唯一化处理
card_id_offset = 800000

def map_card_id(value):
    return int(value) + card_id_offset

def read_csv(file_path, usecols, names, converters):
    try:
        return pd.read_csv(file_path, sep=",", header=None, usecols=usecols, names=names, converters=converters)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return pd.DataFrame()

def construct_graph(data_dir):
    # 读取点数据
    account_df = read_csv(data_dir + "account", usecols=[0, 1], names=['id', 'name'], converters={'name': map_name})
    card_df = read_csv(data_dir + "card", usecols=[0, 1], names=['id', 'name'], converters={'id': map_card_id, 'name': map_name})

    # 读取边数据
    acc2acc_df = read_csv(data_dir + "account_to_account", usecols=[0, 1, 3, 4, 6], names=['source_id', 'target_id', 'amt', 'strategy_name', 'buscode'], converters={'amt': convert_amt_to_int, 'strategy_name': extract_last_char_as_int, 'buscode': extract_last_char_as_int})
    acc2card_df = read_csv(data_dir + "account_to_card", usecols=[0, 1, 3, 4, 6], names=['source_id', 'target_id', 'amt', 'strategy_name', 'buscode'], converters={'target_id': map_card_id, 'amt': convert_amt_to_int, 'strategy_name': extract_last_char_as_int, 'buscode': extract_last_char_as_int})

    G = nx.MultiDiGraph()

    # 添加节点
    for _, row in account_df.iterrows():
        G.add_node(row['id'], name=row['name'], type='account')

    for _, row in card_df.iterrows():
        G.add_node(row['id'], name=row['name'], type='card')

    # 添加边
    for _, row in acc2acc_df.iterrows():
        G.add_edge(row['source_id'], row['target_id'], amt=row['amt'], strategy_name=row['strategy_name'], buscode=row['buscode'])

    for _, row in acc2card_df.iterrows():
        G.add_edge(row['source_id'], row['target_id'], amt=row['amt'], strategy_name=row['strategy_name'], buscode=row['buscode'])

    print("Graph construction completed.")

    return G

G = construct_graph(data_dir)

print(f"Number of nodes: {G.number_of_nodes()}")
print(f"Number of edges: {G.number_of_edges()}")