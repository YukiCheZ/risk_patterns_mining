import pandas as pd
from my_graph import Graph

# 数据目录路径
data_dir = "./data/"

# 将点类型的 name 字段映射为整数
name_mapping = {'Jobs': 0, 'Mike': 1, 'John': 2}

v_type_mapping = {'account': 0, 'card': 1}
e_type_mapping = {'account_to_account': 2, 'account_to_card': 3}

def map_name(value):
    return name_mapping.get(value, -1)

# 将边类型的 strategy_name 和 buscode 字段的最后一个字符提取为整数
def extract_last_char_as_int(value):
    return int(str(value)[-1])

# 将边类型的 amt 字段转换为整数
def convert_amt_to_int(value):
    return int(float(value))

# 对点类型的 card_id 做唯一化处理
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
    # 创建图实例
    graph = Graph()

    # 读取点数据
    account_df = read_csv(data_dir + "account", usecols=[0, 1], names=['id', 'name'], converters={'name': map_name})
    card_df = read_csv(data_dir + "card", usecols=[0, 1], names=['id', 'name'], converters={'id': map_card_id, 'name': map_name})

    # 读取边数据
    acc2acc_df = read_csv(data_dir + "account_to_account", usecols=[0, 1, 3, 4, 6], 
                          names=['source_id', 'target_id', 'amt', 'strategy_name', 'buscode'], 
                          converters={'amt': convert_amt_to_int, 'strategy_name': extract_last_char_as_int, 'buscode': extract_last_char_as_int})
    acc2card_df = read_csv(data_dir + "account_to_card", usecols=[0, 1, 3, 4, 6], 
                           names=['source_id', 'target_id', 'amt', 'strategy_name', 'buscode'], 
                           converters={'target_id': map_card_id, 'amt': convert_amt_to_int, 'strategy_name': extract_last_char_as_int, 'buscode': extract_last_char_as_int})

    # 添加节点到图
    for _, row in account_df.iterrows():
        graph.add_vertex(row['id'], v_type_mapping['account'], {'name': row['name']})

    for _, row in card_df.iterrows():
        graph.add_vertex(row['id'], v_type_mapping['card'], {'name' : row['name']})

    # 添加边到图
    for _, row in acc2acc_df.iterrows():
        graph.add_edge(eid=None,  # 使用自动生成的边ID
                       frm=row['source_id'], 
                       to=row['target_id'], 
                       elb=e_type_mapping['account_to_account'],
                       attributes={'amt': row['amt'], 'strategy_name': row['strategy_name'], 'buscode': row['buscode']})

    for _, row in acc2card_df.iterrows():
        graph.add_edge(eid=None,  # 使用自动生成的边ID
                       frm=row['source_id'], 
                       to=row['target_id'], 
                       elb=e_type_mapping['account_to_card'],  # 可根据需求设置边标签
                       attributes={'amt': row['amt'], 'strategy_name': row['strategy_name'], 'buscode': row['buscode']})

    print("Graph construction completed.")

    return graph

# 构建图并检查节点和边的数量
graph = construct_graph(data_dir)
print(f"Number of vertices: {graph.get_num_vertices()}")
# 你可以根据需要添加其他方法来打印或检查图的结构
