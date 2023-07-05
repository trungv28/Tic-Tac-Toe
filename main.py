# Imports
from .minimax.tboard import TBoard
from .minimax import player
from .vanilla_mcts.board import Board
from .vanilla_mcts.mcts import Old_MCTS
from .mcts.mcts import MCTS

def main():
	board = TBoard(Board.max_row, Board.max_col, 5)
	last_move = None
	# playerO = player.BotPlayer('O', 2)
	while not board.gameover():
		bboard = board.convert_to_binh_board()
		bboard = Board(bboard)
		old_mcts = Old_MCTS(bboard, last_move, 20, 2000)
		old_mcts.search()
		
		r, c = old_mcts.advise().move

		last_move = r, c
		moveX = c+1, r+1
		board.set_move(moveX, 'X')
		print(f"Old_MCTS move: {moveX}")
		board.render()

		if board.gameover(): break

		bboard = board.convert_to_binh_board()
		bboard = Board(bboard)
		mcts = MCTS(bboard, last_move, depth=6, max_sims=2000)
		mcts.think()

		r, c = mcts.advise().last_move

		last_move = r, c
		moveO = c+1, r+1
		board.set_move(moveO, 'O')
		print(f"MCTS move: {moveO}")
		board.render()

		if board.gameover(): break

		# moveO = playerO.get_move(board)
		# board.set_move(moveO, 'O')
		# print(f"MinMax move: {moveO}")

	if board.iswin('X'):
		print('Player X has won!')
	elif board.iswin('O'):
		print('Player O has won!')
	elif len(board.possible_moves()) == 0:
		print('Draw!')

main()
