
"""
GoCalc/gui/main_gui.py
"""

"""
possible app names:
    (dentaku(calculator))
    (suji(development of the stones) dentaku(calculator))
    (dentaku(calculator) go(game))
    (keisansuru(calculate) go(game))
"""

"""
TO-DOS:
- Update Content Settings Input ToggleButtons to stay 'down' if already 'down' when pressed.
"""

# Dynamically add parent folder to path.
import os, sys
cur_dir = os.getcwd()
insert_sys_path = cur_dir[:cur_dir.rfind('\\')]
sys.path.insert(1, insert_sys_path)

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window

from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from kivy.properties import NumericProperty, ObjectProperty

from gui.contentpanels.gameboardpanel import GameBoardPanel

from board import Board
from player import Player

####################################################################################################

APP_DATA = {

    'board': None,
    'player': {'black': None, 'white': None},

    'default_window_size': [800, 500],
    'board_size': 9, # 9, 13, or 19
    'grid_star_size': 5,
    'grid_star_coords': {
        9: [[2, 2], [2, 6], [4, 4], [6, 2], [6, 6]],
        13: [[3, 3], [3, 9], [6, 6], [9, 3], [9, 9]],
        19: [[3, 3], [3, 9], [3, 15], [9, 3], [9, 9], [9, 15], [15, 3], [15, 9], [15, 15]]
    },
    'game_board': {
        'location': 'scroll', # 'stationary', 'scroll', or 'unselected'
        'mode': 'edit', # 'edit' or 'play'
        'edit_mode': 'alternate', # 'alternate' or 'consecutive'
        'next_stone': 'black', # 'black' or 'white'
    },
    # 'panel_select': {
    #     'location': 'scroll' # Always remains as last index of ContentScroll.
    # }
}

####################################################################################################

def main():

    doBeforeStart()

    GoCalcApp().run()

    exit()

####################################################################################################

def doBeforeStart():
    Builder.load_file('gui/gocalc.kv')
    Window.size = APP_DATA['default_window_size']

####################################################################################################



class MainWindow (BoxLayout):

    def __init__(self, app):
        super(MainWindow, self).__init__()
        self.main_menu_bar = MainMenuBar()
        self.add_widget(self.main_menu_bar)
        self.content_scroll = ContentScroll()
        self.add_widget(self.content_scroll)

        app.data['board'] = Board(app.data['board_size'])
        app.data['player']['black'] = Player(app.data['board'], 'black')
        app.data['player']['white'] = Player(app.data['board'], 'white')



class GoCalcApp (App):
    data = APP_DATA

    def __init__(self, **kwargs):
        super(GoCalcApp, self).__init__(**kwargs)
        self.main = MainWindow(self)

    def build(self):  return self.main



class MainMenuBar (BoxLayout):
    button_width = NumericProperty()

    def __init__(self):
        super(MainMenuBar, self).__init__()

        """ TEMPORARY / FOR DISPLAY PURPOSES """
        for button_title in ['main', 'options', 'help']:
            self.add_widget(Button(
                text=button_title, size_hint=[None, 1.0], width=self.button_width
            ))



class ContentScroll (ScrollView):
    layout = ObjectProperty()

    def __init__(self):
        super(ContentScroll, self).__init__()

        self.game_board_panel = GameBoardPanel()

        self.layout.add_widget(self.game_board_panel)

        """ TEMPORARY / FOR DISPLAY PURPOSES """
        for i in range(20):
            self.layout.add_widget(Button(
                text=f'{i + 1}', width=100, size_hint=[None, 1.0]
            ))



####################################################################################################

main()

####################################################################################################

""" WITH MOUSE OVER """
# class MainWindow(BoxLayout):
#     def __init__(self):
#         super().__init__()
#
#         """ mouse over """
#         # Window.bind(mouse_pos=self.onMousePos)
#
#         self.main_menu_bar = MainMenuBar()
#         self.add_widget(self.main_menu_bar)
#
#         self.content = Content()
#         self.add_widget(self.content)
#
#     """ mouse over """
#     # def onMousePos(self, window, pos):
#     #     for button in self.board_display.pos_buttons:
#     #         if button.collide_point(*pos):
#     #             print(button.text)
