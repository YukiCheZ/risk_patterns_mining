from my_graph import Graph

# 数据目录路径
data_dir = "./data/"

# 将点类型的 name 字段映射为整数
name_mapping = {'Jobs': 0, 'Mike': 1, 'John': 2}
v_type_mapping = {'account': 0, 'card': 1}
e_type_mapping = {'account_to_account': 2, 'account_to_card': 3}

card_id_offset = 800000

# 辅助函数
def map_name(value):
    return name_mapping.get(value, -1)

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
                graph.add_vertex(vid, v_type_mapping['account'], {'name': name_int})
    except Exception as e:
        print(f"Error reading account file: {e}")

    # 读取并处理 card 文件
    try:
        with open(data_dir + "card", "r") as file:
            for line in file:
                id_str, name = line.strip().split(",")[:2]
                vid = map_card_id(id_str)
                name_int = map_name(name)
                graph.add_vertex(vid, v_type_mapping['card'], {'name': name_int})
    except Exception as e:
        print(f"Error reading card file: {e}")

    # 读取并处理 account_to_account 文件
    try:
        with open(data_dir + "account_to_account", "r") as file:
            for line in file:
                parts = line.strip().split(",")
                source_id = int(parts[0])
                target_id = int(parts[1])
                amt = convert_amt_to_int(parts[3])  # 注意这里是 parts[3] 对应 amt
                strategy_name = extract_last_char_as_int(parts[4])  # parts[4] 对应 strategy_name
                buscode = extract_last_char_as_int(parts[6])  # parts[6] 对应 buscode
                graph.add_edge(
                    eid=None,  # 自动生成边ID
                    frm=source_id,
                    to=target_id,
                    elb=e_type_mapping['account_to_account'],
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
                amt = convert_amt_to_int(parts[3])  # parts[3] 对应 amt
                strategy_name = extract_last_char_as_int(parts[4])  # parts[4] 对应 strategy_name
                buscode = extract_last_char_as_int(parts[6])  # parts[6] 对应 buscode
                graph.add_edge(
                    eid=None,  # 自动生成边ID
                    frm=source_id,
                    to=target_id,
                    elb=e_type_mapping['account_to_card'],
                    attributes={'amt': amt, 'strategy_name': strategy_name, 'buscode': buscode}
                )
    except Exception as e:
        print(f"Error reading account_to_card file: {e}")

    print("Graph construction completed.")
    return graph

# 构建图并检查节点和边的数量
graph = construct_graph(data_dir)
print(f"Number of vertices: {graph.get_num_vertices()}")
print(f"Number of edges: {graph.get_num_edges()}")