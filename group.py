
"""
GoThink/group.py
"""

####################################################################################################

class Group:

    def __init__(self, _board, _stones=[]):
        self.board = _board
        self.stones = _stones
        self.stones_count = len(self.stones)
        self.color = self.stones[0].color
        self.neighbor_pos = self.getNeighborPos()
        self.neighbor_count = len(self.neighbor_pos)
        self.liberty_pos = self.getLibertyPos()
        self.liberty_count = len(self.liberty_pos)



    def __repr__(self):
        return "Group(%s%s)" % (self.color, [ stone.pos for stone in self.stones ])



    def getNeighborPos(self):
        all_neighbor_pos_ = []
        all_stone_pos = [ stone.pos for stone in self.stones ]
        # print("\n{} getNeighborPos()".format(self))
        for stone in self.stones:
            for neighbor_pos in stone.neighbor_pos.values():
                # print("neighbor_pos =", neighbor_pos)
                if not neighbor_pos in all_neighbor_pos_ + all_stone_pos:
                    all_neighbor_pos_ += [ neighbor_pos ]
        # print("all_neighbor_pos_ =", all_neighbor_pos_)
        return all_neighbor_pos_



    def getLibertyPos(self):
        liberty_pos_ = []
        for pos in self.neighbor_pos:
            if not self.board.grid[pos[0]][pos[1]]:  liberty_pos_ += [ pos ]
        return liberty_pos_



    def captured(self):
        opponent_color = 'black' if self.color == 'white' else 'white'
        self.board.players[opponent_color].captures += self.stones_count
        for stone in self.stones:  stone.remove()
        del self



    def isCapturing(self):
        for stone in self.stones:
            if not stone.is_capturing:  return False
        return True



####################################################################################################
                                                                                ###   OBSOLETE   ###
                                                                                ####################

# def addStone(self, _stone):
#     self.stones += [ _stone ]
#     self.stones_count = len(self.stones)
#     self.neighbor_pos = self.getNeighborPos()
#     self.neighbor_count = len(self.neighbor_pos)
#     self.liberty_pos = self.getLibertyPos()
#     self.liberty_count = len(self.liberty_pos)
