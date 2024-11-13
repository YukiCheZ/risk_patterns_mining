import collections
import itertools

VACANT_EDGE_ID = -1
VACANT_VERTEX_ID = -1
VACANT_GRAPH_ID = -1
AUTO_EDGE_ID = -1

class Edge(object):
    """Edge class that supports multiple attributes."""

    def __init__(self, eid=VACANT_EDGE_ID, frm=VACANT_VERTEX_ID, 
                 to=VACANT_VERTEX_ID, attributes=None):
        """Initialize Edge instance with multiple attributes.

        Args:
            eid: edge id.
            frm: source vertex id.
            to: destination vertex id.
            elb: edge label (optional).
            attributes: dictionary of edge attributes (e.g., weight, type).
        """
        self.eid = eid
        self.frm = frm
        self.to = to
        self.attributes = attributes if attributes is not None else {}

    def get_attribute(self, key):
        """Get an attribute value by key."""
        return self.attributes.get(key)

    def set_attribute(self, key, value):
        """Set an attribute value by key."""
        self.attributes[key] = value

class Vertex(object):
    """Vertex class that supports multiple attributes and efficient edge lookup."""

    def __init__(self, vid=VACANT_VERTEX_ID, attributes=None):
        """Initialize Vertex instance with multiple attributes and an edge dictionary.

        Args:
            vid: id of this vertex.
            attributes: dictionary of vertex attributes (e.g., labels, types).
        """
        self.vid = vid
        self.attributes = attributes if attributes is not None else {}
        self.edges = collections.defaultdict(list)

    def add_edge(self, eid, frm, to, attributes=None):
        """Add an outgoing edge with multiple attributes, allowing multiple edges to the same target.

        Args:
            eid: edge id.
            frm: source vertex id.
            to: destination vertex id.
            attributes: dictionary of edge attributes.
        """
        edge = Edge(eid, frm, to, attributes)
        self.edges[to].append(edge)  # Append edge to the list for the target vertex

    def get_edges(self, to):
        """Get all edges from this vertex to the specified target vertex.

        Args:
            to: id of the target vertex.

        Returns:
            List of edges from this vertex to the target vertex, or an empty list if no such edges exist.
        """
        return self.edges[to]

    def get_attribute(self, key):
        """Get an attribute value by key."""
        return self.attributes.get(key)

    def set_attribute(self, key, value):
        """Set an attribute value by key."""
        self.attributes[key] = value


class Graph(object):
    """Graph class that supports multiple attributes."""

    def __init__(self, gid=VACANT_GRAPH_ID, is_undirected=False, eid_auto_increment=True):
        """Initialize Graph instance.

        Args:
            gid: id of this graph.
            is_undirected: whether this graph is directed or not.
            eid_auto_increment: whether to increment edge ids automatically.
        """
        self.gid = gid
        self.is_undirected = is_undirected
        self.vertices = dict()
        self.eid_auto_increment = eid_auto_increment
        self.counter = itertools.count()
        # Add a new attribute for indexing edges by their attributes
        self.edge_attribute_index = collections.defaultdict(list)

    def add_vertex(self, vid, attributes=None):
        """Add a vertex to the graph with multiple attributes.

        Args:
            vid: id of the vertex.
            attributes: dictionary of vertex attributes (optional).
        """
        if vid in self.vertices:
            print("Vertex already exists.")
            return self
        self.vertices[vid] = Vertex(vid, attributes)
        return self

    def add_edge(self, eid, frm, to, attributes=None):
        """Add an edge to the graph with multiple attributes.

        Args:
            eid: edge id.
            frm: source vertex id.
            to: destination vertex id.
            attributes: dictionary of edge attributes.
        """
        if frm not in self.vertices or to not in self.vertices:
            print("Source or target vertex does not exist.")
            return self
        if self.eid_auto_increment:
            eid = next(self.counter)
        # Add the edge to the source vertex
        self.vertices[frm].add_edge(eid, frm, to, attributes)
        if self.is_undirected:
            # Add the edge to the target vertex as well, if the graph is undirected
            self.vertices[to].add_edge(eid, to, frm, attributes)
        
        # Update the edge_attribute_index
        e_att = tuple(attributes.items()) if attributes else ()
        frm_att = tuple(self.vertices[frm].attributes.items())
        to_att = tuple(self.vertices[to].attributes.items())
        key = (e_att, frm_att, to_att)
        self.edge_attribute_index[key].append((frm, to, eid))
        
        return self

    def get_num_vertices(self):
        """Return number of vertices in the graph."""
        return len(self.vertices)
    
    def get_num_edges(self):
        """Return the total number of edges in the graph."""
        num_edges = 0
        for vertex in self.vertices.values():
            num_edges += sum(len(edges) for edges in vertex.edges.values())

        if self.is_undirected:
            num_edges //= 2
        
        return num_edges
    
    def get_total_edges_from_index(self):
        """Calculate the total number of edges using the edge_attribute_index.

        Returns:
            Total number of edges in the graph.
        """
        total_edges = 0
        for edge_list in self.edge_attribute_index.values():
            total_edges += len(edge_list)
        return total_edges
