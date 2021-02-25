
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf

from functions import (
    reshapeFlatten, reshapeInsertDim, reshapeAddDim, reshapeMergeDims, getCountOfValue,
    getPosOfValue, replaceValueAtIndex
)

####################################################################################################

print("")

BLACK_VALUE = +1
WHITE_VALUE = -1
print(f"BLACK_VALUE = {BLACK_VALUE}")
print(f"WHITE_VALUE = {WHITE_VALUE}")
print("")

BOARD = tf.constant([
    [ 0, +1,  0,  0],
    [ 0, +1, +1, -1],
    [+1, -1, -1,  0],
    [-1,  0,  0,  0],
], dtype='int32')

# BOARD = tf.constant([
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0],
#     [ 0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0],
#     [ 0,  0,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  1,  0,  1,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  1,  0,  0,  1,  1,  0,  0,  0,  0,  0,  0,  1,  1,  0,  0,  0,  0],
#     [ 0,  0,  1,  1,  1,  0,  1,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  1,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  1,  1,  1,  0,  0,  0,  1,  0,  0,  0,  1,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  1,  0,  0,  1,  0,  1,  1,  0,  0],
#     [ 0,  0,  0,  1,  0,  1,  1,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,  0,  0],
#     [ 0,  0,  0,  0,  1,  0,  1,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  1,  0,  0,  0,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0]
# ], dtype='int32')

# BOARD = tf.tile(BOARD, [10] * 2)

print(BOARD, "<- BOARD\n")

####################################################################################################

BOARD_SIZE = BOARD.shape.as_list()[0]
# BOARD_POS_COUNT = BOARD_SIZE ** 2

# print(f"BOARD_SIZE = {BOARD_SIZE}")
# print(f"BOARD_POS_COUNT = {BOARD_POS_COUNT}")
# print("")

####################################################################################################

def main():

    # exit()

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

    black_group_assign = getGroupAssign(black_stones_count, black_stones_pos_2d)
    print(black_group_assign, "<- black_group_assign\n")

    black_group_lib_pos = getGroupLibPos(black_stones_count, black_stones_pos_2d, black_group_assign)
    print(black_group_lib_pos, "<- black_group_lib_pos\n")

####################################################################################################

def getGroupAssign(stone_count, stone_pos):

    """ temp_board (shape=(BOARD.shape + 2)):
    - temp_board is a representation of BOARD.
    - temp_board has an additional boarder of 0s around the perimeter.  The purpose of this is to
    avoid errors when finding neighbors of stones on the BOARD edge.
    - temp_board also replaces each value of BOARD from stone_pos with a unique int. The purpose of
    this is for easy stone reference/representation.
    """
    temp_coords = tf.cast(stone_pos + 1, dtype='int64')
    temp_value = tf.range(1, stone_count + 1, dtype='int64')
    temp_shape = tf.constant([BOARD_SIZE + 2] * 2, dtype='int64')
    temp_board = tf.sparse.to_dense(tf.SparseTensor(temp_coords, temp_value, temp_shape))
    temp_board = tf.cast(temp_board, dtype=BOARD.dtype)
    # print(temp_board, "<- temp_board\n")

    """ neighbors (shape=(?, 2)):
    - neighbors is a tensor where each value set within the 1st dim represents a neighbor set.
    - Each scalar value in neighbors is a mapping to temp_board.  So, if a neighbor set (1st dim
    values) is [1, 2], then that means that the 1 and 2 in temp_board are neighbors.
    - neighbors, as a list of all neighbor sets, is needed for building group_assign.
    """
    def getNeighbors(pos):
        y = pos[0] + 1
        x = pos[1] + 1
        neighbors = tf.stack([
            [temp_board[y][x], temp_board[y - 1][x]],
            [temp_board[y][x], temp_board[y][x + 1]],
            [temp_board[y][x], temp_board[y + 1][x]],
            [temp_board[y][x], temp_board[y][x - 1]],
        ])
        return neighbors
    neighbors = tf.map_fn(fn=lambda elem: getNeighbors(elem), elems=stone_pos)
    neighbors = reshapeMergeDims(neighbors, [0, 1])
    neighbors_mask = tf.equal(tf.reduce_any(tf.equal(neighbors, 0), axis=1), False)
    neighbors = tf.boolean_mask(neighbors, neighbors_mask)
    # print(neighbors, "<- neighbors\n")

    """ group_assign (shape=(stone_count)):
    - group_assign is a 1-dim list tensor, that is parallel to dim-1 of stone_pos, where each value
    of group_assign represents the group label assignment for that stone (paraellel to stone_pos).
    """
    ### init group_assign
    group_assign = tf.TensorArray(
        dtype=BOARD.dtype, size=0, dynamic_size=True, clear_after_read=False
    )
    _, group_assign = tf.while_loop(
        lambda i, _:  i < stone_count,
        lambda i, group_assign:  (i + 1, group_assign.write(i, i + 1)),
        (0, group_assign)
    )
    ### set group_assign
    def setGroupAssign(i, group_assign):
        a = neighbors[i, 0] - 1
        b = neighbors[i, 1] - 1
        group_assign = group_assign.write(b, group_assign.read(a))
        return i + 1, group_assign
    _, group_assign = tf.while_loop(
        lambda i, _:  i < neighbors.shape[0],
        lambda i, group_assign:  setGroupAssign(i, group_assign),
        (0, group_assign)
    )
    group_assign = group_assign.stack()
    ### format group_assign
    _, group_assign = tf.unique(group_assign, out_idx=BOARD.dtype)
    group_assign = group_assign + 1
    # print(group_assign, "<- group_assign\n")

    return group_assign

####################################################################################################

def getGroupLibPos(stone_count, stones_pos, group_assign):

    boarder_padded_board = tf.pad(BOARD, [[1, 1], [1, 1]], constant_values=2)
    # print(boarder_padded_board, "<- boarder_padded_board\n")

    zeros_pos = tf.cast(getPosOfValue(boarder_padded_board, 0), dtype='int64')
    zeros_count = getCountOfValue(boarder_padded_board, 0)
    new_zeros_values = tf.range(1, zeros_count + 1, dtype='int64')
    zeros_incr_board = tf.sparse.to_dense(tf.SparseTensor(
        zeros_pos, new_zeros_values, boarder_padded_board.shape
    ))
    zeros_incr_board = tf.cast(zeros_incr_board, dtype=BOARD.dtype)
    # print(zeros_incr_board, "<- zeros_incr_board\n")

    def getZeroNeighbors(pos):
        y = pos[0] + 1
        x = pos[1] + 1
        zero_neighbors = tf.stack([
            zeros_incr_board[y - 1][x], zeros_incr_board[y][x + 1],
            zeros_incr_board[y + 1][x], zeros_incr_board[y][x - 1],
        ])
        return zero_neighbors
    zero_neighbors = tf.map_fn(fn=lambda elem: getZeroNeighbors(elem), elems=stones_pos)
    # print(zero_neighbors, "<- zero_neighbors\n")

    zip_group_assign = reshapeAddDim(reshapeFlatten(tf.tile(reshapeAddDim(group_assign), [1, 4])))
    zip_zero_neighbors = reshapeAddDim(reshapeFlatten(zero_neighbors))
    group_zero_neighbors = tf.concat([zip_group_assign, zip_zero_neighbors], axis=1)
    zero_mask = tf.equal(tf.reduce_any(tf.equal(group_zero_neighbors, 0), axis=1), False)
    group_zero_neighbors = tf.boolean_mask(group_zero_neighbors, zero_mask)
    group_zero_neighbors = tf_unique_2d(group_zero_neighbors)
    # print(group_zero_neighbors, "<- group_zero_neighbors\n")

    group_lib_pos = tf.map_fn(
        fn=lambda elem: getPosOfValue(zeros_incr_board, elem),
        elems=group_zero_neighbors[:, 1]
    )
    group_lib_pos = reshapeMergeDims(group_lib_pos, [1, 2])
    group_lib_pos = tf.concat([reshapeAddDim(group_assign), group_lib_pos], axis=1)
    # print(group_lib_pos, "<- group_lib_pos\n")

    return group_lib_pos

    # group_lib_pos = tf.TensorArray(
    #     dtype=BOARD.dtype, size=0, dynamic_size=True, clear_after_read=False
    # )
    # def setGroupLibPos(i, group_lib_pos):
    #
    #     return i + 1, group_lib_pos
    # _, group_lib_pos = tf.while_loop(
    #     lambda i, _:  i < stones_count,
    #     lambda i, group_lib_pos:  setGroupLibPos(i, group_lib_pos),
    #     (0, group_lib_pos)
    # )
    # print(group_lib_pos, "<- group_lib_pos\n")

    # def getAllNeighbors(pos):
    #     some_neighbors = tf.stack([
    #
    #     ])
    #     return some_neighbors
    # all_neighbors = tf.vectorized_map(
    #     fn=lambda elem: getAllNeighbors(elem),
    #     elems=stones_pos
    # )

    exit()

####################################################################################################

def tf_unique_2d(x):
    """ Copied from stackoverflow...
    https://stackoverflow.com/questions/51487990/find-unique-values-in-a-2d-tensor-using-tensorflow
    """
    x_shape = tf.shape(x)  # (3,2)
    x1 = tf.tile(x, [1, x_shape[0]])  # [[1,2],[1,2],[1,2],[3,4],[3,4],[3,4]..]
    x2 = tf.tile(x, [x_shape[0], 1])  # [[1,2],[1,2],[1,2],[3,4],[3,4],[3,4]..]

    x1_2 = tf.reshape(x1, [x_shape[0] * x_shape[0], x_shape[1]])
    x2_2 = tf.reshape(x2, [x_shape[0] * x_shape[0], x_shape[1]])
    cond = tf.reduce_all(tf.equal(x1_2, x2_2), axis=1)
    cond = tf.reshape(cond, [x_shape[0], x_shape[0]])  # reshaping cond to match x1_2 & x2_2
    cond_shape = tf.shape(cond)
    cond_cast = tf.cast(cond, tf.int32)  # convertin condition boolean to int
    cond_zeros = tf.zeros(cond_shape, tf.int32)  # replicating condition tensor into all 0's

    # CREATING RANGE TENSOR
    r = tf.range(x_shape[0])
    r = tf.add(tf.tile(r, [x_shape[0]]), 1)
    r = tf.reshape(r, [x_shape[0], x_shape[0]])

    # converting TRUE=1 FALSE=MAX(index)+1 (which is invalid by default) so when we take min it wont
    # get selected & in end we will only take values <max(indx).
    f1 = tf.multiply(tf.ones(cond_shape, tf.int32), x_shape[0] + 1)
    f2 = tf.ones(cond_shape, tf.int32)
    # if false make it max_index+1 else keep it 1
    cond_cast2 = tf.where(tf.equal(cond_cast, cond_zeros), f1, f2)

    # multiply range with new int boolean mask
    r_cond_mul = tf.multiply(r, cond_cast2)
    r_cond_mul2 = tf.reduce_min(r_cond_mul, axis=1)
    r_cond_mul3, unique_idx = tf.unique(r_cond_mul2)
    r_cond_mul4 = tf.subtract(r_cond_mul3, 1)

    # get actual values from unique indexes
    op = tf.gather(x, r_cond_mul4)

    return (op)

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



# temp_temp_value = reshapeAddDim(reshapeInsertDim(temp_value, 1))
# n_compare_this = tf.cast(tf.tile(temp_temp_value, [1, stone_count, 5]), dtype=BOARD.dtype)
# # print(n_compare_this, "<- n_compare_this\n")
#
# n_compare_to_that = tf.tile(reshapeInsertDim(neighbors, 0), [stone_count, 1, 1])
# # print(n_compare_to_that, "<- n_compare_to_that\n")
#
# compare_bool_mask = tf.equal(n_compare_this, n_compare_to_that)
# # print(compare_bool_mask, "<- compare_bool_mask\n")
# compare_bool_mask = tf.reduce_any(compare_bool_mask, axis=2)
# compare_bool_mask = reshapeAddDim(compare_bool_mask)
# print(compare_bool_mask, "<- compare_bool_mask\n")



# """ get single_neighbors """
# single_neighbors = tf.TensorArray(
#     dtype=BOARD.dtype, size=0, dynamic_size=True, clear_after_read=False
# )
# def setSingleNeighbors(i, single_neighbors):
#     pos = stone_pos[i]
#     y, x = pos[0] + 1, pos[1] + 1
# single_neighbors = tf.while_loop(
#     lambda i, _: i < stone_count,
#     lambda i, single_neighbors:  setSingleNeighbors(i, single_neighbors),
#     (0, single_neighbors)
# )
#
# print(single_neighbors )

# while_out = tf.TensorArray(dtype=BOARD.dtype, size=0, dynamic_size=True, clear_after_read=False)
# _, while_out = tf.while_loop(
#     lambda i, _: i < stone_count,
#     lambda i, while_out: (i + 1, while_out.write(i, i + 1)),
#     (0, while_out)
# )
#
# def whileFunc(i, while_out):
#     pos = stone_pos[i]
#     group_value = while_out.read(i)
#
#
#
#     # while_out = while_out.write(i, group_value)
#
#     return (i + 1, while_out)
#
# _, while_out = tf.while_loop(
#     lambda i, _: i < stone_count, # cond
#     lambda i, while_out: whileFunc(i, while_out), # body
#     (0, while_out) # loop_vars
# )
# while_out = while_out.stack()
# print(while_out, "<- while_out\n")



# """
# # inp = tf.constant([0, 1, 2, 3])
# inp = tf.range(0, 1000)
#
# outp = tf.TensorArray(dtype='int32', size=0, dynamic_size=True, clear_after_read=False)
# outp = outp.write(0, inp[0])
#
# cond = lambda i, _: i < inp.shape[0]
# body = lambda i, outp: (i + 1, outp.write(i, inp[i] + outp.read(i - 1)))
# _, outp = tf.while_loop(cond, body, (1, outp))
# outp = outp.stack()
#
# print(inp)
# print(outp)
# """
