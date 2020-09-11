
"""
GoCalc/main_ui.py
"""

import kivy
from kivy.app import App
from kivy.core.window import Window

from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

####################################################################################################

PRESET_WINDOW_WIDTH = 800
PRESET_WINDOW_HEIGHT = 500

GREY_SCALE = 0.5
GREY = [*[GREY_SCALE] * 3, 1]
DARK_PRISMARINE = [0.0, 0.2, 0.2, 1]

BACKGROUND_COLOR = DARK_PRISMARINE

BOARD_SIZE = 9

####################################################################################################

def main():

    presets()

    GoCalcApp().run()

    exit()

####################################################################################################



class GoCalcApp(App):
    def build(self):
        self.root = MainWindow()
        # with self.root.canvas:
        #     Color(rgba=(.1, 1, .1))
        #     Rectangle(size=self.root.size, pos=self.root.pos)
        return self.root



class MainWindow(BoxLayout):
    def __init__(self):
        super().__init__()

        self.width = PRESET_WINDOW_WIDTH
        self.height = PRESET_WINDOW_HEIGHT

        """ mouse over """
        # Window.bind(mouse_pos=self.onMousePos)

        # self.canvas = Color(0, 0, 0, 1)
        self.orientation = 'vertical'

        self.add_widget(Button(size_hint=[None, 0.1]))

        self.content_scroll = ContentScroll()
        self.add_widget(self.content_scroll)

    """ mouse over """
    # def onMousePos(self, window, pos):
    #     for button in self.board_display.pos_buttons:
    #         if button.collide_point(*pos):
    #             print(button.text)



class MenuBar(BoxLayout):
    def __init__(self):
        super().__init__()




class ContentScroll(ScrollView):
    def __init__(self):
        super().__init__()
        self.size_hint = [1.0, 1.0]
        self.do_scroll_x = True
        self.do_scroll_y = False

        self.layout = BoxLayout(orientation='horizontal', size_hint=[None, None])
        self.layout.bind(minimum_width=self.layout.setter('width'))

        for i in range(20):
            self.layout.add_widget(Button(
                text=str(i), size=[100, 100], size_hint=[None, None]
            ))

        self.add_widget(self.layout)



# class BoardDisplay(GridLayout):
#     def __init__(self):
#         super().__init__()
#         self.cols = BOARD_SIZE
#         # self.size = [500, 500]
#         # self.size_hint = [0.5, None]
#         self.height = self.width
#         self.pos_buttons = self.getPosButtons()
#         self.addPosButtons()
#
#     def getPosButtons(self):
#         pos_buttons = []
#         for each in range(self.cols ** 2):
#             button = Button(
#                 text='pos{}'.format(str(each + 1).rjust(2, '0')),
#                 size_hint=[1/9, 1/9]
#             )
#             pos_buttons += [ button ]
#         return pos_buttons
#
#     def addPosButtons(self):
#         for pos_button in self.pos_buttons:  self.add_widget(pos_button)



####################################################################################################

def presets():
    Window.size = [PRESET_WINDOW_WIDTH, PRESET_WINDOW_HEIGHT]
    Window.clearcolor = BACKGROUND_COLOR

####################################################################################################

main()
