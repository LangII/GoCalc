
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf

from functions import (
    reshapeFlatten, reshapeInsertDim, reshapeAddDim, getCountOfValue, getPosOfValue,
    replaceValueAtIndex
)

####################################################################################################

print("")

BLACK_VALUE = +1
WHITE_VALUE = -1
# print(f"BLACK_VALUE = {BLACK_VALUE}")
# print(f"WHITE_VALUE = {WHITE_VALUE}")
# print("")

BOARD = tf.constant([
    [ 0,  0,  0,  0],
    [-1, +1, +1,  0],
    [ 0, -1,  0,  0],
    [ 0,  0, +1,  0],
], dtype='int32')
print(BOARD, "<- BOARD\n")

####################################################################################################

BOARD_SIZE = BOARD.shape.as_list()[0]
# BOARD_POS_COUNT = BOARD_SIZE ** 2

# print(f"BOARD_SIZE = {BOARD_SIZE}")
# print(f"BOARD_POS_COUNT = {BOARD_POS_COUNT}")
# print("")

####################################################################################################

def main():

    # flat_board = reshapeFlatten(BOARD)
    # print(flat_board, "<- flat_board\n")

    black_stones_count = getCountOfValue(BOARD, BLACK_VALUE)
    # white_stones_count = getCount(BOARD, WHITE_VALUE)

    black_stones_pos_2d = getPosOfValue(BOARD, BLACK_VALUE)
    # white_stones_pos_2d = getPosOfValue(BOARD, WHITE_VALUE)
    # black_stones_pos_1d = getPosOfValue(flat_board, BLACK_VALUE)
    # white_stones_pos_1d = getPosOfValue(flat_board, WHITE_VALUE)
    print(black_stones_pos_2d, "<- black_stones_pos_2d\n")
    # print(white_stones_pos_2d, "<- white_stones_pos_2d\n")
    # print(black_stones_pos_1d, "<- black_stones_pos_1d\n")
    # print(white_stones_pos_1d, "<- white_stones_pos_1d\n")

    black_groups = getGroups(black_stones_count, black_stones_pos_2d)

####################################################################################################

def getGroups(stone_count, stone_pos):

    group_assign = tf.range(1, stone_count + 1)

    def vectorLoop(pos, group_assign):
        return

    tf.vectorized_map(
        fn=lambda pos: vectorLoop(pos, group_assign),
        elems=stone_pos
    )

    return

####################################################################################################

main()
