


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
    GetCoords2dByStone, GetStoneDistAngle3d, GetInfluences3d, ApplyLtLinWeight1d
)

np.set_printoptions(linewidth=300)



####################################################################################################



BLACK_STONE_VALUE = +1
WHITE_STONE_VALUE = -1
NO_STONE_VALUE = 0

BOARD_SIZE = [9, 9]

BOARD = tf.constant([
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0, +1,  0, -1,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0, -1,  0],
    [ 0,  0, +1,  0,  0,  0, +1,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0, -1,  0,  0, -1, +1,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0]
], dtype='int8')

# BOARD = tf.constant([
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0, +1,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
#     [ 0,  0,  0,  0,  0,  0,  0,  0,  0]
# ], dtype='int8')

# TESTING = False
TESTING = True



####################################################################################################



def main():

    """

    weights:
        - raw_dist_decay:       How much the infl decays with distance from pos.
        - barrier_decay:        How much more a proceeding opposing stone's infl decays.
        - barrier_angle_cap:    How much of an angle is accepted to designate an proceeding opposing
                                stone after a barrier stone.
        - barrier_angle_decay:  How much more a proceeding opposing stone's infl decays based on
                                angle from barrier stone.

    -   Need to first get the model to accurately produce the dist/angle sub tensors for each coord
        point on the squashed board.

    -   Perform tests on a dist/angle tensor to produce coord point influence.

    """

    # nums1 = tf.constant([1, 2, 3, 4, 5])
    # print(tf.cond(
    #     nums1 < 3, lambda: nums1 * 2, lambda: nums1
    # ))
    # exit()

    """ TESTING """
    # input = keras.Input(shape=BOARD_SIZE, dtype='int8')
    input = BOARD

    get_coords_by_no_stone = GetCoords2dByStone(stone=NO_STONE_VALUE, testing=TESTING)
    no_stone_coords = get_coords_by_no_stone(input)

    get_coords_by_black_stone = GetCoords2dByStone(stone=BLACK_STONE_VALUE, testing=TESTING)
    black_stone_coords = get_coords_by_black_stone(input)

    get_coords_by_white_stone = GetCoords2dByStone(stone=WHITE_STONE_VALUE, testing=TESTING)
    white_stone_coords = get_coords_by_white_stone(input)

    all_coords = tf.concat([no_stone_coords, black_stone_coords, white_stone_coords], axis=0)
    all_coords = sort2dByCol(all_coords, 2)
    all_coords = sort2dByCol(all_coords, 1)

    all_stone_coords = tf.concat([black_stone_coords, white_stone_coords], axis=0)
    all_stone_coords = sort2dByCol(all_stone_coords, 2)
    all_stone_coords = sort2dByCol(all_stone_coords, 1)

    """ Testing influence calc (only using single coord). """
    coord_y, coord_x = 0, 0
    coord_i = (BOARD_SIZE[0] * coord_y) + coord_x
    all_coords = all_coords[coord_i]
    all_coords = tf.reshape(all_coords, [1, -1])
    # print(all_coords) ; exit()

    stone_dist_angle = GetStoneDistAngle3d()(all_coords, all_stone_coords)
    # print(stone_dist_angle) ; exit()

    get_influences = GetInfluences3d(BOARD_SIZE)
    # influences = get_influences(stone_dist_angle)
    # print(influences) ; exit()
    infl_steps = get_influences.getSingleInflSteps(stone_dist_angle[0])
    # infl_steps = roundFloat(infl_steps, 4)
    print("")
    print(all_stone_coords)
    print("")
    print(stone_dist_angle)
    print("")
    print(infl_steps)
    exit()

    # Show final GetInfluences3d results.
    influences = tf.map_fn(fn=lambda x: tf.reduce_sum(x), elems=influences)
    influences = tf.reshape(influences, BOARD_SIZE)
    influences_sum = tf.reduce_sum(influences)
    influences = roundFloat(influences)
    print(influences)
    print(influences_sum)
    exit()



    # get_fuseki_table = GetFusekiTableLayer(stone=BLACK_STONE_VALUE)
    # fuseki_tbl = get_fuseki_table(no_stone_coord, all_stone_coord)

    # fuseki_model = keras.Model(inputs=input, outputs=all_stone_coord)

    # fuseki_model.summary()

    # fuseki_model.compile(
    #     optimizer='adam',
    #     loss='sparse_categorical_crossentropy',
    #     metrics=['accuracy']
    # )
    # fuseki_model.fit(
    #     BOARD,
    #     batch_size=10,
    #     epochs=3,
    #     callbacks=[tensorboard]
    # )



####################################################################################################



if __name__ == '__main__':  main()



####################################################################################################



""" GetInfluences3d """
# """                                                                                             TESTING >>> """
#
# """ TURNOVER NOTES:  Next to do is translate testing functions here into a class in layers.py.
# Then start unit testing influence's barrier bias calculations. """
#
# """ testing on a single stone_dist_angle (coord [0, 0]) """
# stone_dist_angle = stone_dist_angle[0]
# print("\nstone_dist_angle ="), print(stone_dist_angle)
# # exit()
#
# global infls
# max_dist = tf.norm(tf.constant(BOARD.shape, dtype='float32'), ord='euclidean')
# infls = max_dist - stone_dist_angle[:, 1]
# infls = tf.reshape(infls, [-1, 1]) # for printing
# print("\ninfls (original) ="), print(infls)
#
# # Normalize infls.
# infls = applyScale(
#     infls,
#     tf.concat([tf.constant(0, dtype='float32'), max_dist], axis=0),
#     tf.constant([0, 1], dtype='float32')
# )
# print("\ninfls (normalized) ="), print(infls)
#
# # Apply first dist bias to infls.
# dist_bias_lt_point_w = 0.6
# dist_bias_w = 0.2
# infls = ApplyLtLinWeight1d(dist_bias_lt_point_w, dist_bias_w)(infls)
# print("\ninfls (with dist bias) ="), print(infls)
#
# def getBools(t, all_t):
#     return tf.map_fn(
#         fn=lambda t1: tf.cond(
#             tf.reduce_all(tf.equal(t, t1)),
#             true_fn=lambda: tf.constant(True, dtype='bool'),
#             false_fn=lambda: tf.constant(False, dtype='bool')
#         ),
#         elems=all_t,
#         dtype='bool'
#     )
#
# def calcBarrierBias(def_dist, def_angle, agr_dist, agr_angle, infl):
#     """
#     def_power = X # The amount infl is adjusted by.
#     1. The further away DEF_dist gets from ORIGIN, reduce def_power by X.
#     2. The further away AGR_angle is from DEF_angle, reduce def_power by X.
#         - I think +/- 90d should be the max.
#     3. If AGR_angle is < DEF_angle + X or AGR_angle is > DEF_angle - X, apply def_power.
#     """
#
#     """
#     angle1, angle2, dif = 180, 355, 45
#     angle_dif = abs(angle1 - angle2)
#     if angle_dif > 180:  angle_dif = 360 - angle_dif
#     if angle_dif <= dif:  print('within dif')
#     else:  print('not within dif')
#     print("angle1    =", angle1)
#     print("angle2    =", angle2)
#     print("dif       =", dif)
#     print("angle_dif =", angle_dif)
#     """
#
#     # print("")
#     # print("def_dist  =", def_dist)
#     # print("def_angle =", def_angle)
#     # print("agr_dist  =", agr_dist)
#     # print("agr_angle =", agr_angle)
#     # print("infl      =", infl)
#
#     angle_bias_lt_point_w = 45
#     angle_bias_w = 0.2
#
#     # Have to use tf.cond to get angle_dif to handle angle wrap from 360 back to 0.
#     angle_dif = tf.abs(def_angle - agr_angle)
#     angle_dif = tf.cond(angle_dif > 180, true_fn=lambda: 360 - angle_dif, false_fn=lambda: angle_dif)
#
#     # Apply bias to infl.
#     infl = tf.cond(
#         angle_dif < angle_bias_lt_point_w,
#         true_fn=lambda: infl * angle_bias_w,
#         false_fn=lambda: infl
#     )
#
#     # print("")
#     # print(infl)
#     # exit()
#
#     return infl
#
# def applyBarrierBias(def_row, agr_row, infl):
#     def_stone, def_dist, def_angle = def_row[0], def_row[1], def_row[2]
#     agr_stone, agr_dist, agr_angle = agr_row[0], agr_row[1], agr_row[2]
#     return tf.cond(
#         def_stone == agr_stone,
#         true_fn=lambda: infl,
#         false_fn=lambda: calcBarrierBias(def_dist, def_angle, agr_dist, agr_angle, infl)
#     )
#
# """ Perform sub loop through each row of stone_dist_angle. """
# def innerLoop(sub_row, row_i, stone_dist_angle, infls):
#     sub_row_i = tf.reshape(tf.where(getBools(sub_row, stone_dist_angle)), [-1])[0]
#     return tf.cond(
#         sub_row_i <= row_i,
#         true_fn=lambda: infls[sub_row_i],
#         false_fn=lambda: applyBarrierBias(
#             stone_dist_angle[row_i],
#             stone_dist_angle[sub_row_i],
#             infls[sub_row_i]
#         )
#     )
#
# # def outerLoop(row, stone_dist_angle, infls):
# def outerLoop(row, stone_dist_angle):
#     """  """
#     global infls
#     # Get the current row being worked on.
#     row_i = tf.reshape(tf.where(getBools(row, stone_dist_angle)), [-1])[0]
#     infls = tf.map_fn(
#         fn=lambda sub_row: innerLoop(sub_row, row_i, stone_dist_angle, infls),
#         elems=stone_dist_angle,
#     )
#     return infls
#
# """ Loop through each row of stone_dist_angle. """
# # infls = tf.map_fn(
# tf.map_fn(
#     # fn=lambda row: outerLoop(row, stone_dist_angle, infls),
#     fn=lambda row: outerLoop(row, stone_dist_angle),
#     elems=stone_dist_angle
# )
#
# # infls = FloatRoundLayer(7)(infls)
# print("\ninfls (with barrier bias) =")
# np.set_printoptions(precision=8, suppress=True)
# print(infls.numpy())
#
# exit()
#
# """                                                                                             <<< TESTING """

""" print board plot """
# plt.imshow(board, cmap=plt.cm.binary)
# plt.show()

""" loop through board tensor to get stone indices """
# height, width = board.get_shape().as_list()
# black, white = [], []
# for y in range(height):
#     for x in range(width):
#         if   tf.gather_nd(board, [y, x]) == +1:  black += [ [y, x] ]
#         elif tf.gather_nd(board, [y, x]) == -1:  white += [ [y, x] ]
# black = tf.constant(np.array(black))
# white = tf.constant(np.array(white))
# print("\nblack"), print(black)
# print("\nwhite"), print(white)

""" GetCoordsByStoneLayer """
# stone_coord = []
# _, height, width = input.get_shape().as_list()
# for y in range(height):
#     for x in range(width):
#         # value = tf.gather_nd(input, [y, x])
#         value = float(input[:, y, x])
#         print(value)
#         exit()
#         if value == self.stone:  stone_coord += [ [value, y, x] ]
# for coord in stone_coord:  print(coord)
# exit()
# return tf.constant(np.array(stone_coord))

""" model class """
# class FusekiModel (keras.Model):
#     def __init__(self):
#         super(FusekiModel, self).__init__()
#
#     def call(self, input):
#
#         no_stone_coord = GetCoordByStoneLayer(stone=NO_STONE_VALUE)(board=input)
#
#         black_stone_coord = GetCoordByStoneLayer(stone=BLACK_STONE_VALUE)(board=input)
#
#         white_stone_coord = GetCoordByStoneLayer(stone=WHITE_STONE_VALUE)(board=input)
#
#         all_stone_coord = tf.concat([black_stone_coord, white_stone_coord], axis=0)
#
#         fuseki_tbl = GetFusekiTableLayer(stone=BLACK_STONE_VALUE)(
#             no_stone_coord_input=no_stone_coord,
#             all_stone_coord_input=all_stone_coord
#         )
#
#         fuseki_grid = GetFusekiGridLayer()(fuseki_tbl)
#
#         fuseki_grid = NormalizationLayer()(fuseki_grid)
#
#         # Normalization turns no_stone values (0) into negative values.  Relu turns them back to 0.
#         fuseki_grid = tf.nn.relu(fuseki_grid)
#
#         fuseki_grid = FloatRoundLayer(2)(fuseki_grid)
#
#         return fuseki_grid

""" main """
# fuseki_model = FusekiModel()
#
# fuseki_model.compile(
#     optimizer='adam',
#     loss='sparse_categorical_crossentropy',
#     metrics=['accuracy']
# )
#
# fuseki_results = fuseki_model(BOARD)
#
# print("fuseki_results:") ; print(fuseki_results)

""" layers """
# class GetFusekiTableLayer (keras.layers.Layer):
#     def __init__(self, stone):
#         super(GetFusekiTableLayer, self).__init__()
#         self.stone = stone
#         self.max_dist = getDistTwoPoints([0, 0], BOARD.get_shape().as_list())
#         self.infl_skew_value_weight = self.add_weight(
#             shape=[],
#             initializer='zeros',
#             constraint=keras.constraints.MinMaxNorm(
#                 min_value=0.0,
#                 max_value=-0.5,
#                 rate=1.0,
#                 axis=0
#             ),
#             trainable=True
#         )
#
#     def getStoneDists(self, coord, stone_coords):
#         """
#         Using tensors to get distance between no stone point and all stone points.
#         """
#         coord = coord[1:]
#         print(coord)
#         exit()
#
#
#     def call(self, no_stone_coord_input, all_stone_coord_input):
#         """
#         Loop through all coord in no_stone_coord_input.  Each coord will be added to
#         all_stone_coord_input, then influences and fuseki_score will be calculated for each new
#         board layout of stones in all_stone_coord_input.  Returned will be a table consisting of
#         each coord from no_stone_coord_input and it's fuseki_score in descending order.
#         """
#
#         """ tf.map_fn() """
#
#         stone_dists = tf.map_fn(
#             fn=lambda coord: self.getStoneDists(coord, all_stone_coord_input),
#             elems=no_stone_coord_input
#         )
#
#         print(coord_table)
#
#         # print(all_stone_coord_input)
#         exit()

""" layers """
#     def getStoneDataTable(self, y, x, stone_coords):
#         """
#         Build stone_data_tbl for coord y, x with data from new_all_stone_coord_input.
#         """
#         stone_data_tbl = np.array([])
#         for i in range(stone_coords.get_shape().as_list()[0]):
#             stone, stone_y, stone_x = stone_coords[i, :].numpy().T
#             dist = getDistTwoPoints([y, x], [stone_y, stone_x])
#             angle = getAngleTwoPoints([y, x], [stone_y, stone_x])
#             raw_infl = self.max_dist - dist
#             stone_data_tbl = np.append(stone_data_tbl, [
#                 stone, stone_y, stone_x, dist, angle, raw_infl
#             ])
#         stone_data_tbl = np.reshape(stone_data_tbl, [-1, 6])
#         stone_data_tbl = np.array(sorted(stone_data_tbl, key=lambda x: x[3]))
#         return stone_data_tbl
#
#     def calcInfluence(self, stone_data_tbl):
#         """
#         Apply weights to data from stone_data_tbl to calculate influence.
#         """
#         influence = 0.0
#         for stone, stone_y, stone_x, dist, angle, raw_infl in stone_data_tbl:
#             skewed_infl = applySkew(
#                 raw_infl,
#                 skew_point=0.0,
#                 skew_value=self.infl_skew_value_weight,
#                 # skew_value=0.1,
#                 skew_type='exp'
#             )
#             if stone < 0:  skewed_infl = -skewed_infl
#             influence += skewed_infl
#         return influence
#
# class GetFusekiGridLayer (keras.layers.Layer):
#     def __init__(self):
#         super(GetFusekiGridLayer, self).__init__()
#
#     def call(self, fuseki_options):
#         fuseki_scores = np.zeros(BOARD.get_shape().as_list())
#         for y, x, score in fuseki_options:
#             # score = float(f'{score:.2f}') # <- for printing
#             fuseki_scores[int(y)][int(x)] = score
#         return tf.constant(fuseki_scores)
#
# class NormalizationLayer (keras.layers.Layer):
#     def __init__(self):
#         super(NormalizationLayer, self).__init__()
#
#     def call(self, input):
#         uniques = np.unique(input.numpy())
#         min_value, max_value = uniques[1], uniques[-1]
#         normalized = (input - min_value) / (max_value - min_value)
#         return normalized
#
# class FloatRoundLayer (keras.layers.Layer):
#     def __init__(self, round_to):
#         self.round_to = round_to
#         super(FloatRoundLayer, self).__init__()
#
#     def call(self, input):
#         multiplier = tf.constant(10 ** self.round_to, dtype=input.dtype)
#         rounded = tf.round(input * multiplier) / multiplier
#         return rounded

""" layers """
# fuseki_options = np.array([])
#
# # Loop through all coord with no stone.
# for _, new_stone_y, new_stone_x in no_stone_coord_input.numpy():
#
#     # Create new_stone (temporary stone added to board), add it to all_stone_coord_input to
#     # make new_all_stone_coord_input.
#     new_stone = tf.constant([[int(self.stone), new_stone_y, new_stone_x]])
#     new_all_stone_coord_input = tf.concat([all_stone_coord_input, new_stone], axis=0)
#
#     # Container for storing all board pos influences.
#     influences = np.zeros(BOARD.get_shape().as_list())
#
#     # Loop through all pos on board with no stone.
#     for i in range(no_stone_coord_input.get_shape().as_list()[0]):
#
#         # Get coord of pos with no stone.  If coord is position of new_stone (temporary
#         # stone added to board), ignore.
#         y, x = no_stone_coord_input[i, 1:].numpy().T
#         if (y, x) == (new_stone_y, new_stone_x):  continue
#
#         # Build stone_data_tbl for coord (y, x) with data from new_all_stone_coord_input.
#         stone_data_tbl = self.getStoneDataTable(y, x, new_all_stone_coord_input)
#
#         # Apply weights to data from stone_data_tbl to calculate influence.
#         influence = self.calcInfluence(stone_data_tbl)
#
#         # Assign influence to influence 2D array.
#         influences[y][x] = influence
#
#     # Get overall fuseki_score for current new_stone, then build fuseki_options.
#     fuseki_score = influences.sum()
#     fuseki_options = np.append(fuseki_options, [new_stone_y, new_stone_x, fuseki_score])
#
# # Reshape fuseki_options, sort by fuseki_score, and convert to tensor.
# fuseki_options = np.reshape(fuseki_options, [-1, 3])
# fuseki_options = tf.constant(sorted(fuseki_options, key=lambda x: x[2], reverse=True))
#
# return fuseki_options
