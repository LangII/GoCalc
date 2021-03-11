
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.splitter import Splitter

from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from kivy.graphics import Color, Rectangle, Line, Ellipse

from gui.contentbasewidgets import (
    ContentPanel, PanelSettings, PanelSettingsInput, PanelStationarySettings,
    PanelSettingsSingleLabel
)

import messenger

####################################################################################################

class GameBoardPanel (ContentPanel):
    board_size = NumericProperty()
    grid_star_size = NumericProperty()

    def __init__(self):
        super(GameBoardPanel, self).__init__(title="Game Board")
        self.app = App.get_running_app()
        self.board_size = self.app.data['board_size']
        self.grid_star_size = self.app.data['grid_star_size']

        # Override ContentPanel attr (GameBoardPanel is unique).
        self.title_label.halign = 'center'
        self.close_button.parent.remove_widget(self.close_button)

        self.display = GameBoardDisplay()
        self.add_widget(self.display)

        self.display.bind(height=self.displayHeightChange)

        """ Need to implement a no scroll section. """
        # self.captures_display = CapturesDisplay()
        # self.add_widget(self.captures_display)



        self.stationary_settings = PanelStationarySettings()
        self.captures_display = CapturesDisplay()
        self.stationary_settings.add_widget(self.captures_display)
        self.add_widget(self.stationary_settings)

        self.add_widget(PanelSettingsSingleLabel('settings'))



        self.settings = PanelSettings()
        self.add_widget(self.settings)

        # self.captures_display = CapturesDisplay()
        # self.settings.layout.add_widget(self.captures_display)

        self.mode_input = GameBoardModeInput()
        self.settings.layout.add_widget(self.mode_input)

        self.edit_mode_input = GameBoardEditModeInput()
        self.settings.layout.add_widget(self.edit_mode_input)

        self.next_stone_input = GameBoardNextStoneInput()
        self.settings.layout.add_widget(self.next_stone_input)

        ### Leaving in for future gui responsiveness debugging.
        # for i in range(20):
        #     self.settings.layout.add_widget(Label(text=f'{i + 1}', size_hint=[1.0, None], height=20))

    def displayHeightChange(self, obj, value):
        self.width = value



class GameBoardDisplay (Splitter):
    board_size = NumericProperty()
    grid_star_size = NumericProperty()
    layout = ObjectProperty()

    def __init__(self):
        super(GameBoardDisplay, self).__init__()
        self.app = App.get_running_app()
        self.sizable_from = 'bottom'
        self.board_size = self.app.data['board_size']
        self.grid_star_size = self.app.data['grid_star_size']
        self.buttons = self.getAndAddButtons()

    def getAndAddButtons(self):
        buttons = {}
        for i in range(self.layout.cols ** 2):
            coord = [i // self.board_size, i % self.board_size]
            button = GameBoardButton(coord)
            self.layout.add_widget(button)
            buttons[str(coord)] = button
        return buttons



class GameBoardButton (ButtonBehavior, Widget):
    board_color = ListProperty()
    no_stone_color = ListProperty([0, 0, 0, 0])
    black_stone_color = ListProperty()
    white_stone_color = ListProperty()
    board_size = NumericProperty()
    grid_star_size = NumericProperty()

    def __init__(self, coord):
        super(GameBoardButton, self).__init__()
        self.app = App.get_running_app()
        self.board_size = self.app.data['board_size']
        self.size_hint = [1 / self.board_size, 1 / self.board_size]
        self.grid_star_size = self.app.data['grid_star_size']
        self.grid_star_coords = self.app.data['grid_star_coords']
        self.coord = coord

        self.size = [30, 30]

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
        line_type = self.grid_hor_line_type
        pos_x, pos_y = self.board_rect.pos
        size_x, size_y = self.board_rect.size
        x1 = pos_x if line_type in ['center', 'right'] else pos_x + (size_x / 2)
        x2 = pos_x + size_x if line_type in ['center', 'left'] else pos_x + (size_x / 2)
        y1, y2 = [pos_y + (size_y / 2)] * 2
        return [x1, y1, x2, y2]

    def getVertLinePoints(self):
        line_type = self.grid_vert_line_type
        pos_x, pos_y = self.board_rect.pos
        size_x, size_y = self.board_rect.size
        y1 = pos_y + size_y if line_type in ['center', 'bottom'] else pos_y + (size_y / 2)
        y2 = pos_y if line_type in ['center', 'top'] else pos_y + (size_y / 2)
        x1, x2 = [pos_x + (size_x / 2)] * 2
        return [x1, y1, x2, y2]

    def getGridStarPos(self):
        pos_x = (self.pos[0] + (self.size[0] / 2)) - (self.grid_star.size[0] / 2)
        pos_y = (self.pos[1] + (self.size[1] / 2)) - (self.grid_star.size[1] / 2)
        return pos_x, pos_y

    def getStoneLineCircleArgs(self):
        return [self.center_x, self.center_y, self.width / 2]

    def on_release(self):
        move_legality = messenger.updateLogicBoardWithStone(self.coord)
        if move_legality == 'illegal':  return
        else:  self.updateNextStoneValues()

        # self.app.data['board'].prettyPrint()

    def updateNextStoneValues(self):
        next_stone_input = self.parent.parent.parent.next_stone_input
        if self.app.data['game_board']['edit_mode'] == 'alternate':
            if self.app.data['game_board']['next_stone'] == 'black':
                self.app.data['game_board']['next_stone'] = 'white'
                next_stone_input.value = 'white'
                next_stone_input.white_button.state = 'down'
                next_stone_input.black_button.state = 'normal'
            elif self.app.data['game_board']['next_stone'] == 'white':
                self.app.data['game_board']['next_stone'] = 'black'
                next_stone_input.value = 'black'
                next_stone_input.black_button.state = 'down'
                next_stone_input.white_button.state = 'normal'



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



class GameBoardModeInput (PanelSettingsInput):

    def __init__(self):
        super(GameBoardModeInput, self).__init__("game mode")
        self.app = App.get_running_app()
        self.value = self.app.data['game_board']['mode']
        self.options = BoxLayout(orientation='horizontal', size_hint=[1.0, None], height=20)
        self.play_button = ToggleButton(text="play", group='game_board_mode', font_size=13)
        self.edit_button = ToggleButton(text="edit", group='game_board_mode', font_size=13)
        self.play_button.allow_no_selection = False
        self.edit_button.allow_no_selection = False
        self.options.add_widget(self.play_button)
        self.options.add_widget(self.edit_button)
        self.add_widget(self.options)

        if self.value == 'edit':  self.edit_button.state = 'down'
        elif self.value == 'play':  self.play_button.state = 'down'

        self.play_button.bind(on_release=self.playButtonPressed)
        self.edit_button.bind(on_release=self.editButtonPressed)

    def playButtonPressed(self, *largs):
        self.app.data['game_board']['mode'] = 'play'
        self.value = 'play'

    def editButtonPressed(self, *largs):
        self.app.data['game_board']['mode'] = 'edit'
        self.value = 'edit'



class GameBoardEditModeInput (PanelSettingsInput):

    def __init__(self):
        super(GameBoardEditModeInput, self).__init__("edit mode")
        self.app = App.get_running_app()
        self.value = self.app.data['game_board']['edit_mode']
        self.options = BoxLayout(orientation='horizontal', size_hint=[1.0, None], height=20)
        self.alternate_button = ToggleButton(
            text="alternate", group='game_board_edit_mode', font_size=13
        )
        self.consecutive_button = ToggleButton(
            text="consecutive", group='game_board_edit_mode', font_size=13
        )
        self.alternate_button.allow_no_selection = False
        self.consecutive_button.allow_no_selection = False
        self.options.add_widget(self.alternate_button)
        self.options.add_widget(self.consecutive_button)
        self.add_widget(self.options)

        if self.value == 'alternate':  self.alternate_button.state = 'down'
        elif self.value == 'consecutive':  self.consecutive_button.state = 'down'

        self.alternate_button.bind(on_release=self.alternateButtonPressed)
        self.consecutive_button.bind(on_release=self.consecutiveButtonPressed)

    def alternateButtonPressed(self, *largs):
        self.app.data['game_board']['edit_mode'] = 'alternate'
        self.value = 'alternative'

    def consecutiveButtonPressed(self, *largs):
        self.app.data['game_board']['edit_mode'] = 'consecutive'
        self.value = 'consecutive'


class GameBoardNextStoneInput (PanelSettingsInput):

    def __init__(self):
        super(GameBoardNextStoneInput, self).__init__("next stone")
        self.app = App.get_running_app()
        self.value = self.app.data['game_board']['next_stone']
        self.options = BoxLayout(orientation='horizontal', size_hint=[1.0, None], height=20)

        self.black_button = ToggleButton(text="black", group='game_board_next_stone', font_size=13)
        self.white_button = ToggleButton(text="white", group='game_board_next_stone', font_size=13)
        self.black_button.allow_no_selection = False
        self.white_button.allow_no_selection = False
        self.options.add_widget(self.black_button)
        self.options.add_widget(self.white_button)
        self.add_widget(self.options)

        if self.value == 'black':  self.black_button.state = 'down'
        elif self.value == 'white':  self.white_button.state = 'down'

        self.black_button.bind(on_release=self.blackButtonPressed)
        self.white_button.bind(on_release=self.whiteButtonPressed)

    def blackButtonPressed(self, *largs):
        self.app.data['game_board']['next_stone'] = 'black'
        self.value = 'black'

    def whiteButtonPressed(self, *largs):
        self.app.data['game_board']['next_stone'] = 'white'
        self.value = 'white'
