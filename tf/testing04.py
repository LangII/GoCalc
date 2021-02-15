
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
    [+1, +1,  0,  0],
    [ 0, +1, +1,  0],
    [ 0,  0,  0, +1],
    [ 0, +1,  0, +1],
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

    # inp = tf.constant([0, 1, 2, 3])
    inp = tf.range(0, 100000)

    outp = tf.TensorArray(dtype='int32', size=0, dynamic_size=True, clear_after_read=False)
    outp = outp.write(0, inp[0])

    cond = lambda i, _: i < inp.shape[0]
    body = lambda i, outp: (i + 1, outp.write(i, inp[i] + outp.read(i - 1)))
    _, outp = tf.while_loop(cond, body, (1, outp))
    outp = outp.stack()

    print(inp)
    print(outp)

    exit()

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

    temp_coords = tf.cast(stone_pos + 1, dtype='int64')
    # temp_value = tf.constant(BLACK_VALUE, shape=[stone_count], dtype='int64')
    temp_value = tf.range(1, stone_count + 1, dtype='int64')
    temp_shape = tf.constant([BOARD_SIZE + 2] * 2, dtype='int64')
    temp_board = tf.sparse.to_dense(tf.SparseTensor(temp_coords, temp_value, temp_shape))
    temp_board = tf.cast(temp_board, dtype=BOARD.dtype)
    print(temp_board, "<- temp_board\n")

    def getNeighbors(pos):
        y, x = pos[0] + 1, pos[1] + 1
        neighbors = tf.stack([
            temp_board[y][x],
            temp_board[y - 1][x],
            temp_board[y][x + 1],
            temp_board[y + 1][x],
            temp_board[y][x - 1],
        ])
        return neighbors
    neighbors = tf.map_fn(
        fn=lambda elem: getNeighbors(elem),
        elems=stone_pos,
    )
    # neighbors = tf.sort(neighbors, direction='DESCENDING')
    # neighbors = tf.sort(neighbors)
    print(neighbors, "<- neighbors\n")

    temp_temp_value = reshapeAddDim(reshapeInsertDim(temp_value, 1))
    n_compare_this = tf.cast(tf.tile(temp_temp_value, [1, stone_count, 5]), dtype=BOARD.dtype)
    # print(n_compare_this, "<- n_compare_this\n")

    n_compare_to_that = tf.tile(reshapeInsertDim(neighbors, 0), [stone_count, 1, 1])
    # print(n_compare_to_that, "<- n_compare_to_that\n")

    compare_bool_mask = tf.equal(n_compare_this, n_compare_to_that)
    # print(compare_bool_mask, "<- compare_bool_mask\n")
    compare_bool_mask = tf.reduce_any(compare_bool_mask, axis=2)
    compare_bool_mask = reshapeAddDim(compare_bool_mask)
    print(compare_bool_mask, "<- compare_bool_mask\n")


    return

####################################################################################################

main()

####################################################################################################

# rag_neighbors = tf.RaggedTensor.from_tensor(neighbors, padding=0)
# rag_neighbors = tf.argsort(rag_neighbors)
# print(rag_neighbors)

# def getRaggedMap(t):
#     value = t[0]
#     return tf.where(t > 0, value, t)
# ragged_map = tf.vectorized_map(
#     fn=lambda elem:  getRaggedMap(elem),
#     elems=neighbors
# )
# print(ragged_map, "<- ragged_map\n")
#
# neighbors = reshapeFlatten(neighbors)
# ragged_map = reshapeFlatten(ragged_map)
#
# print(neighbors)
# print(ragged_map)
#
# rag_neighbors = tf.RaggedTensor.from_value_rowids(
#     values=neighbors,
#     value_rowids=ragged_map
# )
# print(rag_neighbors)
