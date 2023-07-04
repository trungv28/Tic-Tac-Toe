# Imports
import torch
from .vanilla_mcts.board import Board
from .minimax.tboard import TBoard
from .minimax import player
from .vanilla_mcts.mcts import MCTS
from .alphazero.mcts0 import MCTS0
from .alphazero.model import NeuralNetwork
from .alphazero.helper import get_device

def main():
    board = TBoard(10, 10, 5)

    playerX = player.HumanPlayer()
    playerO = player.BotPlayer('O', 2)
    last_move = None
    # device = get_device()
    # nn_args = {
    #     'num_filter': 32,
    #     'filter_size': 3,
    #     'hidden_size': 128, # for policy head
    #     'num_block': 9 # for resnet (should be 19 or 39)
    # }
    # nn = NeuralNetwork(nn_args, device)
    # path = './runs/iteration_7.pt'
    # nn.load_state_dict(torch.load(path))
    
    while not board.gameover():
        board.render()
        
        bboard = board.convert_to_binh_board()
        bboard = Board(bboard)
        mcts = MCTS(bboard, last_move, 20, 200)
        # mcts = MCTS0(bboard, last_move, nn, 100, 1000)
        mcts.search()

        r, c = mcts.advise().move
        moveX = c+1, r+1
        board.set_move(moveX, 'X')
        board.render()
        # exit(0)
        if board.gameover(): break

        moveO = playerO.get_move(board)
        board.set_move(moveO, 'O')
        print(f"Computer Move: {moveO}")
        board.render()
        tc, tr = moveO
        last_move = tr-1, tc-1

    
    board.render()
    if board.iswin('X'):
        print('Player X has won!')
    elif board.iswin('O'):
        print('Player O has won!')
    elif len(board.possible_moves()) == 0:
        print('Draw!')

main()
