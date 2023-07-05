from .board import Board
def config_board(b:Board):
	b[(2,3)] = -1
	# b[(2,4)] = -1
	b[(3,2)] = -1

	b[(3,5)] = 1
	b[(4,6)] = 1
	b[(5,7)] = 1
	# b[(6,8)] = 1
	move = (4,6)
	# move = None
	return move