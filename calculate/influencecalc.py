
import math
import pandas

from calcfuncs import getDistTwoPoints, getAngleTwoPoints, applyScale, applyBias

####################################################################################################

import matplotlib.pyplot as plt

nums = [ (i * 1.5) + 2 for i in range(11) ]

nums_with_bias = applyBias(nums, +5.0, +0.4, 'exp')

for i in range(len(nums)):  plt.plot([ nums[i], nums_with_bias[i] ], [ 1, 2 ], 'b-')

plt.axis([-5, 30, 0.5, 2.5])
plt.grid(True)
plt.show()

####################################################################################################

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
