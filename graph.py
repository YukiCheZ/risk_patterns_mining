import collections

VACANT_VERTEX_ID = -1
VACANT_GRAPH_ID = -1
AUTO_EDGE_ID = -1

class Edge(object):
    """Edge class that supports multiple attributes."""

    def __init__(self, frm=VACANT_VERTEX_ID, 
                 to=VACANT_VERTEX_ID, attributes=None):
        """Initialize Edge instance with multiple attributes.

        Args:
            frm: source vertex id.
            to: destination vertex id.
            attributes: dictionary of edge attributes (e.g., weight, type).
        """
        self.frm = frm
        self.to = to
        self.attributes = attributes if attributes is not None else {}

    def get_attribute(self, key):
        """Get an attribute value by key."""
        return self.attributes.get(key)
    

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

    def add_edge(self, frm, to, attributes=None):
        """Add an outgoing edge with multiple attributes, allowing multiple edges to the same target.

        Args:
            frm: source vertex id.
            to: destination vertex id.
            attributes: dictionary of edge attributes.
        """
        edge = Edge(frm, to, attributes)
        self.edges[to].append(edge)

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
    

class Graph(object):
    """Graph class that supports multiple attributes."""

    def __init__(self, gid=VACANT_GRAPH_ID):
        """Initialize Graph instance.

        Args:
            gid: id of this graph.
        """
        self.gid = gid
        self.vertices = dict()

    def add_vertex(self, vid, attributes=None):
        """Add a vertex to the graph with multiple attributes.

        Args:
            vid: id of the vertex.
            attributes: dictionary of vertex attributes (optional).
        """
        if vid in self.vertices:
            return self
        self.vertices[vid] = Vertex(vid, attributes)
        return self

    def add_edge(self, frm, to, attributes=None):
        """Add an edge to the graph with multiple attributes.

        Args:
            frm: source vertex id.
            to: destination vertex id.
            attributes: dictionary of edge attributes.
        """
        if frm not in self.vertices or to not in self.vertices:
            print("Source or target vertex does not exist.")
            return self
        # Add the edge to the source vertex
        self.vertices[frm].add_edge(frm, to, attributes)
        
        return self

    def get_num_vertices(self):
        """Return number of vertices in the graph."""
        return len(self.vertices)
    
    def get_num_edges(self):
        """Return the total number of edges in the graph."""
        num_edges = 0
        for vertex in self.vertices.values():
            num_edges += sum(len(edges) for edges in vertex.edges.values())
        
        return num_edges
