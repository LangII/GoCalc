
from kivy.app import App

from gui.contentpanels.taxicabinflpanel import TaxiCabInflPanel

###########################################################################   LOGIC - to - GUI   ###

def updateGuiBoardButton(color, coord):
    app = App.get_running_app()
    game_board_panel = app.main.content_scroll.game_board_panel
    game_board_button = game_board_panel.display.buttons[str(coord)]
    if color == 'white':
        game_board_button.stone_color.rgba = game_board_button.white_stone_color
        game_board_button.stone_line_color.rgba = game_board_button.black_stone_color
    elif color == 'black':
        game_board_button.stone_color.rgba = game_board_button.black_stone_color
        game_board_button.stone_line_color.rgba = game_board_button.black_stone_color
    elif color == 'no_stone':
        game_board_button.stone_color.rgba = game_board_button.no_stone_color
        game_board_button.stone_line_color.rgba = game_board_button.no_stone_color
    if any([ isinstance(c, TaxiCabInflPanel) for c in app.main.content_scroll.layout.children ]):
        infl_calc_panel = app.main.content_scroll.taxi_cab_infl_panel
        infl_calc_button = infl_calc_panel.display.buttons[str(coord)]
        if color == 'white':
            infl_calc_button.stone_color.rgba = infl_calc_button.white_stone_color
            infl_calc_button.stone_line_color.rgba = infl_calc_button.black_stone_color
        elif color == 'black':
            infl_calc_button.stone_color.rgba = infl_calc_button.black_stone_color
            infl_calc_button.stone_line_color.rgba = infl_calc_button.black_stone_color
        elif color == 'no_stone':
            infl_calc_button.stone_color.rgba = infl_calc_button.no_stone_color
            infl_calc_button.stone_line_color.rgba = infl_calc_button.no_stone_color

###########################################################################   GUI - to - LOGIC   ###

def updateLogicBoardWithStone(stone_pos):
    app = App.get_running_app()
    player = app.data['player']
    next_stone_color = app.data['game_board']['next_stone']
    # Handle edit option to remove stone from board.
    stone_at_pos = app.data['board'].grid[stone_pos[0]][stone_pos[1]]
    if stone_at_pos and (next_stone_color == stone_at_pos.color):
        app.data['board'].grid[stone_pos[0]][stone_pos[1]].remove()
        app.data['board'].updateAllBoardData()
        return
    # Handle most update stone scenarios.
    move_legality = player[next_stone_color].makeMove(stone_pos)
    return move_legality
