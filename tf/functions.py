
""" Need to update old functions to tensor format. """

import tensorflow as tf
import numpy as np

import math



####################################################################################################



def applyScale(t, scale_from=[], scale_to=[]):
    """
    t =             Input tensor.
    scale_from =    Tensor of shape [2] where scale_from[0] is minimum value to be scaled from and
                    scale_from[1] is maximum value to be scaled from.
    scale_to =      Tensor of shape [2] where scale_to[0] is minimum value to be scaled to and
                    scale_to[1] is maximum value to be scaled to.
    Return tensor parallel to t where each value is scaled from scale_from to scale_to.
    """
    t = (t - scale_from[0]) / (scale_from[1] - scale_from[0])
    return t * (scale_to[1] - scale_to[0]) + scale_to[0]



def roundFloat(t, round_to=2):
    """
    t =         Input tensor.
    round_to =  Decimal place that t values should be rounded to.
    Return tensor parallel to t where each value is rounded to the round_to decimal place.
    """
    multiplier = tf.constant(10 ** round_to, dtype=t.dtype)
    return tf.round(t * multiplier) / multiplier



def sort2dByCol(t, col=0, dir=-1):
    """
    t =     2D input tensor.
    col =   Which column of t to sort by.
    dir =   Accepts +1 or -1 to determine descending sort or ascending sort respectively.
    Return tensor parallel to t where rows are sorted in dir order based on col.
    """
    return tf.gather(t, tf.nn.top_k((t[:, col] * dir), k=t.shape[0]).indices)



def getIndexOfRowIn2d(row, tens_2d):
    """
    row =
    tens_2d =
    """
    return tf.reshape(
        tf.where(
            tf.map_fn(
                fn=lambda row_x: tf.cond(
                    tf.reduce_all(tf.equal(row, row_x)),
                    true_fn=lambda: tf.constant(True, dtype='bool'),
                    false_fn=lambda: tf.constant(False, dtype='bool')
                ),
                elems=tens_2d,
                dtype='bool'
            )
        ),
        [-1]
    )[0]



def printNotFloatPt(t):
    np.set_printoptions(precision=8, suppress=True)
    print(t.numpy())



####################################################################################################



# def getDistTwoPoints(pt1=[0, 0], pt2=[0, 0]):
#     return math.hypot(pt2[0] - pt1[0], pt2[1] - pt1[1])



# def getAngleTwoPoints(vertex_pt=[0, 0], ray_pt=[0, 0]):
#     """ Return angle between ray(vertex_pt, [0, 1]) and ray(vertex_pt, ray_pt) represented as
#     degrees between 0 and 360. """
#     angle_rad = math.atan2(ray_pt[0] - vertex_pt[0], ray_pt[1] - vertex_pt[1])
#     angle_deg = math.degrees(angle_rad)
#     angle_deg360 = abs(180 + (180 - abs(-angle_deg)) if -angle_deg < 0 else angle_deg)
#     return angle_deg360



# def applyScale(values, scale_from=[], scale_to=[]):
#     """
#     value =         Value to have scale applied to.
#     scale_from =    Array with len() of 2, representing the start and end of the 'scale_from'
#                     number line.
#     scale_to =      Array with len() of 2, representing the start and end of the 'scale_to'
#                     number line.
#     Return value with scale applied.
#     """
#     # Controls for handling single value or array of values.
#     is_array = True
#     if not isinstance(values, (list, tuple, set)):  values, is_array = [values], False
#     values_to_scale = []
#     for value in values:
#         # Apply scale to value.
#         to_scale = value - scale_from[0]
#         adjust = scale_to[1] / (scale_from[1] - scale_from[0])
#         to_scale = abs(to_scale * adjust)
#         values_to_scale += [ to_scale ]
#     return values_to_scale if is_array else values_to_scale[0]



# def applySkew(values, skew_point=0.0, skew_value=0.0, skew_type='exp'):
#     """
#     value =         Value to have skew applied.
#     skew_point =    Value designating whether 'value' is to have skew applied.  If 'skew_point' is
#                     positive and 'value' is greater than 'skew_point' then skew will be applied.  if
#                     'skew_point' is negative and 'value' is less than 'skew_point' than skew will be
#                     applied.
#     skew_value =    Growth rate of the skew.  If 'skew_value' is positive then the growrth rate will
#                     be increasing in value away from 'skew_point'.  If 'skew_value' is negative then
#                     the growth rate will be diminish in value away from 'skew_point'.
#     skew_type =     Accepts 'l', 'lin', 'linear', 'e', 'exp', or 'exponential' designating whether
#                     the growth rate is linear or exponential.
#     Return value with skew applied.
#     """
#     # Controls for handling single value or array of values.
#     is_array = True
#     if not isinstance(values, (list, tuple, set)):  values, is_array = [values], False
#     values_with_skew = []
#     for value in values:
#         skew_point_x, skew_value_x = skew_point, skew_value
#         with_skew = value
#         # Determine if skew needs to be applied.
#         skew_less_than = skew_point_x < 0 and value < abs(skew_point_x)
#         skew_greater_than = skew_point_x >= 0 and value >= abs(skew_point_x)
#         if skew_less_than or skew_greater_than:
#             # Controls for neg value skew_point (flip value about skew_point).
#             unflip_value = False
#             if skew_point < 0:
#                 skew_point_x = skew_point_x * -1
#                 value = skew_point_x + (skew_point_x - value)
#                 unflip_value = True
#             # Apply skew_value.
#             value -= skew_point_x
#             skew_value_x = 1 + skew_value_x
#             if skew_type in ['l', 'lin', 'linear']:  with_skew = value * skew_value_x
#             elif skew_type in ['e', 'exp', 'exponential']:  with_skew = value ** skew_value_x
#             with_skew += skew_point_x
#             # Controls for neg value skew_point (unflip value about skew_point).
#             if unflip_value:  with_skew = skew_point_x - (with_skew - skew_point_x)
#         values_with_skew += [ with_skew ]
#     return values_with_skew if is_array else values_with_skew[0]



# def applyClamp(value, min_max):
#     """ Return value if value is within the limits of min_max ([min_value, max_value]).  If value is
#     less than min_value return min_value or if value is greater than max_value return max_value. """
#     min_value, max_value = min_max
#     return max(min_value, min(value, max_value))



# print(applyClamp(2, [1.9, 3.1]))

# import matplotlib.pyplot as plt
# nums = [ (i + 1) * 0.1 for i in range(10) ]
# nums_with_bias = applyBias(nums, +0.2, +0.8, 'exp')
#
# for i in range(len(nums)):  plt.plot([ nums[i], nums_with_bias[i] ], [ 1, 2 ], 'b-')
# plt.axis([-1, 2, 0.5, 2.5])
# plt.grid(True)
# plt.show()
