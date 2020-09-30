
import math
import pandas


def getInfluence(board):

    max_dist = getDistTwoPoints([0, 0], [ x - 1 for x in board.size ])

    # List-of-lists parallel to board.grid.
    infl_board = []

    # for stone in stones:  print(stone)

    # for y, row in enumerate(board.grid):
    #     infl_row = []
    #     for x, stone_in_row in enumerate(row):
    #         for stone in stones:
    #             """ put calculations here """
    #             # print(math.hypot(stone.pos[0] - y, stone.pos[1] - x))
    #             # infl_stone = math.dist([y, x], stone.pos) if stone else 0
    #
    #         # break
    #     # break

    infl_matrix = []

    y, x = 0, 0
    for stone in board.stones['black'] + board.stones['white']:

        stone_values = {}

        stone_values['pos'] = str([y, x])
        stone_values['stone_pos'] = str(stone.pos)
        stone_values['stone_color'] = stone.color
        stone_values['distance'] = getDistTwoPoints([y, x], stone.pos)
        stone_values['angle'] = getAngleTwoPoints([y, x], stone.pos)

        # stone_values['to_scale'] = applyScaleToValue(
        #     stone_values['distance'], [max_dist, 1.0], [0.0, 100.0]
        # )

        infl = applyLinBiasToValue(stone_values['distance'], +5.0, -0.1)

        stone_values['influence'] = infl

        infl_matrix += [ stone_values ]

    infl_matrix = sorted(infl_matrix, key=lambda x: x['angle'])
    infl_matrix = sorted(infl_matrix, key=lambda x: x['distance'])

    # print("\ninfl_matrix")
    # for row in infl_matrix:  print(row)

    infl_matrix = pandas.DataFrame(infl_matrix)
    print(infl_matrix)

    return infl_board

####################################################################################################



def getDistTwoPoints(pt1, pt2):
    return math.hypot(pt2[0] - pt1[0], pt2[1] - pt1[1])



def getAngleTwoPoints(origin_pt, angle_pt):
    rad_angle = math.atan2(angle_pt[0] - origin_pt[0], angle_pt[1] - origin_pt[1])
    deg_angle = math.degrees(rad_angle)
    deg360_angle = abs(180 + (180 - abs(-deg_angle)) if -deg_angle < 0 else deg_angle)
    return deg360_angle



def applyScale(values, scale_from=[], scale_to=[]):
    """
    value =         Value to have scale applied to.
    scale_from =    Array with len() of 2, representing the start and end of the 'scale_from'
                    number line.
    scale_to =      Array with len() of 2, representing the start and end of the 'scale_to'
                    number line.
    """
    # Controls for handling single value or array of values.
    is_array = True
    if not isinstance(values, (list, tuple, set)):  values, is_array = [values], False
    values_to_scale = []
    for value in values:
        # Apply scale to value.
        to_scale = value - scale_from[0]
        adjust = scale_to[1] / (scale_from[1] - scale_from[0])
        to_scale = abs(to_scale * adjust)
        values_to_scale += [ to_scale ]
    return values_to_scale if is_array else values_to_scale[0]



def applyBias(values, bias_point=0.0, bias_value=0.0, bias_type='exp'):
    """
    value =         Value to have bias applied.
    bias_point =    Value designating whether 'value' is to have bias applied.  If 'bias_point' is
                    positive and 'value' is greater than 'bias_point' then bias will be applied.  if
                    'bias_point' is negative and 'value' is less than 'bias_point' than bias will be
                    applied.
    bias_value =    Growth rate of the bias.  If 'bias_value' is positive then the growrth rate will
                    be increasing in value away from 'bias_point'.  If 'bias_value' is negative then
                    the growth rate will be diminish in value away from 'bias_point'.
    bias_type =     Accepts 'l', 'lin', 'linear', 'e', 'exp', or 'exponential' designating whether
                    the growth rate is linear or exponential.
    """
    # Controls for handling single value or array of values.
    is_array = True
    if not isinstance(values, (list, tuple, set)):  values, is_array = [values], False
    values_with_bias = []
    for value in values:
        bias_point_x, bias_value_x = bias_point, bias_value
        with_bias = value
        # Determine if bias needs to be applied.
        bias_less_than = bias_point_x < 0 and value < abs(bias_point_x)
        bias_greater_than = bias_point_x >= 0 and value >= abs(bias_point_x)
        if bias_less_than or bias_greater_than:
            # Controls for neg value bias_point (flip value about bias_point).
            unflip_value = False
            if bias_point < 0:
                bias_point_x = bias_point_x * -1
                value = bias_point_x + (bias_point_x - value)
                unflip_value = True
            # Apply bias_value.
            value -= bias_point_x
            bias_value_x = 1 + bias_value_x
            if bias_type in ['l', 'lin', 'linear']:  with_bias = value * bias_value_x
            elif bias_type in ['e', 'exp', 'exponential']:  with_bias = value ** bias_value_x
            with_bias += bias_point_x
            # Controls for neg value bias_point (unflip value about bias_point).
            if unflip_value:  with_bias = bias_point_x - (with_bias - bias_point_x)
        values_with_bias += [ with_bias ]
    return values_with_bias if is_array else values_with_bias[0]



####################################################################################################

import matplotlib.pyplot as plt

nums = [ (i * 1.5) + 2 for i in range(11) ]
nums_with_bias = applyBias(nums, +5.0, +0.4, 'l')
# nums_with_bias = [ applyBias(i, +12.0, +0.2, 'exp') for i in nums ]

# for i, num in enumerate(nums):
    # print(f"{num:05.02f} {nums_with_bias[i]:05.02f} {abs(num-nums_with_bias[i]):05.02f}")

for i in range(len(nums)):
    plt.plot([ nums[i], nums_with_bias[i] ], [ 1, 2 ], 'b-')

# plt.plot(nums, [1] * len(nums), 'ro')
# plt.plot(nums_with_bias, [2] * len(nums), 'bo')
plt.axis([-5, 30, 0.5, 2.5])
plt.grid(True)
plt.show()
