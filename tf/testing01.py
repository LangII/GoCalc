


import os, sys
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
# from tensorflow.keras.callbacks import TensorBoard

import math

from functions import (
    applyScale, sort2dByCol, getIndexOfRowIn2d, printNotFloatPt, roundFloat, getCoordiByCoordyx
)
from layers import (
    GetCoords2dByStone, GetStoneDistAngle3d, GetInfluences3d, ApplyLtLinWeight1d,
    GetInflPredictions3d
)

np.set_printoptions(linewidth=300)

BOARD = tf.constant([
    [ 0,  0, +1,  0],
    [ 0, +1, +1,  0],
    [+1,  0,  0, +1],
    [ 0, +1, +1,  0],
])
# print(""), print(BOARD)

""" GET COORDS """

empty_coords = tf.cast(tf.where(tf.equal(BOARD, 0)), dtype='int32')
# print(""), print(empty_coords)

black_coords = tf.cast(tf.where(tf.equal(BOARD, +1)), dtype='int32')
# print(""), print(black_coords)

# white_coords = tf.cast(tf.where(tf.equal(BOARD, -1)), dtype='int32')
# print(white_coords)

""" GET DISTS """

dist_black_size = black_coords.shape[0]
dist_empty_coords = tf.tile(empty_coords, tf.constant([1, dist_black_size], dtype='int32'))
dist_empty_coords = tf.reshape(dist_empty_coords, [-1, dist_black_size, 2])
dist_empty_coords = tf.cast(dist_empty_coords, dtype='float32')
# print(""), print(dist_empty_coords)

dist_empty_size = empty_coords.shape[0]
dist_black_coords = tf.tile(black_coords, tf.constant([dist_empty_size, 1], dtype='int32'))
dist_black_coords = tf.reshape(dist_black_coords, [dist_empty_size, -1, 2])
dist_black_coords = tf.cast(dist_black_coords, dtype='float32')
# print(""), print(dist_black_coords)

norm_coord = dist_empty_coords - dist_black_coords
flat_norm_coord = tf.reshape(norm_coord, [-1, 2])
black_dist = tf.norm(flat_norm_coord, ord='euclidean', axis=1)
black_dist = tf.reshape(black_dist, norm_coord.shape[:-1])
# print(""), print(black_dist)

""" GET ANGLES """

import math
print(tf.atan2(
    tf.constant([1, 2], dtype='float32'),
    tf.constant([1, 1], dtype='float32')
) * (180 / math.pi))
