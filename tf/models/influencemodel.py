
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.callbacks import TensorBoard

import math

from calcfuncs import getDistTwoPoints, getAngleTwoPoints, applyScale, applySkew, applyClamp

"""''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''' CONSTANTS """

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

"""'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''' MAIN """

def main():

    """

    -   Need to first get the model to accurately produce the dist/angle sub tensors for each coord
        point on the squashed board.

    -   Perform tests on a dist/angle tensor to produce coord point influence.

    """

    # print(tf.linalg.normalize(tf.constant([1, 2], dtype='float32')))
    # print(tf.constant(0))
    # exit()

    """ TESTING """
    # input = keras.Input(shape=BOARD_SIZE, dtype='int8')
    input = BOARD

    get_coords_by_no_stone = GetCoordsByStone2DLayer(stone=NO_STONE_VALUE)
    no_stone_coords = get_coords_by_no_stone(input)

    get_coords_by_black_stone = GetCoordsByStone2DLayer(stone=BLACK_STONE_VALUE)
    black_stone_coords = get_coords_by_black_stone(input)

    get_coords_by_white_stone = GetCoordsByStone2DLayer(stone=WHITE_STONE_VALUE)
    white_stone_coords = get_coords_by_white_stone(input)

    all_coords = tf.concat([no_stone_coords, black_stone_coords, white_stone_coords], axis=0)
    all_coords = Sort2DByColLayer(col=2, rev=False)(all_coords)
    all_coords = Sort2DByColLayer(col=1, rev=False)(all_coords)

    all_stone_coords = tf.concat([black_stone_coords, white_stone_coords], axis=0)
    all_stone_coords = Sort2DByColLayer(col=2, rev=False)(all_stone_coords)
    all_stone_coords = Sort2DByColLayer(col=1, rev=False)(all_stone_coords)

    stone_dist_angle = GetStoneDistAngle3DLayer()(all_coords, all_stone_coords)

    """                                                                                             TESTING >>> """

    """ testing on a single stone_dist_angle (coord [0, 0]) """
    stone_dist_angle = stone_dist_angle[0]
    print("\nstone_dist_angle ="), print(stone_dist_angle)

    # Get raw infls.
    global infls
    max_dist = tf.norm(tf.constant(BOARD.shape, dtype='float32'), ord='euclidean')
    infls = tf.reshape(max_dist - stone_dist_angle[:, 1], [-1, 1])
    print("\ninfls ="), print(infls)

    # Normalize infls.
    def applyScale(t, scale_from=[], scale_to=[]):
        t = (t - scale_from[0]) / (scale_from[1] - scale_from[0])
        return t * (scale_to[1] - scale_to[0]) + scale_to[0]
    infls = applyScale(infls, [0, max_dist], [0, 1])
    print("\ninfls ="), print(infls)

    # Apply first bias to infls.
    raw_infl_point_w = 0.6
    raw_infl_bias_w = 0.2
    infls = tf.map_fn(
        fn=lambda row: tf.cond(
            row < raw_infl_point_w,
            true_fn=lambda: (row * raw_infl_bias_w),
            false_fn=lambda: row
        ),
        elems=infls
    )
    print("\ninfls ="), print(infls)

    exit()

    def getBools(t, all_t):
        return tf.map_fn(
            fn=lambda t1: tf.cond(
                tf.reduce_all(tf.equal(t, t1)),
                true_fn=lambda: tf.constant(True, dtype='bool'),
                false_fn=lambda: tf.constant(False, dtype='bool')
            ),
            elems=all_t,
            dtype='bool'
        )

    def getInfls(sda_row, sda_tbl, infls):
        row_i = tf.reshape(tf.where(getBools(sda_row, sda_tbl)), [-1])[0]
        remaining_tbl = sda_tbl[row_i + 1:]
        print(remaining_tbl)
        """ row_i is the index of the current tensor.  it will be used to loop through the remaining
        tensors within sda_tbl. """
        return tf.constant(0, dtype='float32')

    print(tf.map_fn(
        fn=lambda row: getInfls(row, stone_dist_angle, infls),
        elems=stone_dist_angle
    ))

    # print(stone_dist_angle)
    exit()

    """                                                                                             <<< TESTING """

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

"""'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''' LAYERS """

class GetCoordsByStone2DLayer (keras.layers.Layer):
    """
    Return tensor[?, 3] of coords from input where value is self.stone_value.  Each row of return
    tensor has data of [stone_value, y_coord, x_coord].  Number of rows is number of values in
    input with value of self.stone_value.
    """
    def __init__(self, stone):
        super(GetCoordsByStone2DLayer, self).__init__()
        self.coord_height_dim = 1 if not TESTING else 0
        self.stone_value = tf.constant(stone, dtype='int8')

    def call(self, input):
        # Convert input into parallel bool tensor, where True = self.stone_value.
        input_as_bool = tf.equal(input, self.stone_value)
        # Get tensor of coords from input_as_bool where value = True.
        coords = tf.cast(tf.where(input_as_bool), dtype='int8')
        # Make tensor of same height as coords, of self.stone_value to be joined with coords.
        stone = tf.constant(
            self.stone_value,
            shape=[coords.shape[self.coord_height_dim], 1],
            dtype='int8'
        )
        # Vertically join stone and coords.
        stone_coords = tf.concat([stone, coords], axis=1)
        return stone_coords

class Sort2DByColLayer (keras.layers.Layer):
    """
    Return tensor[?, ?] of input tensor, with rows sorted by value of self.col.  self.multr
    designates whether the sort is ascending or descending.
    """
    def __init__(self, col=0, rev=False):
        super(Sort2DByColLayer, self).__init__()
        self.col = col
        self.multr = -1 if not rev else 1

    def call(self, input):
        # Sort a 2D tensor by values of self.col.  rev / self.multr indicates if the sort will be
        # asc or desc.
        return tf.gather(
            input, tf.nn.top_k((input[:, self.col] * self.multr), k=input.shape[0]).indices
        )

class GetStoneDistAngle3DLayer (keras.layers.Layer):
    """
    Return tensor[?, ?, 3].  Return tensor 1st dim size is same as all_coord_input 1st dim size.
    Return tensor 2nd dim size is same as stone_coord_input 1st dim size.  The 1st dim of the
    return tensor is a squashed tensor of the original board input. Each 2nd dim sub tensor
    of return tensor is a 2d tensor where each row represents a stone, and the values of each stone
    are the stone's value itself (+1 or -1), the distance from the board's coord to the stone's
    coord, and the angle from the board's coord to the stone's coord.
    """
    def __init__(self):
        super(GetStoneDistAngle3DLayer, self).__init__()

    def call(self, all_coord_input, stone_coord_input):
        # Convert dtypes.
        all_coord_input = tf.cast(all_coord_input, dtype='float32')
        stone_coord_input = tf.cast(stone_coord_input, dtype='float32')
        # Loop through all_coord_input.
        return tf.map_fn(
            fn=lambda coord: self.checkForStone(coord, stone_coord_input),
            elems=all_coord_input
        )

    def checkForStone(self, coord, stone_coord_input):
        # Check to see if current coord in loop is has a stone or not.  If current coord in loop
        # does not have a stone then proceed with self.getOutput(), else return empty zeros tensor.
        return tf.cond(
            coord[0] == tf.constant(0, dtype='float32'),
            true_fn=lambda: self.getOutput(coord, stone_coord_input),
            false_fn=lambda: tf.zeros([stone_coord_input.shape[0], 3])
        )

    def getOutput(self, coord, stone_coord_input):
        # Build and return 2nd dimension output tensor of values of stones, dists, and angles.
        stones = stone_coord_input[:, :1]
        dists = self.getDists(coord, stone_coord_input)
        angles = self.getAngles(coord, stone_coord_input)
        output = tf.concat([stones, dists, angles], axis=1)
        output = Sort2DByColLayer(col=1, rev=False)(output)
        return output

    def getDists(self, coord, stone_coord_input):
        # Calculate distance between coord and each stone_coord in stone_coord_input.
        return tf.reshape(
            tf.map_fn(
                fn=lambda stone_coord: tf.norm(stone_coord[1:] - coord[1:], ord='euclidean'),
                elems=stone_coord_input
            ),
            [-1, 1]
        )

    def getAngles(self, coord, stone_coord_input):
        # Calculate angle (deg) between coord and each stone_coord in stone_coord_input.
        return tf.reshape(
            tf.map_fn(
                fn=lambda stone_coord: tf.atan2(
                    -(stone_coord[1] - coord[1]),
                    stone_coord[2] - coord[2]
                ) * (180 / math.pi),
                elems=stone_coord_input,
            ),
            [-1, 1]
        )

"""
weights:
    - raw_dist_decay:       How much the infl decays with distance from pos.
    - barrier_decay:        How much more a proceeding opposing stone's infl decays.
    - barrier_angle_cap:    How much of an angle is accepted to designate an proceeding opposing
                            stone after a barrier stone.
    - barrier_angle_decay:  How much more a proceeding opposing stone's infl decays based on
                            angle from barrier stone.
"""

"""''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''' MAIN CALL """

if __name__ == '__main__':  main()

"""'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''' OBSOLETE """

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
