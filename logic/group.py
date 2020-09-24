
"""
GoCalc/group.py
"""

from kivy.app import App

####################################################################################################

class Group:

    def __init__(self, board, stones=[]):
        self.board = board
        self.stones = stones
        self.stones_count = len(self.stones)
        self.color = self.stones[0].color
        self.neighbor_pos = self.getNeighborPos()
        self.neighbor_count = len(self.neighbor_pos)
        self.liberty_pos = self.getLibertyPos()
        self.liberty_count = len(self.liberty_pos)



    def __repr__(self):
        return "Group(%s%s)" % (self.color, [ stone.pos for stone in self.stones ])



    def getNeighborPos(self):
        all_neighbor_pos = []
        all_stone_pos = [ stone.pos for stone in self.stones ]
        for stone in self.stones:
            for neighbor_pos in stone.neighbor_pos.values():
                if not neighbor_pos in all_neighbor_pos + all_stone_pos:
                    all_neighbor_pos += [ neighbor_pos ]
        return all_neighbor_pos



    def getLibertyPos(self):
        liberty_pos = []
        for pos in self.neighbor_pos:
            if not self.board.grid[pos[0]][pos[1]]:  liberty_pos += [ pos ]
        return liberty_pos



    def captured(self):
        opponent_color = 'black' if self.color == 'white' else 'white'
        self.board.players[opponent_color].captures += self.stones_count


        app = App.get_running_app()
        if app:  app.main.content_scroll.game_board_panel.captures_display.updateText()



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
