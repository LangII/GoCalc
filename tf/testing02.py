
import os, sys
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

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
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, +1,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0]
# ], dtype='int32')
# print(""), print(BOARD)

####################################################################################################$

# empty_board = tf.zeros(BOARD.shape, dtype='int32')
# print(""), print(empty_board)

empty_coords = tf.cast(tf.where(tf.equal(BOARD, 0)), dtype='int32')
print(""), print(empty_coords)

empty_coords_count = empty_coords.shape[0]

""" GET NEXT MOVES """
def getNextMoves(coord):
    next_move = tf.SparseTensor([coord], [BLACK_STONE_VALUE], BOARD.shape)
    next_move = tf.sparse.to_dense(next_move)
    return next_move
next_moves = tf.vectorized_map(fn=lambda coord: getNextMoves(coord), elems=empty_coords)
tiled_board = tf.tile(tf.reshape(BOARD, [1, *BOARD.shape]), [empty_coords_count, 1, 1])
next_moves = tiled_board + next_moves
print(""), print(next_moves)

next_empty_coords = tf.cast(tf.where(tf.equal(next_moves, NO_STONE_VALUE)), dtype='int32')
next_empty_coords = tf.reshape(next_empty_coords[:, 1:], [empty_coords_count, -1, 2])
print(""), print(next_empty_coords)

next_black_coords = tf.cast(tf.where(tf.equal(next_moves, BLACK_STONE_VALUE)), dtype='int32')
next_black_coords = tf.reshape(next_black_coords[:, 1:], [empty_coords_count, -1, 2])
print(""), print(next_black_coords)

""" TURNOVER NOTES:  Have successfully used only tensor play to get series of coords for all empty
coords and all black coords for all next move possibilities.  Next to do is continue to reshape
next_empty_coords and next_black_coords to get next_black_dist. """
