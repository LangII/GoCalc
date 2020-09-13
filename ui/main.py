
"""
GoCalc/ui/main.py
"""

import os, sys
cur_dir = os.getcwd()
insert_sys_path = cur_dir[:cur_dir.rfind('\\')]
sys.path.insert(1, insert_sys_path)

from kivy.app import App
from kivy.core.window import Window

from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from kivy.properties import NumericProperty, StringProperty, ListProperty, ObjectProperty
from kivy.graphics import Color, Rectangle

####################################################################################################

DEFAULT_WINDOW_SIZE = DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT = 800, 500

BOARD_SIZE = 9

####################################################################################################

def main():

    doBeforeStart()

    GoCalcApp().run()

    exit()

####################################################################################################

def doBeforeStart():
    Window.size = DEFAULT_WINDOW_SIZE

####################################################################################################



class GoCalcApp(App):
    def build(self):
        return MainWindow()



class MainWindow(BoxLayout):
    def __init__(self):
        super().__init__()
        self.main_menu_bar = MainMenuBar()
        self.add_widget(self.main_menu_bar)
        self.content = ContentScroll()
        self.add_widget(self.content)



class MainMenuBar(BoxLayout):
    button_width = NumericProperty()
    def __init__(self):
        super().__init__()

        """ TEMPORARY / FOR DISPLAY PURPOSES """
        for button_title in ['main', 'options', 'help']:
            self.add_widget(Button(
                text=button_title, size_hint=[None, 1.0], width=self.button_width
            ))



class ContentScroll(ScrollView):
    layout = ObjectProperty()
    def __init__(self):
        super().__init__()

        for _ in range(3):  self.layout.add_widget(MainBoardPanel())

        """ TEMPORARY / FOR DISPLAY PURPOSES """
        for i in range(20):
            self.layout.add_widget(Button(
                text=str(i), width=100, size_hint=[None, 1.0]
            ))



class ContentPanel(BoxLayout):
    panel_title = StringProperty()
    def __init__(self, title=''):
        super().__init__()

        self.panel_title = title

        self.add_widget(ContentPanelMenuBar())



class ContentPanelMenuBar(BoxLayout):
    button_size_hint = ListProperty()
    def __init__(self):
        super().__init__()

        self.move_left_button = Button(text='<', size_hint=self.button_size_hint)
        self.lock_toggle_button = Button(text='<<', size_hint=self.button_size_hint)
        self.window_toggle_button = Button(text='[< >]', size_hint=self.button_size_hint)
        self.move_right_button = Button(text='>', size_hint=self.button_size_hint)

        self.add_widget(self.move_left_button)
        self.add_widget(self.lock_toggle_button)
        self.add_widget(self.window_toggle_button)
        self.add_widget(self.move_right_button)



class MainBoardPanel(ContentPanel):
    def __init__(self):
        super().__init__(title='play board')
        self.add_widget(BoardDisplay())
        self.add_widget(Label(text='temp panel text', size_hint=[1.0, 1.0]))



class BoardDisplay(GridLayout):
    board_size = NumericProperty(BOARD_SIZE)
    def __init__(self):
        super().__init__()
        self.spacing = 0
        self.pos_buttons = self.getPosButtons()
        self.addPosButtons()

    def getPosButtons(self):
        pos_buttons = []
        for each in range(self.cols ** 2):
            button = Button(
                # text=str(each),
                size_hint=[1/9, 1/9]
            )
            pos_buttons += [ button ]
        return pos_buttons

    def addPosButtons(self):
        for pos_button in self.pos_buttons:  self.add_widget(pos_button)



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
