
"""
GoCalc/main_console.py
"""

"""
TO-DOS:
-
"""

# Dynamically add parent folder to path.
import os, sys
cur_dir = os.getcwd()
insert_sys_path = cur_dir[:cur_dir.rfind('\\')]
sys.path.insert(1, insert_sys_path)

from gamelogic.board import Board
from gamelogic.stone import Stone
# from gamelogic.group import Group
from gamelogic.player import Player
from gamelogic.bot import Bot

import calculate.influencecalc as infl_calc

####################################################################################################

settings = {}

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

    board = Board()

    black = Player(board, 'black')
    white = Player(board, 'white')

    # for pos in [
    #     # [2, 3], [5, 4], [6, 2]
    #     [1, 1], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8]
    # ]:  black.makeMove(pos)

    for pos in [
        [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7], [0, 8]
    ]:  white.makeMove(pos)

    board.prettyPrint()

    infl_calc.getInfluence(board)

    # print(black_bot.getAngularProxInflGrid())

    # print(black_bot.getWholeBoardRawInfluenceGrid(to_print=True))

    # print("abs_life =", black_bot.groupHasAbsLife([7, 2]))

    exit()

####################################################################################################

main()
