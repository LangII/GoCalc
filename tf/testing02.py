
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
    [ 0, -1, +1,  0],
    [-1,  0,  0, -1],
    [ 0, +1, +1,  0],
], dtype='int32')
print(""), print(BOARD)

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
# print(""), print(BOARD)

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
# print(""), print(BOARD)

####################################################################################################$



""" In case I need an empty board at a later point. """
# empty_board = tf.zeros(BOARD.shape, dtype='int32')
# print(""), print(empty_board)



""" empty_coords is a list of all empty coords.  It is needed as a reference regularly through out
the model. (as well as empty_coords_count) """

empty_coords = tf.cast(tf.where(tf.equal(BOARD, 0)), dtype='int32')
empty_coords_count = empty_coords.shape[0]
# print(""), print(empty_coords)



""" next_moves is a list of all possible next moves.  Where each "next move" is represented by a
full board position. """

def getNextMoves(coord):
    next_move = tf.SparseTensor([coord], [BLACK_STONE_VALUE], BOARD.shape)
    return tf.sparse.to_dense(next_move)
next_moves = tf.vectorized_map(fn=lambda coord: getNextMoves(coord), elems=empty_coords)
tiled_board = tf.tile(tf.reshape(BOARD, [1, *BOARD.shape]), [empty_coords_count, 1, 1])
next_moves = tiled_board + next_moves
# print(""), print(next_moves)



""" next_empty_coords is a tensor very similar to empty_coords.  Except what empty_coords does for
the current board position, next_empty_coords does for every possible board position in
next_moves. """

next_empty_coords = tf.cast(tf.where(tf.equal(next_moves, NO_STONE_VALUE)), dtype='int32')
next_empty_coords = tf.reshape(next_empty_coords[:, 1:], [empty_coords_count, -1, 2])
# print(""), print(next_empty_coords)



""" next_black_coords is very similar to next_empty_coords except what next_empty_coords does for
positions on board with value of 0, next_black_coords does for positions on board with value of 1. """

next_black_coords = tf.cast(tf.where(tf.equal(next_moves, BLACK_STONE_VALUE)), dtype='int32')
next_black_coords = tf.reshape(next_black_coords[:, 1:], [empty_coords_count, -1, 2])
# print(""), print(next_black_coords)



""" next_empty_tiled takes the values from next_empty_coords and tiles them for calculating
next_black_dist and next_white_dist. """

next_black_size = next_black_coords.shape[1]
next_empty_coords_shape = next_empty_coords.get_shape().as_list()
next_empty_coords_shape.insert(2, 1)
next_empty_coords = tf.reshape(next_empty_coords, next_empty_coords_shape)
next_empty_tiled = tf.tile(next_empty_coords, tf.constant([1, 1, next_black_size, 1]))
# print(""), print(next_empty_tiled)



""" next_black_tiled takes the values from next_black_coords and tiles them for calculating
next_black_dist. """

next_empty_size = next_empty_coords.shape[1]
next_black_coords_shape = next_black_coords.get_shape().as_list()
next_black_coords_shape.insert(1, 1)
next_black_coords = tf.reshape(next_black_coords, next_black_coords_shape)
next_black_tiled = tf.tile(next_black_coords, tf.constant([1, next_empty_size, 1, 1]))
# print(""), print(next_black_tiled)



""" next_black_dist is a complex tensor.  The outer most dimension (D1) represents board positions
for every possible move that could come next.  The next inner dimension (D2) represents every
empty position on the board (for each board of (D1)).  The next inner dimension (D3) represents
every black stone on the board.  The lowest dimension (D4) contains the calculated values of the
distance between every empty position on the board (D2) and every position on the board with a black
stone (D3) (for every possible next move (D1)).  """
next_norms = next_empty_tiled - next_black_tiled
flat_next_norms = tf.reshape(tf.cast(next_norms, dtype='float32'), [-1, 2])
next_black_dist = tf.norm(flat_next_norms, ord='euclidean', axis=1)
next_black_dist = tf.reshape(next_black_dist, next_norms.shape[:-1])
print(""), print(next_black_dist)
