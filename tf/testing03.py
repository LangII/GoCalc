
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
    applyLtLinWeights, getCount
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

BOT_STONE_VALUE = BLACK_STONE_VALUE
# BOT_STONE_VALUE = WHITE_STONE_VALUE

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
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, +1,  0,  0,  0],
    [ 0,  0,  0, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
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

BOARD_SHAPE = BOARD.shape.as_list()
NO_STONE_COUNT = getCount(BOARD, NO_STONE_VALUE)
BLACK_STONE_COUNT = getCount(BOARD, BLACK_STONE_VALUE)
WHITE_STONE_COUNT = getCount(BOARD, WHITE_STONE_VALUE)

####################################################################################################



""" no_stone_coords """
""" A list of all coords with no stone. """
no_stone_coords = tf.cast(tf.where(tf.equal(BOARD, 0)), dtype='int32')
# print(no_stone_coords)



""" pred_moves """
""" A list of all possible next moves that will have influence predicted. """
def getPredMoves(coord):
    return tf.sparse.to_dense(tf.SparseTensor([coord], [BOT_STONE_VALUE], BOARD_SHAPE))
pred_moves = tf.vectorized_map(fn=lambda coord: getPredMoves(coord), elems=no_stone_coords)
tiled_board = tf.tile(tf.reshape(BOARD, [1, *BOARD_SHAPE]), [NO_STONE_COUNT, 1, 1])
pred_moves = pred_moves + tiled_board
# print("\npred_moves =", pred_moves)



""" pred_no_stone_coords """
""" pred_black_coords """
""" pred_white_coords """
""" Each is a tensor similar to no_stone_coords.  Except what no_stone_coords does for the current
board position, each tensor does for every possible board position in pred_moves for each value. """
def getPredValueCoords(pred_moves, value):
    pred_color_coords = tf.cast(tf.where(tf.equal(pred_moves, value)), dtype='int32')
    return tf.reshape(pred_color_coords[:, 1:], [NO_STONE_COUNT, -1, 2])
pred_no_stone_coords = getPredValueCoords(pred_moves, NO_STONE_VALUE)
pred_black_coords = getPredValueCoords(pred_moves, BLACK_STONE_VALUE)
pred_white_coords = getPredValueCoords(pred_moves, WHITE_STONE_VALUE)
# print("\npred_no_stone_coords =", pred_no_stone_coords)
# print("\npred_black_coords =", pred_black_coords)
# print("\npred_white_coords =", pred_white_coords)
