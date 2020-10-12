

from kivy.app import App

""" This is stupid...  Not sure why, but this import line needs to be commented out if
running from main_console.py. """
from gamelogic.stone import Stone

# def getStoneRawInfluenceGrid(self, pos, opponent=False):
def getStoneRawInfluenceGrid(pos, opponent=False, board_grid=None):

    board_grid = App.get_running_app().data['board'].grid

    # pos = [4, 4]
    raw_infl_max_steps = 36
    raw_infl_bias = 5
    raw_infl_ceiling = 10

    """ Returns a list-of-lists parallel to board.grid where the individual values are floats
    representing the influence of an individual stone. """
    if isinstance(pos, Stone):  pos = pos.pos
    influence_grid = []
    for y, row in enumerate(board_grid):
        influence_row = []
        for x, stone in enumerate(row):
            # influence_grid ignores grid positions with stones (sets influence to 0).
            if board_grid[y][x] != None or (y == pos[0] and x == pos[1]):
                raw_influence = 0
            else:
                # Total (taxicab geometry) steps from pos to [y, x].
                total_steps = abs(pos[0] - y) + abs(pos[1] - x)
                # Invert steps to make value assignment on grid applicable.

                # inverted_steps = self.RAW_INFLUENCE_MAX_STEPS - total_steps
                inverted_steps = raw_infl_max_steps - total_steps

                # Apply bias (to make points closer to stone more valuable).

                # raw_influence = inverted_steps ** self.RAW_INFLUENCE_BIAS
                raw_influence = inverted_steps ** raw_infl_bias

            influence_row += [ raw_influence ]
        influence_grid += [ influence_row ]
    # Calculate ceiling_transition value:
    max_infl = max([ i for row in influence_grid for i in row ])

    # ceiling_transition = self.RAW_INFLUENCE_CEILING / max_infl
    ceiling_transition = raw_infl_ceiling / max_infl

    for y in range(len(influence_grid)):
        for x in range(len(influence_grid[0])):
            # Apply ceiling_transition to each value in influence_grid.
            influence_grid[y][x] = influence_grid[y][x] * ceiling_transition
            # If calculating for opponent, make all values negative.
            if opponent:  influence_grid[y][x] = -influence_grid[y][x]
    return influence_grid



# def getAllStonesRawInfluenceGrid(self, opponent=False):
def getAllStonesRawInfluenceGrid(opponent=False):

    board = App.get_running_app().data['board']

    # influence_grids is a list of individual influence grids for each individual stone.
    if opponent:

        # opponent_color = 'white' if self.color == 'black' else 'black'
        opponent_color = 'white'

        influence_grids = []

        # for stone in self.board.stones[opponent_color]:
        for stone in board.stones[opponent_color]:

            stone_infl = getStoneRawInfluenceGrid(stone, True)
            influence_grids += [ stone_infl ]
    else:
        influence_grids = []

        # for stone in self.stones:
        for stone in board.players['black'].stones:

            stone_infl = getStoneRawInfluenceGrid(stone)
            influence_grids += [ stone_infl ]
    # Generate the base all_influence_grid.
    all_influence_grid = []

    # for _ in range(self.board.size[0]):
    for _ in range(board.size[0]):

        # all_influence_grid += [[ 0 for _ in range(self.board.size[1]) ]]
        all_influence_grid += [[ 0 for _ in range(board.size[1]) ]]

    # Populate all_influence_grid with influence_grids.
    for y in range(len(all_influence_grid)):
        for x in range(len(all_influence_grid[0])):
            all_influence_grid[y][x] = sum([ grid[y][x] for grid in influence_grids ])
    return all_influence_grid



# def getWholeBoardRawInfluenceGrid(self, to_print=False):
def getWholeBoardRawInfluenceGrid(to_print=False):

    print_justify_by = 7
    print_round_dec_by = 2

    board = App.get_running_app().data['board']

    bot_influence = getAllStonesRawInfluenceGrid()
    opponent_influence = getAllStonesRawInfluenceGrid(opponent=True)
    # Generate the base all_influence_grid.
    whole_board_influence = []
    for _ in range(board.size[0]):
        whole_board_influence += [[ 0 for _ in range(board.size[1]) ]]
    # Populate whole_board_influence with influence_grids.
    for y in range(len(whole_board_influence)):
        for x in range(len(whole_board_influence[0])):
            whole_board_influence[y][x] = bot_influence[y][x] + opponent_influence[y][x]

    # If requested, convert to a single pretty-print string.
    if to_print:
        to_print = []
        for y, row in enumerate(whole_board_influence):
            new_row = []
            for x, i in enumerate(row):
                if isinstance(board.grid[y][x], Stone):
                    i = '(%s)' % board.grid[y][x].print_char
                    new_row += [ i.center(print_justify_by) ]
                elif i >  0:
                    i = '+%.*f' % (print_round_dec_by, i)
                    new_row += [ i.rjust(print_justify_by) ]
                elif i <= 0:
                    i = '%.*f' % (print_round_dec_by, i)
                    new_row += [ i.rjust(print_justify_by) ]
            to_print += [ ' '.join(new_row) ]
        whole_board_influence = '\n\n'.join(to_print)

    return whole_board_influence
