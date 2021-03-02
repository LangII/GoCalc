
"""
GoCalc/gui/contentbasewidgets.py
"""

from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput

from kivy.properties import StringProperty, ListProperty, ObjectProperty

import time

####################################################################################################



class ContentPanel (BoxLayout):
    title_label = ObjectProperty()
    panel_title_text = StringProperty()
    close_button = ObjectProperty()

    def __init__(self, title=''):
        super(ContentPanel, self).__init__()
        self.panel_title_text = title
        self.close_button.bind(on_release=self.closeButtonPressed)

        self.add_widget(ContentPanelMenuBar())

    def closeButtonPressed(self, button_state):
        """ PLACEHOLDER for panel closing functionality """
        return



class ContentPanelMenuBar (BoxLayout):
    button_size_hint = ListProperty()

    def __init__(self):
        super(ContentPanelMenuBar, self).__init__()

        self.move_left_button = Button(text="<", size_hint=self.button_size_hint)
        self.lock_toggle_button = Button(text="<<", size_hint=self.button_size_hint)
        self.window_toggle_button = Button(text="[< >]", size_hint=self.button_size_hint)
        self.move_right_button = Button(text=">", size_hint=self.button_size_hint)

        self.add_widget(self.move_left_button)
        self.add_widget(self.lock_toggle_button)
        self.add_widget(self.window_toggle_button)
        self.add_widget(self.move_right_button)



class PanelSettings (ScrollView):
    layout = ObjectProperty()

    def __init__(self):
        super(PanelSettings, self).__init__()



class PanelSettingsInput (BoxLayout):
    title_label_text = StringProperty()

    def __init__(self, title):
        super(PanelSettingsInput, self).__init__()
        self.title_label_text = title



class PanelSettingsSingleButton (Button):
    title_label_text = StringProperty()

    def __init__(self, title):
        super(PanelSettingsSingleButton, self).__init__()
        self.title_label_text = title



class PanelSettingsSliderInput (BoxLayout):
    title_label_text = StringProperty()
    inputs = ObjectProperty()
    slider_input = ObjectProperty()
    text_input = ObjectProperty()

    def __init__(self, title, min_value, max_value, start_value):
        super(PanelSettingsSliderInput, self).__init__()
        self.title_label_text = title
        self.slider_input.min = min_value
        self.slider_input.max = max_value
        self.slider_input.value = start_value
        self.text_input.text = str(start_value)

        self.slider_input.bind(on_touch_up=self.sliderValueChange)
        self.text_input.bind(on_text_validate=self.textValueChange)

    def sliderValueChange(self, *largs):
        input_value = str(self.slider_input.value)
        left_dec_count = len(input_value[:input_value.find('.')])
        right_dec_count = 10 - left_dec_count
        self.text_input.text f"{float(input_value):.{right_dec_count}f}"

    def textValueChange(self, *largs):
        is_number = self.text_input.text.replace('.', '', 1).isdigit()
        if not is_number:
            self.text_input.text = "only numbers" ; return
        text_value = float(self.text_input.text)
        if (self.slider_input.min > text_value) or (text_value > self.slider_input.max):
            self.text_input.text = f"{self.slider_input.min} <-> {self.slider_input.max}" ; return
        self.slider_input.value = text_value
