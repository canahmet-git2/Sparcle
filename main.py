import kivy
kivy.require('2.1.0') # Or your Kivy version

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
from kivy.uix.actionbar import ActionBar, ActionView, ActionPrevious, ActionGroup, ActionButton

# Optional: Set a default window size for easier viewing
Window.size = (1280, 720) # width, height

class PlaceholderPanel(BoxLayout):
    def __init__(self, text, panel_color_hex='#333333', **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(rgba=get_color_from_hex(panel_color_hex))
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self._update_rect, size=self._update_rect)
        self.add_widget(Label(text=text))

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class SparcleApp(App):
    def build(self):
        root_layout = BoxLayout(orientation='vertical')

        # Action Bar (Menu Bar)
        action_bar = ActionBar()
        action_view = ActionView()
        # App icon and title (optional)
        action_view.add_widget(ActionPrevious(title='Sparcle', with_previous=False, app_icon='data/logo/kivy-icon-32.png')) 
        
        file_group = ActionGroup(text='File')
        file_group.add_widget(ActionButton(text='New'))
        file_group.add_widget(ActionButton(text='Open'))
        file_group.add_widget(ActionButton(text='Save'))
        action_view.add_widget(file_group)

        edit_group = ActionGroup(text='Edit')
        edit_group.add_widget(ActionButton(text='Undo'))
        edit_group.add_widget(ActionButton(text='Redo'))
        action_view.add_widget(edit_group)

        view_group = ActionGroup(text='View')
        view_group.add_widget(ActionButton(text='Toggle Something'))
        action_view.add_widget(view_group)

        action_bar.add_widget(action_view)
        root_layout.add_widget(action_bar) # Add ActionBar to the root

        # Main content area (below the ActionBar)
        main_content_area = BoxLayout(orientation='vertical')

        top_panels_container = BoxLayout(orientation='horizontal', size_hint_y=0.75)
        node_graph_panel = BoxLayout(size_hint_x=0.4)
        node_graph_panel.add_widget(PlaceholderPanel(text='Node Graph Area', panel_color_hex='#2A2A2A'))
        top_panels_container.add_widget(node_graph_panel)

        preview_panel = BoxLayout(size_hint_x=0.3)
        preview_panel.add_widget(PlaceholderPanel(text='Preview Area', panel_color_hex='#252525'))
        top_panels_container.add_widget(preview_panel)

        right_dock_panel = BoxLayout(orientation='vertical', size_hint_x=0.3)
        tree_panel = BoxLayout(size_hint_y=0.5)
        tree_panel.add_widget(PlaceholderPanel(text='Tree/Hierarchy Area', panel_color_hex='#2C2C2C'))
        right_dock_panel.add_widget(tree_panel)
        inspector_panel = BoxLayout(size_hint_y=0.5)
        inspector_panel.add_widget(PlaceholderPanel(text='Inspector/Parameters Area', panel_color_hex='#2E2E2E'))
        right_dock_panel.add_widget(inspector_panel)
        top_panels_container.add_widget(right_dock_panel)
        
        main_content_area.add_widget(top_panels_container) # Add top panels to main content area

        timeline_panel = BoxLayout(size_hint_y=0.25)
        timeline_panel.add_widget(PlaceholderPanel(text='Timeline/Dopesheet Area', panel_color_hex='#202020'))
        main_content_area.add_widget(timeline_panel) # Add timeline to main content area

        root_layout.add_widget(main_content_area) # Add main content area to root

        return root_layout

if __name__ == '__main__':
    SparcleApp().run() 