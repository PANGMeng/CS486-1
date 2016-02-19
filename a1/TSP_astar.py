import math
import sys
import bisect

class Vertex:

    def __init__(self, node, x, y):
        self.node = node;
        self.x = x;
        self.y = y;
        self.adjacent = {};

    def __getitem__(self, item):
        if item in self.adjacent:
            return self.adjacent[item];

    def closest_neighbour(self, exclude = []):
        min_edge = None;
        min_value = float("inf");
        for i in self.adjacent:
            if i in exclude:
                continue
            if self.adjacent[i].weight < min_value:
                min_value = self.adjacent[i].weight;
                min_edge = i;
        return (min_edge, min_value);


class Edge:
    def __init__(self, vertex1, vertex2):
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.weight = math.sqrt( math.pow(self.vertex2.x - self.vertex1.x, 2) + math.pow(self.vertex2.y - self.vertex1.y, 2) );


class Graph:

    def __init__(self):
        self.vertexes = {}
        self.n_vertex = 0;

    def add_vertex(self, node, x, y):

    	# Create a Vertex Object
        vertex = Vertex(node,x,y);

        # Store in a Vertex Dictionary
        self.vertexes[node] = vertex;

        # Increment Vertex Counter
        self.n_vertex += 1;

    def add_edge(self, node1, node2):

    	# Create an Edge Object
        edge = Edge(self.vertexes[node1], self.vertexes[node2]);

        # Update Vertex adjacency dictionary
        self.vertexes[node1].adjacent[node2] = edge;
        self.vertexes[node2].adjacent[node1] = edge;

    def __getitem__(self, item):
        if item in self.vertexes:
            return self.vertexes[item];

    def mst(self, node, exclude = []):

    	# Extrapolate all vertexes
        nodes = [ self.vertexes[vertex].node for vertex in self.vertexes ];

        # Remove the vertexes in the exclude list
        if not exclude == []:
            nodes = [ other for other in nodes if not other in exclude ];

        # Instatiate a new graph obbject
        g = Graph();

        # Add the first vertex
        g.add_vertex(node, self[node].x, self[node].y);

        # Get all nodes not in exclude that isn't the added node
        nodes = [ a for a in nodes if not a == node ]

        # Get all Edges that connect to node
        edges = [ self[node].adjacent[i] for i in self[node].adjacent ];

        # Calculate MST using Prim-like Algorithm
        while len(nodes) > 0:
            min_edge = None
            min_value = float("inf");

            # Find the edge that connects to one of the accepted nodes that has the minimum weight
            for i in edges:
                if i.vertex1.node in nodes or i.vertex2.node in nodes:
                    if i.weight < min_value:
                        min_edge = i;
                        min_value = i.weight;

            # Create a new_node, but we need to figure out if it is a1 or a2 in a1a2 edge
            new_node = None;
            if min_edge.vertex1.node in nodes:
                new_node = min_edge.vertex1.node;
            else:
                new_node = min_edge.vertex2.node;

            # Add this node to the graph
            g.add_vertex(new_node, self[new_node].x, self[new_node].y);
            g.add_edge(min_edge.vertex1.node, min_edge.vertex2.node);

            # Remove this node from the current nodes.
            nodes = [a for a in nodes if not a == new_node ];

            # Get all of its edges
            edges += [ self[new_node].adjacent[i] for i in self[new_node].adjacent ];
        return g;

    # Calculate all of the edges in a graph
    def total_edge_weight(self):
        total = 0;
        for i in self.vertexes:
            for j in self[i].adjacent:
                total += self[i][j].weight;
        # This implementation of a graph will never have a a1a1 edge and will always have a1a2 with a2a1. 
        # So divide the total weight by 2.
        return total / 2;

    # Construct a graph given the cs486 graph definition
    def construct_cs486_a1_graph(self, input_file):
        input_fh = open(input_file);
        input_data = input_fh.read().splitlines()[1:];
        vertexes = [];
        for i in input_data:
            tmp = i.split();
            self.add_vertex(tmp[0], int(tmp[1]), int(tmp[2]));
            vertexes.append(tmp[0]);
        for i in vertexes:
            vertexes = [ node for node in vertexes if not node == i ];
            for j in vertexes:
                self.add_edge(i,j);

    # g, the distance from A to the last item in include.
    def g(self, include):
        value = 0;
        for i in range(len(include)-1):
            value += self[include[i]][include[i+1]].weight;
        return value;

    # h, the MST plus the closest neighbour from A that is unvisited.
    def h(self, exclude):
        value = 0;
        value += self.mst(exclude[-1:][0], exclude).total_edge_weight();
        value += self[exclude[0]].closest_neighbour(exclude)[1];
        return value;

    # g + h
    def f(self, seen_so_far):
        if len(seen_so_far) == self.n_vertex:
            return self.g(seen_so_far + [seen_so_far[0]])
        return self.h(seen_so_far) + self.g(seen_so_far);

# This Is an Item stored in a priority Queue. Really could be called a State/
class Node:

    ### NOTE, what about lexigraphical order
    def __init__(self, graph, seen_so_far):
        self.graph = graph;
        self.f = graph.f(seen_so_far);
        self.seen_so_far = seen_so_far;

    # Define the ordering of states
    def __lt__(self, other):
        if self.f < other.f:
            return True;
        else:
            return False;

    def __gt__(self, other):
        if self.f > other.f:
            return True;
        else:
            return False;

    def __eq__(self, other):
        if self.f == other.f:
            return True;
        else:
            return False;

    def __le__(self, other):
        return self < other or self == other;

    def __ge__(self, other):
        return self > other or self == other;


# Core Function
if __name__ == "__main__":

    # Instatiate a graph object
    g = Graph();

    # Build from the input
    g.construct_cs486_a1_graph(sys.argv[1]);

    # Null to A
    iterations = 1 
    if (g.n_vertex == 1):
        print iterations;
        sys.exit();

    # Create the first set of states.
    paths = [];
    for node in g.vertexes:
        if node == 'A':
            continue;
        else:
            bisect.insort(paths, Node(g, ['A', node]));

    # go on until the first item in the priority queue is the goal state.
    while not len(paths[0].seen_so_far) == g.n_vertex:
        iterations += 1;
        current_node = paths.pop(0);
        seen_so_far = current_node.seen_so_far;
        new_nodes = [ node for node in g.vertexes if not node in seen_so_far ];
        for node in new_nodes:
            bisect.insort(paths, Node(g, seen_so_far + [node]))

    print str(len(paths))
    print iterations