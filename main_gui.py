

"""
GoCalc/main_gui.py
"""


####################################################################################################


import sys
import numpy as np

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ObjectProperty

from gui.contentpanels.gameboardpanel import GameBoardPanel
from gui.contentpanels.influencepanel import InfluencePanel
from gamelogic.board import Board
from gamelogic.player import Player


####################################################################################################


APP_DATA = {

    'board': None,
    'player': {'black': None, 'white': None},

    'default_window_size': [1000, 700],
    'board_size': 19,  # 9, 13, or 19
    'grid_star_size': 5,
    'grid_star_coords': {
        9: [[2, 2], [2, 6], [4, 4], [6, 2], [6, 6]],
        13: [[3, 3], [3, 9], [6, 6], [9, 3], [9, 9]],
        19: [[3, 3], [3, 9], [3, 15], [9, 3], [9, 9], [9, 15], [15, 3], [15, 9], [15, 15]]
    },
    'game_board': {
        'panel_location': 'scroll',  # 'stationary', 'scroll', or 'unselected'
        'mode': 'edit',  # 'edit' or 'play'
        'edit_mode': 'alternate',  # 'alternate' or 'consecutive'
        'next_stone': 'black',  # 'black' or 'white'
    },
    'influence': {
        'panel_location': 'scroll',  # 'stationary', 'scroll', or 'unselected'
        'display_mode': 'cur_infl',  # 'cur_infl' or 'infl_pred'
        'predicting_stone': 'black',  # 'black' or 'white'
        'display_stones': 'yes',  # 'yes' or 'no'
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
                'min': 1.0, 'max': 20.0, 'value': 8.0,
            },
            'clamp_within': {
                'min': 0.0, 'max': 20.0, 'value': 3.8,
            },
        }
    }
    ### TODO
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



        """ TESTING / DEBUGGING >>> """

        infl_panel = self.content_scroll.influence_panel

        coord = [12, 16]
        # char = "A"

        self.test_button = infl_panel.display.buttons[str(coord)]

        Window.bind(on_key_down=self.keyboardInput)

    def keyboardInput(self, obj, num1, num2, text, *args):
        if text == ' ':  self.spaceBarInput()
        elif text == 'x':  self.xKeyInput()

    def spaceBarInput(self):
        app = App.get_running_app()

        print("\n<><><>")

        # self.test_button.setCanvasToStone('white')
        # self.test_button.setCanvasToColor([1, 0, 0, 1])
        self.test_button.setCanvasToText("4")

        # from kivy.graphics import Color, Rectangle, Line, Ellipse
        # from kivy.core.text import Label as CoreLabel
        #
        # self.test_button.canvas.before.clear()
        # self.test_button.canvas.after.clear()
        # with self.test_button.canvas.before:
        #     self.test_button.board_rect_color = Color(*self.test_button.board_color)
        #     self.test_button.board_rect = Rectangle()
        # self.test_button.updateCanvas()
        #
        # core_label = CoreLabel(text="A", font_size=100, color=[0, 0, 0, 1])
        # core_label.refresh()
        # text_texture = core_label.texture
        #
        # with self.test_button.canvas.after:
        #     self.text_line_color = Color(0, 0, 0, 1)
        #     self.text_line = Line()
        #     self.test_button.text_label = Rectangle(texture=text_texture)
        # self.test_button.text_label.pos = self.test_button.pos
        # self.test_button.text_label.size = self.test_button.size
        # self.text_line.rectangle = [*self.test_button.pos, *self.test_button.size]

        print("space bar pressed ... \_(**)_/")
        print("<><><>")

    def xKeyInput(self):

        print("\n<><><>")

        # self.test_button.setCanvasToDefault()
        self.test_button.setCanvasToColor([1, 0, 0, 1])

        # self.test_button.canvas.before.clear()
        # self.test_button.canvas.after.clear()
        # self.test_button.setAndAddCanvasBeforeObjects()
        # self.test_button.setAndAddCanvasAfterObjects()
        # self.test_button.updateCanvas()

        print("x key pressed ... \_(**)_/")
        print("<><><>")

        """ <<< TESTING / DEBUGGING """



class MainMenuBar (BoxLayout):
    button_width = NumericProperty()

    def __init__(self):
        super(MainMenuBar, self).__init__()
        self.app = App.get_running_app()

        """ Main buttons currently not functional. """
        self.main_button = Button(text='main', size_hint=[None, 1.0], width=self.button_width)
        self.add_widget(self.main_button)
        self.options_button = Button(text='options', size_hint=[None, 1.0], width=self.button_width)
        self.add_widget(self.options_button)
        self.help_button = Button(text='help', size_hint=[None, 1.0], width=self.button_width)
        self.add_widget(self.help_button)

    def doStuff(self, *args, **kwargs):
        print(self.app.main)
        self.app.main.content_scroll.infl_calc_panel.display.height = self.app.main.content_scroll.game_board_panel.display.height



class ContentScroll (ScrollView):
    layout = ObjectProperty()

    def __init__(self):
        super(ContentScroll, self).__init__()

        self.game_board_panel = GameBoardPanel()
        self.layout.add_widget(self.game_board_panel)

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
