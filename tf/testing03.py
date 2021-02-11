
import os, sys
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras

import math

from functions import (
    applyScale, sort2dByCol, roundFloat, getCount, reshapeInsertDim, reshapeAddDim, reshapeMergeDims
)

np.set_printoptions(
    linewidth=220, # <- How many characters per line before new line.
    threshold=300, # <- How many lines allowed before summarized print.
    # threshold=sys.maxsize, # <- How many lines allowed before summarized print. (no summarization)
    edgeitems=10, # <- When summarized, how many edge values are printed.
    suppress=True, # <- Suppress scientific notation.
    precision=4, # <- How many decimal places on floats.
    # sign='+', # <- Display + for positive numbers.
)

####################################################################################################

BOARD = tf.constant([
    [ 0,  0,  0,  0],
    [-1,  0, +1,  0],
    [ 0, -1,  0,  0],
    [ 0,  0, +1,  0],
], dtype='int32')
print("\nBOARD =", BOARD)

# BOARD = tf.constant([
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0, +1,  0, -1,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0, -1,  0],
#     [ 0,  0, +1,  0, -1,  0, +1,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0, -1,  0,  0, -1, +1,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0]
# ], dtype='int32')
# print("\nBOARD =", BOARD)

# BOARD = tf.constant([
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, +1,  0,  0,  0],
#     [ 0,  0,  0, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, +1,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, +1,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0]
# ], dtype='int32')
# print("\nBOARD =", BOARD)

# BOARD = tf.constant([
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0]
# ], dtype='int32')
# print("\nBOARD =", BOARD)

####################################################################################################

EMPTY_VALUE = 0
BLACK_VALUE = +1
WHITE_VALUE = -1

PRED_VALUE = BLACK_VALUE
# PRED_VALUE = WHITE_VALUE

BOARD_SHAPE = BOARD.shape.as_list()
EMPTY_COUNT = getCount(BOARD, EMPTY_VALUE)
BLACK_COUNT = getCount(BOARD, BLACK_VALUE)
WHITE_COUNT = getCount(BOARD, WHITE_VALUE)
BOTH_COUNT = BLACK_COUNT + WHITE_COUNT
EMPTY_COUNT_PER_PRED = EMPTY_COUNT - 1
BLACK_COUNT_PER_PRED = BLACK_COUNT if PRED_VALUE == WHITE_VALUE else BLACK_COUNT + 1
WHITE_COUNT_PER_PRED = WHITE_COUNT if PRED_VALUE == BLACK_VALUE else WHITE_COUNT + 1
BOTH_COUNT_PER_PRED = BLACK_COUNT_PER_PRED + WHITE_COUNT_PER_PRED
EMPTY_COUNT_ALL_PRED = EMPTY_COUNT * EMPTY_COUNT_PER_PRED
MAX_DIST = math.hypot(*BOARD_SHAPE)

print("")
print(f"BOARD_SHAPE = {BOARD_SHAPE}")
print(f"EMPTY_COUNT = {EMPTY_COUNT}")
print(f"BLACK_COUNT = {BLACK_COUNT}")
print(f"WHITE_COUNT = {WHITE_COUNT}")
print(f"BOTH_COUNT = {BOTH_COUNT}")
print(f"EMPTY_COUNT_PER_PRED = {EMPTY_COUNT_PER_PRED}")
print(f"BLACK_COUNT_PER_PRED = {BLACK_COUNT_PER_PRED}")
print(f"WHITE_COUNT_PER_PRED = {WHITE_COUNT_PER_PRED}")
print(f"BOTH_COUNT_PER_PRED = {BOTH_COUNT_PER_PRED}")
print(f"EMPTY_COUNT_ALL_PRED = {EMPTY_COUNT_ALL_PRED}")
print(f"MAX_DIST = {MAX_DIST}")
print("")

####################################################################################################

""" WEIGHTS """
DIST_DECAY_GREATERTHAN_WEIGHT = 4.0
DIST_DECAY_LINEAR_WEIGHT = 0.2
DIST_ZERO_GREATERTHAN_WEIGHT = 8.0
ANGLES_LESSTHAN_WEIGHT = 45.0
ANGLES_LINEAR_WEIGHT = 0.2
OPP_STONE_ANGLE_LESSTHAN_WEIGHT = 15.0
OPP_STONE_DIST_LESSTHAN_WEIGHT = 5.0
OPP_STONE_GROWTH_LINEAR_WEIGHT = 8.0
PRED_MOVE_EMPTY_INFL_CLAMP_WEIGHT = 1.0

####################################################################################################



PRED_MOVE_I = 60
# TESTING_PRINT = 'pred_move_infls'
TESTING_PRINT = 'prediction'

# print(tf.gather_nd(tf.constant([
#     [[2, 2], [4, 4], [6, 6], [8, 8]],
#     [[3, 3], [5, 5], [7, 7], [9, 9]]
# ]), tf.constant([[0, 1], [1, 1]])))
# exit()



"""'''''''''''''''''''''''''''''''''''''''''''''''''
'''  GET PRIMARY TENSOR FOR WEIGHT APPLICATION   '''
'''''''''''''''''''''''''''''''''''''''''''''''''"""



""" empty_coords """
""" A list of all coords with no stone. """
empty_coords = tf.cast(tf.where(tf.equal(BOARD, 0)), dtype='int32')
# print(empty_coords, "<- empty_coords")



""" pred_moves """
""" A list of all possible next moves that will have influence predicted. """
def getPredMoves(coord):
    return tf.sparse.to_dense(tf.SparseTensor([coord], [PRED_VALUE], BOARD_SHAPE))
pred_moves = tf.vectorized_map(fn=lambda coord: getPredMoves(coord), elems=empty_coords)
tiled_board = tf.tile(tf.reshape(BOARD, [1, *BOARD_SHAPE]), [EMPTY_COUNT, 1, 1])
pred_moves = pred_moves + tiled_board
# print(pred_moves, "<- pred_moves")



""" pred_empty_coords """
""" pred_black_coords """
""" pred_white_coords """
""" Tensor similar to empty_coords.  Except what empty_coords does for the current board
position, each tensor does for every possible board position in pred_moves for each value. """
def getPredValueCoords(pred_moves, value):
    pred_color_coords = tf.cast(tf.where(tf.equal(pred_moves, value)), dtype='int32')
    return tf.reshape(pred_color_coords[:, 1:], [EMPTY_COUNT, -1, 2])
pred_empty_coords = getPredValueCoords(pred_moves, EMPTY_VALUE)
pred_black_coords = getPredValueCoords(pred_moves, BLACK_VALUE)
pred_white_coords = getPredValueCoords(pred_moves, WHITE_VALUE)
# print(pred_empty_coords, "<- pred_empty_coords")
# print(pred_black_coords, "<- pred_black_coords")
# print(pred_white_coords, "<- pred_white_coords")



""" pred_black_normals """
""" pred_white_normals """
""" Tensors representing the coord normals of each stone in each predicted next move. """
def getPredValueNormals(
    pred_empty_coords, pred_value_coords, empty_count_per_pred, value_count_per_pred
):
    pred_empty_coords_resh = reshapeInsertDim(pred_empty_coords, 2)
    empty_multiples =  tf.constant([1, 1, value_count_per_pred, 1])
    pred_empty_coords_tiled = tf.tile(pred_empty_coords_resh, empty_multiples)
    pred_value_coords_resh = reshapeInsertDim(pred_value_coords, 1)
    value_multiples = tf.constant([1, empty_count_per_pred, 1, 1])
    pred_value_coords_tiled = tf.tile(pred_value_coords_resh, value_multiples)
    return pred_value_coords_tiled - pred_empty_coords_tiled
pred_black_normals = getPredValueNormals(
    pred_empty_coords, pred_black_coords, EMPTY_COUNT_PER_PRED, BLACK_COUNT_PER_PRED
)
pred_white_normals = getPredValueNormals(
    pred_empty_coords, pred_white_coords, EMPTY_COUNT_PER_PRED, WHITE_COUNT_PER_PRED
)
# print(pred_black_normals, "<- pred_black_normals")
# print(pred_white_normals, "<- pred_white_normals")



""" pred_black_dists """
""" pred_white_dists """
""" Tensors representing the distance between each empty coord and each value coord for each
predicted next move. """
def getDistsFromNormals(normals):
    flat_pred_value_normals = tf.reshape(tf.cast(normals, dtype='float32'), [-1, 2])
    pred_value_dists = tf.norm(flat_pred_value_normals, ord='euclidean', axis=1)
    return tf.reshape(pred_value_dists, normals.shape[:-1])
pred_black_dists = getDistsFromNormals(pred_black_normals)
pred_white_dists = getDistsFromNormals(pred_white_normals)
# print(pred_black_dists, "<- pred_black_dists")
# print(pred_white_dists, "<- pred_white_dists")



""" pred_black_angles """
""" pred_white_angles """
""" Tensors representing the angle of each value coord from each empty coord for each predicted
next move. """
def getAnglesFromNormals(normals):
    y_normals = tf.cast(normals[:, :, :, 0] * -1, dtype='float32')
    x_normals = tf.cast(normals[:, :, :, 1], dtype='float32')
    pred_value_angles = tf.atan2(y_normals, x_normals) * (180 / math.pi)
    return tf.where(pred_value_angles >= 0, pred_value_angles, pred_value_angles + 360)
pred_black_angles = getAnglesFromNormals(pred_black_normals)
pred_white_angles = getAnglesFromNormals(pred_white_normals)
# print(pred_black_angles, "<- pred_black_angles")
# print(pred_white_angles, "<- pred_white_angles")



""" pred_stones_dists_angles """
""" Tensor representing each stone's data (value, dist, angle) in relation to each empty coord, for
each pred move board (each empty coord's sub dim is sorted by stone's dist).
NOTE:  pred_stones_dists_angles is the primary tensor to be fed into the model's weights application
layers.
NOTE:  pred_stones_dists_angles' shape remains to not have the outer layer representing each
predicted next move.  This is for the purpose of faster calculations and the output must be reshaped
after calculations. """
def getStoneDistsAngles(pred_value_dists, pred_value_angles, stone_value):
    pred_value_dists_resh = reshapeAddDim(pred_value_dists)
    pred_value_angles_resh = reshapeAddDim(pred_value_angles)
    stone_value = tf.constant(stone_value, dtype='float32')
    pred_value_stones = tf.fill(pred_value_dists_resh.shape, stone_value)
    return tf.concat([pred_value_stones, pred_value_dists_resh, pred_value_angles_resh], axis=3)
pred_black_stone_dists_angles = getStoneDistsAngles(pred_black_dists, pred_black_angles, BLACK_VALUE)
pred_white_stone_dists_angles = getStoneDistsAngles(pred_white_dists, pred_white_angles, WHITE_VALUE)
pred_stones_dists_angles = tf.concat(
    [pred_black_stone_dists_angles, pred_white_stone_dists_angles], axis=2
)
pred_stones_dists_angles = reshapeMergeDims(pred_stones_dists_angles, [0, 1])
pred_stones_dists_angles = tf.vectorized_map(
    fn=lambda pred_empty: sort2dByCol(pred_empty, 1),
    elems=pred_stones_dists_angles
)
# print(pred_stones_dists_angles, "<- pred_stones_dists_angles")



""" pred_stones """
""" pred_dists """
""" pred_angles """
""" Tensors needed for tensor play in calculating predicted influences. """
pred_stones = pred_stones_dists_angles[:, :, 0]
pred_dists = pred_stones_dists_angles[:, :, 1]
pred_angles = pred_stones_dists_angles[:, :, 2]



"""'''''''''''''''''''''''''''
'''   GET RAW INFLUENCES   '''
'''''''''''''''''''''''''''"""



""" raw_infls """
""" Tensor representing the raw base influences of each stone on each empty coord for each
predicted next move."""
raw_infls = (MAX_DIST - pred_dists) * pred_stones
raw_infls = applyScale(raw_infls, [0, MAX_DIST], [0, 1])
# print(raw_infls, "<- raw_infls")



"""''''''''''''''''''''''''''''''''''''''''
'''   GET DISTANCE WEIGHT ADJUSTMENTS   '''
''''''''''''''''''''''''''''''''''''''''"""



""" infls_dist_decay_weight_adjs """
""" Tensor representing the decay of values of raw_infls based on dist. """
infls_dist_decay_weight_adjs = tf.cast(tf.where(
    pred_dists > DIST_DECAY_GREATERTHAN_WEIGHT, DIST_DECAY_LINEAR_WEIGHT, 1
), dtype='float32')
# print(infls_dist_decay_weight_adjs, "<- infls_dist_decay_weight_adjs")



""" infls_dist_zero_weight_adjs """
""" Tensor representing the zero out of values of raw_infls based on dist. """
infls_dist_zero_weight_adjs = tf.cast(tf.where(
    pred_dists > DIST_ZERO_GREATERTHAN_WEIGHT, 0, 1
), dtype='float32')
# print(infls_dist_zero_weight_adjs, "<- infls_dist_zero_weight_adjs")



"""'''''''''''''''''''''''''''''''''''''''
'''   GET BARRIER WEIGHT ADJUSTMENTS   '''
'''''''''''''''''''''''''''''''''''''''"""



""" angle_difs """
""" A tensor (with mirrored values) representing a matrix of angular differences between each stone
within each empty coord within each predicted next move. """
angle_tiled_y = tf.tile(reshapeInsertDim(pred_angles, 1), [1, BOTH_COUNT_PER_PRED, 1])
angle_tiled_x = tf.tile(reshapeAddDim(pred_angles), [1, 1, BOTH_COUNT_PER_PRED])
angle_difs = tf.abs(angle_tiled_x - angle_tiled_y)
angle_difs = tf.where(angle_difs > 180, 360 - angle_difs, angle_difs)
print(angle_difs, "<- angle_difs")
exit()



""" raw_angle_infls """
""" A tensor (with mirrored values) representing a matrix of influences for each stone's angle vs
each stone's angle per empty coord for each predicted move. """
raw_angle_infls = tf.where(angle_difs <= ANGLES_LESSTHAN_WEIGHT, ANGLES_LINEAR_WEIGHT, 1)
# print(raw_angle_infls, "<- raw_angle_infls")



""" angle_mirror_mask """
""" A bool tensor used to cancel out the unwanted mirrored values in raw_angle_infls. """
mirror_shape = [BOTH_COUNT_PER_PRED] * 2
mirror_coords = tf.cast(tf.where(tf.equal(tf.zeros(mirror_shape), 0)), dtype='int32')
mirror_y = -tf.cast(mirror_coords[:, 0], dtype='float32')
mirror_x = tf.cast(mirror_coords[:, 1], dtype='float32')
mirror_angles = tf.atan2(mirror_y, mirror_x) * (180 / math.pi)
mirror_angles = tf.where(mirror_angles > 0, mirror_angles, mirror_angles + 360)
angle_mirror_mask = tf.where(mirror_angles < 315, True, False)
angle_mirror_mask = tf.reshape(angle_mirror_mask, [1] + mirror_shape)
angle_mirror_mask = tf.tile(angle_mirror_mask, [EMPTY_COUNT_ALL_PRED, 1, 1])
# print(angle_mirror_mask, "<- angle_mirror_mask")



""" angle_stones_mask """
""" A bool tensor used to cancel out the unwanted like-stone values in raw_angle_infls. """
stones_tiled_y = tf.reshape(pred_stones, [-1, 1, BOTH_COUNT_PER_PRED])
stones_tiled_y = tf.tile(stones_tiled_y, [1, BOTH_COUNT_PER_PRED, 1])
stones_tiled_x = tf.reshape(pred_stones, [-1, BOTH_COUNT_PER_PRED, 1])
stones_tiled_x = tf.tile(stones_tiled_x, [1, 1, BOTH_COUNT_PER_PRED])
angle_stones_mask = stones_tiled_y * stones_tiled_x
angle_stones_mask = tf.where(angle_stones_mask == -1, True, False)
# print(angle_stones_mask, "<- angle_stones_mask")



""" masked_angle_infls """
""" A tensor with the values of raw_angle_infls masked by angle_mirror_mask and
angle_stones_mask. """
masked_angle_infls = tf.where(angle_stones_mask, raw_angle_infls, 1)
masked_angle_infls = tf.where(angle_mirror_mask, masked_angle_infls, 1)
# print(masked_angle_infls, "<- masked_angle_infls")



""" infls_angle_decay_weight_adjs """
"""  """
infls_angle_decay_weight_adjs = tf.reduce_prod(masked_angle_infls, axis=2)
# print(infls_angle_decay_weight_adjs, "<- infls_angle_decay_weight_adjs")



"""'''''''''''''''''''''''''''''''''''''''
'''   GET SUPPORT WEIGHT ADJUSTMENTS   '''
'''''''''''''''''''''''''''''''''''''''"""



"""
The idea is that under the current conditions, influence predictions favor the center of the board
too much.  The model needs to understand the ease of securing territory closer to the walls.  There
is another similar benefit in territory development:  Developing near like stones.  A stone can have
similar support from the wall as from a like stone.

The plan is too have an infls_angle(support)_growth weight_adjs.  The growth is that the empty
coords influence will increase under this condition.  And it is angular because it verifies a
greater than angular condition.

The closest stone to the empty, will collect stones that are at an angle greater than a weight.
These collected stones will maintain their sort by distance.  If the closest stone within this group
of collected stones is a stone like the stone closest to the empty, then the empty will receive the
growth adjustment.

Somehow, this calculation will also need to be made for if there are no stones that meet the
greater than requirements, then the calculation will be made based on the closest wall as a support.
"""



# print(pred_stones_dists_angles, "<- pred_stones_dists_angles")

# print(pred_empty_coords)

pred_empty_coords_resh = tf.cast(reshapeMergeDims(pred_empty_coords, [0, 1]), dtype='int64')
# print(pred_empty_coords_resh)

min_filler = tf.fill([EMPTY_COUNT_ALL_PRED, 1], tf.constant(-1, dtype='int64'))
max_filler = tf.fill([EMPTY_COUNT_ALL_PRED, 1], tf.constant(BOARD_SHAPE[0], dtype='int64'))
top_wall_coords = tf.concat([min_filler, reshapeAddDim(pred_empty_coords_resh[:, 1])], axis=1)
top_wall_coords = reshapeInsertDim(top_wall_coords, 1)
# print(top_wall_coords)
bottom_wall_coords = tf.concat([max_filler, reshapeAddDim(pred_empty_coords_resh[:, 1])], axis=1)
bottom_wall_coords = reshapeInsertDim(bottom_wall_coords, 1)
# print(bottom_wall_coords)
left_wall_coords = tf.concat([reshapeAddDim(pred_empty_coords_resh[:, 0]), min_filler], axis=1)
left_wall_coords = reshapeInsertDim(left_wall_coords, 1)
# print(left_wall_coords)
right_wall_coords = tf.concat([reshapeAddDim(pred_empty_coords_resh[:, 0]), max_filler], axis=1)
right_wall_coords = reshapeInsertDim(right_wall_coords, 1)
# print(right_wall_coords)

wall_coords = tf.concat([
    top_wall_coords, bottom_wall_coords, left_wall_coords, right_wall_coords
], axis=1)
# print(wall_coords)

wall_dists = tf.concat([
    reshapeInsertDim(pred_empty_coords_resh[:, 0], 1),
    reshapeInsertDim(BOARD_SHAPE[0] - pred_empty_coords_resh[:, 0] - 1, 1),
    reshapeInsertDim(pred_empty_coords_resh[:, 1], 1),
    reshapeInsertDim(BOARD_SHAPE[1] - pred_empty_coords_resh[:, 1] - 1, 1),
], axis=1)
# print(wall_dists)

wall_dists_min = tf.argmin(wall_dists, axis=1)
# print(reshapeAddDim(wall_dists_min))



wall_coords = tf.reshape(tf.gather_nd(
    wall_coords,
    tf.concat([
        reshapeAddDim(tf.cast(tf.range(EMPTY_COUNT_ALL_PRED), dtype='int64')),
        reshapeAddDim(wall_dists_min)
    ], axis=1)
), [EMPTY_COUNT, EMPTY_COUNT_PER_PRED, 2])
# print(wall_coords)



"""
Now that I have closest_wall_coords I need to append a like stone to the end of each coord data set
of pred_stones_dists_angles at the coord of closest_wall_coords (with calculations of dist and
angle).

Then run the calculations for support adjustments:
- For each empty coord data set in pred_stones_dists_angles:
    - Get closest stone.
    - Get list of stones that are "opposite" of closest stone from empty coord using angle greater
    than weight.
    - If closest stone in "opposite" list is a like stone, apply support adjustment.
        - This is considering that the closest_wall_coords has been appended as like stones.
"""



# print(pred_empty_coords, "<- pred_empty_coords")

# pred_empty_coords_resh = reshapeMergeDims(pred_empty_coords, [0, 1])
# print(pred_empty_coords_resh)

wall_normals = wall_coords - tf.cast(pred_empty_coords, dtype='int64')
wall_normals = reshapeInsertDim(wall_normals, 2)
# print(wall_normals, "<- wall_normals")

wall_dists = getDistsFromNormals(wall_normals)
# print(wall_dists, "<- wall_dists")

wall_angles = getAnglesFromNormals(wall_normals)
# print(wall_angles, "<- wall_angles")

wall_stones = tf.reshape(pred_stones_dists_angles[:, 0, 0], [EMPTY_COUNT, -1, 1])
# print(wall_stones)

# wall_stone_dists_angles = getStoneDistsAngles(wall_dists, wall_angles, PRED_VALUE)

wall_stone_dists_angles = reshapeInsertDim(tf.concat([
    wall_stones, wall_dists, wall_angles
], axis=2), 2)
# print(wall_stone_dists_angles)
# exit()

wall_stone_dists_angles = reshapeMergeDims(wall_stone_dists_angles, [0, 1])
# print(wall_stone_dists_angles, "<- wall_stone_dists_angles")

pred_sda_w_wall = tf.concat([pred_stones_dists_angles, wall_stone_dists_angles], axis=1)
pred_sda_w_wall = tf.vectorized_map(
    fn=lambda pred_empty: sort2dByCol(pred_empty, 1),
    elems=pred_sda_w_wall
)
# print(pred_sda_w_wall, "<- pred_sda_w_wall")

"""
I now have wall stones present in pred_stones_dists_angles (as pred_sda_w_wall).  Should be all set
to start calculating support adjustments.
"""

""" Get support stone (closest stone on opposite side of closest stone to empty). """

closest_stones = pred_stones_dists_angles[:, 0, :]
# print(closest_stones, "<- closest_stones")

closest_stones_angles = closest_stones[:, 2]
# print(closest_stones_angles, "<- closest_stones_angles")

opposite_angles = tf.where(
    closest_stones_angles >= 180, closest_stones_angles - 180, closest_stones_angles + 180
)
# print(opposite_angles, "<- opposite_angles")

opposite_angles_tiled = tf.tile(reshapeAddDim(opposite_angles), [1, BOTH_COUNT_PER_PRED + 1])
# print(opposite_angles_tiled)

opp_angles_dif = tf.abs(pred_sda_w_wall[:, :, 2] - opposite_angles_tiled)
opp_angles_dif = tf.where(opp_angles_dif > 180, 360 - opp_angles_dif, opp_angles_dif)
# print(opp_angles_dif)

opp_angles_mask = tf.where(opp_angles_dif <= OPP_STONE_ANGLE_LESSTHAN_WEIGHT, True, False)
# opp_angles_mask_resh = reshapeAddDim(opp_angles_mask)
# opp_angles_mask_resh = tf.cast(opp_angles_mask_resh, dtype='float32')
# print(opp_angles_mask)

closest_opp_stone = tf.argmax(opp_angles_mask, axis=1)
closest_opp_stone = tf.gather_nd(
    pred_sda_w_wall,
    tf.concat([
        reshapeAddDim(tf.range(EMPTY_COUNT_ALL_PRED)),
        tf.cast(reshapeAddDim(closest_opp_stone), dtype='int32')
    ], axis=1)
)
# print(closest_opp_stone, "<- closest_opp_stone")

# i = 21
# print(pred_sda_w_wall[i], "<- pred_sda_w_wall")
# print("")
# print(closest_opp_stone[i], "<- closest_opp_stone")



"""
TURNOVER NOTES:  Just got closest_opp_stone.  Now need to create a new weight comparing dist between
closest_stone and closest_opp_stone.  If closest_stone and closest_opp_stone are like, and If dist
is within weight then apply adj weight.
"""



is_support_stone = closest_stones[:, 0] == closest_opp_stone[:, 0]
is_within_dist = (closest_stones[:, 1] + closest_opp_stone[:, 1]) < OPP_STONE_DIST_LESSTHAN_WEIGHT


infls_opp_angle_growth_weight_adjs = tf.where(
    tf.logical_and(is_support_stone, is_within_dist), OPP_STONE_GROWTH_LINEAR_WEIGHT, 1.0
)
pred_empty_coords_3d = tf.where(tf.equal(pred_moves, 0))
infls_opp_angle_growth_weight_adjs = tf.SparseTensor(
    pred_empty_coords_3d, infls_opp_angle_growth_weight_adjs, pred_moves.shape
)
infls_opp_angle_growth_weight_adjs = tf.sparse.to_dense(infls_opp_angle_growth_weight_adjs)
# print(infls_opp_angle_growth_weight_adjs, "<- infls_opp_angle_growth_weight_adjs")



"""
pred_move_infls = tf.reduce_sum(pred_moves_stone_infls, axis=1)
pred_empty_coords_3d = tf.where(tf.equal(pred_moves, 0))
pred_move_infls = tf.SparseTensor(pred_empty_coords_3d, pred_move_infls, pred_moves.shape)
pred_move_infls = tf.sparse.to_dense(pred_move_infls)
# print(pred_move_infls, "<- pred_move_infls")
"""

"""
angle_tiled_y = tf.tile(reshapeInsertDim(pred_angles, 1), [1, BOTH_COUNT_PER_PRED, 1])
angle_tiled_x = tf.tile(reshapeAddDim(pred_angles), [1, 1, BOTH_COUNT_PER_PRED])
angle_difs = tf.abs(angle_tiled_x - angle_tiled_y)
angle_difs = tf.where(angle_difs > 180, 360 - angle_difs, angle_difs)
# print(angle_difs, "<- angle_difs")
"""

"""
wall_coords = tf.reshape(tf.gather_nd(
    wall_coords,
    tf.concat([
        reshapeAddDim(tf.cast(tf.range(EMPTY_COUNT_ALL_PRED), dtype='int64')),
        reshapeAddDim(wall_dists_min)
    ], axis=1)
), [EMPTY_COUNT, EMPTY_COUNT_PER_PRED, 2])
"""

# closest_stones_value = closest_stones[:, 0]
# closest_stones_tiled = tf.tile(reshapeAddDim(closest_stones_value), [1, BOTH_COUNT_PER_PRED + 1])
# print(closest_stones_tiled)
# print(pred_sda_w_wall[:, :, 0])
# stones_mask = tf.where(closest_stones_tiled == pred_sda_w_wall[:, :, 0], True, False)
# print(stones_mask)

# support_mask = tf.logical_and(opp_angles_mask, stones_mask)
# support_mask = tf.where(opp_angles_mask and stones_mask, True, False)
# print(support_mask)

# print(pred_sda_w_wall[:, :, 0])
# print(opp_angles_mask)

# is_opp_like_stone = tf.where((pred_sda_w_wall[:, :, 0] + opp_angles_mask) == 2, 1.0, 0.0)
# print(is_opp_like_stone)

# is_opp_stone = tf.where(pred_sda_w_wall[:, :, 0] + )
# print(opp_angles_mask_resh)

# print(tf.concat([pred_sda_w_wall, reshapeAddDim(is_opp_like_stone)], axis=-1))



# i = 117643
# print("")
# print(wall_coords[i])
# print("")
# print(wall_dists[i])
# print("")
# print(wall_dists_min[i])
# print("")
# print(closest_wall_coords[i])

# wall_dists_min_mask = tf.where(tf.equal(wall_dists == wall_dists_min))



"""'''''''''''''''''''''''''''''''''''''''
'''   GET CLAMPED WEIGHT ADJUSTMENTS   '''
'''''''''''''''''''''''''''''''''''''''"""



"""
Influences should have some degree of a value clamp.  It's not like if you have an empty surrounded
by 10 black stones vs surrounded by 4 black stones the empty will be worth more points in the end.
An empty that is claimed by a player will still have the same value whether it is influenced by 20
like stones or 5 like stones.
"""



"""'''''''''''''''''''''''''''''''''''''''''''''''''''
'''   APPLY WEIGHT ADJUSTMENTS TO RAW INFLUENCES   '''
'''''''''''''''''''''''''''''''''''''''''''''''''''"""



""" pred_moves_stone_infls """
"""  """
pred_moves_stone_infls = raw_infls
pred_moves_stone_infls *= infls_dist_decay_weight_adjs
pred_moves_stone_infls *= infls_dist_zero_weight_adjs
pred_moves_stone_infls *= infls_angle_decay_weight_adjs
# print(pred_moves_stone_infls, "<- pred_moves_stone_infls")



"""'''''''''''''''''''''''''''''''''''''''''''''''''''''''
'''   REDUCE STONE INFLUENCES TO GET MOVE INFLUENCES   '''
'''''''''''''''''''''''''''''''''''''''''''''''''''''''"""



""" pred_move_infls """
"""  """
pred_move_infls = tf.reduce_sum(pred_moves_stone_infls, axis=1)
pred_empty_coords_3d = tf.where(tf.equal(pred_moves, 0))
pred_move_infls = tf.SparseTensor(pred_empty_coords_3d, pred_move_infls, pred_moves.shape)
pred_move_infls = tf.sparse.to_dense(pred_move_infls)
# print(pred_move_infls, "<- pred_move_infls")



"""''''''''''''''''''''''''''''''''''''''''''''''''''''
'''   APPLY WEIGHT ADJUSTMENTS TO MOVE INFLUENCES   '''
''''''''''''''''''''''''''''''''''''''''''''''''''''"""



# PRED_MOVE_EMPTY_INFL_CLAMP_WEIGHT
pred_move_infls *= infls_opp_angle_growth_weight_adjs
pred_move_infls = tf.clip_by_value(
    pred_move_infls, -PRED_MOVE_EMPTY_INFL_CLAMP_WEIGHT, PRED_MOVE_EMPTY_INFL_CLAMP_WEIGHT
)



"""''''''''''''''''''''''''''''''''''''''''''''''''''''''''
'''   REDUCE MOVE INFLUENCES TO GET PREDICTION OUTPUT   '''
''''''''''''''''''''''''''''''''''''''''''''''''''''''''"""



""" prediction """
"""  """
prediction = tf.reduce_sum(tf.reduce_sum(pred_move_infls, axis=2), axis=1)
prediction = tf.SparseTensor(tf.cast(empty_coords, dtype='int64'), prediction, BOARD_SHAPE)
prediction = tf.sparse.to_dense(prediction)
prediction = applyScale(prediction, [tf.reduce_min(prediction), tf.reduce_max(prediction)], [0, 1])
prediction = tf.where(BOARD == 0, prediction, 0)
# print(prediction, "<- prediction")



####################################################################################################



if TESTING_PRINT == 'pred_move_infls':  print(pred_move_infls[PRED_MOVE_I])
elif TESTING_PRINT == 'prediction':  print(prediction)
