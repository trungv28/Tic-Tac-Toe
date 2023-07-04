from torch import nn
from ..vanilla_mcts.board import MAX_COL, MAX_ROW

class ResidualLayer(nn.Module):
	def __init__(self, num_filter, filter_size = 3):
		'''
		num_filter: number of filter in each state
		filter_size: the dimension of filter
		'''
		super().__init__()
		self.block = nn.Sequential(
			nn.Conv2d(num_filter, num_filter, filter_size, 1, 1, bias=False),
			nn.BatchNorm2d(num_filter),
			nn.ReLU(),
			nn.Conv2d(num_filter, num_filter, filter_size, 1, 1, bias=False),
			nn.BatchNorm2d(num_filter)
		)
		self.final_relu = nn.ReLU()
	
	def forward(self, x):
		out = self.block(x)
		out += x
		out = self.final_relu(out)
		return out

class ConvolutionalLayer(nn.Module):
	def __init__(self, num_filter, filter_size=3):
		'''
		num_filter: number of filter in each state
		filter_size: the dimension of filter
		'''
		super().__init__()
		self.cv = nn.Sequential(
			nn.Conv2d(3, num_filter, filter_size, 1, 1),
			nn.BatchNorm2d(num_filter),
			nn.ReLU()
		)

	def forward(self, x):
		return self.cv(x)
	
class ValueHead(nn.Module):
	def __init__(self, num_old_filter, hidden_size):
		'''
		num_old_filter: number of filter in the previous state
		hidden_size: the size of the linear layer
		'''
		super().__init__()
		self.vh = nn.Sequential(
			nn.Conv2d(num_old_filter, 1, 1),
			nn.BatchNorm2d(1),
			nn.ReLU(),
			nn.Flatten(),
			nn.Linear(MAX_ROW*MAX_COL, hidden_size),
			nn.ReLU(),
			nn.Linear(hidden_size, 1),
			nn.Tanh()
		)

	def forward(self, x):
		return self.vh(x)
	
class PolicyHead(nn.Module):
	def __init__(self, num_old_filter):
		super().__init__()
		self.ph = nn.Sequential(
			nn.Conv2d(num_old_filter, 2, 1),
			nn.BatchNorm2d(2),
			nn.ReLU(),
			nn.Flatten(),
			nn.Linear(MAX_ROW*MAX_COL*2, MAX_ROW*MAX_COL)
		)

	def forward(self, x):
		return self.ph(x)
	
class NeuralNetwork(nn.Module):
	def __init__(self, args:dict, device):
		'''
		num_filter: number of filter
		hidden_size: the size of hidden layer
		num_block: the number of residual blocks
		'''
		super().__init__()
		self.device = device

		num_filter, filter_size, hidden_size, num_block = \
		args['num_filter'], args['filter_size'], args['hidden_size'], args['num_block']
		
		self.convolution_layer = ConvolutionalLayer(num_filter, filter_size)
		self.resnet = nn.ModuleList(
			[ResidualLayer(num_filter, filter_size) for _ in range(num_block)]
		)

		self.value_head = ValueHead(num_filter, hidden_size)
		self.policy_head = PolicyHead(num_filter)

	def forward(self, x):
		out = self.convolution_layer(x)
		for block in self.resnet:
			out = block(out)
		value = self.value_head(out)
		policy = self.policy_head(out)
		return policy, value