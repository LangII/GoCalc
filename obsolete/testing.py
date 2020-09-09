
"""

- Need to have a (safe) value assigned for each (Group):  Assigning how likely the group is to be
able to form 2 eyes or connect to a group that can form 2 eyes.

- Need to have a (points) value assigned for each (Group):  Assigning the value of points the group
contributes.

- Need to have a (points_potential) value assigned for each (Group):  Assigning how likely the
(points) are to becoming true points.

"""

# from datetime import datetime
from copy import deepcopy

####################################################################################################

# start_time = datetime.now()

####################################################################################################

BOARD_SIZE = 9

NO_STONE_CHAR = '-'
BLACK_STONE_CHAR = '#'
WHITE_STONE_CHAR = 'O'
STAR_CHAR = '*'
KO_CHAR = 'K'

BOARDER_CORNER_CHAR = '+'
BOARDER_HOR_CHAR = '-'
BOARDER_VERT_CHAR = '|'

# How much the influence is biased in favor of the positions closer to the stone.
RAW_INFLUENCE_BIAS = 5
# This value determines the maximum value of the influence grid, and adjusts all other influence
# values to be proportionate with this maximum value.
RAW_INFLUENCE_CEILING = 10
# If a stone is in a corner of a 19x19 board, 37 is the # of steps (taxicab geometry) it takes to
# get from that stone, to the farthest corner from that stone.  This value controls the lower end
# of the values of the influence grid.
# NOTE:  The reason this is a global is because I feel strongly that it should be a non-changing
# constant, but I'm not 100% certain as of now.
RAW_INFLUENCE_MAX_STEPS = 37

RAW_INFLUENCE_PRINT_JUSTIFY_BY = 6
RAW_INFLUENCE_PRINT_ROUND_DEC_BY = 2

####################################################################################################

def main():

    # center = [4, 4]
    # point1 = center
    #
    # exit()

    board = Board(BOARD_SIZE)

    black_bot, white = Bot(board, 'black'), Player(board, 'white')

    # for pos in [
    #     [5, 0], [5, 1], [6, 2], [6, 3], [6, 4], [6, 5], [7, 5], [8, 5], [5, 2], [5, 3]
    # ]:  white.makeMove(pos)
    # for pos in [
    #     [7, 2], [7, 3], [7, 4], [8, 2], [8, 4], [6, 1], [6, 2], [6, 0]
    # ]:  black_bot.makeMove(pos)
    for pos in [
        [2, 2], [3, 4], [6, 2], [5, 2], [7, 6], [6, 7], [8, 7]
    ]:  white.makeMove(pos)
    for pos in [
        [6, 5], [4, 6], [5, 3], [2, 6], [4, 3], [6, 6], [5, 7]
    ]:  black_bot.makeMove(pos)

    board.prettyPrint()

    print(black_bot.getAngularProxInflGrid())

    # print(black_bot.getWholeBoardRawInfluenceGrid(True))

    # print("abs_life =", black_bot.groupHasAbsLife([7, 2]))

    exit()

####################################################################################################
                                                                                   ###   BOARD   ###
                                                                                   #################

class Board:

    def __init__(self, _grid_size):
        self.size = self.convertInitGridSize(_grid_size)
        self.grid = self.getNewGrid(self.size)
        # Variables for class containers.
        self.players = {'black': None, 'white': None}
        self.stones = {'black': [], 'white': []}
        self.groups = {'black': [], 'white': []}
        # Variables for print purposes.
        self.print_grid = self.getPrintGrid()
        self.print_with_lines = False
        self.print_row_width = self.getPrintRowWidth()



    def convertInitGridSize(self, _grid_size):
        if isinstance(_grid_size, int):  return [_grid_size, _grid_size]
        else:  return _grid_size



    def getNewGrid(self, _grid_size):
        """ self.grid (list of lists) containing either Stone instances or None. """
        grid_ = []
        for _ in range(_grid_size[0]):
            grid_ += [[ None for _ in range(_grid_size[1]) ]]
        return grid_



    def getPrintGrid(self):
        """ self.print_grid (list of lists parallel to self.grid) containing string characters
        representing the black/white stones or no stones. """
        print_grid_ = []
        for row in self.grid:
            print_row = []
            for stone in row:
                if not stone:  print_char = NO_STONE_CHAR
                else:  print_char = stone.print_char
                print_row += [ print_char ]
            print_grid_ += [ print_row ]
        return print_grid_



    def getPrintRowWidth(self):
        """ self.print_row_width (int) representing the length of the string that represents a
        printed grid row. """
        return len(self.getPrintMidRow(self.print_grid[0]))



    def updatePlayer(self, _player):
        """ Called from Player to update Board's internal reference to Player. """
        if _player.color == 'black':  self.players['black'] = _player
        else:  self.players['white'] = _player



####################################################################################################



    def getMoveLegality(self, _player, _pos):
        """ The primary purpose of getMoveLegality() is to handle the not too common scenario Where
        a move that is played would be considered illegal, if not for the fact that the move
        performs a capture in the process. """
        # Setup hypothetical temporary board with _player Stone and Group played on _pos.
        temp_board = deepcopy(self)
        temp_stone = Stone(temp_board, _player.color, _pos)
        temp_board.grid[_pos[0]][_pos[1]] = temp_stone
        temp_board.updateAllBoardData()
        temp_group = temp_board.getGroupByPos(_pos)
        # If new played stone's group has no liberties then check liberties of neighboring groups.
        if temp_group.liberty_count <= 0:
            # Check each neighbor pos.
            for pos in temp_stone.neighbor_pos.values():
                neighbor_group = temp_board.getGroupByPos(pos)
                # Set conditional bool values.
                group_is_opponent = neighbor_group != temp_group
                group_is_being_captured = neighbor_group.liberty_count <= 0
                # If a neighboring opponent's group is being captured by this play, then move is
                # legal and is_capturing in the process.
                if group_is_opponent and group_is_being_captured:
                    return {'is_legal_move': True, 'is_capturing': True}
            # If stone played has no liberties and is not capturing any opponents group, then move
            # is illegal.
            return {'is_legal_move': False, 'is_capturing': False}
        # If new played stone's group has liberties, move is legal and is not capturing.
        else:  return {'is_legal_move': True, 'is_capturing': False}



    def playerMakesMove(self, _player, _pos, _is_capturing=False):
        stone = Stone(self, _player.color, _pos)
        self.grid[_pos[0]][_pos[1]] = stone
        if _is_capturing:  stone.is_capturing = True
        self.updateAllBoardData()
        self.handleCapturedGroups()
        self.updateAllBoardData()
        if _is_capturing:  stone.is_capturing = False



    def updateAllBoardData(self):
        self.print_grid = self.getPrintGrid()
        self.stones = self.getStones()
        self.updateAllStones()
        self.groups = self.getGroups()
        for player in self.players.values():  player.boardUpdated()



    def getStones(self):
        stones_ = {'black': [], 'white': []}
        for row in self.grid:
            for stone in row:
                if stone:
                    if stone.color == 'black':  stones_['black'] += [ stone ]
                    elif stone.color == 'white':  stones_['white'] += [ stone ]
        return stones_



    def updateAllStones(self):
        for color, stones in self.stones.items():
            for stone in stones:  stone.update()



    def getStoneByPos(self, _pos):
        return self.grid[_pos[0]][_pos[1]]



    def getGroupByPos(self, _pos):
        for color in self.groups:
            for group in self.groups[color]:
                for stone in group.stones:
                    if stone.pos == _pos:  return group
        return 'pos has no stone / no group'



    def getGroups(self):
        """ Groups are generated from stones[color].  Each stone in stones[color] is compared to all
        other stones in stones[color], if the stones being compared are neighbors
        (stone.isNeighbor()) then the stones being compared are assigned a group. """
        groups_ = {'black': [], 'white': []}
        for color, stones in self.stones.items():
            if not stones:  continue
            # (group_labels) is a parallel array to (stones).  Where each value is an
            # int and each int value represents a group.  Examples:
            # [1, 1] = 1 group:  1 group of 2 stones
            # [1, 1, 2] = 2 groups:  1 group of 2 stones and 1 group of 1 stone
            # [1, 1, 2, 3] = 3 groups:  1 group of 2 stones, 1 group of 1 stone, and 1 group of 1 stone
            group_labels = [0] * len(stones)

            new_label = 1
            for i, stone in enumerate(stones):
                # Assign new label to stone, if stone has yet to be labelled.
                if group_labels[i] == 0:
                    group_labels[i] = new_label
                    new_label += 1
                # Inner loop compares outer loop (stone) with all other (stones).
                for other_i, other_stone in enumerate(stones):
                    if i == other_i:  continue
                    if stone.isNeighbor(other_stone):
                        # If inner loop stone has yet to be labelled, then inner loop stone is
                        # labelled with outer loop stones label.
                        if group_labels[other_i] == 0:
                            group_labels[other_i] = group_labels[i]
                        # If inner loop stone has already been labelled, then all stones previously
                        # labelled with outer loop stone's label, get their labels reassigned to the
                        # inner loop stone's label.
                        else:
                            new_labels = []
                            for ga in group_labels:
                                if ga == group_labels[i]:  new_labels += [ group_labels[other_i] ]
                                else:  new_labels += [ ga ]
                            group_labels = new_labels
            # (groups_) are created now that (group_labels) has been generated.
            for master_label in range(max(group_labels)):
                master_label += 1
                stones_to_group = []
                for i, label in enumerate(group_labels):
                    if master_label == label:
                        stones_to_group += [ self.stones[color][i] ]
                groups_[color] += [ Group(self, stones_to_group) ]
        return groups_



    def handleCapturedGroups(self):
        for color in self.groups:
            for group in self.groups[color]:
                if group.liberty_count <= 0 and not group.isCapturing():  group.captured()



####################################################################################################
                                                                          ###   BOARD - PRINTS   ###
                                                                          ##########################

    def prettyPrint(self, _coord=True, _captures=True):
        # Get all_printed_mid_rows.
        printed_mid_rows = []
        for row in self.print_grid:  printed_mid_rows += [ self.getPrintMidRow(row) ]
        printed_mid_sep_rows = '\n{}\n'.format(self.getPrintMidSepRow())
        all_printed_mid_rows = printed_mid_sep_rows.join(printed_mid_rows)
        # Get printed_topbot_row and printed_topbot_sep_row.
        printed_topbot_row = self.getPrintTopBotRow()
        printed_topbot_sep_row = self.getPrintTopBotSepRow()
        all_printed = '\n'.join([
            printed_topbot_row,
            printed_topbot_sep_row,
            all_printed_mid_rows,
            printed_topbot_sep_row,
            printed_topbot_row
        ])
        if _coord:  all_printed = self.addCoordToPrettyPrint(all_printed)
        print('\n' + all_printed)
        # Print captures.
        if _captures:
            format_largs = [
                str(self.players['black'].captures).rjust(2, '0'),
                str(self.players['white'].captures).rjust(2, '0')
            ]
            print("    captures:  black={}  white={}".format(*format_largs))



    def getPrintTopBotRow(self):
        hor_char_row = BOARDER_HOR_CHAR * (self.print_row_width - 2)
        return BOARDER_CORNER_CHAR + hor_char_row + BOARDER_CORNER_CHAR



    def getPrintMidSepRow(self):
        lines = '|' if self.print_with_lines else ' '
        outer_chars = BOARDER_VERT_CHAR + '  {}  ' + BOARDER_VERT_CHAR
        inner_chars = '  '.join([lines] * len(self.print_grid[0]))
        return outer_chars.format(inner_chars)



    def getPrintTopBotSepRow(self):
        return BOARDER_VERT_CHAR + (' ' * (self.print_row_width - 2)) + BOARDER_VERT_CHAR



    def getPrintMidRow(self, _print_row):
        lines = '--' if self.print_with_lines else '  '
        outer_chars = BOARDER_VERT_CHAR + '  {}  ' + BOARDER_VERT_CHAR
        inner_chars = lines.join(_print_row)
        return outer_chars.format(inner_chars)



    def addCoordToPrettyPrint(self, _printed):
        print_with_coord = []
        print_with_coord += [ self.getTopCoordsPrintLine(_printed) ]
        print_with_coord += self.getListOfPrintLinesWithLeftCoord(_printed)
        print_with_coord = '\n'.join(print_with_coord)
        return print_with_coord



    def getTopCoordsPrintLine(self, _printed):
        # Format top_coord_ to list of chars of only ' ' and NO_STONE_CHAR.
        top_coords_ = deepcopy(_printed.split('\n')[2])
        top_coords_ = top_coords_.replace(BOARDER_VERT_CHAR, ' ')
        for each in [BLACK_STONE_CHAR, WHITE_STONE_CHAR]:
            top_coords_ = top_coords_.replace(each, NO_STONE_CHAR)
        top_coords_ = list(top_coords_)
        # Replace NO_STONE_CHAR with coord.
        for coord in range(self.size[1]):
            top_coords_[top_coords_.index(NO_STONE_CHAR)] = str(coord)
        # Reallign white space for double digit coords.
        to_delete = []
        for i in range(len(top_coords_)):
            if len(top_coords_[i]) == 2:  to_delete += [ i - 1 ]
        to_delete.reverse()
        for deleting in to_delete:  del top_coords_[deleting]
        # Reformat coord line and add to output.
        top_coords_ = '   ' + ''.join(top_coords_)
        return top_coords_



    def getListOfPrintLinesWithLeftCoord(self, _printed):
        lines_with_coord_ = []
        # Designate which lines need coords.
        coord_indexes = range(2, (self.size[0] + 1) * 2, 2)
        added_coord = 0
        for i, print_line in enumerate(_printed.split('\n')):
            # Add coords to lines that need them.
            if i in coord_indexes:
                print_line = '{} '.format(str(added_coord).rjust(2)) + print_line
                added_coord += 1
            else:
                print_line = '   ' + print_line
            lines_with_coord_ += [ print_line ]
        return lines_with_coord_



####################################################################################################
                                                                                   ###   STONE   ###
                                                                                   #################

class Stone:

    def __init__(self, _board, _color, _pos):
        self.board = _board
        self.color = _color
        self.print_char = WHITE_STONE_CHAR if _color == 'white' else BLACK_STONE_CHAR
        self.pos = _pos
        self.neighbor_pos = {}
        self.neighbors = {}
        self.is_capturing = False



    def __repr__(self):
        return "Stone(%s%s)" % (self.color, self.pos)



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



    def isNeighbor(self, _stone):
        if _stone in self.neighbors.values():  return True
        else:  return False



    def getNeighborPosInOrder(self, _order=['N', 'E', 'S', 'W']):
        neighbor_pos_in_order_ = []
        for dir in _order:
            if not dir in self.neighbor_pos:  continue
            neighbor_pos_in_order_ += [[ dir, self.neighbor_pos[dir] ]]
        return neighbor_pos_in_order_



    def getNeighborsInOrder(self, _order=['N', 'E', 'S', 'W']):
        neighbors_in_order_ = []
        for dir in _order:
            if not dir in self.neighbors:  continue
            neighbors_in_order_ += [[ dir, self.neighbors[dir] ]]
        return neighbors_in_order_



    def remove(self):
        self.board.grid[self.pos[0]][self.pos[1]] = None



####################################################################################################
                                                                                   ###   GROUP   ###
                                                                                   #################

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
                                                                                  ###   PLAYER   ###
                                                                                  ##################

class Player:

    def __init__(self, _board, _color):
        self.colorCheck(_color)
        self.board = _board
        self.color = _color
        self.print_char = WHITE_STONE_CHAR if _color == 'white' else BLACK_STONE_CHAR
        self.captures = 0
        self.stones = self.board.stones[_color]
        self.groups = self.board.groups[_color]

        self.board.updatePlayer(self)



    def __repr__(self):
        return "Player(%s)" % self.color



    def colorCheck(self, _color):
        if not _color in ['black', 'white']:
            exit_print = "Player.__init__() _color arg only accepts 'black' or 'white' not '%s'."
            print(exit_print % _color)
            exit()



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
                                                                                     ###   BOT   ###
                                                                                     ###############

class Bot(Player):

    def __init__(self, _board, _color):
        super().__init__(_board, _color)



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



    def getStoneRawInfluenceGrid(
        self, _pos, _opponent=False, _bias=RAW_INFLUENCE_BIAS, _ceiling=RAW_INFLUENCE_CEILING,
        _max_steps=RAW_INFLUENCE_MAX_STEPS
    ):
        """ Returns a list-of-lists parallel to board.grid where the individual values are floats
        representing the influence of an individual stone. """
        if isinstance(_pos, Stone):  _pos = _pos.pos
        influence_grid_ = []
        for y, row in enumerate(self.board.grid):
            influence_row = []
            for x, stone in enumerate(row):
                # influence_grid_ ignores grid positions with stones (sets influence to 0).
                if self.board.grid[y][x] != None or (y == _pos[0] and x == _pos[1]):  influence = 0
                # influence is basically determined by distance from stone (using taxicab geometry).
                else:  influence = (_max_steps - (abs(_pos[0] - y) + abs(_pos[1] - x))) ** _bias
                influence_row += [ influence ]
            influence_grid_ += [ influence_row ]
        # Apply ceiling to grid.
        max_infl = max([ i for row in influence_grid_ for i in row ])
        ceiling_transition = _ceiling / max_infl
        for y in range(len(influence_grid_)):
            for x in range(len(influence_grid_[0])):
                influence_grid_[y][x] = influence_grid_[y][x] * ceiling_transition
                # Adjust for calculations of opponent.
                if _opponent:  influence_grid_[y][x] = -influence_grid_[y][x]
        return influence_grid_



    def getAllStonesRawInfluenceGrid(
        self, _opponent=False, _bias=RAW_INFLUENCE_BIAS, _ceiling=RAW_INFLUENCE_CEILING,
        _max_steps=RAW_INFLUENCE_MAX_STEPS
    ):
        # influence_grids is a list of individual influence grids for each individual stone.
        if _opponent:
            opponent_color = 'white' if self.color == 'black' else 'black'
            influence_grids = []
            for stone in self.board.stones[opponent_color]:
                stone_infl = self.getStoneRawInfluenceGrid(
                    stone, True, _bias=_bias, _ceiling=_ceiling, _max_steps=_max_steps
                )
                influence_grids += [ stone_infl ]
        else:
            influence_grids = []
            for stone in self.stones:
                stone_infl = self.getStoneRawInfluenceGrid(
                    stone, _bias=_bias, _ceiling=_ceiling, _max_steps=_max_steps
                )
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



    def getWholeBoardRawInfluenceGrid(
        self, _to_print=False, _bias=RAW_INFLUENCE_BIAS, _ceiling=RAW_INFLUENCE_CEILING,
        _max_steps=RAW_INFLUENCE_MAX_STEPS, _print_justify_by=RAW_INFLUENCE_PRINT_JUSTIFY_BY,
        _print_round_dec_by=RAW_INFLUENCE_PRINT_ROUND_DEC_BY
    ):
        bot_influence = self.getAllStonesRawInfluenceGrid(
            _bias=_bias, _ceiling=_ceiling, _max_steps=_max_steps
        )
        opponent_influence = self.getAllStonesRawInfluenceGrid(
            True, _bias=_bias, _ceiling=_ceiling, _max_steps=_max_steps
        )
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
                    elif i >  0:  i = '+%.*f' % (_print_round_dec_by, i)
                    elif i <= 0:  i = '%.*f' % (_print_round_dec_by, i)
                    new_row += [ i.rjust(_print_justify_by) ]
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

main()

####################################################################################################



""" Bot """
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



""" Board """
# def updatePrintGrid(self, _stone_char, _pos):
#     self.print_grid[_pos[0]][_pos[1]] = _stone_char



""" Board """
# def changeCell(self, _coord, _change_to):
#     """
#     _coord =        Int array of len 2, representing x, y coordinates on the grid where 1, 1 is
#                     the top-left corner.
#     _change_to =    String of single char to which the cell is to be changed to.
#     """
#     self.print_grid[_coord[1] - 1][_coord[0] - 1] = _change_to
#     for player in self.players:  player.boardUpdated()



""" Board """
# def posAreAdjacent(self, _pos1, _pos2):
#     if _pos1[0] == _pos2[0]:
#         if (_pos1[1] == _pos2[1] + 1) or (_pos1[1] == _pos2[1] - 1):  return True
#     elif _pos1[1] == _pos2[1]:
#         if (_pos1[0] == _pos2[0] + 1) or (_pos1[0] == _pos2[0] - 1):  return True
#     return False



""" Player """
# def boardUpdated(self):
#     self.stones_pos = self.getStonesPos()
#     self.groups = self.getStoneGroups()



""" Player """
# def getStonesPos(self):
#     stones_pos_ = []
#     for y, row in enumerate(self.board.grid):
#         for x, stone in enumerate(row):
#             if self.board.grid[y][x] == self.stone_char:  stones_pos_ += [[x + 1, y + 1]]
#     return stones_pos_



""" Player """
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



""" Group """
# def addStone(self, _stone):
#     self.stones += [ _stone ]
#     self.stones_count = len(self.stones)
#     self.neighbor_pos = self.getNeighborPos()
#     self.neighbor_count = len(self.neighbor_pos)
#     self.liberty_pos = self.getLibertyPos()
#     self.liberty_count = len(self.liberty_pos)
