
from kivy.app import App

###########################################################################   LOGIC - to - GUI   ###

def updateGuiBoardButton(color, coord):
    button = App.get_running_app().main.content_scroll.game_board_panel.display.buttons[str(coord)]
    if color == 'white':  button.stone_color.rgba = button.white_stone_color
    elif color == 'black':  button.stone_color.rgba = button.black_stone_color
    elif color == 'no_stone':  button.stone_color.rgba = button.no_stone_color

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
