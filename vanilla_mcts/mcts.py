from .board import Board
from .think_node import *
from .simulate_node import SimulateNode

# TODO: Add bound to reduce width of tree

class Old_MCTS:
	def __init__(self, board:Board, last_move:tuple[int, int], sims_per:int=1, max_sims=1) -> None:
		self.root = ThinkNode(board, last_move)
		self.sims_per = sims_per
		self.max_sims = max_sims
	
	def advise(self):
		print([(edge.w, edge.n) for edge in self.root.edges])
		advise_move = max(self.root.edges, key=lambda edge:edge.n)
		print(advise_move.move, advise_move.w, advise_move.n)
		return advise_move

	def search(self):
		# for first time root node
		self.__iter_search()
		if len(self.root.edges) == 1: return

		sims = min(self.sims_per * len(self.root.edges), self.max_sims)
		for i in range(sims):
			# if i%100 == 99: print(f'sims no.{i+1}:')
			self.__iter_search()

	def __iter_search(self):
		node = self.select()
		value = self.evaluate(node) 
		self.backprop(node, value)

	
	def select(self):
		node = self.root
		while not node.isleaf:
			best_edge = node.best_edge

			if best_edge.node is None:
				best_edge.node = InnerNode(best_edge)

			node = best_edge.node

		return node

	def evaluate(self, node:InnerNode):
		if node.check_lose(): return 0
		moves = node.get_moves()
		if not moves: return 0.5

		# append possible edges
		for move in moves:
			node.edges.append(Edge(node, move))

		sim_node = SimulateNode(node)
		return sim_node.simulate()

	def backprop(self, n:InnerNode, v:float):
		node = n
		while node is not self.root:
			node.parent.w += 1-v
			node.parent.n += 1

			v = 1-v
			node = node.parent.owner



import numpy as np	
if __name__ == "__main__":
	x = np.zeros((Board.max_row, Board.max_col))
	b = Board(x)
	sims_per = 200
	mcts = MCTS(b, None, sims_per) 
	# 2 bots demo
	while True:
		mcts.search()
		advise_node = mcts.advise().node
		print(advise_node.state)
		if advise_node.isleaf:
			break

		# new search
		mcts = MCTS(advise_node.state, advise_node.last_move, sims_per)


