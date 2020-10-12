
from kivy.app import App
# from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.uix.label import Label
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.togglebutton import ToggleButton
from kivy.uix.splitter import Splitter

from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from kivy.graphics import Color, Rectangle, Line, Ellipse

from gui.contentbasewidgets import ContentPanel, PanelSettings, PanelSettingsInput

import messenger

####################################################################################################

class InflCalcPanel (ContentPanel):
    board_size = NumericProperty()
    grid_star_size = NumericProperty()

    def __init__(self, **kwargs):
        super(InflCalcPanel, self).__init__(title="Influence Calculator")
        self.app = App.get_running_app()
        self.board_size = self.app.data['board_size']
        self.grid_star_size = self.app.data['grid_star_size']

        self.display = DataBoardDisplay()
        self.add_widget(self.display)

        self.display.bind(height=self.displayHeightChange)

        self.captures_display = CapturesDisplay()
        self.add_widget(self.captures_display)
        self.remove_widget(self.captures_display)

        self.settings = PanelSettings()
        self.add_widget(self.settings)

        for i in range(20):
            self.settings.layout.add_widget(Label(text=f'{i + 1}', size_hint=[1.0, None], height=20))

        # self.do_once = True

        # print(self.display.height)

    def displayHeightChange(self, obj, value):
        self.width = value
        # if self.do_once:
        #     self.do_once = False
        #     self.

    # def on_parent(self, obj, parent):
    #     print(self.display.height)



class DataBoardDisplay (Splitter):
    board_size = NumericProperty()
    grid_star_size = NumericProperty()
    layout = ObjectProperty()

    def __init__(self):
        super(DataBoardDisplay, self).__init__()
        self.app = App.get_running_app()
        self.sizable_from='bottom'
        self.board_size = self.app.data['board_size']
        self.grid_star_size = self.app.data['grid_star_size']
        self.buttons = self.getAndAddButtons()

        # self.width = self.app.main.content_scroll.game_board_panel.width
        # self.width = 200

    # def on_kv_post(self, *args, **kwargs):
    #     self.width = 200

    def getAndAddButtons(self):
        buttons = {}
        for i in range(self.layout.cols ** 2):
            coord = [i // self.board_size, i % self.board_size]
            button = DataBoardButton(coord)
            self.layout.add_widget(button)
            buttons[str(coord)] = button
        return buttons

class DataBoardButton (ButtonBehavior, Widget):
    board_color = ListProperty()
    no_stone_color = ListProperty([0, 0, 0, 0])
    black_stone_color = ListProperty()
    white_stone_color = ListProperty()
    board_size = NumericProperty()
    grid_star_size = NumericProperty()

    def __init__(self, coord):
        super(DataBoardButton, self).__init__()
        self.app = App.get_running_app()
        self.board_size = self.app.data['board_size']
        self.size_hint = [1 / self.board_size, 1 / self.board_size]
        self.grid_star_size = self.app.data['grid_star_size']
        self.grid_star_coords = self.app.data['grid_star_coords']
        self.coord = coord

        self.grid_hor_line_type = self.getHorLineType()
        self.grid_vert_line_type = self.getVertLineType()
        self.setAndAddCanvasBeforeObjects()
        self.setAndAddCanvasAfterObjects()

        self.bind(pos=self.updateCanvas, size=self.updateCanvas)

    def setAndAddCanvasBeforeObjects(self):
        with self.canvas.before:
            self.board_rect_color = Color(*self.board_color)
            self.board_rect = Rectangle()
            self.grid_hor_line_color = Color(0, 0, 0, 1)
            self.grid_hor_line = Line()
            self.grid_vert_line_color = Color(0, 0, 0, 1)
            self.grid_vert_line = Line()
            self.grid_star = self.getGridStar()

    def setAndAddCanvasAfterObjects(self):
        with self.canvas.after:
            self.stone_color = Color(*self.no_stone_color)
            self.stone = Ellipse(size=self.size)

    def getHorLineType(self):
        if self.coord[1] == 0:  return 'left'
        elif self.coord[1] == self.board_size - 1:  return 'right'
        else:  return 'center'

    def getVertLineType(self):
        if self.coord[0] == 0:  return 'top'
        elif self.coord[0] == self.board_size - 1:  return 'bottom'
        else:  return 'center'

    def getGridStar(self):
        if self.coord not in self.grid_star_coords[self.board_size]:  return None
        else:  return Ellipse(size=[self.grid_star_size] * 2)

    def updateCanvas(self, instance, value):
        self.board_rect.pos = self.pos
        self.board_rect.size = self.size
        self.grid_hor_line.points = self.getHorLinePoints()
        self.grid_vert_line.points = self.getVertLinePoints()
        if self.grid_star:
            pos_x = (self.pos[0] + (self.size[0] / 2)) - (self.grid_star.size[0] / 2)
            pos_y = (self.pos[1] + (self.size[1] / 2)) - (self.grid_star.size[1] / 2)
            self.grid_star.pos = pos_x, pos_y
        self.stone.pos = self.pos
        self.stone.size = self.size

    def getHorLinePoints(self):
        type = self.grid_hor_line_type
        pos_x, pos_y = self.board_rect.pos
        size_x, size_y = self.board_rect.size

        x1 = pos_x if type in ['center', 'right'] else pos_x + (size_x / 2)
        x2 = pos_x + size_x if type in ['center', 'left'] else pos_x + (size_x / 2)
        y1, y2 = [pos_y + (size_y / 2)] * 2

        return [x1, y1, x2, y2]

    def getVertLinePoints(self):
        type = self.grid_vert_line_type
        pos_x, pos_y = self.board_rect.pos
        size_x, size_y = self.board_rect.size

        y1 = pos_y + size_y if type in ['center', 'bottom'] else pos_y + (size_y / 2)
        y2 = pos_y if type in ['center', 'top'] else pos_y + (size_y / 2)
        x1, x2 = [pos_x + (size_x / 2)] * 2

        return [x1, y1, x2, y2]





class CapturesDisplay (Label):
    def __init__(self):
        super(CapturesDisplay, self).__init__()
        self.app = App.get_running_app()
        self.black_captures = 0
        self.white_captures = 0
        self.template = "black:  {}        white:  {}"
        self.text = self.template.format(self.black_captures, self.white_captures)

    def updateText(self):
        self.black_captures = self.app.data['player']['black'].captures
        self.white_captures = self.app.data['player']['white'].captures
        self.text = self.template.format(self.black_captures, self.white_captures)
