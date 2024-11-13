import collections
import itertools
from my_graph import Graph
from my_graph import VACANT_GRAPH_ID
from my_graph import AUTO_EDGE_ID

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
                graph.add_vertex(vid, {'type' : v_type_mapping['account'], 'name': name_int})
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


class DFSedge(object):
    """DFSedge class representing an edge in a DFS code."""

    def __init__(self, frm, to, vevlb):
        """Initialize DFSedge instance.
        
        Args:
            frm (int): The starting vertex identifier.
            to (int): The ending vertex identifier.
            vevlb (tuple): A tuple containing (frm_attributes, edge_attributes, to_attributes).
        """
        self.frm = frm
        self.to = to
        self.vevlb = vevlb

    def __eq__(self, other):
        """Check equivalence of DFSedge based on attributes, ignoring vertex IDs.
        
        Two edges are considered equal if their vertex and edge attributes are the same.
        """
        # Unpack vertex and edge attributes
        frm_attrs_self, edge_attrs_self, to_attrs_self = self.vevlb
        frm_attrs_other, edge_attrs_other, to_attrs_other = other.vevlb

        # Simplified comparison: compare attributes only
        return (frm_attrs_self == frm_attrs_other and
                edge_attrs_self == edge_attrs_other and
                to_attrs_self == to_attrs_other)

    def __ne__(self, other):
        """Check if not equal."""
        return not self.__eq__(other)

    def __repr__(self):
        """String representation of a DFSedge."""
        return '(frm={}, to={}, vevlb={})'.format(self.frm, self.to, self.vevlb)
    

class DFScode(list):
    """DFScode is a list of DFSedge, representing a sequence of edges in a DFS traversal."""

    def __init__(self):
        """Initialize DFScode."""
        self.rmpath = list()

    def __eq__(self, other):
        """Check equivalence of DFScode."""
        if len(self) != len(other):
            return False
        return all(self[i] == other[i] for i in range(len(self)))

    def __ne__(self, other):
        """Check if not equal."""
        return not self.__eq__(other)

    def __repr__(self):
        """String representation of DFScode."""
        return '[' + ', '.join(str(dfsedge) for dfsedge in self) + ']'

    def push_back(self, frm, to, vevlb):
        """Add an edge to the DFScode."""
        self.append(DFSedge(frm, to, vevlb))
        return self

    def to_graph(self, gid=VACANT_GRAPH_ID, is_undirected=False):
        """Construct a graph from the DFS code."""
        g = Graph(gid, is_undirected=is_undirected, eid_auto_increment=True)
        for dfsedge in self:
            frm, to, (vlb1, elb, vlb2) = dfsedge.frm, dfsedge.to, dfsedge.vevlb
            g.add_vertex(frm, vlb1)
            g.add_vertex(to, vlb2)
            g.add_edge(AUTO_EDGE_ID, frm, to, elb)
        return g

    def from_graph(self, g):
        """Build a DFScode from a given graph."""
        raise NotImplementedError('Not implemented yet.')

    # 是否适用于多重图？
    def build_rmpath(self):
        """Build the right-most path in the DFS code."""
        self.rmpath = []
        old_frm = None
        for i in range(len(self) - 1, -1, -1):
            dfsedge = self[i]
            frm, to = dfsedge.frm, dfsedge.to
            if frm < to and (old_frm is None or to == old_frm):
                self.rmpath.append(i)
                old_frm = frm
        return self

    def get_num_vertices(self):
        """Return the number of unique vertices in the DFS code."""
        return len(set(dfsedge.frm for dfsedge in self) | set(dfsedge.to for dfsedge in self))


def generate_1edge_frequent_subgraphs(g, min_support, is_undirected):
    """Generate frequent 1-edge subgraphs from a list of graphs."""
    vevlb_counter = collections.Counter()
    vevlb_counted = set()
    for v in g.vertices():
        for to, edges in v.edges.items():
            for e in edges:
                v1_attrs = v.attributes
                v2_attrs = g.vertices[to].attributes
                e_attrs = e.attributes

                if is_undirected and v.vid > to:
                    v1_attrs, v2_attrs = v2_attrs, v1_attrs

                vevlb_counted.add((v1_attrs, e_attrs, v2_attrs))
                vevlb_counter[(v1_attrs, e_attrs, v2_attrs)] += 1
    
    fre_sub_gs = list()

    for (v1_attrs, e_attrs, v2_attrs), count in vevlb_counter.items():
        if count >= min_support:
            sub_g = Graph(VACANT_GRAPH_ID, is_undirected=is_undirected, eid_auto_increment=True)
            sub_g.add_vertex(0, v1_attrs)
            sub_g.add_vertex(1, v2_attrs)
            sub_g.add_edge(0, 0, 1, e_attrs)
            fre_sub_gs.append(sub_g)
    
    return fre_sub_gs

                