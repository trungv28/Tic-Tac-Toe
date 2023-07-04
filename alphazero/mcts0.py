from .node0 import *
from .model import NeuralNetwork
from ..vanilla_mcts.board import MAX_COL

class MCTS0:
	def __init__(self, board:Board, last_move:tuple[int, int],
				model:NeuralNetwork, sims_per:int=1, max_sims=1) -> None:

		self.root = ThinkNode0(board, last_move)
		self.model = model
		self.model.to(get_device())
		self.sims_per = sims_per
		self.max_sims = max_sims
	
	def advise(self):
		if len(self.root.edges) == 0: return None
		if len(self.root.edges) == 1:
			self.root.policies = [1]
			edge = self.root.edges[0]
			edge.node = InnerNode0(edge)
			return edge
		self.root.calculate_policies()
		return random.choices(self.root.edges, self.root.policies)[0]

	def search(self):
		# for first time root node
		self.__iter_search()
		if len(self.root.edges) <= 1: return

		sims = min(self.sims_per * len(self.root.edges), self.max_sims)
		for i in range(sims):
			# print(f'sims no.{i+1}:')
			self.__iter_search()

	def __iter_search(self):
		node = self.select()
		node.value = self.evaluate(node) 
		self.backprop(node)

	
	def select(self):
		node = self.root
		while not node.isleaf:
			best_edge = node.best_edge

			if best_edge.node is None:
				best_edge.node = InnerNode0(best_edge)

			node = best_edge.node

		return node

	def evaluate(self, node:InnerNode0)->float:
		if node.check_lose(): return -1
		moves = node.get_moves()
		if not moves: return 0

		policy, value = self.model.forward(node.tensor_input)
		policy = torch.softmax(policy, axis=1)
		policy, value = policy[0], value.item()

		# append possible edges
		for move in moves:
			r, c = move
			index = r*MAX_COL + c
			node.edges.append(Edge0(node, move, policy[index].item()))

		return value

	def backprop(self, n:InnerNode0):
		node, v = n, n.value
		while node is not self.root:
			node.parent.w += -v
			node.parent.n += 1

			v = -v
			node = node.parent.owner

times = []
def self_play(_):
	board = Board(np.zeros((Board.max_row, Board.max_col)))
	last_move = None
	nn_args = {
		'num_filter': 32,
		'filter_size': 3,
		'hidden_size': 128, # for policy head
		'num_block': 9 # for resnet (should be 19 or 39)
	}
	model = NeuralNetwork(nn_args, get_device())
	mcts = MCTS0(board, last_move, model, 1000, 1000)
	start = time()
	mcts.search()
	end = time()
	return f'Total time: {end-start}'


from time import time
from multiprocessing import Pool
if __name__ == '__main__':
	# p = Process(self_play)
	# p.start()
	# p = Process(self_play)
	# p.start()
	# p = Process(self_play)
	# p.start()

	# p.join()
	with Pool(2) as p:
		print(p.map(self_play, [None for _ in range(12)]))

	print('hello')



		
