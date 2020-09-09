
"""
GoCalc/board.py
"""

from copy import deepcopy

from stone import Stone
from group import Group

####################################################################################################

class Board:

    def __init__(self, _settings):
        # Main settings attributes:
        self.BOARD_SIZE = _settings['BOARD_SIZE']
        self.NO_STONE_CHAR = _settings['NO_STONE_CHAR']
        self.BLACK_STONE_CHAR = _settings['BLACK_STONE_CHAR']
        self.WHITE_STONE_CHAR = _settings['WHITE_STONE_CHAR']
        self.STAR_CHAR = _settings['STAR_CHAR']
        self.KO_CHAR = _settings['KO_CHAR']
        self.BOARDER_CORNER_CHAR = _settings['BOARDER_CORNER_CHAR']
        self.BOARDER_HOR_CHAR = _settings['BOARDER_HOR_CHAR']
        self.BOARDER_VERT_CHAR = _settings['BOARDER_VERT_CHAR']
        # Primary attributes:
        self.size = self.convertInitGridSize(self.BOARD_SIZE)
        self.grid = self.getNewGrid(self.size)
        # Attributes for class containers:
        self.players = {'black': None, 'white': None}
        self.stones = {'black': [], 'white': []}
        self.groups = {'black': [], 'white': []}
        # Attributes for print purposes:
        self.print_grid = self.getPrintGrid()
        self.print_with_lines = False
        self.print_row_width = self.getPrintRowWidth()



####################################################################################################
                                                                                   ###   INITS   ###
                                                                                   #################



    def convertInitGridSize(self, grid_size):
        if isinstance(grid_size, int):  return [grid_size, grid_size]
        else:  return grid_size



    def getNewGrid(self, grid_size):
        """ self.grid (list of lists) containing either Stone instances or None. """
        grid = []
        for _ in range(grid_size[0]):
            grid += [[ None for _ in range(grid_size[1]) ]]
        return grid



    def getPrintGrid(self):
        """ self.print_grid (list of lists parallel to self.grid) containing string characters
        representing the black/white stones or no stones. """
        print_grid = []
        for row in self.grid:
            print_row = []
            for stone in row:
                if not stone:  print_char = self.NO_STONE_CHAR
                else:  print_char = stone.print_char
                print_row += [ print_char ]
            print_grid += [ print_row ]
        return print_grid



    def getPrintRowWidth(self):
        """ self.print_row_width (int) representing the length of the string that represents a
        printed grid row. """
        return len(self.getPrintMidRow(self.print_grid[0]))



####################################################################################################
                                                                                ###   GAMEPLAY   ###
                                                                                ####################

    def updatePlayer(self, player):
        """ Called from Player to update Board's internal reference to Player. """
        if player.color == 'black':  self.players['black'] = player
        else:  self.players['white'] = player



    def getMoveLegality(self, player, pos):
        """ The primary purpose of getMoveLegality() is to handle the not too common scenario Where
        a move that is played would be considered illegal, if not for the fact that the move
        performs a capture in the process. """
        # Setup hypothetical temporary board with player Stone and Group played on pos.
        temp_board = deepcopy(self)
        temp_stone = Stone(temp_board, player.color, pos)
        temp_board.grid[pos[0]][pos[1]] = temp_stone
        temp_board.updateAllBoardData()
        temp_group = temp_board.getGroupByPos(pos)
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



    def playerMakesMove(self, player, pos, is_capturing=False):
        stone = Stone(self, player.color, pos)
        self.grid[pos[0]][pos[1]] = stone
        if is_capturing:  stone.is_capturing = True
        self.updateAllBoardData()
        self.handleCapturedGroups()
        self.updateAllBoardData()
        if is_capturing:  stone.is_capturing = False



    def updateAllBoardData(self):
        self.print_grid = self.getPrintGrid()
        self.stones = self.getStones()
        self.updateAllStones()
        self.groups = self.getGroups()
        for player in self.players.values():  player.boardUpdated()



    def getStones(self):
        stones = {'black': [], 'white': []}
        for row in self.grid:
            for stone in row:
                if stone:
                    if stone.color == 'black':  stones['black'] += [ stone ]
                    elif stone.color == 'white':  stones['white'] += [ stone ]
        return stones



    def updateAllStones(self):
        for color, stones in self.stones.items():
            for stone in stones:  stone.update()



    def getStoneByPos(self, pos):
        return self.grid[pos[0]][pos[1]]



    def getGroupByPos(self, pos):
        for color in self.groups:
            for group in self.groups[color]:
                for stone in group.stones:
                    if stone.pos == pos:  return group
        return 'pos has no stone / no group'



    def getGroups(self):
        """ Groups are generated from stones[color].  Each stone in stones[color] is compared to all
        other stones in stones[color], if the stones being compared are neighbors
        (stone.isNeighbor()) then the stones being compared are assigned a group. """
        groups = {'black': [], 'white': []}
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
            # (groups) are created now that (group_labels) has been generated.
            for master_label in range(max(group_labels)):
                master_label += 1
                stones_to_group = []
                for i, label in enumerate(group_labels):
                    if master_label == label:
                        stones_to_group += [ self.stones[color][i] ]
                groups[color] += [ Group(self, stones_to_group) ]
        return groups



    def handleCapturedGroups(self):
        for color in self.groups:
            for group in self.groups[color]:
                if group.liberty_count <= 0 and not group.isCapturing():  group.captured()



####################################################################################################
                                                                                  ###   PRINTS   ###
                                                                                  ##################

    def prettyPrint(self, coord=True, captures=True):
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
        if coord:  all_printed = self.addCoordToPrettyPrint(all_printed)
        print('\n' + all_printed)
        # Print captures.
        if captures:
            format_largs = [
                str(self.players['black'].captures).rjust(2, '0'),
                str(self.players['white'].captures).rjust(2, '0')
            ]
            print("    captures:  black={}  white={}".format(*format_largs))



    def getPrintTopBotRow(self):
        hor_char_row = self.BOARDER_HOR_CHAR * (self.print_row_width - 2)
        return self.BOARDER_CORNER_CHAR + hor_char_row + self.BOARDER_CORNER_CHAR



    def getPrintMidSepRow(self):
        lines = '|' if self.print_with_lines else ' '
        outer_chars = self.BOARDER_VERT_CHAR + '  {}  ' + self.BOARDER_VERT_CHAR
        inner_chars = '  '.join([lines] * len(self.print_grid[0]))
        return outer_chars.format(inner_chars)



    def getPrintTopBotSepRow(self):
        return self.BOARDER_VERT_CHAR + (' ' * (self.print_row_width - 2)) + self.BOARDER_VERT_CHAR



    def getPrintMidRow(self, print_row):
        lines = '--' if self.print_with_lines else '  '
        outer_chars = self.BOARDER_VERT_CHAR + '  {}  ' + self.BOARDER_VERT_CHAR
        inner_chars = lines.join(print_row)
        return outer_chars.format(inner_chars)



    def addCoordToPrettyPrint(self, printed):
        print_with_coord = []
        print_with_coord += [ self.getTopCoordsPrintLine(printed) ]
        print_with_coord += self.getListOfPrintLinesWithLeftCoord(printed)
        print_with_coord = '\n'.join(print_with_coord)
        return print_with_coord



    def getTopCoordsPrintLine(self, printed):
        # Format top_coord_ to list of chars of only ' ' and NO_STONE_CHAR.
        top_coords = deepcopy(printed.split('\n')[2])
        top_coords = top_coords.replace(self.BOARDER_VERT_CHAR, ' ')
        for each in [self.BLACK_STONE_CHAR, self.WHITE_STONE_CHAR]:
            top_coords = top_coords.replace(each, self.NO_STONE_CHAR)
        top_coords = list(top_coords)
        # Replace NO_STONE_CHAR with coord.
        for coord in range(self.size[1]):
            top_coords[top_coords.index(self.NO_STONE_CHAR)] = str(coord)
        # Reallign white space for double digit coords.
        to_delete = []
        for i in range(len(top_coords)):
            if len(top_coords[i]) == 2:  to_delete += [ i - 1 ]
        to_delete.reverse()
        for deleting in to_delete:  del top_coords[deleting]
        # Reformat coord line and add to output.
        top_coords = '   ' + ''.join(top_coords)
        return top_coords



    def getListOfPrintLinesWithLeftCoord(self, printed):
        lines_with_coord = []
        # Designate which lines need coords.
        coord_indexes = range(2, (self.size[0] + 1) * 2, 2)
        added_coord = 0
        for i, print_line in enumerate(printed.split('\n')):
            # Add coords to lines that need them.
            if i in coord_indexes:
                print_line = '{} '.format(str(added_coord).rjust(2)) + print_line
                added_coord += 1
            else:
                print_line = '   ' + print_line
            lines_with_coord += [ print_line ]
        return lines_with_coord



####################################################################################################
                                                                                ###   OBSOLETE   ###
                                                                                ####################

# def updatePrintGrid(self, _stone_char, _pos):
#     self.print_grid[_pos[0]][_pos[1]] = _stone_char



# def changeCell(self, _coord, _change_to):
#     """
#     _coord =        Int array of len 2, representing x, y coordinates on the grid where 1, 1 is
#                     the top-left corner.
#     _change_to =    String of single char to which the cell is to be changed to.
#     """
#     self.print_grid[_coord[1] - 1][_coord[0] - 1] = _change_to
#     for player in self.players:  player.boardUpdated()



# def posAreAdjacent(self, _pos1, _pos2):
#     if _pos1[0] == _pos2[0]:
#         if (_pos1[1] == _pos2[1] + 1) or (_pos1[1] == _pos2[1] - 1):  return True
#     elif _pos1[1] == _pos2[1]:
#         if (_pos1[0] == _pos2[0] + 1) or (_pos1[0] == _pos2[0] - 1):  return True
#     return False
