


import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow import keras

import math

from functions import sort2dByCol



"""''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''"""



class GetCoords2dByStone (keras.layers.Layer):
    """
    Return tensor[?, 3] of coords from input where value is self.stone_value.  Each row of return
    tensor has data of [stone_value, y_coord, x_coord].  Number of rows is number of values in
    input with value of self.stone_value.
    """
    def __init__(self, stone, testing=False):
        super(GetCoords2dByStone, self).__init__()
        self.coord_height_dim = 1 if not testing else 0
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



class GetStoneDistAngle3d (keras.layers.Layer):
    """
    Return tensor[?, ?, 3].  Return tensor 1st dim size is same as all_coord_input 1st dim size.
    Return tensor 2nd dim size is same as stone_coord_input 1st dim size.  The 1st dim of the
    return tensor is a squashed tensor of the original board input. Each 2nd dim sub tensor
    of return tensor is a 2d tensor where each row represents a stone, and the values of each stone
    are the stone's value itself (+1 or -1), the distance from the board's coord to the stone's
    coord, and the angle from the board's coord to the stone's coord.
    """
    def __init__(self):
        super(GetStoneDistAngle3d, self).__init__()

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
        output = sort2dByCol(output, 1)
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
        """ Calculate angle (360d) between coord and each stone_coord in stone_coord_input. """
        # Have to reshape for future concatenation.
        return tf.reshape(
            # Outer loop is for converting neg 180 values to pos 360 values.
            tf.map_fn(
                fn=lambda x: tf.cond(x > 0, true_fn=lambda: x, false_fn=lambda: 360 + x),
                # Inner loop calculates the angle of the coord with tf.atan2.
                elems=tf.map_fn(
                    fn=lambda stone_coord: tf.atan2(
                        -(stone_coord[1] - coord[1]),
                        stone_coord[2] - coord[2]
                    # Convert from rad to deg.
                    ) * (180 / math.pi),
                    elems=stone_coord_input,
                )
            ),
            [-1, 1]
        )



class ApplyLtLinWeight1d (keras.layers.Layer):
    """
    Takes 1d tensor and outputs parallel tensor where each value is converted to (value * lin_w) if
    (value < lt_w).
    """
    def __init__(self, lt_w, lin_w):
        super(ApplyLtLinWeight1d, self).__init__()
        self.lt_w = lt_w
        self.lin_w = lin_w

    def call(self, input):
        return tf.map_fn(
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
