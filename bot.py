
"""
GoThink/bot.py
"""

from copy import deepcopy

from player import Player
from stone import Stone
from group import Group

####################################################################################################

class Bot(Player):

    def __init__(self, _board, _color, _settings):
        super().__init__(_board, _color)
        # Main settings attributes:
        self.RAW_INFLUENCE_BIAS = _settings['RAW_INFLUENCE_BIAS']
        self.RAW_INFLUENCE_CEILING = _settings['RAW_INFLUENCE_CEILING']
        self.RAW_INFLUENCE_MAX_STEPS = _settings['RAW_INFLUENCE_MAX_STEPS']
        self.RAW_INFLUENCE_PRINT_JUSTIFY_BY = _settings['RAW_INFLUENCE_PRINT_JUSTIFY_BY']
        self.RAW_INFLUENCE_PRINT_ROUND_DEC_BY = _settings['RAW_INFLUENCE_PRINT_ROUND_DEC_BY']



####################################################################################################



    def getGroupLibCountEval(self, _group):
        """ Return an evaluation of all possible moves that would increase the stone count of a
        group, and what that group's liberty count would be if that move was made.  The format of
        the evaluation is a list-of-lists, where the sublist is [move_pos, liberty_count], parent
        list is sorted by liberty_count highest-to-lowest. """
        eval_ = []
        for pos in _group.liberty_pos:
            temp_board = deepcopy(self.board)
            temp_board.grid[pos[0]][pos[1]] = Stone(temp_board, self.color, pos)
            temp_board.updateAllBoardData()
            temp_group = temp_board.getGroupByPos(pos)
            eval_ += [[ pos, temp_group.liberty_count ]]
        eval_.sort(key=lambda x: x[1], reverse=True)
        return eval_



####################################################################################################



    def getStoneRawInfluenceGrid(self, _pos, _opponent=False):
        """ Returns a list-of-lists parallel to board.grid where the individual values are floats
        representing the influence of an individual stone. """
        if isinstance(_pos, Stone):  _pos = _pos.pos
        influence_grid_ = []
        for y, row in enumerate(self.board.grid):
            influence_row = []
            for x, stone in enumerate(row):
                # influence_grid_ ignores grid positions with stones (sets influence to 0).
                if self.board.grid[y][x] != None or (y == _pos[0] and x == _pos[1]):
                    influence = 0
                else:
                    # Total (taxicab geometry) steps from _pos to [y, x].
                    total_steps = abs(_pos[0] - y) + abs(_pos[1] - x)
                    # Invert steps to make value assignment on grid applicable.
                    inverted_steps = self.RAW_INFLUENCE_MAX_STEPS - total_steps
                    # Apply bias (to make points closer to stone more valuable).
                    raw_influence = inverted_steps ** self.RAW_INFLUENCE_BIAS
                influence_row += [ raw_influence ]
            influence_grid_ += [ influence_row ]
        # Calculate ceiling_transition value:
        max_infl = max([ i for row in influence_grid_ for i in row ])
        ceiling_transition = self.RAW_INFLUENCE_CEILING / max_infl
        for y in range(len(influence_grid_)):
            for x in range(len(influence_grid_[0])):
                # Apply ceiling_transition to each value in influence_grid_.
                influence_grid_[y][x] = influence_grid_[y][x] * ceiling_transition
                # If calculating for opponent, make all values negative.
                if _opponent:  influence_grid_[y][x] = -influence_grid_[y][x]
        return influence_grid_



    def getAllStonesRawInfluenceGrid(self, _opponent=False):
        # influence_grids is a list of individual influence grids for each individual stone.
        if _opponent:
            opponent_color = 'white' if self.color == 'black' else 'black'
            influence_grids = []
            for stone in self.board.stones[opponent_color]:
                stone_infl = self.getStoneRawInfluenceGrid(stone)
                influence_grids += [ stone_infl ]
        else:
            influence_grids = []
            for stone in self.stones:
                stone_infl = self.getStoneRawInfluenceGrid(stone)
                influence_grids += [ stone_infl ]
        # Generate the base all_influence_grid_.
        all_influence_grid_ = []
        for _ in range(self.board.size[0]):
            all_influence_grid_ += [[ 0 for _ in range(self.board.size[1]) ]]
        # Populate all_influence_grid_ with influence_grids.
        for y in range(len(all_influence_grid_)):
            for x in range(len(all_influence_grid_[0])):
                all_influence_grid_[y][x] = sum([ grid[y][x] for grid in influence_grids ])
        return all_influence_grid_



    def getWholeBoardRawInfluenceGrid(self, _to_print=False):
        bot_influence = self.getAllStonesRawInfluenceGrid()
        opponent_influence = self.getAllStonesRawInfluenceGrid(_opponent=True)
        # Generate the base all_influence_grid_.
        whole_board_influence_ = []
        for _ in range(self.board.size[0]):
            whole_board_influence_ += [[ 0 for _ in range(self.board.size[1]) ]]
        # Populate whole_board_influence_ with influence_grids.
        for y in range(len(whole_board_influence_)):
            for x in range(len(whole_board_influence_[0])):
                whole_board_influence_[y][x] = bot_influence[y][x] + opponent_influence[y][x]
        # If requested, convert to a single pretty-print string.
        if _to_print:
            to_print = []
            for y, row in enumerate(whole_board_influence_):
                new_row = []
                for x, i in enumerate(row):
                    if isinstance(self.board.grid[y][x], Stone):
                        i = '(%s)' % self.board.grid[y][x].print_char
                        new_row += [ i.center(self.RAW_INFLUENCE_PRINT_JUSTIFY_BY) ]
                    elif i >  0:
                        i = '+%.*f' % (self.RAW_INFLUENCE_PRINT_ROUND_DEC_BY, i)
                        new_row += [ i.rjust(self.RAW_INFLUENCE_PRINT_JUSTIFY_BY) ]
                    elif i <= 0:
                        i = '%.*f' % (self.RAW_INFLUENCE_PRINT_ROUND_DEC_BY, i)
                        new_row += [ i.rjust(self.RAW_INFLUENCE_PRINT_JUSTIFY_BY) ]
                to_print += [ ' '.join(new_row) ]
            whole_board_influence_ = '\n\n'.join(to_print)
        return whole_board_influence_



####################################################################################################



    def getAngularProxInflGrid(self):
        all_stones = self.board.stones['black'] + self.board.stones['white']
        for y, row in enumerate(self.board.grid):
            for x, stone in enumerate(row):
                pos = [y, x]
                angle = 0
                ang_prox_table = []

        return



####################################################################################################
                                                                                ###   ABS LIFE   ###
                                                                                ####################

    def groupHasAbsLife(self, _group, _board='default'):
        """ The difference between "life" and "abs (absolute) life" is a state where the opponent
        of the group could make an infinite # of unopposed moves against the group, and the group
        would remain alive. """
        # Handle argument variations.
        if isinstance(_group, Stone):  _group = self.board.getGroupByPos(_group.pos)
        elif not isinstance(_group, Group):  _group = self.board.getGroupByPos(_group)
        if _board == 'default':  _board = self.board
        # Working vars.
        opponent_color = 'white' if self.color == 'black' else 'black'
        temp_board = deepcopy(_board)
        # Get illegal_moves_count.
        illegal_moves_count = 0
        for pos in _group.liberty_pos:
            if temp_board.players[opponent_color].makeMove(pos) == 'illegal':
                illegal_moves_count += 1
        # Return based on value of illegal_moves_count.
        if illegal_moves_count >= 2:  return True
        else:  return False



####################################################################################################
                                                                                ###   OBSOLETE   ###
                                                                                ####################

# def getStoneRawInfluenceGrid(
#     self, _pos, _opponent=False, _bias=RAW_INFLUENCE_BIAS, _max_infl=RAW_INFLUENCE_MAX_INFL
# ):
#     """ Returns a list-of-lists parallel to board.grid where the individual values are ints
#     representing the influence of an individual stone. """
#     if isinstance(_pos, Stone):  _pos = _pos.pos
#     # max_steps is the maximum number of steps possible on a board.  This allows for the
#     # two furthest points on the board to have the lowest level of influence be a value of 1.
#     max_steps = self.board.size[0] + self.board.size[1] - 1
#     influence_grid_ = []
#     for y, row in enumerate(self.board.grid):
#         influence_row = []
#         for x, stone in enumerate(row):
#             # influence_grid_ ignores grid positions with stones (sets influence to 0).
#             if self.board.grid[y][x] != None or (y == _pos[0] and x == _pos[1]):
#                 influence = 0
#             # influence is basically determined by distance from stone (using taxicab geometry).
#             # else:  influence = max_steps - (abs(_pos[0] - y) + abs(_pos[1] - x))
#             else:
#                 influence = max_steps - (abs(_pos[0] - y) + abs(_pos[1] - x))
#                 # Apply bias, i.e., have influenced results be biased in favor of closer to stone.
#                 if _bias > 1:
#                     influence = influence ** _bias
#                     for _ in range(_bias - 1):  influence = influence / max_steps
#             if _opponent:  influence = -influence
#             influence_row += [ influence ]
#         influence_grid_ += [ influence_row ]
#     return influence_grid_
