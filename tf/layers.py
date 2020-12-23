


# import os
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow import keras
import numpy as np
import pandas as pd

import math

from functions import sort2dByCol, applyScale, getIndexOfRowIn2d



####################################################################################################



class GetCoords2dByStone (keras.layers.Layer):
    """ Return tensor[?, 3] of coords from input where value is self.stone_value.  Each row of
    return tensor has data of [stone_value, y_coord, x_coord].  Number of rows is number of values
    in input with value of self.stone_value. """
    def __init__(self, stone, testing=False):
        super(GetCoords2dByStone, self).__init__()
        self.coord_height_dim = 1 if not testing else 0
        self.stone_value = tf.constant(stone)

    def call(self, input):
        # Convert input into parallel bool tensor, where True = self.stone_value.
        input_as_bool = tf.equal(input, self.stone_value)
        # Get tensor of coords from input_as_bool where value = True.
        coords = tf.cast(tf.where(input_as_bool), dtype='int32')
        # Make tensor of same height as coords, of self.stone_value to be joined with coords.
        stone = tf.constant(
            self.stone_value,
            shape=[coords.shape[self.coord_height_dim], 1],
        )
        # Vertically join stone and coords.
        stone_coords = tf.concat([stone, coords], axis=1)
        return stone_coords



class GetStoneDistAngle3d (keras.layers.Layer):
    """ Return tensor[?, ?, 3].  Return tensor 1st dim size is same as all_coord_input 1st dim size.
    Return tensor 2nd dim size is same as stone_coord_input 1st dim size.  The 1st dim of the
    return tensor is a squashed tensor of the original board input. Each 2nd dim sub tensor
    of return tensor is a 2d tensor where each row represents a stone, and the values of each stone
    are the stone's value itself (+1 or -1), the distance from the board's coord to the stone's
    coord, and the angle from the board's coord to the stone's coord. """
    def __init__(self):
        super(GetStoneDistAngle3d, self).__init__()

    def call(self, all_coord_input, stone_coord_input):
        # Convert dtypes.
        all_coord_input = tf.cast(all_coord_input, dtype='float32')
        stone_coord_input = tf.cast(stone_coord_input, dtype='float32')
        # Loop through all_coord_input.
        return tf.vectorized_map(
            fn=lambda coord: self.checkForStone(coord, stone_coord_input),
            elems=all_coord_input
        )

    @tf.function
    def checkForStone(self, coord, stone_coord_input):
        # Check to see if current coord in loop is has a stone or not.  If current coord in loop
        # does not have a stone then proceed with self.getOutput(), else return empty zeros tensor.
        return tf.cond(
            coord[0] == tf.constant(0, dtype='float32'),
            true_fn=lambda: self.getOutput(coord, stone_coord_input),
            false_fn=lambda: tf.zeros([stone_coord_input.shape[0], 3])
        )

    @tf.function
    def getOutput(self, coord, stone_coord_input):
        # Build and return 2nd dimension output tensor of values of stones, dists, and angles.
        stones = stone_coord_input[:, :1]
        dists = self.getDists(coord, stone_coord_input)
        angles = self.getAngles(coord, stone_coord_input)
        output = tf.concat([stones, dists, angles], axis=1)
        output = sort2dByCol(output, 1)
        return output

    @tf.function
    def getDists(self, coord, stone_coord_input):
        # Calculate distance between coord and each stone_coord in stone_coord_input.
        return tf.reshape(
            tf.vectorized_map(
                fn=lambda stone_coord: tf.norm(stone_coord[1:] - coord[1:], ord='euclidean'),
                elems=stone_coord_input
            ),
            [-1, 1]
        )

    @tf.function
    def getAngles(self, coord, stone_coord_input):
        """ Calculate angle (360d) between coord and each stone_coord in stone_coord_input. """
        # Have to reshape for future concatenation.
        return tf.reshape(
            # Outer loop is for converting neg 180 values to pos 360 values.
            tf.map_fn(
                fn=lambda x: tf.cond(x > 0, true_fn=lambda: x, false_fn=lambda: 360 + x),
                # Inner loop calculates the angle of the coord with tf.atan2.
                elems=self.getRawAngles(coord, stone_coord_input)
            ),
            [-1, 1]
        )

    @tf.function
    def getRawAngles(self, coord, stone_coord_input):
        return tf.vectorized_map(
            fn=lambda stone_coord: tf.atan2(
                -(stone_coord[1] - coord[1]),
                stone_coord[2] - coord[2]
            # Convert from rad to deg.
            ) * (180 / math.pi),
            elems=stone_coord_input
        )


class GetInfluences3d (keras.layers.Layer):
    """ Take the data sets of stone_dist_angle for each board coord pos and calculate each coord's
    player influence by applying weights.  Angular bias requires deep calculations with multiple
    loop layers. """
    def __init__(self, board_shape):
        super(GetInfluences3d, self).__init__()
        self.board_shape = board_shape
        self.max_dist = tf.norm(tf.constant(self.board_shape, dtype='float32'), ord='euclidean')

        # WEIGHTS (TESTING)
        self.dist_bias_lt_w = 0.5
        self.dist_bias_lin_w = 0.5
        self.angle_bias_lt_w = 45.0
        self.angle_bias_lin_w = 0.5

    def call(self, stone_dist_angle_input):
        # Loop through each coord's stone_dist_angle data set to get each coord's influence.
        return tf.map_fn(
            fn=lambda each: self.getEachInfluences(each),
            elems=stone_dist_angle_input
        )

    def getEachInfluences(self, stone_dist_angle):
        """ Initiate, modify, and return infls. """
        # Initialize infls.
        self.infls = self.max_dist - stone_dist_angle[:, 1]
        self.normalizeInfls()
        self.updateInflsWithDistBias()
        self.updateInflsWithAngleBias(stone_dist_angle)
        # Update infls with stone values.
        self.infls = self.infls * stone_dist_angle[:, 0]

        # Convert from each stone's influence to overall influence for no stone coord.
        self.infls = tf.reduce_sum(self.infls)

        return self.infls

    def normalizeInfls(self):
        # Normalize infls based on scale of max possible distance on board.
        self.infls = applyScale(
            self.infls,
            tf.concat([tf.constant(0, dtype='float32'), self.max_dist], axis=0),
            tf.constant([0, 1], dtype='float32')
        )

    def updateInflsWithDistBias(self):
        # Calculate fall off of dist bias with class weights.
        self.infls = ApplyLtLinWeight1d(self.dist_bias_lt_w, self.dist_bias_lin_w)(self.infls)

    def updateInflsWithAngleBias(self, stone_dist_angle):
        # Calculate fall off of angle bias with class weights.  Requires deeper calculations with
        # an outer loop and an inner loop through the stone_dist_angle data set.
        tf.map_fn(
            fn=lambda row: self.outerLoop(row, stone_dist_angle),
            elems=stone_dist_angle
        )

    def outerLoop(self, outer_row, stone_dist_angle):
        outer_row_i = getIndexOfRowIn2d(outer_row, stone_dist_angle)
        self.infls = tf.map_fn(
            fn=lambda inner_row: self.innerLoop(inner_row, outer_row_i, stone_dist_angle),
            elems=stone_dist_angle
        )
        # map_fn (in updateInflsWithBarrierBias()) requires a return value.
        return tf.constant(0.0)

    def innerLoop(self, inner_row, outer_row_i, stone_dist_angle):
        inner_row_i = getIndexOfRowIn2d(inner_row, stone_dist_angle)
        return tf.cond(
            inner_row_i <= outer_row_i,
            true_fn=lambda: self.infls[inner_row_i],
            false_fn=lambda: self.applyAngleBias(
                stone_dist_angle[outer_row_i, 0],
                stone_dist_angle[outer_row_i, 2],
                stone_dist_angle[inner_row_i, 0],
                stone_dist_angle[inner_row_i, 2],
                self.infls[inner_row_i]
            )
        )

    def applyAngleBias(self, def_stone, def_angle, agr_stone, agr_angle, infl):
        # Apply angle bias under the condition that it's necessary.  It is not necessary if
        # the defensive stone and aggressive stone are the same.
        return tf.cond(
            def_stone == agr_stone,
            true_fn=lambda: infl,
            false_fn=lambda: self.calcAngleBias(def_angle, agr_angle, infl)
        )

    def calcAngleBias(self, def_angle, agr_angle, infl):
        """ Get the angle difference and apply the bias weights if the angle difference is within
        the weight value. """
        angle_dif = tf.abs(def_angle - agr_angle)
        # Handle angle wrap from 360 to 0.
        angle_dif = tf.cond(
            angle_dif > 180,
            true_fn=lambda: 360 - angle_dif,
            false_fn=lambda: angle_dif
        )
        # Apply bias to infl.
        return tf.cond(
            angle_dif < self.angle_bias_lt_w,
            true_fn=lambda: infl * self.angle_bias_lin_w,
            false_fn=lambda: infl
        )

    """ The "Steps" functions are for analytics and testing purposes.  They're separate functions to
    not slow down the model with unnecessary conditionals. """

    def getSingleInflSteps(self, single_stone_dist_angle):
        """ Through out the initiation and updates of infls, concatenate each update of infls to
        infl_steps. This is for analysis to ensure accuracy of each layer of calculations. """
        # Initialize infls.
        self.infls = self.max_dist - single_stone_dist_angle[:, 1]
        self.infl_steps = tf.reshape(self.infls, [-1, 1])
        self.normalizeInfls()
        self.infl_steps = tf.concat([self.infl_steps, tf.reshape(self.infls, [-1, 1])], axis=1)
        self.updateInflsWithDistBias()
        self.infl_steps = tf.concat([self.infl_steps, tf.reshape(self.infls, [-1, 1])], axis=1)
        self.updateInflsWithAngleBiasForSteps(single_stone_dist_angle)
        # Update infls with stone values.
        self.infls = self.infls * single_stone_dist_angle[:, 0]
        self.infl_steps = tf.concat([self.infl_steps, tf.reshape(self.infls, [-1, 1])], axis=1)
        return self.infl_steps

    def updateInflsWithAngleBiasForSteps(self, stone_dist_angle):
        # Calculate fall off of angle bias with class weights.  Requires deeper calculations with
        # an outer loop and an inner loop through the stone_dist_angle data set.
        tf.map_fn(
            fn=lambda row: self.outerLoopForSteps(row, stone_dist_angle),
            elems=stone_dist_angle
        )

    def outerLoopForSteps(self, outer_row, stone_dist_angle):
        outer_row_i = getIndexOfRowIn2d(outer_row, stone_dist_angle)
        self.infls = tf.map_fn(
            fn=lambda inner_row: self.innerLoop(inner_row, outer_row_i, stone_dist_angle),
            elems=stone_dist_angle
        )
        self.infl_steps = tf.concat([self.infl_steps, tf.reshape(self.infls, [-1, 1])], axis=1)
        # map_fn (in updateInflsWithBarrierBias()) requires a return value.
        return tf.constant(0.0)

    def saveSingleInflSteps(self, single_stone_dist_angle, file_name):
        infl_steps = self.getSingleInflSteps(single_stone_dist_angle)
        infl_steps_df = pd.DataFrame(tf.concat([single_stone_dist_angle, infl_steps], axis=1).numpy())
        cols = ['stone', 'dist', 'angle', 'init', 'norm', 'dist_b']
        cols += [ f'angle_b_{i}' for i in range(single_stone_dist_angle.shape[0]) ] + ['final']
        infl_steps_df.columns = cols
        infl_steps_df.to_csv(file_name)



class GetInflPredictions3d (keras.layers.Layer):
    def __init__(self, stone_value):
        super(GetInflPredictions3d, self).__init__()
        self.stone_value = tf.reshape(tf.constant(stone_value, dtype='int32'), [1])

    def call(self, all_coords, board):
        all_coords = tf.cast(all_coords, dtype='float32')
        return tf.map_fn(
            fn=lambda coord: self.eachCoordLoop(coord, board),
            elems=all_coords
        )

    def eachCoordLoop(self, coord, board):
        return tf.cond(
            coord[0] == tf.constant(0, dtype='float32'),
            true_fn=lambda: self.predInfl(coord, board),
            false_fn=lambda: tf.constant(0, dtype='float32')
        )

    def predInfl(self, coord, board):
        print(coord)
        with_pred_stone = tf.SparseTensor([coord[1:]], self.stone_value, board.shape)
        with_pred_stone = tf.sparse.to_dense(with_pred_stone)
        board = board + with_pred_stone

        get_coords_by_no_stone = GetCoords2dByStone(stone=0, testing=True)
        no_stone_coords = get_coords_by_no_stone(board)

        get_coords_by_black_stone = GetCoords2dByStone(stone=1, testing=True)
        black_stone_coords = get_coords_by_black_stone(board)

        get_coords_by_white_stone = GetCoords2dByStone(stone=-1, testing=True)
        white_stone_coords = get_coords_by_white_stone(board)

        all_coords = tf.concat([no_stone_coords, black_stone_coords, white_stone_coords], axis=0)
        all_coords = sort2dByCol(all_coords, 2)
        all_coords = sort2dByCol(all_coords, 1)

        all_stone_coords = tf.concat([black_stone_coords, white_stone_coords], axis=0)
        all_stone_coords = sort2dByCol(all_stone_coords, 2)
        all_stone_coords = sort2dByCol(all_stone_coords, 1)

        get_stone_dist_angle = GetStoneDistAngle3d()
        all_stone_dist_angle = get_stone_dist_angle(all_coords, all_stone_coords)

        get_influences = GetInfluences3d([9, 9])
        influences = get_influences(all_stone_dist_angle)
        influences = tf.reshape(influences, [9, 9])
        infl_score = tf.reduce_sum(influences)
        print(infl_score)
        return infl_score





####################################################################################################



class ApplyLtLinWeight1d (keras.layers.Layer):
    """ Takes 1d tensor and outputs parallel tensor where each value is converted to (each * lin_w)
    if (each < lt_w). """
    def __init__(self, lt_w, lin_w):
        super(ApplyLtLinWeight1d, self).__init__()
        self.lt_w = lt_w
        self.lin_w = lin_w

    def call(self, input):
        # Loop through each element of input.
        return tf.map_fn(
            # Apply calculation to each if condition returns true.
            fn=lambda each: tf.cond(
                each < self.lt_w,
                true_fn=lambda: (each * self.lin_w),
                false_fn=lambda: each
            ),
            elems=input
        )



####################################################################################################



# class Sort2DByColLayer (keras.layers.Layer):
#     """
#     Return tensor[?, ?] of input tensor, with rows sorted by value of self.col.  self.multr
#     designates whether the sort is ascending or descending.
#     """
#     def __init__(self, col=0, rev=False):
#         super(Sort2DByColLayer, self).__init__()
#         self.col = col
#         self.multr = -1 if not rev else 1
#
#     def call(self, input):
#         # Sort a 2D tensor by values of self.col.  rev / self.multr indicates if the sort will be
#         # asc or desc.
#         return tf.gather(
#             input, tf.nn.top_k((input[:, self.col] * self.multr), k=input.shape[0]).indices
#         )
