import collections
import itertools


VACANT_EDGE_ID = -1
VACANT_VERTEX_ID = -1
VACANT_EDGE_LABEL = -1
VACANT_VERTEX_LABEL = -1
VACANT_GRAPH_ID = -1
AUTO_EDGE_ID = -1

class Edge(object):
    """Edge class that supports multiple attributes."""

    def __init__(self,
                 eid=VACANT_EDGE_ID,
                 frm=VACANT_VERTEX_ID,
                 to=VACANT_VERTEX_ID,
                 elb=VACANT_EDGE_LABEL,
                 attributes=None):
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
        self.elb = elb
        self.attributes = attributes if attributes is not None else {}

    def get_attribute(self, key):
        """Get an attribute value by key."""
        return self.attributes.get(key)

    def set_attribute(self, key, value):
        """Set an attribute value by key."""
        self.attributes[key] = value


class Vertex(object):
    """Vertex class that supports multiple attributes."""

    def __init__(self,
                 vid=VACANT_VERTEX_ID,
                 vlb=VACANT_VERTEX_LABEL,
                 attributes=None):
        """Initialize Vertex instance with multiple attributes.

        Args:
            vid: id of this vertex.
            vlb: label of this vertex (optional).
            attributes: dictionary of vertex attributes (e.g., labels, types).
        """
        self.vid = vid
        self.vlb = vlb
        self.attributes = attributes if attributes is not None else {}
        self.edges = dict()

    def add_edge(self, eid, frm, to, elb=None, attributes=None):
        """Add an outgoing edge with multiple attributes."""
        self.edges[to] = Edge(eid, frm, to, elb, attributes)

    def get_attribute(self, key):
        """Get an attribute value by key."""
        return self.attributes.get(key)

    def set_attribute(self, key, value):
        """Set an attribute value by key."""
        self.attributes[key] = value

class Graph(object):
    """Graph class that supports multiple attributes."""

    def __init__(self,
                 gid=VACANT_GRAPH_ID,
                 is_undirected=True,
                 eid_auto_increment=True):
        """Initialize Graph instance.

        Args:
            gid: id of this graph.
            is_undirected: whether this graph is directed or not.
            eid_auto_increment: whether to increment edge ids automatically.
        """
        self.gid = gid
        self.is_undirected = is_undirected
        self.vertices = dict()
        self.set_of_elb = collections.defaultdict(set)
        self.set_of_vlb = collections.defaultdict(set)
        self.eid_auto_increment = eid_auto_increment
        self.counter = itertools.count()

    def get_num_vertices(self):
        """Return number of vertices in the graph."""
        return len(self.vertices)

    def add_vertex(self, vid, vlb, attributes=None):
        """Add a vertex to the graph with multiple attributes.

        Args:
            vid: id of the vertex.
            vlb: label of the vertex.
            attributes: dictionary of vertex attributes (optional).
        """
        if vid in self.vertices:
            return self
        self.vertices[vid] = Vertex(vid, vlb, attributes)
        self.set_of_vlb[vlb].add(vid)
        return self

    def add_edge(self, eid, frm, to, elb=None, attributes=None):
        """Add an edge to the graph with multiple attributes.

        Args:
            eid: edge id.
            frm: source vertex id.
            to: destination vertex id.
            elb: edge label (optional).
            attributes: dictionary of edge attributes.
        """
        if (frm in self.vertices and
                to in self.vertices and
                to in self.vertices[frm].edges):
            print(f"Edge {self.counter} already exists {frm} -> {to}.")
            return self
        if self.eid_auto_increment:
            eid = next(self.counter)
        self.vertices[frm].add_edge(eid, frm, to, elb, attributes)
        self.set_of_elb[elb].add((frm, to))
        if self.is_undirected:
            self.vertices[to].add_edge(eid, to, frm, elb, attributes)
            self.set_of_elb[elb].add((to, frm))
        return self
