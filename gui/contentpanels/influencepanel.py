

"""
GoCalc/gui/contentpanels/influencepanel.py
"""


####################################################################################################


from kivy.app import App
from kivy.uix.button import ButtonBehavior, Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.splitter import Splitter
from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from kivy.graphics import Color, Rectangle, Line, Ellipse

from gui.contentbasewidgets import (
    ContentPanel, PanelSettings, PanelSettingsInput, PanelSettingsSingleButton,
    PanelSettingsSliderInput, PanelStationarySettings, PanelSettingsSingleLabel
)
import calculate.influencecalc as infl_calc
import messenger

from kivy.core.text import Label as CoreLabel


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

        self.stationary_settings = PanelStationarySettings()
        self.details_display = DetailsDisplay()
        self.stationary_settings.add_widget(self.details_display)
        self.refresh = Refresh()
        self.stationary_settings.add_widget(self.refresh)
        self.add_widget(self.stationary_settings)

        self.add_widget(PanelSettingsSingleLabel('settings'))

        self.settings = PanelSettings()
        self.add_widget(self.settings)

        self.display_mode = DisplayModeInput()
        self.settings.layout.add_widget(self.display_mode)

        self.display_stones = DisplayStonesInput()
        self.settings.layout.add_widget(self.display_stones)

        self.pred_stone = PredictionStoneInput()
        self.settings.layout.add_widget(self.pred_stone)

        self.pred_display_type = PredictionDisplayTypeInput()
        self.settings.layout.add_widget(self.pred_display_type)

        self.infl_adjs = InflAdjsInput()
        self.settings.layout.add_widget(self.infl_adjs)

        self.weights_title = PanelSettingsSingleLabel('weights')
        self.settings.layout.add_widget(self.weights_title)

        self.dist_decay_gt_weight_input = DistDecayGtWeightInput()
        self.settings.layout.add_widget(self.dist_decay_gt_weight_input)

        self.dist_decay_lin_weight_input = DistDecayLinWeightInput()
        self.settings.layout.add_widget(self.dist_decay_lin_weight_input)

        self.dist_zero_gt_weight_input = DistZeroGtWeightInput()
        self.settings.layout.add_widget(self.dist_zero_gt_weight_input)

        self.angle_decay_lt_weight_input = AngleDecayLtWeightInput()
        self.settings.layout.add_widget(self.angle_decay_lt_weight_input)

        self.angle_decay_lin_weight_input = AngleDecayLinWeightInput()
        self.settings.layout.add_widget(self.angle_decay_lin_weight_input)

        self.opp_angle_growth_angle_lt_weight_input = OppAngleGrowthAngleLtWeightInput()
        self.settings.layout.add_widget(self.opp_angle_growth_angle_lt_weight_input)

        self.opp_angle_growth_dist_lt_weight_input = OppAngleGrowthDistLtWeightInput()
        self.settings.layout.add_widget(self.opp_angle_growth_dist_lt_weight_input)

        self.opp_angle_growth_lin_weight_input = OppAngleGrowthLinWeightInput()
        self.settings.layout.add_widget(self.opp_angle_growth_lin_weight_input)

        self.clamp_within_weight_input = ClampWithinWeightInput()
        self.settings.layout.add_widget(self.clamp_within_weight_input)

        ### Leaving in for future gui responsiveness debugging.
        # for i in range(20):
        #     self.settings.layout.add_widget(Label(text=f'{i + 1}', size_hint=[1.0, None], height=20))

    def displayHeightChange(self, obj, value):
        self.width = value


####################################################################################################


class DataBoardDisplay (Splitter):
    board_size = NumericProperty()
    grid_star_size = NumericProperty()
    layout = ObjectProperty()

    def __init__(self):
        super(DataBoardDisplay, self).__init__()
        self.app = App.get_running_app()
        self.sizable_from = 'bottom'
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
        self.canvas_state = 'default'

        self.grid_hor_line_type = self.getHorLineType()
        self.grid_vert_line_type = self.getVertLineType()
        self.setAndAddCanvasBeforeObjects()
        self.setAndAddCanvasAfterObjects()

        self.bind(pos=self.refreshCanvas, size=self.refreshCanvas)

    def setAndAddCanvasBeforeObjects(self):
        self.canvas.before.clear()
        with self.canvas.before:
            self.board_rect_color = Color(*self.board_color)
            self.board_rect = Rectangle()

    def setAndAddCanvasAfterObjects(self):
        self.canvas.after.clear()
        with self.canvas.after:
            self.grid_line_color = Color(0, 0, 0, 1)
            self.grid_hor_line = Line()
            self.grid_vert_line = Line()
            self.grid_star_line = self.getGridStarLine()
            self.stone_color = Color(*self.no_stone_color)
            self.stone = Ellipse(size=self.size)
            self.stone_line_color = Color(0, 0, 0, 0)
            self.stone_line = Line()
            self.text_color = Color(0, 0, 0, 0)
            self.text_boarder_line = Line()
            self.text_rect = Rectangle()

    def refreshCanvas(self, *largs):
        self.board_rect.pos = self.pos
        self.board_rect.size = self.size
        self.grid_hor_line.points = self.getHorLinePoints()
        self.grid_vert_line.points = self.getVertLinePoints()
        if self.grid_star_line:  self.grid_star_line.pos = self.getGridStarPos()
        self.stone.pos = self.pos
        self.stone.size = self.size
        self.stone_line.circle = self.getStoneLineCircleArgs()
        self.text_boarder_line.rectangle = [*self.pos, *self.size]
        self.text_rect.pos = self.pos
        self.text_rect.size = self.size

    def setCanvasToDefault(self):
        self.board_rect_color.rgba = self.board_color
        self.grid_line_color.a = 1
        self.stone_color.rgba = self.no_stone_color
        self.stone_line_color.a = 0
        self.text_color.a = 0
        self.refreshCanvas()

    def setCanvasToStone(self, stone):
        self.board_rect_color.rgba = self.board_color
        self.grid_line_color.a = 0
        if stone == 'black':  self.stone_color.rgba = self.black_stone_color
        elif stone == 'white':  self.stone_color.rgba = self.white_stone_color
        self.stone_line_color.a = 1
        self.text_color.a = 0
        self.refreshCanvas()

    def setCanvasToColor(self, color):
        self.board_rect_color.rgba = color
        self.grid_line_color.a = 1
        self.stone_color.rgba = self.no_stone_color
        self.stone_line_color.a = 0
        self.text_color.a = 0
        self.refreshCanvas()

    def setCanvasToText(self, text):
        self.board_rect_color.rgba = self.board_color
        self.grid_line_color.a = 0
        self.stone_color.rgba = self.no_stone_color
        self.stone_line_color.a = 0
        self.text_color.a = 1
        core_label = CoreLabel(text=text, font_size=100, color=[0, 0, 0, 1])
        core_label.refresh()
        self.text_rect.texture = core_label.texture
        self.refreshCanvas()

    def getHorLineType(self):
        if self.coord[1] == 0:  return 'left'
        elif self.coord[1] == self.board_size - 1:  return 'right'
        else:  return 'center'

    def getVertLineType(self):
        if self.coord[0] == 0:  return 'top'
        elif self.coord[0] == self.board_size - 1:  return 'bottom'
        else:  return 'center'

    def getGridStarLine(self):
        if self.coord not in self.grid_star_coords[self.board_size]:  return None
        else:  return Ellipse(size=[self.grid_star_size] * 2)

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
        pos_x = (self.pos[0] + (self.size[0] / 2)) - (self.grid_star_line.size[0] / 2)
        pos_y = (self.pos[1] + (self.size[1] / 2)) - (self.grid_star_line.size[1] / 2)
        return pos_x, pos_y

    def getStoneLineCircleArgs(self):
        return [self.center_x, self.center_y, self.width / 2]



class DetailsDisplay (Label):
    def __init__(self):
        super(DetailsDisplay, self).__init__()
        self.app = App.get_running_app()
        self.template = "details:  [{}, {}] {}"
        self.text = self.template.format('?', '?', '0.0')

    def updateText(self):
        return



class Refresh (PanelSettingsSingleButton):

    def __init__(self):
        super(Refresh, self).__init__("refresh")
        self.app = App.get_running_app()
        self.size_hint = [0.25, None]
        self.bind(on_release=self.triggerRefresh)

    def triggerRefresh(self, *largs):
        """ Refresh of the influence panel's display, based on data from infl_calc.getInfluenceData(). """
        display_mode = self.app.data['influence']['display_mode']
        pred_display_type = self.app.data['influence']['prediction_display_type']
        infl_display_buttons = self.app.main.content_scroll.influence_panel.display.buttons
        infl_data = infl_calc.getInfluenceData()

        print(infl_data)

        if display_mode == 'cur_infl':
            self.displayCurInfl(infl_data, infl_display_buttons)
        elif display_mode == 'infl_pred':
            if pred_display_type == 'top_5':
                self.displayInflPredTopNum(infl_data, infl_display_buttons, 5)
            elif pred_display_type == 'top_20':
                self.displayInflPredTopNum(infl_data, infl_display_buttons, 20)
            elif pred_display_type == 'color_steps':
                self.displayInflPredColorSteps(infl_data, infl_display_buttons)
            elif pred_display_type == 'color_gradient':
                self.displayInflPredColorGradient(infl_data, infl_display_buttons)
        if self.app.data['influence']['display_stones'] == 'yes':  self.displayStones()

    def displayCurInfl(self, infl_data, buttons):
        for y, data_row in enumerate(infl_data):
            for x, data_value in enumerate(data_row):
                if data_value > 0:  rgba_values = [1 - data_value, 1 - data_value, 1, 1]
                elif data_value < 0:  rgba_values = [1, 1 - abs(data_value), 1 - abs(data_value), 1]
                elif data_value == 0:  rgba_values = [1, 1, 1, 1]
                buttons[str([y, x])].setCanvasToColor(rgba_values)

    def displayInflPredTopNum(self, infl_data, buttons, num):
        if num == 5:  text_format = "{}"
        elif num == 20:  text_format = "{0:02d}"
        button_map = []
        for y, data_row in enumerate(infl_data):
            for x, data_value in enumerate(data_row):
                button_map += [{'coord': str([y, x]), 'value': data_value}]
        button_map = sorted(button_map, key=lambda x: x['value'], reverse=True)
        for i, each in enumerate(button_map):
            if i >= num:  buttons[each['coord']].setCanvasToDefault(); continue
            buttons[each['coord']].setCanvasToText(text_format.format((i + 1)))

    def displayInflPredColorSteps(self, infl_data, buttons):
        for y, data_row in enumerate(infl_data):
            for x, data_value in enumerate(data_row):

                # TODO:  Need to come back to color steps.  Looks like I need to play around with
                # TODO:  the values (10 and 5 in this case) to get a good display.  Maybe even think
                # TODO:  about cutting off the bottom half of the data_values.  As in if data_value
                # TODO:  < 0.5 then don't even display it and color step the top 0.5.

                # print(f"\ndata_value = {data_value}")
                data_value = data_value * 10
                # print(f"data_value = {data_value}")
                data_value = 5 * round((data_value / 5))
                # print(f"data_value = {data_value}")
                data_value = data_value / 10
                # print(f"data_value = {data_value}")

                if data_value != 0:  rgba_values = [1 - data_value, 1, 1 - data_value, 1]
                else:  rgba_values = [1, 1, 1, 1]
                buttons[str([y, x])].setCanvasToColor((rgba_values))

    def displayInflPredColorGradient(self, infl_data, buttons):
        for y, data_row in enumerate(infl_data):
            for x, data_value in enumerate(data_row):
                if data_value != 0:  rgba_values = [1 - data_value, 1, 1 - data_value, 1]
                else:  rgba_values = [1, 1, 1, 1]
                buttons[str([y, x])].setCanvasToColor(rgba_values)

    def displayStones(self):
        """ Update InfluencePanel board display to also display stones. """
        # Get reference variables.
        infl_display_buttons = self.app.main.content_scroll.influence_panel.display.buttons
        seg_stones = self.app.data['board'].stones
        all_stones = seg_stones['black'] + seg_stones['white']
        # Loop through all_stones and update infl_display_buttons to display stones.
        for stone in all_stones:  infl_display_buttons[str(stone.pos)].setCanvasToStone(stone.color)



class DisplayModeInput (PanelSettingsInput):

    def __init__(self):
        super(DisplayModeInput, self).__init__("display mode")
        self.app = App.get_running_app()
        self.value = self.app.data['influence']['display_mode']
        self.options = BoxLayout(orientation='horizontal', size_hint=[1.0, None], height=20)
        self.infl_pred_button = ToggleButton(
            text="influence prediction", group='influence_display_mode', font_size=13
        )
        self.cur_infl_button = ToggleButton(
            text="current influence", group='influence_display_mode', font_size=13
        )
        self.infl_pred_button.allow_no_selection = False
        self.cur_infl_button.allow_no_selection = False
        self.options.add_widget(self.infl_pred_button)
        self.options.add_widget(self.cur_infl_button)
        self.add_widget(self.options)

        if self.value == 'cur_infl':  self.cur_infl_button.state = 'down'
        elif self.value == 'infl_pred':  self.infl_pred_button.state = 'down'

        self.cur_infl_button.bind(on_release=self.curInflButtonPressed)
        self.infl_pred_button.bind(on_release=self.inflPredButtonPressed)

    def curInflButtonPressed(self, *largs):
        self.app.data['influence']['display_mode'] = 'cur_infl'
        self.value = 'cur_infl'

    def inflPredButtonPressed(self, *largs):
        self.app.data['influence']['display_mode'] = 'infl_pred'
        self.value = 'infl_pred'



class PredictionStoneInput (PanelSettingsInput):

    def __init__(self):
        super(PredictionStoneInput, self).__init__("prediction stone")
        self.app = App.get_running_app()
        self.value = self.app.data['influence']['prediction_stone']
        self.options = BoxLayout(orientation='horizontal', size_hint=[1.0, None], height=20)
        self.black_button = ToggleButton(
            text="black", group='influence_prediction_stone', font_size=13
        )
        self.white_button = ToggleButton(
            text="white", group='influence_prediction_stone', font_size=13
        )
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
        self.app.data['influence']['prediction_stone'] = 'black'
        self.value = 'black'

    def whiteButtonPressed(self, *largs):
        self.app.data['influence']['prediction_stone'] = 'white'
        self.value = 'white'



class PredictionDisplayTypeInput (PanelSettingsInput):

    def __init__(self):
        super(PredictionDisplayTypeInput, self).__init__("prediction display type")
        self.app = App.get_running_app()
        self.value = self.app.data['influence']['prediction_display_type']

        self.options1 = BoxLayout(orientation='horizontal', size_hint=[1.0, None], height=20)
        self.options2 = BoxLayout(orientation='horizontal', size_hint=[1.0, None], height=20)

        self.top_5_button = ToggleButton(
            text="top 5", group='infl_pred_display_type', font_size=13
        )
        self.top_20_button = ToggleButton(
            text="top 20", group='infl_pred_display_type', font_size=13
        )
        self.color_steps_button = ToggleButton(
            text="color steps", group='infl_pred_display_type', font_size=13
        )
        self.color_gradient_button = ToggleButton(
            text="color gradient", group='infl_pred_display_type', font_size=13
        )
        self.top_5_button.allow_no_selection = False
        self.top_20_button.allow_no_selection = False
        self.color_steps_button.allow_no_selection = False
        self.color_gradient_button.allow_no_selection = False

        self.options1.add_widget(self.top_5_button)
        self.options1.add_widget(self.top_20_button)
        self.options2.add_widget(self.color_steps_button)
        self.options2.add_widget(self.color_gradient_button)
        self.add_widget(self.options1)
        self.add_widget(self.options2)

        if self.value == 'top_5':  self.top_5_button.state = 'down'
        elif self.value == 'top_20':  self.top_20_button.state = 'down'
        elif self.value == 'color_steps':  self.color_steps_button.state = 'down'
        elif self.value == 'color_gradient':  self.color_gradient_button.state = 'down'

        self.top_5_button.bind(on_release=self.top5ButtonPressed)
        self.top_20_button.bind(on_release=self.top20ButtonPressed)
        self.color_steps_button.bind(on_release=self.colorStepsButtonPressed)
        self.color_gradient_button.bind(on_release=self.colorGradientButtonPressed)

    def top5ButtonPressed(self, *largs):
        self.app.data['influence']['prediction_display_type'] = 'top_5'
        self.value = 'top_5'

    def top20ButtonPressed(self, *largs):
        self.app.data['influence']['prediction_display_type'] = 'top_20'
        self.value = 'top_20'

    def colorStepsButtonPressed(self, *largs):
        self.app.data['influence']['prediction_display_type'] = 'color_steps'
        self.value = 'color_steps'

    def colorGradientButtonPressed(self, *largs):
        self.app.data['influence']['prediction_display_type'] = 'color_gradient'
        self.value = 'color_gradient'




class DisplayStonesInput (PanelSettingsInput):

    def __init__(self):
        super(DisplayStonesInput, self).__init__("display stones")
        self.app = App.get_running_app()
        self.value = self.app.data['influence']['display_stones']
        self.options = BoxLayout(orientation='horizontal', size_hint=[1.0, None], height=20)
        self.yes_button = ToggleButton(
            text="yes", group='influence_display_stones', font_size=13
        )
        self.no_button = ToggleButton(
            text="no", group='influence_display_stones', font_size=13
        )
        self.yes_button.allow_no_selection = False
        self.no_button.allow_no_selection = False
        self.options.add_widget(self.yes_button)
        self.options.add_widget(self.no_button)
        self.add_widget(self.options)

        if self.value == 'yes':  self.yes_button.state = 'down'
        elif self.value == 'no':  self.no_button.state = 'down'

        self.yes_button.bind(on_release=self.yesButtonPressed)
        self.no_button.bind(on_release=self.noButtonPressed)

    def yesButtonPressed(self, *largs):
        self.app.data['influence']['display_stones'] = 'yes'
        self.value = 'yes'

    def noButtonPressed(self, *largs):
        self.app.data['influence']['display_stones'] = 'no'
        self.value = 'no'



class InflAdjsInput (PanelSettingsInput):

    def __init__(self):
        super(InflAdjsInput, self).__init__("influence adjustments")
        self.app = App.get_running_app()
        self.value = self.app.data['influence']['adjustments']

        self.options1 = BoxLayout(orientation='horizontal', size_hint=[1.0, None], height=20)
        self.options2 = BoxLayout(orientation='horizontal', size_hint=[1.0, None], height=20)
        self.options3 = BoxLayout(orientation='horizontal', size_hint=[1.0, None], height=20)

        self.all_none_button = Button(text="( all / none )", font_size=13)
        self.dist_decay_button = ToggleButton(text="distance decay", font_size=13)
        self.dist_zero_button = ToggleButton(text="distance zero", font_size=13)
        self.angle_decay_button = ToggleButton(text="angle decay", font_size=13)
        self.opp_angle_growth_button = ToggleButton(text="opposite angle growth", font_size=13)
        self.clamp_button = ToggleButton(text="clamp", font_size=13)

        self.options1.add_widget(self.all_none_button)
        self.options1.add_widget(self.dist_decay_button)
        self.options2.add_widget(self.dist_zero_button)
        self.options2.add_widget(self.angle_decay_button)
        self.options3.add_widget(self.opp_angle_growth_button)
        self.options3.add_widget(self.clamp_button)

        self.add_widget(self.options1)
        self.add_widget(self.options2)
        self.add_widget(self.options3)

        if self.value['distance_decay']:  self.dist_decay_button.state = 'down'
        if self.value['distance_zero']:  self.dist_zero_button.state = 'down'
        if self.value['angle_decay']:  self.angle_decay_button.state = 'down'
        if self.value['opposite_angle_growth']:  self.opp_angle_growth_button.state = 'down'
        if self.value['clamp']:  self.clamp_button.state = 'down'

        self.all_none_button.bind(on_release=self.allNoneButtonPressed)
        self.dist_decay_button.bind(on_release=self.distDecayButtonPressed)
        self.dist_zero_button.bind(on_release=self.distZeroButtonPressed)
        self.angle_decay_button.bind(on_release=self.angleDecayButtonPressed)
        self.opp_angle_growth_button.bind(on_release=self.oppAngleGrowthButtonPressed)
        self.clamp_button.bind(on_release=self.clampButtonPressed)

    def allNoneButtonPressed(self, *largs):
        all_values_count = len(self.value.values())
        half_all_values = all_values_count / 2
        cur_pressed_count = sum([ 1 for v in self.value.values() if v ])
        switch_map = [
            [self.dist_decay_button, 'distance_decay'],
            [self.dist_zero_button, 'distance_zero'],
            [self.angle_decay_button, 'angle_decay'],
            [self.opp_angle_growth_button, 'opposite_angle_growth'],
            [self.clamp_button, 'clamp']
        ]
        def switchStateAndValue(button_state_str, value_bool):
            for button, key in switch_map:
                button.state = button_state_str
                self.app.data['influence']['adjustments'][key] = value_bool
                self.value[key] = value_bool
        if cur_pressed_count == all_values_count:  switchStateAndValue('normal', False)
        elif cur_pressed_count == 0:  switchStateAndValue('down', True)
        elif cur_pressed_count >= half_all_values:  switchStateAndValue('down', True)
        else:  switchStateAndValue('normal', False)

    def distDecayButtonPressed(self, *largs):
        if self.dist_decay_button.state == 'normal':
            self.app.data['influence']['adjustments']['distance_decay'] = False
            self.value['distance_decay'] = False
        else:
            self.app.data['influence']['adjustments']['distance_decay'] = True
            self.value['distance_decay'] = True

    def distZeroButtonPressed(self, *largs):
        if self.dist_zero_button.state == 'normal':
            self.app.data['influence']['adjustments']['distance_zero'] = False
            self.value['distance_zero'] = False
        else:
            self.app.data['influence']['adjustments']['distance_zero'] = True
            self.value['distance_zero'] = True

    def angleDecayButtonPressed(self, *largs):
        if self.angle_decay_button.state == 'normal':
            self.app.data['influence']['adjustments']['angle_decay'] = False
            self.value['angle_decay'] = False
        else:
            self.app.data['influence']['adjustments']['angle_decay'] = True
            self.value['angle_decay'] = True

    def oppAngleGrowthButtonPressed(self, *largs):
        if self.opp_angle_growth_button.state == 'normal':
            self.app.data['influence']['adjustments']['opposite_angle_growth'] = False
            self.value['opposite_angle_growth'] = False
        else:
            self.app.data['influence']['adjustments']['opposite_angle_growth'] = True
            self.value['opposite_angle_growth'] = True

    def clampButtonPressed(self, *largs):
        if self.clamp_button.state == 'normal':
            self.app.data['influence']['adjustments']['clamp'] = False
            self.value['clamp'] = False
        else:
            self.app.data['influence']['adjustments']['clamp'] = True
            self.value['clamp'] = True



class WeightsTitle (Label):

    def __init__(self):
        super(WeightsTitle, self).__init__()
        self.app = App.get_running_app()
        self.text = "<>  WEIGHTS  <>"



class DistDecayGtWeightInput (PanelSettingsSliderInput):

    def __init__(self):
        super(DistDecayGtWeightInput, self).__init__(
            "distance decay greater than",
            App.get_running_app().data['influence']['weights']['dist_decay_gt']
        )

        self.slider_input.bind(on_touch_up=self.valueChange)
        self.text_input.bind(on_text_validate=self.valueChange)
        self.reset.bind(on_release=self.valueChange)

    def valueChange(self, *largs):
        self.app.data['influence']['weights']['dist_decay_gt']['value'] = self.slider_input.value



class DistDecayLinWeightInput (PanelSettingsSliderInput):

    def __init__(self):
        super(DistDecayLinWeightInput, self).__init__(
            "distance decay linear",
            App.get_running_app().data['influence']['weights']['dist_decay_lin']
        )

        self.slider_input.bind(on_touch_up=self.valueChange)
        self.text_input.bind(on_text_validate=self.valueChange)
        self.reset.bind(on_release=self.valueChange)

    def valueChange(self, *largs):
        self.app.data['influence']['weights']['dist_decay_lin']['value'] = self.slider_input.value



class DistZeroGtWeightInput (PanelSettingsSliderInput):

    def __init__(self):
        super(DistZeroGtWeightInput, self).__init__(
            "distance zero greater than",
            App.get_running_app().data['influence']['weights']['dist_zero_gt']
        )

        self.slider_input.bind(on_touch_up=self.valueChange)
        self.text_input.bind(on_text_validate=self.valueChange)
        self.reset.bind(on_release=self.valueChange)

    def valueChange(self, *largs):
        self.app.data['influence']['weights']['dist_zero_gt']['value'] = self.slider_input.value



class AngleDecayLtWeightInput (PanelSettingsSliderInput):

    def __init__(self):
        super(AngleDecayLtWeightInput, self).__init__(
            "angle decay less than",
            App.get_running_app().data['influence']['weights']['angle_decay_lt']
        )

        self.slider_input.bind(on_touch_up=self.valueChange)
        self.text_input.bind(on_text_validate=self.valueChange)
        self.reset.bind(on_release=self.valueChange)

    def valueChange(self, *largs):
        self.app.data['influence']['weights']['angle_decay_lt']['value'] = self.slider_input.value



class AngleDecayLinWeightInput (PanelSettingsSliderInput):

    def __init__(self):
        super(AngleDecayLinWeightInput, self).__init__(
            "angle decay linear",
            App.get_running_app().data['influence']['weights']['angle_decay_lin']
        )

        self.slider_input.bind(on_touch_up=self.valueChange)
        self.text_input.bind(on_text_validate=self.valueChange)
        self.reset.bind(on_release=self.valueChange)

    def valueChange(self, *largs):
        self.app.data['influence']['weights']['angle_decay_lin']['value'] = self.slider_input.value



class OppAngleGrowthAngleLtWeightInput (PanelSettingsSliderInput):

    def __init__(self):
        super(OppAngleGrowthAngleLtWeightInput, self).__init__(
            "opposite angle growth angle less than",
            App.get_running_app().data['influence']['weights']['opp_angle_growth_angle_lt']
        )

        self.slider_input.bind(on_touch_up=self.valueChange)
        self.text_input.bind(on_text_validate=self.valueChange)
        self.reset.bind(on_release=self.valueChange)

    def valueChange(self, *largs):
        self.app.data['influence']['weights']['opp_angle_growth_angle_lt']['value'] = self.slider_input.value



class OppAngleGrowthDistLtWeightInput (PanelSettingsSliderInput):

    def __init__(self):
        super(OppAngleGrowthDistLtWeightInput, self).__init__(
            "opposite angle growth distance less than",
            App.get_running_app().data['influence']['weights']['opp_angle_growth_dist_lt']
        )

        self.slider_input.bind(on_touch_up=self.valueChange)
        self.text_input.bind(on_text_validate=self.valueChange)
        self.reset.bind(on_release=self.valueChange)

    def valueChange(self, *largs):
        self.app.data['influence']['weights']['opp_angle_growth_dist_lt']['value'] = self.slider_input.value



class OppAngleGrowthLinWeightInput (PanelSettingsSliderInput):

    def __init__(self):
        super(OppAngleGrowthLinWeightInput, self).__init__(
            "opposite angle growth linear",
            App.get_running_app().data['influence']['weights']['opp_angle_growth_lin']
        )

        self.slider_input.bind(on_touch_up=self.valueChange)
        self.text_input.bind(on_text_validate=self.valueChange)
        self.reset.bind(on_release=self.valueChange)

    def valueChange(self, *largs):
        self.app.data['influence']['weights']['opp_angle_growth_lin']['value'] = self.slider_input.value



class ClampWithinWeightInput (PanelSettingsSliderInput):

    def __init__(self):
        super(ClampWithinWeightInput, self).__init__(
            "clamp within",
            App.get_running_app().data['influence']['weights']['clamp_within']
        )

        self.slider_input.bind(on_touch_up=self.valueChange)
        self.text_input.bind(on_text_validate=self.valueChange)
        self.reset.bind(on_release=self.valueChange)

    def valueChange(self, *largs):
        self.app.data['influence']['weights']['clamp_within']['value'] = self.slider_input.value


####################################################################################################

