import kivy
kivy.require('2.1.0') # Or your Kivy version

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line, Ellipse, InstructionGroup
from kivy.utils import get_color_from_hex
from kivy.uix.actionbar import ActionBar, ActionView, ActionPrevious, ActionGroup, ActionButton
from kivy.metrics import dp
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.behaviors import DragBehavior
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, ListProperty, NumericProperty, DictProperty, ColorProperty
from kivy.uix.stencilview import StencilView
from kivy.animation import Animation
from enum import Enum

# Optional: Set a default window size for easier viewing
Window.size = (1280, 720) # width, height

class ParamType(Enum):
    FLOAT = float
    INT = int
    STRING = str
    BOOLEAN = bool
    COLOR = tuple # Will be represented as (r,g,b,a) using Kivy's ColorProperty for UI
    VECTOR2 = tuple # (x,y)
    VECTOR3 = tuple # (x,y,z)
    FILEPATH = str # Special string type for file paths
    # Add more as needed, e.g., TEXTURE, CURVE, GRADIENT

class Parameter:
    def __init__(self, name: str, param_type: ParamType, value,
                 display_name: str = None, default_value=None, 
                 ui_hint: str = None, unit: str = None, **kwargs):
        self.name = name # Programmatic name
        self.param_type = param_type
        self.display_name = display_name if display_name else name.replace('_', ' ').title()
        self.value = value
        self.default_value = default_value if default_value is not None else value
        self.ui_hint = ui_hint # e.g., 'slider', 'color_picker', 'checkbox'
        self.unit = unit
        self.options = kwargs # For min, max, step, enum_values, etc.

    def __repr__(self):
        return f"Parameter(name='{self.name}', type={self.param_type.name}, value={self.value}, display='{self.display_name}')"

class Socket(Widget):
    node = ObjectProperty(None)
    is_output = BooleanProperty(False)
    connected_sockets = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(14), dp(14))
        
        # Create socket circle
        with self.canvas.before:
            Color(rgba=get_color_from_hex('#CCCCCC'))  # Light gray for sockets
            self.socket_circle = Ellipse(pos=self.pos, size=self.size)
        
        self.bind(pos=self._update_graphics)
        self.active_connection = None
        self.temp_line = None
        self.temp_color = None
        self.connection_line = None
        self.connection_color = None

    def get_socket_pos(self):
        """Get the socket position in window coordinates"""
        scatter = self.get_scatter()
        if scatter:
            # Transform the position through scatter
            return scatter.to_window(*self.center)
        return self.center

    def get_scatter(self):
        parent = self.parent
        while parent:
            if isinstance(parent, ScatterLayout):
                return parent
            parent = parent.parent
        return None

    def _update_graphics(self, *args):
        self.socket_circle.pos = self.pos
        # Update connection lines if any
        for connected_socket in self.connected_sockets:
            self.update_connection_line(connected_socket)
    
    def update_connection_line(self, other_socket):
        if self.connection_line:
            start_pos = self.get_socket_pos()
            end_pos = other_socket.get_socket_pos()
            
            # Calculate control points for bezier curve
            dx = end_pos[0] - start_pos[0]
            control1_x = start_pos[0] + dx * 0.5
            control1_y = start_pos[1]
            control2_x = start_pos[0] + dx * 0.5
            control2_y = end_pos[1]
            
            # Update the line
            self.connection_line.bezier = [
                start_pos[0], start_pos[1],
                control1_x, control1_y,
                control2_x, control2_y,
                end_pos[0], end_pos[1]
            ]

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.button == 'left':
            touch.grab(self)
            
            # Remove any existing temporary line
            self.remove_temp_line()
            
            # Get the socket position in window coordinates
            start_pos = self.get_socket_pos()
            
            # Create new temporary line
            with self.canvas.after:
                self.temp_color = Color(rgba=get_color_from_hex('#AAAAAA'))
                self.temp_line = Line(points=[start_pos[0], start_pos[1], touch.x, touch.y], width=dp(2))
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self and self.temp_line:
            # Get the socket position in window coordinates
            start_pos = self.get_socket_pos()
            # Update temporary line to follow cursor exactly
            self.temp_line.points = [start_pos[0], start_pos[1], touch.x, touch.y]
            return True
        return super().on_touch_move(touch)

    def remove_temp_line(self):
        if self.temp_line:
            self.canvas.after.remove(self.temp_line)
            self.temp_line = None
        if self.temp_color:
            self.canvas.after.remove(self.temp_color)
            self.temp_color = None

    def remove_connection_line(self):
        if self.connection_line:
            self.canvas.after.remove(self.connection_line)
            self.connection_line = None
        if self.connection_color:
            self.canvas.after.remove(self.connection_color)
            self.connection_color = None

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            # Remove temporary line
            self.remove_temp_line()
            
            # Find potential connection targets
            scatter = self.get_scatter()
            if scatter:
                for widget in scatter.walk():
                    if isinstance(widget, Socket) and widget != self:
                        if widget.collide_point(*widget.to_local(*touch.pos)):
                            if self.is_output != widget.is_output:
                                self.connect_to(widget)
                                break
            
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)

    def connect_to(self, other_socket):
        if other_socket not in self.connected_sockets:
            # Clear existing connections
            self.remove_connection_line()
            for socket in self.connected_sockets:
                socket.remove_connection_line()
            self.connected_sockets.clear()
            
            other_socket.remove_connection_line()
            for socket in other_socket.connected_sockets:
                socket.remove_connection_line()
            other_socket.connected_sockets.clear()
            
            # Create new connection
            self.connected_sockets.append(other_socket)
            other_socket.connected_sockets.append(self)
            
            # Get positions in window coordinates
            start_pos = self.get_socket_pos()
            end_pos = other_socket.get_socket_pos()
            
            # Draw permanent connection line
            with self.canvas.after:
                self.connection_color = Color(rgba=get_color_from_hex('#E0E0E0'))
                self.connection_line = Line(bezier=[
                    start_pos[0], start_pos[1],
                    start_pos[0], start_pos[1],
                    end_pos[0], end_pos[1],
                    end_pos[0], end_pos[1]
                ], width=dp(2))
            self.update_connection_line(other_socket)

class StencilBoxLayout(BoxLayout, StencilView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Add the gray background to StencilBoxLayout
        with self.canvas.before:
            Color(rgba=get_color_from_hex('#2A2A2A'))
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

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

class NodeWidget(BoxLayout):
    title = StringProperty('Node')
    parameters = ListProperty([]) # To store Parameter objects
    
    def __init__(self, title='Node', params_config=None, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.size = (dp(180), dp(120))
        self._touch_offset_x = 0
        self._touch_offset_y = 0
        self.parameters = [] 

        if params_config:
            for p_name, p_data in params_config.items():
                self.add_parameter(
                    name=p_name,
                    param_type=p_data.get('type'),
                    value=p_data.get('value'),
                    display_name=p_data.get('display_name'),
                    default_value=p_data.get('default_value'),
                    ui_hint=p_data.get('ui_hint'),
                    unit=p_data.get('unit'),
                    **p_data.get('options', {})
                )
        
        with self.canvas.before:
            Color(rgba=get_color_from_hex('#424242'))
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
            Color(rgba=get_color_from_hex('#757575'))  # Lighter gray for border
            self.border_line = Line(rectangle=(self.x, self.y, self.width, self.height), width=1.2)
        self.bind(pos=self._update_graphics, size=self._update_graphics)

        # Create title bar
        title_bar = BoxLayout(size_hint_y=None, height=dp(30), padding=(dp(5), dp(2)))
        with title_bar.canvas.before:
            Color(rgba=get_color_from_hex('#2C2C2C'))
            self.title_bg_rect = Rectangle(size=title_bar.size, pos=title_bar.pos)
        title_bar.bind(pos=lambda i,p: setattr(self.title_bg_rect, 'pos', p),
                      size=lambda i,s: setattr(self.title_bg_rect, 'size', s))

        title_label = Label(text=self.title, bold=True, shorten=True, ellipsis_options={'markup': True})
        title_bar.add_widget(title_label)
        self.add_widget(title_bar)

        content_area = BoxLayout(padding=dp(5))
        
        input_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(20))
        self.input_socket = Socket(is_output=False, node=self)
        input_layout.add_widget(Widget()) 
        input_layout.add_widget(self.input_socket)
        input_layout.add_widget(Widget())
        content_area.add_widget(input_layout)
        
        self.node_content_label = Label(text='Node Content')
        content_area.add_widget(self.node_content_label)
        
        output_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(20))
        self.output_socket = Socket(is_output=True, node=self)
        output_layout.add_widget(Widget()) 
        output_layout.add_widget(self.output_socket)
        output_layout.add_widget(Widget())
        content_area.add_widget(output_layout)
        
        self.add_widget(content_area)
        self.update_node_content_display()

    def add_parameter(self, name: str, param_type: ParamType, value, 
                      display_name: str = None, default_value=None, 
                      ui_hint: str = None, unit: str = None, **kwargs):
        param = Parameter(name, param_type, value, 
                          display_name=display_name, default_value=default_value, 
                          ui_hint=ui_hint, unit=unit, **kwargs)
        self.parameters.append(param)
        self.update_node_content_display()

    def get_parameter_value(self, name: str):
        for param in self.parameters:
            if param.name == name:
                return param.value
        return None

    def set_parameter_value(self, name: str, value):
        for param in self.parameters:
            if param.name == name:
                param.value = value
                self.update_node_content_display()
                return True
        return False

    def update_node_content_display(self):
        if hasattr(self, 'node_content_label'):
            if self.parameters:
                param_texts = [f"{p.display_name}: {p.value}{' ' + p.unit if p.unit else ''}" for p in self.parameters[:2]]
                self.node_content_label.text = "\n".join(param_texts)
            else:
                self.node_content_label.text = "(No Params)"

    def _update_graphics(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
        self.border_line.rectangle = (instance.x, instance.y, instance.width, instance.height)
        # Update socket positions
        if hasattr(self, 'input_socket'):
            for connected_socket in self.input_socket.connected_sockets:
                self.input_socket.update_connection_line(connected_socket)
        if hasattr(self, 'output_socket'):
            for connected_socket in self.output_socket.connected_sockets:
                self.output_socket.update_connection_line(connected_socket)

    def get_scatter_pos(self, pos):
        scatter = self.get_scatter()
        if scatter:
            return scatter.to_local(*pos)
        return pos

    def get_scatter(self):
        parent = self.parent
        while parent:
            if isinstance(parent, ScatterLayout):
                return parent
            parent = parent.parent
        return None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Check if touch is on a socket
            if (hasattr(self, 'input_socket') and self.input_socket.collide_point(*touch.pos)) or \
               (hasattr(self, 'output_socket') and self.output_socket.collide_point(*touch.pos)):
                return super().on_touch_down(touch)
            
            # Otherwise, handle node dragging
            touch.grab(self)
            # Calculate offset between touch and node position
            self._touch_offset_x = self.x - touch.x
            self._touch_offset_y = self.y - touch.y
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            # Move node to follow touch position with offset
            new_x = touch.x + self._touch_offset_x
            new_y = touch.y + self._touch_offset_y
            
            # Update position immediately for better responsiveness
            self.pos = (new_x, new_y)
            
            # Update all connected socket lines
            if hasattr(self, 'input_socket'):
                for connected_socket in self.input_socket.connected_sockets:
                    self.input_socket.update_connection_line(connected_socket)
                    connected_socket.update_connection_line(self.input_socket)
            
            if hasattr(self, 'output_socket'):
                for connected_socket in self.output_socket.connected_sockets:
                    self.output_socket.update_connection_line(connected_socket)
                    connected_socket.update_connection_line(self.output_socket)
            
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)

# --- Concrete Node Type Classes ---
class SourceNode(NodeWidget):
    def __init__(self, **kwargs):
        # Define standard parameters for a SourceNode
        params_config = {
            "emission_rate": {
                "type": ParamType.FLOAT, 
                "value": 10.0, 
                "default_value": 10.0,
                "display_name": "Emission Rate", 
                "ui_hint": "slider", 
                "unit": "p/s", 
                "options": {"min": 0.0, "max": 100.0, "step": 0.1}
            },
            "lifespan": {
                "type": ParamType.FLOAT, 
                "value": 2.0, 
                "default_value": 2.0,
                "display_name": "Lifespan",
                "ui_hint": "slider", 
                "unit": "s",
                "options": {"min": 0.1, "max": 10.0, "step": 0.05}
            },
            "particle_color": {
                "type": ParamType.COLOR,
                "value": (1.0, 1.0, 0.0, 1.0), # RGBA Yellow
                "default_value": (1.0, 1.0, 0.0, 1.0),
                "display_name": "Particle Color",
                "ui_hint": "color_picker"
            }
            # Add other source-specific parameters here later (e.g., initial velocity, particle texture)
        }
        # Call the base class __init__ with the title and these parameters
        super().__init__(title='Source', params_config=params_config, **kwargs)

class DisplayNode(NodeWidget):
    def __init__(self, **kwargs):
        # Define any parameters specific to a DisplayNode (maybe blend mode, etc. later)
        params_config = {
             "display_name_param": {
                "type": ParamType.STRING,
                "value": "Default Display",
                "display_name": "Display Name"
            }
        }
        super().__init__(title='Display', params_config=params_config, **kwargs)

class SparcleApp(App):
    def build(self):
        root_layout = BoxLayout(orientation='vertical')

        # Action Bar (Menu Bar)
        action_bar = ActionBar()
        action_bar.size_hint_y = None # Allow setting a fixed height
        action_bar.height = dp(35)    # Set a fixed height for the ActionBar

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

        # Add Node group (New)
        node_group = ActionGroup(text='Node')
        node_group.add_widget(ActionButton(text='Add Source', on_release=self.add_source_node))
        node_group.add_widget(ActionButton(text='Add Display', on_release=self.add_display_node))
        action_view.add_widget(node_group)

        action_bar.add_widget(action_view)
        root_layout.add_widget(action_bar) # Add ActionBar to the root

        # Main content area (below the ActionBar)
        main_content_area = BoxLayout(orientation='vertical')

        top_panels_container = BoxLayout(orientation='horizontal', size_hint_y=0.75)
        node_graph_panel = StencilBoxLayout(size_hint_x=0.4)
        self.node_graph_canvas = ScatterLayout(
            do_rotation=False,
            do_scale=True,
            do_translation_x=True,
            do_translation_y=True,
            scale_min=0.5,
            scale_max=2.0
        )
        node_graph_panel.add_widget(self.node_graph_canvas)
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

    def add_source_node(self, instance):
        source_node = SourceNode() # Create an instance of the specific SourceNode class
        # Position relative to the scatter's center
        scatter_center_x = self.node_graph_canvas.width / 2
        scatter_center_y = self.node_graph_canvas.height / 2
        
        offset_x = dp(20)
        offset_y = dp(20)
        
        source_node.pos = (
            scatter_center_x - source_node.width / 2 + offset_x,
            scatter_center_y - source_node.height / 2 + offset_y
        )
        
        self.node_graph_canvas.add_widget(source_node)
        print("Added Source Node (Specific Class)")

    def add_display_node(self, instance):
        display_node = DisplayNode() # Create an instance of the specific DisplayNode class
        # Position relative to the scatter's center
        scatter_center_x = self.node_graph_canvas.width / 2
        scatter_center_y = self.node_graph_canvas.height / 2
        
        offset_x = dp(-20)
        offset_y = dp(-20)
        
        display_node.pos = (
            scatter_center_x - display_node.width / 2 + offset_x,
            scatter_center_y - display_node.height / 2 + offset_y
        )
        
        self.node_graph_canvas.add_widget(display_node)
        print("Added Display Node (Specific Class)")

if __name__ == '__main__':
    SparcleApp().run() 