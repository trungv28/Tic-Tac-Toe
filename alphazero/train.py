import torch.optim as optim
import torch.nn.functional as F
from tqdm import tqdm
import os
from threading import Thread, Lock
import shutil
from .model import NeuralNetwork
from .mcts0 import MCTS0
from .node0 import *
class Trainer:
	def __init__(self, args):
		self.model:NeuralNetwork = args['model']
		self.optimizer:optim.Adam = args['optimizer']
		self.batch_size = args['batch_size']
		self.num_iterations = args['num_iterations']
		self.num_epochs = args['num_epochs']
		self.num_selfplay = args['num_selfplay']
		self.max_sims = args['max_sims']
		self.sims_per = args['sims_per']

		self.memory = []
		self.model.to(get_device())

		self.lock = Lock()

	def self_play(self):
		board = Board(np.zeros((Board.max_row, Board.max_col)))
		mcts_tree = MCTS0(board, None, self.model, self.sims_per, self.max_sims)

		game_states:list[ThinkNode0|InnerNode0] = []
		print('Start game:')
		while True:
			# print(mcts_tree.root.state)
			game_states.append(mcts_tree.root) # include terminal state
			mcts_tree.search()
			edge = mcts_tree.advise()
			if not edge: break

			mcts_tree.root = edge.node # reuse subtree
			mcts_tree.root.parent = None

		print('Endgame!')
		train_data = self.create_train_data(game_states)

		self.lock.acquire()
		self.memory.extend(train_data)
		self.lock.release()

	def collect_train_data(self):
		no_selfplays = self.num_selfplay
		no_threads = 5
		for _ in range(no_selfplays//no_threads):
			threads:list[Thread] = []
			for _ in range(no_threads):
				t = Thread(target=self.self_play)
				t.start()
				threads.append(t)

			for t in threads:
				t.join()

		print(len(self.memory))
		
	def create_train_data(self, game_states:list[ThinkNode0|InnerNode0]):
		game_moves = len(game_states)-1
		# seperate final state
		*game_states, final_state = game_states

		# các cậu nên hỏi lại chỗ này	
		values = [0 for _ in range(game_moves)] if final_state.value == 0 \
		else [(-1)**((i+game_moves+1)%2) for i in range(game_moves)]

		# O(no_children * game_moves)
		policies = [gs.full_policies for gs in game_states]
		temp_memory = [(gs.tensor_input, value, policy)
			for gs, value, policy in zip(game_states, values, policies)]

		return temp_memory
	
	def train_model(self):
		random.shuffle(self.memory)
		train_losses = []
		for batch_idx in range(0, len(self.memory), self.batch_size):
			sample = self.memory[batch_idx:min(len(self.memory), batch_idx + self.batch_size)] 
			state, value_targets, policy_targets = zip(*sample)

			policy_targets, value_targets = np.array(policy_targets), np.array(value_targets).reshape(-1, 1)
			state  = torch.stack(list(state), dim=0)
			state = state.squeeze(1)
			policy_targets = torch.tensor(policy_targets, dtype=torch.float32, device=self.model.device)
			value_targets = torch.tensor(value_targets, dtype=torch.float32, device=self.model.device)
			out_policy, out_value = self.model(state)

			policy_loss = F.cross_entropy(out_policy, policy_targets)
			value_loss = F.mse_loss(out_value, value_targets)
			loss = policy_loss + value_loss

			self.optimizer.zero_grad() 
			loss.backward()
			self.optimizer.step() 
			train_losses.append(loss.item())
		return sum(train_losses) / len(train_losses)
	
	def train(self):
		# for saving and tensorboard
		save_path = './runs'
		for iteration in range(self.num_iterations):
			print(f'Iteration {iteration + 1}')
			
			self.model.eval()
			print('Begin self-play')
			self.collect_train_data()

			self.model.train()
			for _ in tqdm(range(self.num_epochs), desc = 'Training'):
				mean_train_loss = self.train_model()
				print(f'Train_loss:{mean_train_loss}')
			torch.save(self.model.state_dict(), os.path.join(save_path, f"iteration_{iteration+1}.pt"))
			self.memory = []
		return

"""# Output"""

from time import time
if __name__ == "__main__":
	device = get_device()
	nn_args = {
		'num_filter': 32,
		'filter_size': 3,
		'hidden_size': 128, # for policy head
		'num_block': 9 # for resnet (should be 19 or 39)
	}
	nn = NeuralNetwork(nn_args, device)

	learning_rate = 0.001
	optimizer = optim.Adam(nn.parameters(), lr = learning_rate, weight_decay=0.0001)

	trainer_args = {
		'model': nn,
		'optimizer': optimizer,
		'batch_size': 4,
		'num_iterations': 20,
		'num_epochs': 20,
		'num_selfplay': 20,
		'sims_per':100, 
		'max_sims': 1000,
	}
	train_task = Trainer(trainer_args)
	start = time()
	# train_task.collect_train_data()
	train_task.train()
	end = time()
	print(end - start)
