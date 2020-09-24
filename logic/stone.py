
"""
GoCalc/stone.py
"""

from kivy.app import App

import messenger

####################################################################################################

class Stone:

    def __init__(self, board, color, pos):
        self.board = board
        self.color = color
        self.print_char = self.getPrintChar()
        self.pos = pos
        self.neighbor_pos = {}
        self.neighbors = {}
        self.is_capturing = False



    def __repr__(self):
        return "Stone(%s%s)" % (self.color, self.pos)



    def getPrintChar(self):
        return self.board.white_stone_char if self.color == 'white' else self.board.black_stone_char



####################################################################################################
                                                                               ###   NEIGHBORS   ###
                                                                               #####################

    def getNeighborPos(self):
        neighbor_pos_ = {'N': None, 'E': None, 'S': None, 'W': None}
        # Assign 'N' neighbor_pos.
        if self.pos[0] == 0:  del neighbor_pos_['N']
        else:  neighbor_pos_['N'] = [self.pos[0] - 1, self.pos[1]]
        # Assign 'S' neighbor_pos.
        if self.pos[0] == (self.board.size[0] - 1):  del neighbor_pos_['S']
        else:  neighbor_pos_['S'] = [self.pos[0] + 1, self.pos[1]]
        # Assign 'W' neighbor_pos.
        if self.pos[1] == 0:  del neighbor_pos_['W']
        else:  neighbor_pos_['W'] = [self.pos[0], self.pos[1] - 1]
        # Assign 'E' neighbor_pos.
        if self.pos[1] == (self.board.size[1] - 1):  del neighbor_pos_['E']
        else:  neighbor_pos_['E'] = [self.pos[0], self.pos[1] + 1]
        return neighbor_pos_



    def getNeighbors(self):
        neighbors_ = {'N': None, 'E': None, 'S': None, 'W': None}
        # Assign 'N' neighbor.
        if self.pos[0] == 0:  del neighbors_['N']
        else:  neighbors_['N'] = self.board.grid[self.pos[0] - 1][self.pos[1]]
        # Assign 'S' neighbor.
        if self.pos[0] == (self.board.size[0] - 1):  del neighbors_['S']
        else:  neighbors_['S'] = self.board.grid[self.pos[0] + 1][self.pos[1]]
        # Assign 'W' neighbor.
        if self.pos[1] == 0:  del neighbors_['W']
        else:  neighbors_['W'] = self.board.grid[self.pos[0]][self.pos[1] - 1]
        # Assign 'E' neighbor.
        if self.pos[1] == (self.board.size[1] - 1):  del neighbors_['E']
        else:  neighbors_['E'] = self.board.grid[self.pos[0]][self.pos[1] + 1]
        return neighbors_



    def update(self):
        self.updateNeighborPos()
        self.updateNeighbors()



    def updateNeighborPos(self):
        self.neighbor_pos = self.getNeighborPos()



    def updateNeighbors(self):
        self.neighbors = self.getNeighbors()



    def isNeighbor(self, stone):
        if stone in self.neighbors.values():  return True
        else:  return False



    def getNeighborPosInOrder(self, order=['N', 'E', 'S', 'W']):
        neighbor_pos_in_order = []
        for dir in order:
            if not dir in self.neighbor_pos:  continue
            neighbor_pos_in_order_ += [[ dir, self.neighbor_pos[dir] ]]
        return neighbor_pos_in_order



    def getNeighborsInOrder(self, order=['N', 'E', 'S', 'W']):
        neighbors_in_order = []
        for dir in _order:
            if not dir in self.neighbors:  continue
            neighbors_in_order += [[ dir, self.neighbors[dir] ]]
        return neighbors_in_order



####################################################################################################
                                                                                   ###   OTHER   ###
                                                                                   #################

    def remove(self):
        self.board.grid[self.pos[0]][self.pos[1]] = None
        if App.get_running_app():  messenger.updateGuiBoardButton('no_stone', self.pos)
        del self



####################################################################################################
                                                                                ###   OBSOLETE   ###
                                                                                ####################
