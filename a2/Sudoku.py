from sets import Set;
from more_itertools import unique_everseen;
from itertools import chain;
import sys;

def which_box(i,j):
	return (i / 3 % 3 * 3) + (j / 3 % 3);

def table(list_of_vals):
	table = [0] * 10;
	for val in list_of_vals:
		table[val] += 1;
	return table;

class Unit:

	def __init__(self, val):
		self.val = val;
		self.available_values = Set(range(1,10));

class Sudoku:

	def __init__(self):
		self.grid = [];
		for i in range(9):
			self.grid.append([]);
			for j in range(9):
				self.grid[i].append( Unit(0) );

	def box(self, index):
		index_row = 0;
		index_col = 0;
		if index % 3 == 0:
			index_col = 0;
			index_row = index;
		if index % 3 == 1:
			index_col = 3;
			index_row = index-1;
		if index % 3 == 2:
			index_col = 6;
			index_row = index-2;
		return [ self.grid[i][j] for i in range(index_row, index_row + 3) for j in range(index_col, index_col + 3) ];

	def row(self, index):
		return self.grid[index];

	def col(self, index):
		return [ self.grid[i][index] for i in range(9) ];

	def most_restricted_nodes(self):
		min_avail_value = 9;
		most_restricted_nodes = [];
		for i in range(9):
			for j in range(9):
				if len(self.grid[i][j].available_values) >= 2 and len(self.grid[i][j].available_values) < min_avail_value:
					min_avail_value = len(self.grid[i][j].available_values);
					most_restricted_nodes = [];
				if len(self.grid[i][j].available_values) == min_avail_value:
					most_restricted_nodes.append((i,j));

		return(most_restricted_nodes);	

	def clash_table(self,i,j):
		units = [];
		units.extend(self.row(i));
		units.extend(self.col(j));
		units.extend(self.box(which_box(i,j)));
		units = list(unique_everseen(units));
		values = list(chain(*[ list(unit.available_values) for unit in units ]));
		return(table(values));

	def setup_sudoku_puzzle(self, file):
		fh = open(file);
		row = 0;
		col = 0;
		for line in fh:
			vals = line.split(" ");
			for val in vals:
				if val == "\n":
					continue;
				else:
					self.grid[row][col].val = int(val);
				col += 1;
			row += 1;
			col = 0;
		self.update_available_values();

	# Update the list of available values by removing
	# known values in the row, col and box overlapping with the unit.
	def update_available_values(self):
		for i in range(9):
			for j in range(9):
				k = which_box(i,j);
				if not self.grid[i][j].val == 0:
					self.grid[i][j].available_values = Set();
					continue;
				self.grid[i][j].available_values -= Set([ unit.val for unit in self.row(i) ]);
				self.grid[i][j].available_values -= Set([ unit.val for unit in self.col(j) ]);
				self.grid[i][j].available_values -= Set([ unit.val for unit in self.box(k) ]);

	def __str__(self):
		return '\n'.join([' '.join( [ str(unit.val) for unit in self.row(i)]) for i in range(9) ]);

	# Update Current Values, defined as those that have a single available value.
	def update_values(self):
		breaked = False;
		for i in range(9):
			for j in range(9):
				if len(self.grid[i][j].available_values) == 1:
					self.grid[i][j].val = list(self.grid[i][j].available_values)[0];
					self.grid[i][j].available_values = Set();
					breaked = True;
					break;
			if breaked:
				break;
		self.update_available_values();

	# Does everything have a non-zero value?
	def solved(self):
		solved = True;
		for i in range(9):
			for j in range(9):
				if self.grid[i][j].val == 0:
					solved = False;
		return(solved);

	# Are there any nodes with no available values and have yet to be assigned a val?
	def solveable(self):
		for i in range(9):
			for j in range(9):
				if len(self.grid[i][j].available_values) == 0 and self.grid[i][j].val == 0:
					return False;
		return True;

	# Do any nodes have a single available value?
	def any_to_update(self):
		for i in range(9):
			for j in range(9):
				if len(self.grid[i][j].available_values) == 1:
					return True;
		return False;

	# Pick a new unit using the most restricted node and least constrained value
	def pick_a_unit(self):

		# Get a list of most restricted nodes
		constrained_values = self.most_restricted_nodes();
		
		# For these nodes, find out which have the least constrained value
		unit = None;
		value = 0;
		least_constrained_value = 0;
		for node in constrained_values:
			clashes = self.clash_table(node[0], node[1]);
			for val in self.grid[node[0]][node[1]].available_values:

				# do this by tally the overlapping unit available_values
				# and select the one that is the max across all possible restricted nodes
				if clashes[val] > least_constrained_value:
					least_constrained_value = clashes[val];
					unit = node;
					value = val;


		return((unit, value));

	# Given a index and value, create a new state
	def create_new_state(self, i, j, val):
		
		# Remove the index we are going to try from the previous state
		self.grid[i][j].available_values -= Set([val]);
		
		# Instantiate a new state
		s = Sudoku();
		
		# Which is a copy of the previous state
		for k in range(9):
			for l in range(9):
				s.grid[k][l].val = self.grid[k][l].val;
				s.grid[k][l].available_values = Set();
				for item in list(self.grid[k][l].available_values):
					s.grid[k][l].available_values.add(item);
		
		#Update the guessed value
		s.grid[i][j].val = val;
		s.grid[i][j].available_values = Set();
		s.update_available_values();

		return(s);


# Core Function
if __name__ == "__main__":

	# Instatiate a graph object
	list_of_sudoku_states = [];

	# Instatiate a Sudoku Puzzle
	list_of_sudoku_states.append(Sudoku());

	# Build from a CS486 sudoku file instance (i.e. the first argument sudoku.py)
	list_of_sudoku_states[0].setup_sudoku_puzzle(sys.argv[1]);

	variable_assignments = 0

	# While loop, will break once a solution has been found
	while True:

		# FORWARD CHECKING, If you can fill in a state, do it now
		while (list_of_sudoku_states[0].solveable()):

			if variable_assignments > 10000:
				break;
			elif list_of_sudoku_states[0].any_to_update():
				list_of_sudoku_states[0].update_values();
				variable_assignments += 1;
			else:
				break;

		# Have we found a solution? Break if we have
		if list_of_sudoku_states[0].solved():
			break;

		# Is the current Solution Still solveable?
		elif list_of_sudoku_states[0].solveable():

			# If so, we know that we have forward checked as much as we could, so lets guess at a new value
			unit_data = list_of_sudoku_states[0].pick_a_unit();

			# Create the new state
			list_of_sudoku_states.insert(0, list_of_sudoku_states[0].create_new_state(unit_data[0][0], unit_data[0][1], unit_data[1]));

			variable_assignments += 1;

		# Backtrack, the solution we guessed at failed.
		elif variable_assignments > 10000:
			break;
		else:
			list_of_sudoku_states.pop(0);

	print variable_assignments