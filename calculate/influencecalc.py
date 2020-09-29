
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

def applyScaleToValue(value, scale_from, scale_to):
    to_scale = value - scale_from[0]
    adjust = scale_to[1] / (scale_from[1] - scale_from[0])
    to_scale = abs(to_scale * adjust)
    return to_scale

def applyBiasToValue(value, bias_point, bias_value, bias_type):
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
    with_bias = value
    # Determine if bias needs to be applied at all.
    bias_less_than = bias_point < 0 and value < abs(bias_point)
    bias_greater_than = bias_point >= 0 and value >= abs(bias_point)
    if bias_less_than or bias_greater_than:
        # Sub-routine only used to avoid repetition.
        def calcWithBias(v, bp, bv, bt):
            v -= bp
            bv = 1 + bv
            if bt in ['l', 'lin', 'linear']:  with_bias = v * bv
            elif bt in ['e', 'exp', 'exponential']:  with_bias = v ** bv
            with_bias += bp
            return with_bias
        # Calculations of diminishing bias has to be done after values are converted to positive,
        # calculated, then re-converted back to negative.
        if bias_point < 0:
            bias_point = abs(bias_point)
            value = bias_point + (bias_point - value)
            with_bias = calcWithBias(value, bias_point, bias_value, bias_type)
            with_bias = bias_point - (with_bias - bias_point)
        elif bias_point >= 0:
            # To allow for application of 0 value.
            if value == 0:  value += 0.0000000001
            with_bias = calcWithBias(value, bias_point, bias_value, bias_type)
    return with_bias

####################################################################################################

import matplotlib.pyplot as plt

nums = [ i for i in range(11) ]
nums_with_bias = [ applyBiasToValue(i, +5.0, +0.4, 'exp') for i in nums ]

# for i, num in enumerate(nums):
    # print(f"{num:05.02f} {nums_with_bias[i]:05.02f} {abs(num-nums_with_bias[i]):05.02f}")

for i in range(len(nums)):
    plt.plot([ nums[i], nums_with_bias[i] ], [ 1, 2 ], 'b-')

# plt.plot(nums, [1] * len(nums), 'ro')
# plt.plot(nums_with_bias, [2] * len(nums), 'bo')
plt.axis([-5, 30, 0.5, 2.5])
plt.grid(True)
plt.show()
