
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
# from layers import (
#     GetCoords2dByStone, GetStoneDistAngle3d, GetInfluences3d, ApplyLtLinWeight1d,
#     GetInflPredictions3d
# )

np.set_printoptions(
    linewidth=300,
    threshold=sys.maxsize,
    # threshold=300,
    edgeitems=10,
)

####################################################################################################

# BOARD = tf.constant([
#     [ 0,  0,  0,  0],
#     [-1,  0, +1,  0],
#     [ 0, -1,  0,  0],
#     [ 0,  0, +1,  0],
# ], dtype='int32')
# print("\nBOARD =", BOARD)

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

BOARD = tf.constant([
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0, +1,  0,  0,  0,  0,  0,  0,  0,  0,  0, +1,  0,  0,  0],
    [ 0,  0,  0, -1,  0, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, +1,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, +1,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0]
], dtype='int32')
print("\nBOARD =", BOARD)

####################################################################################################

EMPTY_VALUE = 0
BLACK_VALUE = +1
WHITE_VALUE = -1

PRED_VALUE = BLACK_VALUE
# BOT_VALUE = WHITE_VALUE

BOARD_SHAPE = BOARD.shape.as_list()
EMPTY_COUNT = getCount(BOARD, EMPTY_VALUE)
BLACK_COUNT = getCount(BOARD, BLACK_VALUE)
WHITE_COUNT = getCount(BOARD, WHITE_VALUE)
EMPTY_COUNT_PER_PRED = EMPTY_COUNT - 1
BLACK_COUNT_PER_PRED = BLACK_COUNT if PRED_VALUE == WHITE_VALUE else BLACK_COUNT + 1
WHITE_COUNT_PER_PRED = WHITE_COUNT if PRED_VALUE == BLACK_VALUE else WHITE_COUNT + 1
MAX_DIST = math.hypot(*BOARD_SHAPE)

print("")
print(f"EMPTY_COUNT = {EMPTY_COUNT}, BLACK_COUNT = {BLACK_COUNT}, WHITE_COUNT = {WHITE_COUNT}")
print(f"BLACK_COUNT_PER_PRED = {BLACK_COUNT_PER_PRED}, WHITE_COUNT_PER_PRED = {WHITE_COUNT_PER_PRED}")
print(f"MAX_DIST = {MAX_DIST}")
print("")

####################################################################################################

""" WEIGHTS """
DIST_DECAY_GREATERTHAN_WEIGHT = 4
DIST_DECAY_LINEAR_WEIGHT = 0.5
DIST_ZERO_GREATERTHAN_WEIGHT = 10
ANGLES_LESSTHAN_WEIGHT = 45
ANGLES_LINEAR_WEIGHT = 0.2

####################################################################################################



""" empty_stone_coords """
""" A list of all coords with no stone. """
empty_stone_coords = tf.cast(tf.where(tf.equal(BOARD, 0)), dtype='int32')
# print(empty_stone_coords)



""" pred_moves """
""" A list of all possible next moves that will have influence predicted. """
def getPredMoves(coord):
    return tf.sparse.to_dense(tf.SparseTensor([coord], [PRED_VALUE], BOARD_SHAPE))
pred_moves = tf.vectorized_map(fn=lambda coord: getPredMoves(coord), elems=empty_stone_coords)
tiled_board = tf.tile(tf.reshape(BOARD, [1, *BOARD_SHAPE]), [EMPTY_COUNT, 1, 1])
pred_moves = pred_moves + tiled_board
# print("\npred_moves =", pred_moves)



""" pred_empty_coords """
""" pred_black_coords """
""" pred_white_coords """
""" Tensor similar to empty_stone_coords.  Except what empty_stone_coords does for the current board
position, each tensor does for every possible board position in pred_moves for each value. """
def getPredValueCoords(pred_moves, value):
    pred_color_coords = tf.cast(tf.where(tf.equal(pred_moves, value)), dtype='int32')
    return tf.reshape(pred_color_coords[:, 1:], [EMPTY_COUNT, -1, 2])
pred_empty_coords = getPredValueCoords(pred_moves, EMPTY_VALUE)
pred_black_coords = getPredValueCoords(pred_moves, BLACK_VALUE)
pred_white_coords = getPredValueCoords(pred_moves, WHITE_VALUE)
# print("\npred_empty_coords =", pred_empty_coords)
# print("\npred_black_coords =", pred_black_coords)
# print("\npred_white_coords =", pred_white_coords)



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
# print("\npred_black_normals =", pred_black_normals)
# print("\npred_white_normals =", pred_white_normals)



""" pred_black_dists """
""" pred_white_dists """
""" Tensors representing the distance between each empty coord and each value coord for each
predicted next move. """
def getPredValueDists(pred_value_normals):
    flat_pred_value_normals = tf.reshape(tf.cast(pred_value_normals, dtype='float32'), [-1, 2])
    pred_value_dists = tf.norm(flat_pred_value_normals, ord='euclidean', axis=1)
    return tf.reshape(pred_value_dists, pred_value_normals.shape[:-1])
pred_black_dists = getPredValueDists(pred_black_normals)
pred_white_dists = getPredValueDists(pred_white_normals)
# print("\npred_black_dists =", pred_black_dists)
# print("\npred_white_dists =", pred_white_dists)



""" pred_black_angles """
""" pred_white_angles """
""" Tensors representing the angle of each value coord from each empty coord for each predicted
next move. """
def getPredValueAngles(pred_value_normals):
    y_normals = tf.cast(pred_value_normals[:, :, :, 0] * -1, dtype='float32')
    x_normals = tf.cast(pred_value_normals[:, :, :, 1], dtype='float32')
    pred_value_angles = tf.atan2(y_normals, x_normals) * (180 / math.pi)
    return tf.where(pred_value_angles > 0, pred_value_angles, pred_value_angles + 360)
pred_black_angles = getPredValueAngles(pred_black_normals)
pred_white_angles = getPredValueAngles(pred_white_normals)
# print("\npred_black_angles =", pred_black_angles)
# print("\npred_white_angles =", pred_white_angles)



""" pred_stone_dists_angles """
""" Tensor representing each stone's data (value, dist, angle) in relation to each empty coord, for
each pred move board (each empty coord's sub dim is sorted by stone's dist). """
def getPredValueStoneDistsAngles(pred_value_dists, pred_value_angles, stone_value):
    pred_value_dists_resh = reshapeAddDim(pred_value_dists)
    pred_value_angles_resh = reshapeAddDim(pred_value_angles)
    stone_value = tf.constant(stone_value, dtype='float32')
    pred_value_stones = tf.fill(pred_value_dists_resh.shape, stone_value)
    return tf.concat([pred_value_stones, pred_value_dists_resh, pred_value_angles_resh], axis=3)
pred_black_stone_dists_angles = getPredValueStoneDistsAngles(
    pred_black_dists, pred_black_angles, BLACK_VALUE
)
pred_white_stone_dists_angles = getPredValueStoneDistsAngles(
    pred_white_dists, pred_white_angles, WHITE_VALUE
)
pred_stone_dists_angles = tf.concat(
    [pred_black_stone_dists_angles, pred_white_stone_dists_angles], axis=2
)
pred_stone_dists_angles = reshapeMergeDims(pred_stone_dists_angles, [0, 1])
pred_stone_dists_angles = tf.vectorized_map(
    fn=lambda pred_empty: sort2dByCol(pred_empty, 1),
    elems=pred_stone_dists_angles
)
# print("\npred_stone_dists_angles =", pred_stone_dists_angles)



""" pred_raw_infls """
"""  """
pred_raw_infls = (MAX_DIST - pred_stone_dists_angles[:, :, 1]) * pred_stone_dists_angles[:, :, 0]
pred_raw_infls = applyScale(pred_raw_infls, [0, MAX_DIST], [0, 1])
# print("\npred_raw_infls =", pred_raw_infls)



""" pred_dist_decay_weight_adjs """
pred_dist_decay_weight_adjs = tf.cast(tf.where(
    pred_stone_dists_angles[:, :, 1] > DIST_DECAY_GREATERTHAN_WEIGHT,
    DIST_DECAY_LINEAR_WEIGHT, 1
), dtype='float32')
# print("\npred_dist_decay_weight_adjs =", pred_dist_decay_weight_adjs)



""" pred_dist_zero_weight_adjs """
pred_dist_zero_weight_adjs = tf.cast(tf.where(
    pred_stone_dists_angles[:, :, 1] > DIST_ZERO_GREATERTHAN_WEIGHT,
    0, 1
), dtype='float32')
# print("\pred_dist_zero_weight_adjs =", pred_dist_zero_weight_adjs)

print(pred_dist_decay_weight_adjs * pred_dist_zero_weight_adjs)
