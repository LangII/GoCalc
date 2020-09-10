

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

        Window.bind(mouse_pos=self.on_mouse_pos)

        self.orientation = 'horizontal'

        self.board_display = BoardDisplay()

        self.add_widget(self.board_display)
        self.add_widget(Button(text='button 2'))

    def on_mouse_pos(self, window, pos):
        for button in self.board_display.pos_buttons:
            if button.collide_point(*pos):
                print(button.text)

class BoardDisplay(GridLayout):
    def __init__(self):
        super().__init__()
        self.cols = BOARD_SIZE
        self.size = [500, 500]
        self.size_hint = [None, None]
        self.pos_buttons = self.getPosButtons()
        self.addPosButtons()

    def getPosButtons(self):
        pos_buttons = []
        for each in range(self.cols ** 2):
            button = Button(text='pos{}'.format(str(each + 1).rjust(2, '0')), size_hint=[1/9, 1/9])
            pos_buttons += [ button ]
        return pos_buttons

    def addPosButtons(self):
        for pos_button in self.pos_buttons:  self.add_widget(pos_button)



####################################################################################################

def presets():
    Window.size = [PRESET_WINDOW_WIDTH, PRESET_WINDOW_HEIGHT]

####################################################################################################

main()
