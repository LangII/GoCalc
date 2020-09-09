
"""
GoThink/player.py
"""

####################################################################################################

class Player:

    def __init__(self, _board, _color):
        # Primary attributes:
        self.colorCheck(_color)
        self.board = _board
        self.color = _color
        self.print_char = self.getPrintChar()
        self.captures = 0
        self.stones = self.board.stones[_color]
        self.groups = self.board.groups[_color]
        # Update boards referencing of self.
        self.board.updatePlayer(self)



    def __repr__(self):
        return "Player(%s)" % self.color



    def colorCheck(self, _color):
        if not _color in ['black', 'white']:
            exit_print = "Player.__init__() _color arg only accepts 'black' or 'white' not '%s'."
            print(exit_print % _color)
            exit()



    def getPrintChar(self):
        return self.board.WHITE_STONE_CHAR if self.color == 'white' else self.board.BLACK_STONE_CHAR



    def makeMove(self, _pos, _check_legality=True):
        """ May possibly need to move this logic to board.playerMakesMove()...  The only reason I'm
        suggesting that is out of consistency:  I'm trying to keep as much of the logic in board as
        possible. """
        # Check legality is an argument mainly for testing purposes; not for live gameplay.
        if _check_legality:
            legality = self.board.getMoveLegality(self, _pos)
            is_legal_move, is_capturing = legality['is_legal_move'], legality['is_capturing']
            if not is_legal_move:
                # Will need to update this line with interface update.
                # exit("ILLEGAL MOVE of {} at {}".format(self.color, _pos))
                return 'illegal'
            else:
                # _is_capturing is necessary because of the not too often situation of a move with
                # no liberties, but is legal because it's capturing.
                if is_capturing:  self.board.playerMakesMove(self, _pos, _is_capturing=True)
                else:  self.board.playerMakesMove(self, _pos)
        else:
            self.board.playerMakesMove(self, _pos)



    def boardUpdated(self):
        self.stones = self.board.stones[self.color]
        self.groups = self.board.groups[self.color]



####################################################################################################
                                                                                ###   OBSOLETE   ###
                                                                                ####################

# def boardUpdated(self):
#     self.stones_pos = self.getStonesPos()
#     self.groups = self.getStoneGroups()



# def getStonesPos(self):
#     stones_pos_ = []
#     for y, row in enumerate(self.board.grid):
#         for x, stone in enumerate(row):
#             if self.board.grid[y][x] == self.stone_char:  stones_pos_ += [[x + 1, y + 1]]
#     return stones_pos_



# def getStoneGroups(self):
#
#     group_labels = [0] * len(self.stones_pos)
#     current_assignment = 1
#
#     for i, stone in enumerate(self.stones_pos):
#         if group_labels[i] == 0:
#             group_labels[i] = current_assignment
#             current_assignment += 1
#
#         for other_i, other_stone in enumerate(self.stones_pos):
#             if i == other_i or group_labels[other_i] != 0:  continue
#             if self.board.posAreAdjacent(stone, other_stone):
#                 group_labels[other_i] = group_labels[i]
#
#     # print("group_labels =", group_labels)
#
#     stone_groups_ = []
#     for master_assignment in range(max(group_labels)):
#         master_assignment += 1
#         stones = []
#         for i, assignment in enumerate(group_labels):
#             if master_assignment == assignment:
#                 stones += [ self.stones_pos[i] ]
#         # print("stones =", stones)
#         stone_groups_ += [ StoneGroup(stones) ]
#
#     return stone_groups_
