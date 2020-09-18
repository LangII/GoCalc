
"""
GoCalc/ui/main.py
"""

"""
possible app names:
    (dentaku(calculator))
    (suji(development of the stones) dentaku(calculator))
    (dentaku(calculator) go(game))
    (keisansuru(calculate) go(game))
"""

import os, sys
cur_dir = os.getcwd()
insert_sys_path = cur_dir[:cur_dir.rfind('\\')]
sys.path.insert(1, insert_sys_path)

from kivy.app import App
from kivy.core.window import Window

from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button, ButtonBehavior
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
        super(MainWindow, self).__init__()
        self.main_menu_bar = MainMenuBar()
        self.add_widget(self.main_menu_bar)
        self.content = ContentScroll()
        self.add_widget(self.content)



class MainMenuBar(BoxLayout):
    button_width = NumericProperty()

    def __init__(self):
        super(MainMenuBar, self).__init__()

        """ TEMPORARY / FOR DISPLAY PURPOSES """
        for button_title in ['main', 'options', 'help']:
            self.add_widget(Button(
                text=button_title, size_hint=[None, 1.0], width=self.button_width
            ))



class ContentScroll(ScrollView):
    layout = ObjectProperty()

    def __init__(self):
        super(ContentScroll, self).__init__()

        self.layout.add_widget(PlayBoardPanel())

        """ TEMPORARY / FOR DISPLAY PURPOSES """
        for i in range(20):
            self.layout.add_widget(Button(
                text=str(i), width=100, size_hint=[None, 1.0]
            ))



class ContentPanel(BoxLayout):
    title_label = ObjectProperty()
    panel_title_text = StringProperty()
    close_button = ObjectProperty()

    def __init__(self, title=''):
        super(ContentPanel, self).__init__()
        self.panel_title_text = title
        self.close_button.bind(on_press=self.closeButtonPressed)

        self.add_widget(ContentPanelMenuBar())

    def closeButtonPressed(self, button_state):
        print(self.panel_title)



class ContentPanelMenuBar(BoxLayout):
    button_size_hint = ListProperty()

    def __init__(self):
        super(ContentPanelMenuBar, self).__init__()

        self.move_left_button = Button(text='<', size_hint=self.button_size_hint)
        self.lock_toggle_button = Button(text='<<', size_hint=self.button_size_hint)
        self.window_toggle_button = Button(text='[< >]', size_hint=self.button_size_hint)
        self.move_right_button = Button(text='>', size_hint=self.button_size_hint)

        self.add_widget(self.move_left_button)
        self.add_widget(self.lock_toggle_button)
        self.add_widget(self.window_toggle_button)
        self.add_widget(self.move_right_button)



class PlayBoardPanel(ContentPanel):

    def __init__(self):
        super(PlayBoardPanel, self).__init__(title='Play Board')
        self.title_label.halign = 'center'
        self.close_button.parent.remove_widget(self.close_button)

        self.play_board = PlayBoardDisplay()
        self.add_widget(self.play_board)
        self.add_widget(Label(text='temp panel text', size_hint=[1.0, 1.0]))



class PlayBoardDisplay(GridLayout):
    board_size = NumericProperty(BOARD_SIZE)

    def __init__(self):
        super(PlayBoardDisplay, self).__init__()
        self.spacing = 0
        self.pos_buttons = self.getPosButtons()
        self.addPosButtons()



    def getPosButtons(self):
        pos_buttons = []
        for each in range(self.cols ** 2):
            button = BoardPosButton()
            pos_buttons += [ button ]
        return pos_buttons

    def addPosButtons(self):
        for pos_button in self.pos_buttons:
            self.add_widget(pos_button)
            # pos_button.size_hint = [1 / self.board_size, 1 / self.board_size]
            # pos_button.initCanvasDraw()
            # with pos_button.canvas:
            #     Color(.8, .8, .1, 1)
            #     Rectangle(
            #         # size_hint=[1 / self.board_size, 1 / self.board_size],
            #         # size_hint=[None, None],
            #         # pos_hint=[None, None],
            #         size=pos_button.size,
            #         pos=pos_button.pos
            #     )
            # pos_button.bind(pos=pos_button.update_rectangle, size=pos_button.update_rectangle)



class BoardPosButton(ButtonBehavior, Widget):
# class BoardPosButton(Widget):
# class BoardPosButton(Button):
    board_size = NumericProperty(BOARD_SIZE)
    # button_color = ListProperty([1, 1, 0, 1])
    # pos_state = StringProperty()
    # stone_state = StringProperty()
    def __init__(self):
        super(BoardPosButton, self).__init__()
        self.size_hint = [1 / self.board_size, 1 / self.board_size]
        self.cur_color = [1, 1, 0, 1]

    # def initCanvasDraw(self):
        # self.canvas.clear()
        with self.canvas:
            # this = [1, 1, 0, 1] if self.state == 'normal' else [1, 1, 0, 1]
            self.color = Color(1, 1, 0, 1)
            self.rect = Rectangle(
                # size_hint=[1 / self.board_size, 1 / self.board_size],
                # size_hint=[None, None],
                # pos_hint=[None, None],
                size=self.size,
                pos=self.pos
            )
        self.bind(pos=self.updateRect, size=self.updateRect)

        # print(type(self.parent))
        print(self.pos)

    def updateRect(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_release(self):
        self.color.rgba = [1, 0, 0, 1]
        print("button pressed")




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
