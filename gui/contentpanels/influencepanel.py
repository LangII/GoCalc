
from kivy.app import App
# from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import ButtonBehavior, Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.togglebutton import ToggleButton
from kivy.uix.splitter import Splitter

from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from kivy.graphics import Color, Rectangle, Line, Ellipse

from gui.contentbasewidgets import (
    ContentPanel, PanelSettings, PanelSettingsInput, PanelSettingsSingleButton
)

# import calculate.taxicabinflcalc as tci_calc

import calculate.influencecalc as infl

import messenger

####################################################################################################

class InfluencePanel (ContentPanel):
    board_size = NumericProperty()
    grid_star_size = NumericProperty()

    def __init__(self, **kwargs):
        super(InfluencePanel, self).__init__(title="Influence Calc")
        self.app = App.get_running_app()
        self.board_size = self.app.data['board_size']
        self.grid_star_size = self.app.data['grid_star_size']

        self.display = DataBoardDisplay()
        self.add_widget(self.display)

        self.display.bind(height=self.displayHeightChange)

        self.settings = PanelSettings()
        self.add_widget(self.settings)

        self.refresh = Refresh()
        self.settings.layout.add_widget(self.refresh)

        self.weights_title = WeightsTitle()
        self.settings.layout.add_widget(self.weights_title)

        for i in range(20):
            self.settings.layout.add_widget(Label(text=f'{i + 1}', size_hint=[1.0, None], height=20))

    def displayHeightChange(self, obj, value):
        self.width = value



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
            self.stone_line_color = Color(0, 0, 0, 0)
            self.stone_line = Line()

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
        if self.grid_star:  self.grid_star.pos = self.getGridStarPos()
        self.stone.pos = self.pos
        self.stone.size = self.size
        self.stone_line.circle = self.getStoneLineCircleArgs()

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

    def getGridStarPos(self):
        pos_x = (self.pos[0] + (self.size[0] / 2)) - (self.grid_star.size[0] / 2)
        pos_y = (self.pos[1] + (self.size[1] / 2)) - (self.grid_star.size[1] / 2)
        return pos_x, pos_y

    def getStoneLineCircleArgs(self):
        return [self.center_x, self.center_y, self.width / 2]



class WeightsTitle (Label):

    def __init__(self):
        super(WeightsTitle, self).__init__()
        self.app = App.get_running_app()
        self.text = "WEIGHTS"



class Refresh (PanelSettingsSingleButton):

    def __init__(self):
        super(Refresh, self).__init__("refresh")
        self.app = App.get_running_app()
        self.bind(on_release=self.triggerRefresh)

    def triggerRefresh(self, *args):
        display_buttons = self.app.main.content_scroll.influence_panel.display.buttons
        # infl_grid = tci_calc.getStoneRawInfluenceGrid([4, 4])

        # infl_grid = tci_calc.getWholeBoardRawInfluenceGrid()

        infl_grid = infl.getBoardInfluence(self.app.data['board'])

        # print("")
        # for row in infl_grid:  print([ f"{r:05.02f}" for r in row ])

        # print("\n\n\n")
        # print(tci_calc.getWholeBoardRawInfluenceGrid(to_print=True))
        for y, row in enumerate(infl_grid):
            # print(row)
            for x, each in enumerate(row):
                # print("each =", each)
                # print(display_buttons[str([x, y])])

                if each > 0:
                    display_buttons[str([y, x])].board_rect_color.rgba = [1- (each / 100), 1 - (each / 100), 1, 1]
                if each < 0:
                    each = abs(each)
                    display_buttons[str([y, x])].board_rect_color.rgba = [1, 1- (each / 100), 1 - (each / 100), 1]
                if each == 0:
                    display_buttons[str([y, x])].board_rect_color.rgba = [1, 1, 1, 1]

                # if each > 0:
                #     display_buttons[str([y, x])].board_rect_color.rgba = [1 - (each), 1 - (each), 1, 1]
                # if each < 0:
                #     each = abs(each)
                #     display_buttons[str([y, x])].board_rect_color.rgba = [1, 1 - (each), 1 - (each), 1]
                # if each == 0:
                #     display_buttons[str([y, x])].board_rect_color.rgba = [1, 1, 1, 1]
