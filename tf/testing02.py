
import os, sys
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras

import math

from functions import (
    applyScale, sort2dByCol, getIndexOfRowIn2d, printNotFloatPt, roundFloat, getCoordiByCoordyx,
    applyLtLinWeights
)
from layers import (
    GetCoords2dByStone, GetStoneDistAngle3d, GetInfluences3d, ApplyLtLinWeight1d,
    GetInflPredictions3d
)

np.set_printoptions(
    linewidth=300,
    # threshold=sys.maxsize,
    threshold=300,
    edgeitems=10,
)

NO_STONE_VALUE = 0
BLACK_STONE_VALUE = +1
WHITE_STONE_VALUE = -1

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

####################################################################################################$





# """ TESTING """
# a = [1, 2, 3, 4]
# a[2:3] = [5]
# print(a)
# exit()





""" In case I need an empty board at a later point. """
# empty_board = tf.zeros(BOARD.shape, dtype='int32')
# print("\nempty_board =", empty_board)





""" empty_coords is a list of all empty coords.  It is needed as a reference regularly through out
the model. (as well as empty_coords_count) """

empty_coords = tf.cast(tf.where(tf.equal(BOARD, 0)), dtype='int32')
empty_coords_count = empty_coords.shape[0]
# print("\nempty_coords =", empty_coords)





""" pred_moves is a list of all possible next moves.  Where each "next move" is represented by a
full board position. """

def getNextMoves(coord):
    pred_move = tf.SparseTensor([coord], [BLACK_STONE_VALUE], BOARD.shape)
    return tf.sparse.to_dense(pred_move)
pred_moves = tf.vectorized_map(fn=lambda coord: getNextMoves(coord), elems=empty_coords)
tiled_board = tf.tile(tf.reshape(BOARD, [1, *BOARD.shape]), [empty_coords_count, 1, 1])
pred_moves = tiled_board + pred_moves
# print("\npred_moves =", pred_moves)





""" pred_empty_coords is a tensor very similar to empty_coords.  Except what empty_coords does for
the current board position, pred_empty_coords does for every possible board position in
pred_moves. """

pred_empty_coords = tf.cast(tf.where(tf.equal(pred_moves, NO_STONE_VALUE)), dtype='int32')
pred_empty_coords = tf.reshape(pred_empty_coords[:, 1:], [empty_coords_count, -1, 2])
# print("\npred_empty_coords =", pred_empty_coords)





""" pred_black_coords and pred_white_coords are very similar to pred_empty_coords except what
pred_empty_coords does for positions on board with value of 0, pred_black_coords and
pred_white_coords do for positions on board with value of 1. """

pred_black_coords = tf.cast(tf.where(tf.equal(pred_moves, BLACK_STONE_VALUE)), dtype='int32')
pred_black_coords = tf.reshape(pred_black_coords[:, 1:], [empty_coords_count, -1, 2])
# print("\npred_black_coords =", pred_black_coords)

pred_white_coords = tf.cast(tf.where(tf.equal(pred_moves, WHITE_STONE_VALUE)), dtype='int32')
pred_white_coords = tf.reshape(pred_white_coords[:, 1:], [empty_coords_count, -1, 2])
# print("\npred_white_coords =", pred_white_coords)





""" pred_empty_tiled_b and pred_empty_tiled_w takes the values from pred_empty_coords and tiles them
for calculating pred_black_dist and pred_white_dist. """

pred_empty_coords_shape = pred_empty_coords.get_shape().as_list()
pred_empty_coords_shape.insert(2, 1)
pred_empty_coords_resh = tf.reshape(pred_empty_coords, pred_empty_coords_shape)

pred_black_size = pred_black_coords.shape[1]
pred_empty_tiled_b = tf.tile(pred_empty_coords_resh, tf.constant([1, 1, pred_black_size, 1]))
# print("\npred_empty_tiled_b =", pred_empty_tiled_b)

pred_white_size = pred_white_coords.shape[1]
pred_empty_tiled_w = tf.tile(pred_empty_coords_resh, tf.constant([1, 1, pred_white_size, 1]))
# print("\npred_empty_tiled_w =", pred_empty_tiled_w)




PRED_EMPTY_SIZE = pred_empty_coords_resh.shape[1]

""" pred_black_tiled and pred_white_tiled takes the values from pred_black_coords and
pred_white_coords and tiles them for calculating pred_black_dists, pred_white_dists,
pred_black_angles, and pred_white_angles. """

pred_black_coords_shape = pred_black_coords.get_shape().as_list()
pred_black_coords_shape.insert(1, 1)
pred_black_coords_reshaped = tf.reshape(pred_black_coords, pred_black_coords_shape)
pred_black_tiled = tf.tile(pred_black_coords_reshaped, tf.constant([1, PRED_EMPTY_SIZE, 1, 1]))
# print("\npred_black_tiled =", pred_black_tiled)

pred_white_coords_shape = pred_white_coords.get_shape().as_list()
pred_white_coords_shape.insert(1, 1)
pred_white_coords_reshaped = tf.reshape(pred_white_coords, pred_white_coords_shape)
pred_white_tiled = tf.tile(pred_white_coords_reshaped, tf.constant([1, PRED_EMPTY_SIZE, 1, 1]))
# print("\npred_white_tiled =", pred_white_tiled)





PRED_BLACK_NORMALS = pred_black_tiled - pred_empty_tiled_b
PRED_WHITE_NORMALS = pred_white_tiled - pred_empty_tiled_w

# print(PRED_BLACK_NORMALS)

""" pred_black_dists and pred_white_dists are complex tensors.  The outer most dimension (D1)
represents board positions for every possible move that could come next.  The next inner dimension
(D2) represents every empty position on the board (for each board of (D1)).  The next inner
dimension (D3) represents every black (or white) stone on the board.  The lowest dimension (D4)
contains the calculated values of the distance between every empty position on the board (D2) and
every position on the board with a black stone (or white stone) (D3) (for every possible next move
(D1)). """

flat_pred_black_normals = tf.reshape(tf.cast(PRED_BLACK_NORMALS, dtype='float32'), [-1, 2])
pred_black_dists = tf.norm(flat_pred_black_normals, ord='euclidean', axis=1)
pred_black_dists = tf.reshape(pred_black_dists, PRED_BLACK_NORMALS.shape[:-1])
# print("\npred_black_dists =", pred_black_dists)

flat_pred_white_normals = tf.reshape(tf.cast(PRED_WHITE_NORMALS, dtype='float32'), [-1, 2])
pred_white_dists = tf.norm(flat_pred_white_normals, ord='euclidean', axis=1)
pred_white_dists = tf.reshape(pred_white_dists, PRED_WHITE_NORMALS.shape[:-1])
# print("\npred_white_dists =", pred_white_dists)





""" pred_black_angles and pred_white_angles is a complex tensor (very similar to pred_black_dist).
All dimensions are representative to the same values as the dimensions of pred_black_dist.  Except
the lowest dimension (D4).  The values in D4 represent the angle from an empty position (origin) on
the board to a position with a black (or white) stone (coordinate). """

pred_black_normals_y = tf.cast(PRED_BLACK_NORMALS[:, :, :, 0] * -1, dtype='float32')
pred_black_normals_x = tf.cast(PRED_BLACK_NORMALS[:, :, :, 1], dtype='float32')
pred_black_angles = tf.atan2(pred_black_normals_y, pred_black_normals_x) * (180 / math.pi)
pred_black_angles = tf.where(pred_black_angles > 0, pred_black_angles, pred_black_angles + 360)
# print("\pred_black_angles =", pred_black_angles)

pred_white_normals_y = tf.cast(PRED_WHITE_NORMALS[:, :, :, 0] * -1, dtype='float32')
pred_white_normals_x = tf.cast(PRED_WHITE_NORMALS[:, :, :, 1], dtype='float32')
pred_white_angles = tf.atan2(pred_white_normals_y, pred_white_normals_x) * (180 / math.pi)
pred_white_angles = tf.where(pred_white_angles > 0, pred_white_angles, pred_white_angles + 360)
# print("\pred_white_angles =", pred_white_angles)





""" pred_dists_angles is a concatenated and sorted version of pred_black_dists, pred_black_angles,
pred_white_dists, and pred_white_angles.  It's values are the base for which all infl_model
calculations are calculated from. """

pred_black_dists_resh = tf.reshape(pred_black_dists, pred_black_dists.shape.as_list() + [1])
pred_black_angles_resh = tf.reshape(pred_black_angles, pred_black_angles.shape.as_list() + [1])
black_stone_values = tf.constant(BLACK_STONE_VALUE, dtype='float32')
black_stone_values = tf.fill(pred_black_dists_resh.shape, black_stone_values)
pred_black_dists_angles = tf.concat(
    [black_stone_values, pred_black_dists_resh, pred_black_angles_resh], axis=3
)

pred_white_dists_resh = tf.reshape(pred_white_dists, pred_white_dists.shape.as_list() + [1])
pred_white_angles_resh = tf.reshape(pred_white_angles, pred_white_angles.shape.as_list() + [1])
white_stone_values = tf.constant(WHITE_STONE_VALUE, dtype='float32')
white_stone_values = tf.fill(pred_white_dists_resh.shape, white_stone_values)
pred_white_dists_angles = tf.concat(
    [white_stone_values, pred_white_dists_resh, pred_white_angles_resh], axis=3
)

pred_dists_angles = tf.concat([pred_black_dists_angles, pred_white_dists_angles], axis=2)

pred_dists_angles_resh = tf.reshape(pred_dists_angles, [-1] + pred_dists_angles.shape.as_list()[-2:])
pred_dists_angles_resh = tf.vectorized_map(
    fn=lambda stone_set: sort2dByCol(stone_set, 1),
    elems=pred_dists_angles_resh
)

pred_dists_angles = tf.reshape(pred_dists_angles_resh, pred_dists_angles.shape)
# print("\npred_dists_angles =", pred_dists_angles)





DIST_LT_W = 4
DIST_LIN_W = 0.2
ANGLES_LT_W = 45
ANGLES_LIN_W = 0.2

""" pred_infls """
pred_dists_angles_resh = tf.reshape(pred_dists_angles, [-1] + pred_dists_angles.shape.as_list()[-2:])
# print(pred_dists_angles_resh)

max_dist = tf.norm(tf.constant(BOARD.shape, dtype='float32'), ord='euclidean')
stone_values = pred_dists_angles_resh[:, :, 0]
pred_raw_infls = (max_dist - pred_dists_angles_resh[:, :, 1]) * stone_values

pred_raw_infls = applyScale(pred_raw_infls, [0, max_dist], [0, 1])

# print(pred_raw_infls)

pred_infls_w_dist_w = tf.where(pred_raw_infls < DIST_LT_W, pred_raw_infls * DIST_LIN_W, pred_raw_infls)
# print(pred_infls_w_dist_w)





angles_per_empty = pred_dists_angles_resh.shape[1]
# print(angles_per_empty)
pred_angles_infls = pred_dists_angles_resh[:, :, 2]

pred_angles_infls_resh_x = tf.reshape(pred_angles_infls, pred_angles_infls.shape + [1])
pred_angles_infls_tiled_x = tf.tile(pred_angles_infls_resh_x, [1, 1, angles_per_empty])
# print(pred_angles_infls_tiled_x)

pred_angles_infls_shape = pred_angles_infls.shape.as_list()
pred_angles_infls_shape.insert(1, 1)
pred_angles_infls_resh_y = tf.reshape(pred_angles_infls, pred_angles_infls_shape)
pred_angles_infls_tiled_y = tf.tile(pred_angles_infls_resh_y, [1, angles_per_empty, 1])
# print(pred_angles_infls_tiled_y)

pred_angles_dif = tf.abs(pred_angles_infls_tiled_x - pred_angles_infls_tiled_y)
pred_angles_dif = tf.where(pred_angles_dif > 180, 360 - pred_angles_dif, pred_angles_dif)
# print(pred_angles_dif)

pred_angles_infls = tf.where(pred_angles_dif <= ANGLES_LT_W, ANGLES_LIN_W, 0)
# print(pred_angles_infls

stone_cancel_x = tf.reshape(pred_dists_angles_resh[:, :, 0], [-1, pred_dists_angles_resh.shape[1], 1])
stone_cancel_x = tf.tile(stone_cancel_x, [1, 1, angles_per_empty])
# print(stone_cancel_x)

stone_cancel_y = tf.reshape(pred_dists_angles_resh[:, :, 0], [-1, 1, pred_dists_angles_resh.shape[1]])
stone_cancel_y = tf.tile(stone_cancel_y, [1, angles_per_empty, 1])
# print(stone_cancel_y)

stone_cancel = stone_cancel_x * stone_cancel_y * -1
stone_cancel = tf.where(stone_cancel == -1, 0, stone_cancel)
print(stone_cancel)

pred_angles_infls = pred_angles_infls * stone_cancel
pred_angles_infls = tf.where(pred_angles_infls == 0, 1, pred_angles_infls)
# print(pred_angles_infls)

mirror_coords = tf.cast(tf.where(tf.equal(tf.zeros(pred_angles_infls.shape[1:]), 0)), dtype='int32')
mirror_y = -tf.cast(mirror_coords[:, 0], dtype='float32')
mirror_x = tf.cast(mirror_coords[:, 1], dtype='float32')
mirror_angles = tf.atan2(mirror_y, mirror_x) * (180 / math.pi)
mirror_angles = tf.where(mirror_angles > 0, mirror_angles, mirror_angles + 360)
mirror_mask = tf.where(mirror_angles < 315, True, False)
mirror_mask = tf.reshape(mirror_mask, [1] + pred_angles_infls.shape[1:])
mirror_mask = tf.tile(mirror_mask, [pred_angles_infls.shape[0], 1, 1])
# print(mirror_mask)

pred_angles_infls = tf.where(mirror_mask, pred_angles_infls, tf.constant(1, dtype='float32'))
pred_angles_infls = tf.reduce_prod(pred_angles_infls, axis=2)
# print(pred_angles_infls)




# slicer = tf.range(2, angles_per_empty + 2, dtype='float32')
# slicer = tf.reshape(tf.tile(slicer, [pred_angles_infls.shape[0]]), [-1, 1])
# filler = tf.fill(slicer.shape, tf.constant(1, dtype='float32'))
# pred_angles_infls_resh = tf.reshape(pred_angles_infls, [-1, pred_angles_infls.shape[-1]])
# print(slicer)
# print(pred_angles_infls_resh)
# multiplier_map = tf.concat([slicer, filler, pred_angles_infls_resh], axis=1)
# print(multiplier_map)

# """ TURNOVER NOTES:  Wow...  I am very much in the weeds on this.  So, trying to calculate angle
# influences using only tensor play.  I currently have a pretty strong set of tensors to get the final
# output (like stone_cancel (mask) and pred_angles_dif), now I need to figure out how to ignore the
# un-needed values in pred_angles_infls.  The plan is to use the multiplier_map where the first value
# of each row is the amount to slice the row by.  I think this should work, but I still need to play
# around with the slicer.  Then after all that this section needs a serious clean up. """

# exit()

# """ This mapping is slowing it down!!! """

# angle_infls = tf.reshape(tf.map_fn(
#     fn=lambda row: tf.reduce_prod(row[1:tf.cast(row[0], dtype='int32')]),
#     elems=multiplier_map,
#     # fallback_to_while_loop=False
# ), [-1, angles_per_empty])
# # print(angle_infls)

# pred_angles_infls = tf.reduce_prod(pred_angles_infls, axis=1)
# print(pred_angles_infls)





# print(pred_infls_w_dist_w)

pred_infls = pred_infls_w_dist_w * pred_angles_infls
#
pred_infls = tf.reduce_sum(pred_infls, axis=1)
pred_infls = tf.reshape(pred_infls, pred_dists_angles.shape.as_list()[:2])
pred_infls = tf.reduce_sum(pred_infls, axis=1)

# print("\npred_black_angles =", pred_black_angles[pred_move])
# print("\npred_white_dists =", pred_white_dists[pred_move])
# print("\npred_white_angles =", pred_white_angles[pred_move])
# print("\npred_dists_angles =", pred_dists_angles[pred_move])
