
"""
GoCalc/main_ui.py
"""

import kivy
from kivy.app import App
from kivy.core.window import Window

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

####################################################################################################

PRESET_WINDOW_WIDTH = 800
PRESET_WINDOW_HEIGHT = 500

BOARD_SIZE = 9

####################################################################################################

def main():

    presets()

    GoCalcApp().run()

    exit()

####################################################################################################

class GoCalcApp(App):
    def build(self):
        return MainWindow()

class MainWindow(BoxLayout):
    def __init__(self):
        super().__init__()
        self.orientation = 'horizontal'

        # self.add_widget(Button(text='button1', size_hint=(0.8, None)))
        # self.add_widget(Button(text='button 1', size=[500, 500], size_hint=[None, None]))
        self.add_widget(BoardDisplay())
        self.add_widget(Button(text='button 2'))

class BoardDisplay(GridLayout):
    def __init__(self):
        super().__init__()
        self.cols = BOARD_SIZE
        self.size = [500, 500]
        self.size_hint = [None, None]

        for each in range(BOARD_SIZE ** 2):
            self.add_widget(Button(
                text='pos{}'.format(str(each + 1).rjust(2, '0')), size_hint=[1/9, 1/9]
            ))



####################################################################################################

def presets():
    Window.size = [PRESET_WINDOW_WIDTH, PRESET_WINDOW_HEIGHT]

####################################################################################################

main()
