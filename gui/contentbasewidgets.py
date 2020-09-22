
"""
GoCalc/gui/contentbasewidgets.py
"""

from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton

from kivy.properties import StringProperty, ListProperty, ObjectProperty

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



# class GroupOfToggleButtonsInput (GridLayout):
#
#     def __init__(self, cols=):
#         super(GroupOfToggleButtonsInput, self).__init__()
