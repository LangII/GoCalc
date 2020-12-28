
import os, sys
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras

import math

from functions import (
    applyScale, sort2dByCol, getIndexOfRowIn2d, printNotFloatPt, roundFloat, getCoordiByCoordyx
)
from layers import (
    GetCoords2dByStone, GetStoneDistAngle3d, GetInfluences3d, ApplyLtLinWeight1d,
    GetInflPredictions3d
)

np.set_printoptions(linewidth=300)

NO_STONE_VALUE = 0
BLACK_STONE_VALUE = +1
WHITE_STONE_VALUE = -1

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
#     [ 0,  0, +1,  0,  0,  0, +1,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0, -1,  0,  0, -1, +1,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0]
# ], dtype='int32')
# print("\nBOARD =", BOARD)

# BOARD = tf.constant([
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0, +1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, +1,  0,  0,  0],
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
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, +1,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, +1,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0]
# ], dtype='int32')
# print("\nBOARD =", BOARD)

####################################################################################################$





""" TESTING """
# test_coords = [[0, 1], [1, 3], [2, 2]]
# # test_values = [1] * len(test_coords)
# test_values = [1, 2, 3]
# test_sparse = tf.sparse.to_dense(tf.SparseTensor(test_coords, test_values, [5, 5]))
# print(test_sparse)
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
pred_empty_coords = tf.reshape(pred_empty_coords, pred_empty_coords_shape)

pred_black_size = pred_black_coords.shape[1]
pred_empty_tiled_b = tf.tile(pred_empty_coords, tf.constant([1, 1, pred_black_size, 1]))
# print("\npred_empty_tiled_b =", pred_empty_tiled_b)

pred_white_size = pred_white_coords.shape[1]
pred_empty_tiled_w = tf.tile(pred_empty_coords, tf.constant([1, 1, pred_white_size, 1]))
# print("\npred_empty_tiled_w =", pred_empty_tiled_w)




PRED_EMPTY_SIZE = pred_empty_coords.shape[1]

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





pred_move = 0
print("\npred_moves =", pred_moves[pred_move])
print("\npred_black_dists =", pred_black_dists[pred_move])
print("\npred_black_angles =", pred_black_angles[pred_move])
print("\npred_white_dists =", pred_white_dists[pred_move])
print("\npred_white_angles =", pred_white_angles[pred_move])
