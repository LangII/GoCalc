
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
# from gui.contentpanels.taxicabinflpanel import TaxiCabInflPanel
from gui.contentpanels.influencepanel import InfluencePanel

from gamelogic.board import Board
from gamelogic.player import Player

####################################################################################################

APP_DATA = {

    'board': None,
    'player': {'black': None, 'white': None},

    'default_window_size': [1000, 700],
    'board_size': 19, # 9, 13, or 19
    'grid_star_size': 5,
    'grid_star_coords': {
        9: [[2, 2], [2, 6], [4, 4], [6, 2], [6, 6]],
        13: [[3, 3], [3, 9], [6, 6], [9, 3], [9, 9]],
        19: [[3, 3], [3, 9], [3, 15], [9, 3], [9, 9], [9, 15], [15, 3], [15, 9], [15, 15]]
    },
    'game_board': {
        'panel_location': 'scroll', # 'stationary', 'scroll', or 'unselected'
        'mode': 'edit', # 'edit' or 'play'
        'edit_mode': 'alternate', # 'alternate' or 'consecutive'
        'next_stone': 'black', # 'black' or 'white'
    },
    'influence': {
        'panel_location': 'scroll', # 'stationary', 'scroll', or 'unselected'
        'display_mode': 'cur_infl', # 'cur_infl' or 'infl_pred'
        'predicting_stone': 'black', # 'black' or 'white'
        'display_stones': 'yes', # 'yes' or 'no'
        'adjustments': {
            'distance_decay': True,
            'distance_zero': True,
            'angle_decay': True,
            'opposite_angle_growth': True,
            'clamp': True,
        },
        'weights': {
            'dist_decay_gt': {
                'min': 0.0, 'max': 50.0, 'value': 4.0,
            },
            'dist_decay_lin': {
                'min': 0.0, 'max': 1.0, 'value': 0.5,
            },
            'dist_zero_gt': {
                'min': 0.0, 'max': 50.0, 'value': 8.0,
            },
            'angle_decay_lt': {
                'min': 0.0, 'max': 180.0, 'value': 45.0,
            },
            'angle_decay_lin': {
                'min': 0.0, 'max': 1.0, 'value': 0.5,
            },
            'opp_angle_growth_angle_lt': {
                'min': 0.0, 'max': 180.0, 'value': 15.0,
            },
            'opp_angle_growth_dist_lt': {
                'min': 0.0, 'max': 50.0, 'value': 5.0,
            },
            'opp_angle_growth_lin': {
                'min': 1.0, 'max': 10.0, 'value': 1.0,
            },
            'clamp_within': {
                'min': 0.0, 'max': 20.0, 'value': 1.0,
            },
        }
    }
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



        """ TESTING / DEBUGGING """
        Window.bind(on_key_down=self.keyboardInput)
    def keyboardInput(self, obj, num1, num2, text, *args):
        if text == ' ':  self.spaceBarInput()
    def spaceBarInput(self):
        app = App.get_running_app()

        gameboard_height = app.main.content_scroll.game_board_panel.display.layout.height
        influece_height = app.main.content_scroll.influence_panel.display.layout.height

        gameboard_panel_width = app.main.content_scroll.game_board_panel.width

        influence_panel_width = app.main.content_scroll.influence_panel.width
        influence_display_pos = app.main.content_scroll.influence_panel.display.pos

        print("\n<><><>")

        # print(f"gameboard_panel_width = {gameboard_panel_width}")
        # print(f"influence_panel_width = {influence_panel_width}")

        print("<><><>")
        """ TESTING / DEBUGGING """

        app.main.content_scroll.influence_panel.width = gameboard_panel_width
        # app.main.content_scroll.influence_panel.display.pos[1] = influence_display_pos[1] - 50
        
        # app.main.content_scroll.influence_panel.display.layout.height = gameboard_height
        # app.main.content_scroll.influence_panel.display.layout.width = gameboard_height



class MainMenuBar (BoxLayout):
    button_width = NumericProperty()

    def __init__(self):
        super(MainMenuBar, self).__init__()
        self.app = App.get_running_app()

        """ TEMPORARY / FOR DISPLAY PURPOSES """
        self.main_button = Button(text='main', size_hint=[None, 1.0], width=self.button_width)
        self.add_widget(self.main_button)
        # self.main_button.bind(on_release=self.doStuff)
        # for button_title in ['main', 'options', 'help']:
        for button_title in ['options', 'help']:
            self.add_widget(Button(
                text=button_title, size_hint=[None, 1.0], width=self.button_width
            ))

    def doStuff(self, *args, **kwargs):
        print(self.app.main)
        self.app.main.content_scroll.infl_calc_panel.display.height = self.app.main.content_scroll.game_board_panel.display.height



class ContentScroll (ScrollView):
    layout = ObjectProperty()

    def __init__(self):
        super(ContentScroll, self).__init__()

        self.game_board_panel = GameBoardPanel()
        self.layout.add_widget(self.game_board_panel)

        # self.taxi_cab_infl_panel = TaxiCabInflPanel()
        # self.layout.add_widget(self.taxi_cab_infl_panel)

        self.influence_panel = InfluencePanel()
        self.layout.add_widget(self.influence_panel)

        """ TEMPORARY / FOR DISPLAY PURPOSES """
        for i in range(20):
            self.layout.add_widget(Button(
                text=f'{i + 1}', width=100, size_hint=[None, 1.0]
            ))



class GoCalcApp (App):
    data = APP_DATA

    def __init__(self, **kwargs):
        super(GoCalcApp, self).__init__(**kwargs)
        self.main = MainWindow(self)
        # self.add_widget(self.main)

    # def on_start(self, *args):
    #     print("here", self.main.content_scroll.infl_calc_panel.display.height)

    def build(self):
        return self.main



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
