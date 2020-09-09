
"""
GoThink/main.py
"""

"""
TO-DOS:
- 
"""

from board import Board
from player import Player
from bot import Bot

####################################################################################################

settings = {}

board_settings = {
    # Primary settings:
    'BOARD_SIZE': 9,
    # Console print characters:
    'NO_STONE_CHAR':        '-',
    'BLACK_STONE_CHAR':     '#',
    'WHITE_STONE_CHAR':     'O',
    'STAR_CHAR':            '*',
    'KO_CHAR':              'K',
    'BOARDER_CORNER_CHAR':  '+',
    'BOARDER_HOR_CHAR':     '-',
    'BOARDER_VERT_CHAR':    '|',
}

bot_settings = {
    # How much the influence is biased in favor of the positions closer to the stone.
    'RAW_INFLUENCE_BIAS': 5,
    # This value determines the maximum value of the influence grid, and adjusts all other influence
    # values to be proportionate with this maximum value.
    'RAW_INFLUENCE_CEILING': 10,
    # If a stone is in a corner of a 19x19 board, 37 is the # of steps (taxicab geometry) it takes
    # to get from that stone, to the farthest corner from that stone.  This value controls the lower
    # end of the values of the influence grid.
    # NOTE:  The reason this is a global is because I feel strongly that it should be a non-changing
    # constant, but I'm not 100% certain as of now.
    'RAW_INFLUENCE_MAX_STEPS': 36,
    # Console print settings:
    'RAW_INFLUENCE_PRINT_JUSTIFY_BY': 7,
    'RAW_INFLUENCE_PRINT_ROUND_DEC_BY': 2,
}

####################################################################################################

def main():

    # center = [4, 4]
    # point1 = center
    #
    # exit()

    board = Board(board_settings)

    black_bot = Bot(board, 'black', bot_settings)
    white = Player(board, 'white')

    # for pos in [
    #     [5, 0], [5, 1], [6, 2], [6, 3], [6, 4], [6, 5], [7, 5], [8, 5], [5, 2], [5, 3]
    # ]:  white.makeMove(pos)
    # for pos in [
    #     [7, 2], [7, 3], [7, 4], [8, 2], [8, 4], [6, 1], [6, 2], [6, 0]
    # ]:  black_bot.makeMove(pos)

    # for pos in [
    #     [2, 2], [3, 4], [6, 2], [5, 2], [7, 6], [6, 7], [8, 7]
    # ]:  white.makeMove(pos)
    # for pos in [
    #     [6, 5], [4, 6], [5, 3], [2, 6], [4, 3], [6, 6], [5, 7]
    # ]:  black_bot.makeMove(pos)

    black_bot.makeMove([4, 4])

    board.prettyPrint()

    # print(black_bot.getAngularProxInflGrid())

    print(black_bot.getWholeBoardRawInfluenceGrid(_to_print=True))

    # print("abs_life =", black_bot.groupHasAbsLife([7, 2]))

    exit()

####################################################################################################

main()
