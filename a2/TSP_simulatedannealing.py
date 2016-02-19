import math
import sys
import bisect
import random
import numpy

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

    def del_edge(self, node1, node2):
    	del self.vertexes[node1].adjacent[node2];
    	del self.vertexes[node2].adjacent[node1];


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

    def total_num_edges(self):
        total = 0;
        for i in self.vertexes:
            for j in self[i].adjacent:
                total += 1;
        # This implementation of a graph will never have a a1a1 edge and will always have a1a2 with a2a1. 
        # So divide the total weight by 2.
        return total / 2;


    def random_cycle(self):

    	nodes = [ self.vertexes[vertex].node for vertex in self.vertexes ];

    	random.shuffle(nodes);

    	g = Graph();

    	current_node = nodes[0];

        [ g.add_vertex(node, self[node].x, self[node].y) for node in nodes ]

        nodes.append(nodes[0]);

      	for next_node in nodes[1:]:
      		g.add_edge(current_node, next_node);
      		current_node = next_node;

      	return g;

    def swap(self, method):

    	if method == "swap_on_three":

			nodes = [ self.vertexes[vertex].node for vertex in self.vertexes ];

			node1 = random.sample(nodes, 1)[0];
			node2 = random.sample(self[node1].adjacent,1)[0];
			node3 = [];
			node4 = [];

			while True:
				node3 = random.sample(nodes,1)[0];
				node4 = random.sample(self[node3].adjacent, 1)[0];
				if node3 in [node1, node2]:
					continue;
				if node4 in [node1, node2]:
					continue;
				if node3 in self[node1].adjacent:
					continue;
				if node4 in self[node2].adjacent:
					continue;
				break;

			g = Graph();
			[ g.add_vertex(node, self[node].x, self[node].y) for node in nodes ]
			for node_a in nodes:
				for node_b in self[node_a].adjacent:
					g.add_edge(node_a, node_b);

			g.del_edge(node1, node2);
			g.del_edge(node3, node4);
			g.add_edge(node1, node3);
			g.add_edge(node2, node4);

			if not self.total_num_edges() == g.total_num_edges():
				sys.exit()
			
			return g

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


# # Core Function
if __name__ == "__main__":

	# Instatiate a graph object
	complete_graph = Graph();

	# Build from the input
	complete_graph.construct_cs486_a1_graph("randTSP/problem36");

	# Create Random Cycle
	old_cycle = complete_graph.random_cycle();

	# Calculate cost
	old_cost = old_cycle.total_edge_weight();

	t = 1.0;
	t_low = 0.001;
	alpha = .9999;

	while (t > t_low):
		print(old_cost)
		new_cycle = old_cycle.swap(method="swap_on_three");	
		if t > 0.75:
			new_cycle = new_cycle.swap(method="swap_on_three");	
		if t > 0.5:
			new_cycle = new_cycle.swap(method="swap_on_three");	
		if t > 0.25:
			new_cycle = new_cycle.swap(method="swap_on_three");	
		new_cost = new_cycle.total_edge_weight();
		prob = numpy.exp( abs(old_cost - new_cost) / t );
		if ( new_cost < old_cost ):
			old_cycle = new_cycle;
			old_cost = new_cost;
		elif ( prob < ( float( random.randint(0, 10000) ) ) ):
			old_cycle = new_cycle;
			old_cost = new_cost;
		t *= alpha;