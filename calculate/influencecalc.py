
import math
import pandas

# import matplotlib.pyplot as plt

from calculate.calcfuncs import (
    getDistTwoPoints, getAngleTwoPoints, applyScale, applySkew, applyClamp
)

####################################################################################################



####################################################################################################

# nums = [ (i * 1.5) + 2 for i in range(11) ]
# nums_with_bias = applyBias(nums, +5.0, +0.4, 'exp')
#
# for i in range(len(nums)):  plt.plot([ nums[i], nums_with_bias[i] ], [ 1, 2 ], 'b-')
# plt.axis([-5, 30, 0.5, 2.5])
# plt.grid(True)
# plt.show()



def getBoardInfluence(board):

    max_dist = getDistTwoPoints([0, 0], [ x - 1 for x in board.size ])
    stones = board.stones['black'] + board.stones['white']
    board_infl = []
    for y, row in enumerate(board.grid):
        row_infl = []
        for x, stone_at_pos in enumerate(row):
            pos_infl = 0
            # Positions with stones get 0 influence.
            if stone_at_pos:  row_infl += [ pos_infl ] ; continue

            for stone in stones:

                stone_infl = getDistTwoPoints([y, x], stone.pos)
                stone_infl = applyScale(stone_infl, [max_dist, 1.0], [0.0, 100.0])
                stone_infl = applySkew(stone_infl, -20.0, +0.8, 'lin')
                stone_infl = applyClamp(stone_infl, [0.0, 100.0])

                if stone.color == 'white':  stone_infl = -stone_infl
                pos_infl += stone_infl

            # stones_data = getStonesDataTable([y, x], stones)
            # for i in range(len(stones_data)):

            row_infl += [ pos_infl ]
        board_infl += [ row_infl ]
    return board_infl



def getStonesDataTable(pos, stones):

    stones_data = []
    for stone in stones:
        stone_data = {}

        stone_data['pos'] = str(pos)
        stone_data['stone_pos'] = str(stone.pos)
        stone_data['stone_color'] = stone.color
        stone_data['distance'] = getDistTwoPoints(pos, stone.pos)
        stone_data['angle'] = getAngleTwoPoints(pos, stone.pos)

        stone_data['influence'] = infl

        stones_data += [ stone_data ]

    stones_data = sorted(stones_data, key=lambda x: x['angle'])
    stones_data = sorted(stones_data, key=lambda x: x['distance'])

    stones_data = pandas.DataFrame(stones_data)
    print(stones_data)

    return stones_data
