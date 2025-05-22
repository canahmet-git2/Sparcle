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
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.checkbox import CheckBox
from functools import partial
from kivy.clock import Clock # For animation loop
import random # For potential future use with randomness
import uuid # For generating unique IDs
from kivy.uix.popup import Popup
from kivy.uix.button import Button

# Import from our project
from src.core.ir import EffectIR, EmitterProperties, EmitterParameter, AnimatedParameter, TimelineKeyframe # Add EmitterProperties, EmitterParameter

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

class Particle:
    def __init__(self, pos, color, size, life=1.0, velocity=(0,0)):
        self.pos = list(pos) 
        self.color = tuple(color)
        self.size = tuple(size)
        self.life = float(life)
        self.velocity = list(velocity) # Store velocity

    def __repr__(self):
        return f"Particle(pos={self.pos}, color={self.color}, life={self.life:.2f}, vel={self.velocity})"

class PreviewWindow(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.particles = []
        self.particle_draw_group = InstructionGroup()
        self.current_emitter_node = None
        self.emission_rate = 0
        self.particle_lifespan = 1.0
        self.particle_base_color = (1,1,1,1)
        self.particle_initial_velocity = (0,0)
        self.particle_emitter_offset = (0,0) # Store emitter position offset
        self.emission_debt = 0.0

        with self.canvas:
            Color(rgba=get_color_from_hex('#252525')) 
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.canvas.add(self.particle_draw_group)
        self.bind(pos=self._update_rect, size=self._update_rect)
        self._simulation_event = None

    def _update_rect(self, instance, value):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def start_simulation(self, node):
        self.stop_simulation()
        if not (node and isinstance(node, SourceNode)):
            self.draw_particles() # Draw empty if no valid node
            return

        app = App.get_running_app()
        if not (app and hasattr(app, 'effect_ir') and app.effect_ir):
            print("Warning: EffectIR not found in app. Preview will not use IR data.")
            self.draw_particles()
            return

        emitter_data = app.effect_ir.get_emitter(node.node_id)
        if not emitter_data:
            print(f"Warning: EmitterProperties for node '{node.node_id}' not found in EffectIR. Preview might not reflect true state.")
            # Fallback or clear: For now, let's clear and not simulate if IR data is missing for the selected node
            self.current_emitter_node = None # Ensure no old data is used
            self.draw_particles()
            return

        self.current_emitter_node = node # Still keep a reference to the node for identity, maybe other non-IR uses

        # Fetch parameters from EffectIR, considering current_time for animation
        current_time = app.current_time
        node_id = node.node_id

        self.emission_rate = app.effect_ir.get_animated_param_value(node_id, "emission_rate", current_time)
        self.particle_lifespan = app.effect_ir.get_animated_param_value(node_id, "lifespan", current_time)
        
        color_val = app.effect_ir.get_animated_param_value(node_id, "particle_color", current_time)
        self.particle_base_color = color_val if isinstance(color_val, tuple) and len(color_val) == 4 else (1,1,1,1)
        
        # Debug: Print the color being used
        print(f"Preview: Using particle color {self.particle_base_color} from EffectIR at T={current_time:.2f}")
        
        velocity_val = app.effect_ir.get_animated_param_value(node_id, "initial_velocity", current_time)
        self.particle_initial_velocity = velocity_val if isinstance(velocity_val, tuple) and len(velocity_val) == 2 else (0,0)
        
        emitter_pos_val = app.effect_ir.get_animated_param_value(node_id, "emitter_position", current_time)
        self.particle_emitter_offset = emitter_pos_val if isinstance(emitter_pos_val, tuple) and len(emitter_pos_val) == 2 else (0,0)

        print(f"Preview using IR data for '{node.node_id}' at T={current_time:.2f}: Rate={self.emission_rate}, Life={self.particle_lifespan}, Color={self.particle_base_color}")

        self.emission_debt = 0.0
        if self.emission_rate > 0 or self.particles: 
            self._simulation_event = Clock.schedule_interval(self.update_simulation, 1.0 / 60.0)
        else:
            self.draw_particles()

    def stop_simulation(self):
        if self._simulation_event:
            Clock.unschedule(self._simulation_event)
            self._simulation_event = None
        self.particles.clear()
        self.particle_draw_group.clear()
        self.current_emitter_node = None
        self.emission_debt = 0.0

    def update_simulation(self, dt):
        if not self.current_emitter_node: 
            self.stop_simulation()
            return

        particles_to_emit_float = self.emission_rate * dt + self.emission_debt
        num_to_emit = int(particles_to_emit_float)
        self.emission_debt = particles_to_emit_float - num_to_emit

        particle_size = (dp(10), dp(10))
        # Calculate base emission position using the offset
        base_pos_x = self.center_x + self.particle_emitter_offset[0]
        base_pos_y = self.center_y + self.particle_emitter_offset[1]

        for _ in range(num_to_emit):
            p = Particle(
                pos=(base_pos_x, base_pos_y), # Use base position
                color=self.particle_base_color,
                size=particle_size,
                life=self.particle_lifespan,
                velocity=self.particle_initial_velocity
            )
            self.particles.append(p)

        for i in range(len(self.particles) - 1, -1, -1):
            p = self.particles[i]
            p.life -= dt
            p.pos[0] += p.velocity[0] * dt
            p.pos[1] += p.velocity[1] * dt
            if p.life <= 0:
                self.particles.pop(i)
        
        self.draw_particles()

    def update_preview(self, node):
        if node and isinstance(node, SourceNode):
            self.start_simulation(node)
        else:
            self.stop_simulation()
            self.draw_particles()

    def draw_particles(self):
        self.particle_draw_group.clear() 
        for p in self.particles:
            self.particle_draw_group.add(Color(rgba=p.color))
            ellipse_pos = (p.pos[0] - p.size[0] / 2, p.pos[1] - p.size[1] / 2)
            self.particle_draw_group.add(Ellipse(pos=ellipse_pos, size=p.size))

class NodeWidget(BoxLayout):
    title = StringProperty('Node')
    parameters = ListProperty([])
    is_selected = BooleanProperty(False)
    node_id = StringProperty('')
    
    def __init__(self, title='Node', params_config=None, node_id=None, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        if node_id:
            self.node_id = node_id
        else:
            self.node_id = uuid.uuid4().hex
        
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
            self.border_color_instruction = Color(rgba=get_color_from_hex('#757575'))
            self.border_line = Line(rectangle=(self.x, self.y, self.width, self.height), width=1.2)
            Color(rgba=get_color_from_hex('#424242'))
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
            
        self.bind(pos=self._update_graphics, size=self._update_graphics, is_selected=self.on_selection_change)

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
                old_value = param.value
                param.value = value
                print(f"Parameter '{name}' changed from {old_value} to {value}")
                self.update_node_content_display()
                app = App.get_running_app()
                if app:
                    # Update EffectIR if this node is a source node and has a representation in IR
                    if isinstance(self, SourceNode) and app.effect_ir:
                        emitter_data = app.effect_ir.get_emitter(self.node_id)
                        if emitter_data:
                            # Ensure the parameter exists in the IR's EmitterProperties parameters dict
                            if name in emitter_data.parameters:
                                emitter_data.set_param_value(name, value)
                                print(f"EffectIR: Updated emitter '{self.node_id}' param '{name}' to: {value}")
                            else:
                                # This case should ideally not happen if IR is synced on creation
                                print(f"Warning: Param '{name}' not found in IR for emitter '{self.node_id}'. Creating it.")
                                emitter_data.parameters[name] = EmitterParameter(name=name, value=value)
                                # Or, more strictly, only update if it exists, depends on design
                        else:
                            print(f"Warning: EmitterProperties for node '{self.node_id}' not found in EffectIR.")

                    # Existing notification for UI/Preview updates
                    app.notify_parameter_changed(self, param.name)
                return True
        return False

    def update_node_content_display(self):
        if hasattr(self, 'node_content_label'):
            if self.parameters:
                param_texts = [f"{p.display_name}: {p.value}{' ' + p.unit if p.unit else ''}" for p in self.parameters[:2]]
                self.node_content_label.text = "\n".join(param_texts)
            else:
                self.node_content_label.text = "(No Params)"

    def on_selection_change(self, instance, value):
        if value:
            self.border_color_instruction.rgba = get_color_from_hex('#FFFFFF')
        else:
            self.border_color_instruction.rgba = get_color_from_hex('#757575')
        self._update_graphics(self, self.pos) 

    def _update_graphics(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
        self.border_line.rectangle = (instance.x, instance.y, instance.width, instance.height)
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
            if (hasattr(self, 'input_socket') and self.input_socket.collide_point(*self.input_socket.to_local(*touch.pos))) or \
               (hasattr(self, 'output_socket') and self.output_socket.collide_point(*self.output_socket.to_local(*touch.pos))):
                return super().on_touch_down(touch)
            
            app = App.get_running_app()
            if app:
                app.select_node(self)
            
            touch.grab(self)
            self._touch_offset_x = self.x - touch.x
            self._touch_offset_y = self.y - touch.y
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            new_x = touch.x + self._touch_offset_x
            new_y = touch.y + self._touch_offset_y
            
            self.pos = (new_x, new_y)
            
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
        if 'node_id' not in kwargs:
            kwargs['node_id'] = uuid.uuid4().hex
        
        base_params_config = {
            "emission_rate": { 
                "type": ParamType.FLOAT, "value": 10.0, "default_value": 10.0,
                "display_name": "Emission Rate", "ui_hint": "slider", "unit": "p/s", 
                "options": {"min": 0.0, "max": 100.0, "step": 0.1}
            },
            "lifespan": { 
                "type": ParamType.FLOAT, "value": 2.0, "default_value": 2.0,
                "display_name": "Lifespan", "ui_hint": "slider", "unit": "s",
                "options": {"min": 0.1, "max": 10.0, "step": 0.05}
            },
            "particle_color": { 
                "type": ParamType.COLOR, "value": (1.0, 1.0, 0.0, 1.0),
                "default_value": (1.0, 1.0, 0.0, 1.0), "display_name": "Particle Color",
                "ui_hint": "color_picker"
            },
            "initial_velocity": {
                "type": ParamType.VECTOR2,
                "value": (0.0, 100.0), 
                "default_value": (0.0, 100.0),
                "display_name": "Initial Velocity",
                "unit": "px/s"
            },
            "emitter_position": {
                "type": ParamType.VECTOR2,
                "value": (0.0, 0.0), # Offset from PreviewWindow center
                "default_value": (0.0, 0.0),
                "display_name": "Emitter Position Offset",
                "unit": "px"
            }
        }
        super().__init__(title='Source', params_config=base_params_config, **kwargs)

        app = App.get_running_app()
        if app and hasattr(app, 'effect_ir') and app.effect_ir:
            ir_emitter_params = {}
            for p_name, p_data in base_params_config.items():
                ir_emitter_params[p_name] = EmitterParameter(
                    name=p_name,
                    value=p_data.get('value')
                )
            
            emitter_props = EmitterProperties(
                emitter_id=self.node_id,
                emitter_type="SourceParticleEmitter",
                name=self.title,
                parameters=ir_emitter_params
            )
            app.effect_ir.add_emitter(emitter_props)
            print(f"SourceNode '{self.node_id}' added EmitterProperties to EffectIR: {emitter_props}")

            # Add mock animation data for this new emitter's emission_rate for testing
            if self.node_id == app.effect_ir.emitters[0].emitter_id: # Only for the first source node for predictability
                rate_anim_path = f"{self.node_id}/emission_rate"
                rate_anim = AnimatedParameter(
                    keyframes=[
                        TimelineKeyframe(time=0.0, value=5.0),
                        TimelineKeyframe(time=app.effect_ir.loop_duration / 2, value=50.0),
                        TimelineKeyframe(time=app.effect_ir.loop_duration, value=5.0)
                    ]
                )
                app.effect_ir.add_or_update_timeline(rate_anim_path, rate_anim)
                print(f"Added mock emission_rate animation for '{self.node_id}'")
        else:
            print(f"Warning: Could not register SourceNode '{self.node_id}' with EffectIR (App or EffectIR not found).")

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

# --- Color Picker Popup --- #
class ColorPickerPopup(Popup):
    @staticmethod
    def rgb_to_hsv(r, g, b):
        """Convert RGB to HSV. RGB values should be 0-1."""
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        # Value
        v = max_val
        
        # Saturation
        if max_val == 0:
            s = 0
        else:
            s = diff / max_val
        
        # Hue
        if diff == 0:
            h = 0
        elif max_val == r:
            h = (60 * ((g - b) / diff) + 360) % 360
        elif max_val == g:
            h = (60 * ((b - r) / diff) + 120) % 360
        elif max_val == b:
            h = (60 * ((r - g) / diff) + 240) % 360
        
        return h / 360.0, s, v  # Return h as 0-1 to match Kivy's expected format
    
    @staticmethod
    def hsv_to_rgb(h, s, v):
        """Convert HSV to RGB. H should be 0-1, S and V should be 0-1."""
        h = h * 360  # Convert back to 0-360 for calculation
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        
        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        elif 300 <= h < 360:
            r, g, b = c, 0, x
        else:
            r, g, b = 0, 0, 0
        
        return r + m, g + m, b + m

    def __init__(self, initial_color=(1,1,1,1), callback=None, **kwargs):
        super().__init__(**kwargs)
        self.title = "Select Color"
        self.size_hint = (None, None)
        self.size = (dp(450), dp(400))
        self.auto_dismiss = False # User must click OK or Cancel

        self.initial_color = list(initial_color) # RGBA
        self.current_color_rgba = list(initial_color) # RGBA
        # Use our own RGB to HSV conversion
        h, s, v = self.rgb_to_hsv(*initial_color[:3])
        self.current_color_hsv = [h, s, v, initial_color[3]] # HSVA
        self.callback = callback

        # Main layout for the popup content
        popup_content_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Top section: Swatches and Hex/RGB input
        top_section = BoxLayout(size_hint_y=0.3, spacing=dp(10))
        
        # Swatches (Current and Initial)
        swatches_layout = BoxLayout(orientation='vertical', size_hint_x=0.3, spacing=dp(5))
        self.current_swatch = Widget()
        with self.current_swatch.canvas:
            self.current_swatch_color_instr = Color(rgba=self.current_color_rgba)
            self.current_swatch_rect = Rectangle(size=self.current_swatch.size, pos=self.current_swatch.pos)
        self.current_swatch.bind(pos=self._update_swatch_rect, size=self._update_swatch_rect)
        
        initial_swatch_label = Label(text="Initial", size_hint_y=0.2)
        self.initial_swatch = Widget()
        with self.initial_swatch.canvas:
            Color(rgba=self.initial_color)
            self.initial_swatch_rect = Rectangle(size=self.initial_swatch.size, pos=self.initial_swatch.pos)
        self.initial_swatch.bind(pos=self._update_initial_swatch_rect, size=self._update_initial_swatch_rect)

        swatches_layout.add_widget(Label(text="Current", size_hint_y=0.2))
        swatches_layout.add_widget(self.current_swatch)
        swatches_layout.add_widget(initial_swatch_label)
        swatches_layout.add_widget(self.initial_swatch)
        top_section.add_widget(swatches_layout)

        # RGB and Hex inputs
        rgb_hex_layout = GridLayout(cols=2, size_hint_x=0.7, spacing=dp(5), padding=(0, dp(10)))
        rgb_hex_layout.add_widget(Label(text="R (0-1):"))
        self.r_input = TextInput(text=f"{self.current_color_rgba[0]:.2f}", multiline=False)
        rgb_hex_layout.add_widget(self.r_input)
        rgb_hex_layout.add_widget(Label(text="G (0-1):"))
        self.g_input = TextInput(text=f"{self.current_color_rgba[1]:.2f}", multiline=False)
        rgb_hex_layout.add_widget(self.g_input)
        rgb_hex_layout.add_widget(Label(text="B (0-1):"))
        self.b_input = TextInput(text=f"{self.current_color_rgba[2]:.2f}", multiline=False)
        rgb_hex_layout.add_widget(self.b_input)
        rgb_hex_layout.add_widget(Label(text="Hex (RRGGBBAA):"))
        hex_color = get_color_from_hex(self._rgba_to_hex(self.current_color_rgba)) # This might be redundant, direct hex string needed
        self.hex_input = TextInput(text=self._rgba_to_hex(self.current_color_rgba)[1:], multiline=False) # Remove #
        rgb_hex_layout.add_widget(self.hex_input)
        top_section.add_widget(rgb_hex_layout)
        popup_content_layout.add_widget(top_section)

        # HSV and Alpha Sliders
        sliders_layout = GridLayout(cols=2, size_hint_y=0.5, spacing=dp(5))
        sliders_layout.add_widget(Label(text="Hue (0-360):"))
        self.h_slider = Slider(min=0, max=360, value=self.current_color_hsv[0]*360)
        sliders_layout.add_widget(self.h_slider)
        sliders_layout.add_widget(Label(text="Sat (0-1):"))
        self.s_slider = Slider(min=0, max=1, value=self.current_color_hsv[1])
        sliders_layout.add_widget(self.s_slider)
        sliders_layout.add_widget(Label(text="Val (0-1):"))
        self.v_slider = Slider(min=0, max=1, value=self.current_color_hsv[2])
        sliders_layout.add_widget(self.v_slider)
        sliders_layout.add_widget(Label(text="Alpha (0-1):"))
        self.a_slider = Slider(min=0, max=1, value=self.current_color_rgba[3])
        sliders_layout.add_widget(self.a_slider)
        popup_content_layout.add_widget(sliders_layout)

        # Bindings for sliders and inputs to update methods
        self.h_slider.bind(value=self._on_hsv_alpha_slider_change)
        self.s_slider.bind(value=self._on_hsv_alpha_slider_change)
        self.v_slider.bind(value=self._on_hsv_alpha_slider_change)
        self.a_slider.bind(value=self._on_hsv_alpha_slider_change)

        self.r_input.bind(text=self._on_rgb_input_change)
        self.g_input.bind(text=self._on_rgb_input_change)
        self.b_input.bind(text=self._on_rgb_input_change)
        self.hex_input.bind(text=self._on_hex_input_change)

        # OK and Cancel buttons
        buttons_layout = BoxLayout(size_hint_y=0.15, spacing=dp(10))
        ok_button = Button(text="OK")
        ok_button.bind(on_release=self._on_ok)
        cancel_button = Button(text="Cancel")
        cancel_button.bind(on_release=self.dismiss)
        buttons_layout.add_widget(Widget(size_hint_x=0.5)) # Spacer
        buttons_layout.add_widget(ok_button)
        buttons_layout.add_widget(cancel_button)
        buttons_layout.add_widget(Widget(size_hint_x=0.5)) # Spacer
        popup_content_layout.add_widget(buttons_layout)

        self.content = popup_content_layout
        self._update_ui_from_current_color(source='init') # Initial UI sync

    def _rgba_to_hex(self, rgba_color):
        r, g, b, a_float = rgba_color
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}{int(a_float*255):02x}"

    def _hex_to_rgba(self, hex_color_str):
        hex_color_str = hex_color_str.lstrip('#')
        if len(hex_color_str) == 6:
            hex_color_str += "ff" # Assume full alpha if not provided
        if len(hex_color_str) != 8:
            return None # Invalid hex
        try:
            r = int(hex_color_str[0:2], 16) / 255.0
            g = int(hex_color_str[2:4], 16) / 255.0
            b = int(hex_color_str[4:6], 16) / 255.0
            a = int(hex_color_str[6:8], 16) / 255.0
            return [r,g,b,a]
        except ValueError:
            return None

    def _update_swatch_rect(self, instance, value):
        self.current_swatch_rect.pos = instance.pos
        self.current_swatch_rect.size = instance.size

    def _update_initial_swatch_rect(self, instance, value):
        self.initial_swatch_rect.pos = instance.pos
        self.initial_swatch_rect.size = instance.size

    def _update_color_internals(self, new_rgba, source_of_change):
        """Updates internal RGBA and HSVA representations and the UI elements."""
        self.current_color_rgba = list(new_rgba)
        # Update HSV from RGB (excluding alpha, which is handled separately by its slider)
        rgb_for_hsv = self.current_color_rgba[:3]
        # Use our own RGB to HSV conversion
        h, s, v = self.rgb_to_hsv(*rgb_for_hsv)
        self.current_color_hsv = [h, s, v, self.current_color_rgba[3]]
        self._update_ui_from_current_color(source=source_of_change)

    def _update_ui_from_current_color(self, source='unknown'):
        """Updates all UI elements based on self.current_color_rgba and self.current_color_hsv."""
        # Update Sliders if they were not the source of change
        if source != 'sliders':
            self.h_slider.value = self.current_color_hsv[0] * 360
            self.s_slider.value = self.current_color_hsv[1]
            self.v_slider.value = self.current_color_hsv[2]
            self.a_slider.value = self.current_color_rgba[3]

        # Update RGB inputs if they were not the source of change
        if source != 'rgb_inputs':
            self.r_input.text = f"{self.current_color_rgba[0]:.2f}"
            self.g_input.text = f"{self.current_color_rgba[1]:.2f}"
            self.b_input.text = f"{self.current_color_rgba[2]:.2f}"

        # Update Hex input if it was not the source of change
        if source != 'hex_input':
            self.hex_input.text = self._rgba_to_hex(self.current_color_rgba)[1:9] # RRGGBBAA without #
            
        # Update current color swatch
        self.current_swatch_color_instr.rgba = tuple(self.current_color_rgba)

    def _on_hsv_alpha_slider_change(self, instance, value):
        h = self.h_slider.value / 360.0
        s = self.s_slider.value
        v = self.v_slider.value
        alpha = self.a_slider.value
        
        # Use our own HSV to RGB conversion
        r, g, b = self.hsv_to_rgb(h, s, v)
        new_rgba = [r, g, b, alpha]
        self._update_color_internals(new_rgba, source_of_change='sliders')

    def _on_rgb_input_change(self, instance, value):
        try:
            r = float(self.r_input.text)
            g = float(self.g_input.text)
            b = float(self.b_input.text)
            a = self.current_color_rgba[3] # Keep current alpha from slider/previous state
            
            r = max(0.0, min(1.0, r))
            g = max(0.0, min(1.0, g))
            b = max(0.0, min(1.0, b))

            new_rgba = [r,g,b,a]
            self._update_color_internals(new_rgba, source_of_change='rgb_inputs')
        except ValueError:
            pass # Ignore if text is not a valid float yet

    def _on_hex_input_change(self, instance, value):
        # Ensure it's 6 or 8 chars for RRGGBB or RRGGBBAA
        if len(value) == 6 or len(value) == 8:
            rgba = self._hex_to_rgba(value)
            if rgba:
                self._update_color_internals(rgba, source_of_change='hex_input')
        # No update if hex is partially typed and invalid

    def _on_ok(self, instance):
        if self.callback:
            self.callback(tuple(self.current_color_rgba))
        self.dismiss()

# --- InspectorPanel modifications needed next ---
# In InspectorPanel.observe_node, for ParamType.COLOR:
# 1. Remove the old color layout (BoxLayout with 4 TextInputs).
# 2. Add a small Widget to show the current color (non-interactive swatch).
# 3. Add a Button (e.g., text="Edit Color" or shows hex code).
# 4. Button on_release: create and open ColorPickerPopup instance.
#    - Pass current param color to popup.
#    - Pass a callback to popup that does: node.set_parameter_value(param.name, new_color) and updates swatch in inspector.

class InspectorPanel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(5)
        self.spacing = dp(5)

        title_label = Label(text="Inspector", size_hint_y=None, height=dp(30), bold=True)
        self.add_widget(title_label)

        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.params_layout = GridLayout(
            cols=2, 
            spacing=dp(5),
            size_hint_y=None
        )
        self.params_layout.bind(minimum_height=self.params_layout.setter('height'))
        self.scroll_view.add_widget(self.params_layout)
        self.add_widget(self.scroll_view)
        self.observed_node = None

        # Clear old swatch instructions if any, to prevent memory leaks with Color objects
        if hasattr(self, 'inspector_color_swatches'):
            del self.inspector_color_swatches # Or iterate and properly manage canvas instructions
        self.inspector_color_swatches = {} # param_name: {swatch_widget, color_instr}

    def observe_node(self, node):
        self.params_layout.clear_widgets()
        self.observed_node = node

        if not node:
            no_node_label = Label(text="No node selected.", size_hint_y=None, height=dp(30))
            self.params_layout.add_widget(no_node_label) 
            self.params_layout.add_widget(Widget(size_hint_y=None, height=dp(30))) # Spacer
            return

        if not node.parameters:
            no_params_label = Label(text="Node has no parameters.", size_hint_y=None, height=dp(30))
            self.params_layout.add_widget(no_params_label)
            self.params_layout.add_widget(Widget(size_hint_y=None, height=dp(30))) # Spacer
            return

        for param in node.parameters:
            name_label = Label(
                text=f"{param.display_name}:", 
                size_hint_y=None, height=dp(30),
                halign='right', valign='middle'
            )
            name_label.bind(size=name_label.setter('text_size'))
            self.params_layout.add_widget(name_label)
            
            editor_widget = None
            param_value_str = str(param.value)
            unit_suffix = f" {param.unit}" if param.unit else ""

            if param.param_type == ParamType.FLOAT or param.param_type == ParamType.INT:
                if param.ui_hint == 'slider' and 'min' in param.options and 'max' in param.options:
                    slider_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
                    current_val_label = Label(text=f"{param.value:.2f}{unit_suffix}", size_hint_x=0.3)
                    slider = Slider(
                        min=param.options.get('min', 0),
                        max=param.options.get('max', 1),
                        value=param.value,
                        step=param.options.get('step', 0.01 if param.param_type == ParamType.FLOAT else 1),
                        size_hint_x=0.7
                    )
                    def on_slider_value_change(slider_instance, value, p_name, lbl, node_ref, p_type, suffix):
                        node_ref.set_parameter_value(p_name, p_type.value(value)) 
                        lbl.text = f"{value:.2f}{suffix}"
                    
                    slider.bind(value=partial(on_slider_value_change, 
                                            p_name=param.name, 
                                            lbl=current_val_label, 
                                            node_ref=self.observed_node, 
                                            p_type=param.param_type,
                                            suffix=unit_suffix))
                    slider_layout.add_widget(slider)
                    slider_layout.add_widget(current_val_label)
                    editor_widget = slider_layout
                else:
                    text_input = TextInput(
                        text=param_value_str,
                        size_hint_y=None, height=dp(30),
                        multiline=False,
                        input_filter='float' if param.param_type == ParamType.FLOAT else 'int'
                    )
                    def on_text_input_change(instance, p_name, node_ref, p_type):
                        try:
                            val = p_type.value(instance.text)
                            node_ref.set_parameter_value(p_name, val)
                        except ValueError:
                            instance.text = str(node_ref.get_parameter_value(p_name)) 
                    text_input.bind(text=partial(on_text_input_change, 
                                                p_name=param.name, 
                                                node_ref=self.observed_node,
                                                p_type=param.param_type))
                    editor_widget = text_input
            
            elif param.param_type == ParamType.STRING or param.param_type == ParamType.FILEPATH:
                text_input = TextInput(text=param_value_str, size_hint_y=None, height=dp(30), multiline=False)
                def on_text_input_change_str(instance, p_name, node_ref):
                    node_ref.set_parameter_value(p_name, instance.text)
                text_input.bind(text=partial(on_text_input_change_str, p_name=param.name, node_ref=self.observed_node))
                editor_widget = text_input

            elif param.param_type == ParamType.BOOLEAN:
                checkbox = CheckBox(active=bool(param.value), size_hint_y=None, height=dp(30))
                def on_checkbox_active(instance, value, p_name, node_ref):
                    node_ref.set_parameter_value(p_name, value)
                checkbox.bind(active=partial(on_checkbox_active, 
                                            p_name=param.name, 
                                            node_ref=self.observed_node))
                editor_widget = checkbox    
            
            elif param.param_type == ParamType.COLOR:
                color_display_layout = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(30))
                
                # Ensure param value is a valid color tuple
                rgba_tuple = param.value
                if not (isinstance(rgba_tuple, (list, tuple)) and len(rgba_tuple) == 4):
                    rgba_tuple = (1.0,1.0,1.0,1.0) # Default to white if malformed
                else:
                    try: # Ensure all components are floats
                        rgba_tuple = tuple(float(c) for c in rgba_tuple)
                    except (ValueError, TypeError):
                        rgba_tuple = (1.0,1.0,1.0,1.0)

                # This 'swatch' is the small color indicator in the InspectorPanel
                swatch = Widget(size_hint_x=None, width=dp(50))
                with swatch.canvas:
                    # This Color instruction will be updated by the popup's callback
                    color_instr = Color(rgba=rgba_tuple) 
                    # This Rectangle just draws the color, no texture needed
                    rect_instr = Rectangle(pos=swatch.pos, size=swatch.size) 
                
                # Bind pos and size of the rectangle to the swatch widget itself
                swatch.bind(pos=lambda _, val, r=rect_instr: setattr(r, 'pos', val),
                            size=lambda _, val, r=rect_instr: setattr(r, 'size', val))

                # Store references to update this swatch later
                self.inspector_color_swatches[param.name] = {'widget': swatch, 'color_instr': color_instr, 'rect_instr': rect_instr}
                
                edit_button_text = f"#{''.join([f'{int(c*255):02x}' for c in rgba_tuple[:3]])}" # RGB Hex
                edit_button = Button(text=edit_button_text, size_hint_x=0.7)

                def open_color_picker_popup(button_instance, current_param_obj, node_ref):
                    # Callback for the popup
                    def popup_callback(new_color_rgba):
                        node_ref.set_parameter_value(current_param_obj.name, new_color_rgba)
                        
                        # Update inspector swatch and button text
                        swatch_data = self.inspector_color_swatches.get(current_param_obj.name)
                        if swatch_data:
                            swatch_data['color_instr'].rgba = new_color_rgba
                        
                        hex_str = f"#{''.join([f'{int(c*255):02x}' for c in new_color_rgba[:3]])}"
                        button_instance.text = hex_str # Update button text with new hex
                        
                        app = App.get_running_app()
                        if app: # Notify for preview update if necessary
                            print(f"Color changed to: {new_color_rgba}, updating preview...")
                            app.notify_parameter_changed(node_ref, current_param_obj.name)
                            # Force immediate preview update
                            if app.preview_window and node_ref == app.selected_node:
                                app.preview_window.update_preview(node_ref)

                    # Get current value safely for the popup
                    current_val_for_popup = node_ref.get_parameter_value(current_param_obj.name)
                    if not (isinstance(current_val_for_popup, (list, tuple)) and len(current_val_for_popup) == 4):
                         current_val_for_popup = (1.0,1.0,1.0,1.0) # Default for popup
                    else:
                        try: 
                            current_val_for_popup = tuple(float(c) for c in current_val_for_popup)
                        except (ValueError, TypeError): 
                            current_val_for_popup = (1.0,1.0,1.0,1.0)

                    popup = ColorPickerPopup(
                        initial_color=current_val_for_popup,
                        callback=popup_callback
                    )
                    popup.open()

                # Pass the param object and the observed_node to the handler
                edit_button.bind(on_release=partial(open_color_picker_popup, current_param_obj=param, node_ref=self.observed_node))
                
                color_display_layout.add_widget(swatch)
                color_display_layout.add_widget(edit_button)
                editor_widget = color_display_layout
            
            # Fallback for unhandled types (after all specific elif branches)
            if editor_widget is None: # Check if any previous block handled it
                 editor_widget = Label(text=f"Unhandled: {str(param.value)}", size_hint_y=None, height=dp(30))

            # Add the created editor widget
            self.params_layout.add_widget(editor_widget)

class TimelinePanel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = 0.25 # Overall panel size hint

        with self.canvas.before:
            Color(rgba=get_color_from_hex('#202020'))
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self._update_rect, size=self._update_rect)

        title_label = Label(text="Timeline / Dopesheet", size_hint_y=None, height=dp(25), bold=True)
        self.add_widget(title_label)

        # --- Control Bar (Time Label, Slider, and Key Buttons) ---
        control_bar = BoxLayout(size_hint_y=None, height=dp(30), padding=(dp(5), 0), spacing=dp(5))
        self.time_label = Label(text="T: 0.00s", size_hint_x=0.15, shorten=True)
        control_bar.add_widget(self.time_label)

        self.time_slider = Slider(min=0, max=1.0, value=0, step=0.01, size_hint_x=0.55)
        control_bar.add_widget(self.time_slider)
        
        # Auto Key Toggle Button
        self.auto_key_button = Button(text="Auto Key: OFF", size_hint_x=0.15)
        self.auto_key_button.bind(on_release=self.toggle_auto_key)
        control_bar.add_widget(self.auto_key_button)
        
        # Manual Key Button
        manual_key_button = Button(text="Key", size_hint_x=0.15)
        manual_key_button.bind(on_release=self.create_manual_key)
        control_bar.add_widget(manual_key_button)
        
        self.add_widget(control_bar)

        # --- Main Horizontal Scroll View for Timeline Content ---
        self.main_timeline_scroll = ScrollView(
            size_hint_y=None, height=dp(30),
            do_scroll_x=True, do_scroll_y=False,
            bar_width=dp(8), bar_color=get_color_from_hex('#666666'),
            bar_inactive_color=get_color_from_hex('#444444')
        )
        
        # This layout's width will be dynamic based on loop_duration
        self.scrollable_content_layout = BoxLayout(
            orientation='vertical', 
            size_hint=(None, 1), # size_hint_x=None, size_hint_y=1 to fill scrollview height
        )
        self.scrollable_content_layout.bind(minimum_width=self.scrollable_content_layout.setter('width'))
        
        # --- Widget for drawing Frame Ticks and Labels ---
        self.frame_numbers_widget = Widget(
            size_hint_y=None, height=dp(25)
        )
        # --- Widget for drawing Keyframe Tracks and Playhead ---
        self.keyframe_tracks_widget = Widget(
            size_hint_y=None, height=dp(35)
        )
        with self.keyframe_tracks_widget.canvas.before: # Background for keyframe area
            Color(rgba=get_color_from_hex('#282828'))
            self.keyframe_area_bg_rect = Rectangle(pos=(0,0), size=self.keyframe_tracks_widget.size) # Pos is local
        with self.keyframe_tracks_widget.canvas.after: # Playhead on top
            Color(rgba=get_color_from_hex('#FF3333')) # Bright red for playhead
            self.playhead_line = Line(points=[0, 0, 0, self.keyframe_tracks_widget.height], width=1.5)

        self.scrollable_content_layout.add_widget(self.frame_numbers_widget)
        self.scrollable_content_layout.add_widget(self.keyframe_tracks_widget)
        self.main_timeline_scroll.add_widget(self.scrollable_content_layout)
        self.add_widget(self.main_timeline_scroll)

        self.add_widget(Widget()) # Spacer to push timeline content up

        # Bindings
        app = App.get_running_app()
        if app:
            app.bind(current_time=self.on_app_current_time_change)
            self.time_slider.bind(value=self.on_slider_time_change)
            if app.effect_ir:
                app.effect_ir.bind(loop_duration=self.on_loop_duration_change)
                self.on_loop_duration_change(app.effect_ir, app.effect_ir.loop_duration) # Initial setup
            else: # Fallback if effect_ir is not ready
                self.time_slider.max = 1.0 
                self._redraw_timeline_markings(1.0)

    def _redraw_timeline_markings(self, loop_duration):
        if loop_duration <= 0: loop_duration = 1.0 # Avoid division by zero or negative width
        
        new_width = loop_duration * dp(120) # Assuming DP_PER_SECOND_TIMELINE is defined elsewhere
        self.scrollable_content_layout.width = new_width
        
        # Redraw Frame Numbers/Ticks
        self.frame_numbers_widget.canvas.clear()
        with self.frame_numbers_widget.canvas:
            Color(rgba=get_color_from_hex('#777777')) # Tick color
            num_minor_ticks = int(loop_duration / 0.1) # Assuming MINOR_TICK_INTERVAL_SECONDS is defined elsewhere
            for i in range(num_minor_ticks + 1):
                time_s = i * 0.1
                x_pos = time_s * dp(120)
                is_major_tick = abs(time_s % 1.0) < 0.05 # Assuming MAJOR_TICK_INTERVAL_SECONDS is defined elsewhere
                is_tenth_second_ish = abs(time_s % 0.5) < 0.05 # For labels

                tick_height = dp(25) * (0.6 if is_major_tick else (0.4 if is_tenth_second_ish else 0.25))
                Line(points=[x_pos, 0, x_pos, tick_height], width=1)

                if is_major_tick or (loop_duration <=2 and is_tenth_second_ish) : # Show labels for major ticks
                    lbl = Label(text=f"{time_s:.1f}s", font_size='10sp', size=(dp(40), dp(20)))
                    lbl.texture_update()
                    lbl.pos = (x_pos - lbl.texture_size[0] / 2, dp(25) * 0.65)
                    lbl.color = get_color_from_hex('#AAAAAA')
                    # Add instruction to draw the label's texture
                    Rectangle(texture=lbl.texture, pos=lbl.pos, size=lbl.texture_size)
        
        # Redraw Mock Keyframes on keyframe_tracks_widget
        self.keyframe_tracks_widget.canvas.remove_group('mock_keyframes') # Clear previous keyframes
        with self.keyframe_tracks_widget.canvas:
            Color(rgba=get_color_from_hex('#FFA726')) # Amber color for keyframes
            
            # Get actual keyframes from EffectIR for the selected node
            app = App.get_running_app()
            if app and app.selected_node and hasattr(app, 'effect_ir') and app.effect_ir:
                selected_node = app.selected_node
                if hasattr(selected_node, 'node_id'):
                    # Collect all keyframe times for this node
                    keyframe_times = set()
                    for timeline_path, animated_param in app.effect_ir.timelines.items():
                        if timeline_path.startswith(f"{selected_node.node_id}/"):
                            for keyframe in animated_param.keyframes:
                                if 0 <= keyframe.time <= loop_duration:
                                    keyframe_times.add(keyframe.time)
                    
                    # Draw keyframes
                    for kt_s in keyframe_times:
                        x_pos = kt_s * dp(120)
                        key_y = self.keyframe_tracks_widget.height / 2 - dp(5) / 2 # Centered
                        Ellipse(pos=(x_pos - dp(2.5), key_y), size=(dp(5), dp(5)), group='mock_keyframes')
            else:
                # Fallback: Show mock keyframes if no node selected or no EffectIR
                key_times = [0.5, 1.2, 2.5] 
                for kt_s in key_times:
                    if kt_s <= loop_duration:
                        x_pos = kt_s * dp(120)
                        key_y = self.keyframe_tracks_widget.height / 2 - dp(5) / 2 # Centered
                        Ellipse(pos=(x_pos - dp(2.5), key_y), size=(dp(5), dp(5)), group='mock_keyframes')
        
        self.keyframe_tracks_widget.canvas.ask_update()
        self.frame_numbers_widget.canvas.ask_update()
        self.update_playhead_position(App.get_running_app().current_time if App.get_running_app() else 0)

    def on_app_current_time_change(self, instance, value):
        self.time_label.text = f"T: {value:.2f}s"
        if abs(self.time_slider.value - value) > (self.time_slider.step or 0.01)/2: # Avoid feedback loop, consider step
            self.time_slider.value = value
        self.update_playhead_position(value)

    def on_slider_time_change(self, instance, value):
        app = App.get_running_app()
        if app and abs(app.current_time - value) > (self.time_slider.step or 0.01)/2: # Avoid feedback loop
            app.current_time = value

    def on_loop_duration_change(self, instance, value):
        if value <= 0: value = 1.0 # Sensible minimum for display
        self.time_slider.max = value
        self._redraw_timeline_markings(value)
        # If current_time is beyond new loop_duration, clamp it (optional)
        app = App.get_running_app()
        if app and app.current_time > value:
            app.current_time = value
        self.update_playhead_position(app.current_time if app else 0)

    def _update_rect(self, instance, value): # Updates main panel background
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
        # Update child widget sizes that depend on panel size if necessary
        self.keyframe_tracks_widget.width = self.scrollable_content_layout.width
        self.frame_numbers_widget.width = self.scrollable_content_layout.width
        self.keyframe_area_bg_rect.size = (self.scrollable_content_layout.width, self.keyframe_tracks_widget.height)

    def update_playhead_position(self, current_time):
        app = App.get_running_app()
        loop_duration = 1.0 # Default if IR not ready
        if app and hasattr(app, 'effect_ir') and app.effect_ir and app.effect_ir.loop_duration > 0:
            loop_duration = app.effect_ir.loop_duration
        
        # Playhead position relative to the start of scrollable_content_layout
        playhead_x_on_scrollable_content = (current_time / loop_duration) * self.scrollable_content_layout.width
        
        # The playhead_line is drawn on keyframe_tracks_widget.canvas.
        # Its coordinates are local to keyframe_tracks_widget.
        # Since keyframe_tracks_widget is a direct child of scrollable_content_layout and fills its width,
        # this playhead_x_on_scrollable_content is the correct local X for the line.
        self.playhead_line.points = [
            playhead_x_on_scrollable_content, 0,
            playhead_x_on_scrollable_content, self.keyframe_tracks_widget.height
        ]
        # print(f"Playhead Time: {current_time:.2f}, X: {playhead_x_on_scrollable_content:.2f}, Duration: {loop_duration}, ScrollWidth: {self.scrollable_content_layout.width}")

    def toggle_auto_key(self, instance):
        """Toggle Auto Key mode on/off"""
        app = App.get_running_app()
        if app:
            app.auto_key_enabled = not app.auto_key_enabled
            if app.auto_key_enabled:
                self.auto_key_button.text = "Auto Key: ON"
                # Color the button to indicate it's active (red/orange)
                self.auto_key_button.background_color = (1.0, 0.5, 0.2, 1.0)  # Orange
            else:
                self.auto_key_button.text = "Auto Key: OFF"
                # Reset to default color
                self.auto_key_button.background_color = (1, 1, 1, 1)  # Default
            print(f"Auto Key {'enabled' if app.auto_key_enabled else 'disabled'}")

    def create_manual_key(self, instance):
        """Create manual keyframes for the selected node"""
        app = App.get_running_app()
        if app:
            app.create_manual_keyframe()

class SparcleApp(App):
    selected_node = ObjectProperty(None, allownone=True)
    inspector_panel = ObjectProperty(None)
    preview_window = ObjectProperty(None)
    effect_ir = ObjectProperty(None) 
    current_time = NumericProperty(0.0) # Add current_time property
    auto_key_enabled = BooleanProperty(False) # Add auto key toggle state

    def on_current_time(self, instance, value): # Kivy property observer
        # This method is automatically called when self.current_time changes.
        # We need to update the preview if a node is selected.
        print(f"SparcleApp.current_time changed to: {value:.2f}s")
        if self.selected_node and self.preview_window:
            self.preview_window.update_preview(self.selected_node)

    def build(self):
        self.effect_ir = EffectIR() 
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

        # Create and add the actual PreviewWindow
        self.preview_window = PreviewWindow()
        preview_panel_container = BoxLayout(size_hint_x=0.3)
        preview_panel_container.add_widget(self.preview_window)
        top_panels_container.add_widget(preview_panel_container)

        right_dock_panel = BoxLayout(orientation='vertical', size_hint_x=0.3)
        tree_panel = BoxLayout(size_hint_y=0.5)
        tree_panel.add_widget(PlaceholderPanel(text='Tree/Hierarchy Area', panel_color_hex='#2C2C2C'))
        right_dock_panel.add_widget(tree_panel)
        
        # Create and add the actual InspectorPanel
        self.inspector_panel = InspectorPanel()
        inspector_panel_container = BoxLayout(size_hint_y=0.5)
        inspector_panel_container.add_widget(self.inspector_panel)
        right_dock_panel.add_widget(inspector_panel_container)
        
        top_panels_container.add_widget(right_dock_panel)
        
        main_content_area.add_widget(top_panels_container) # Add top panels to main content area

        self.timeline_panel = TimelinePanel()
        main_content_area.add_widget(self.timeline_panel)

        root_layout.add_widget(main_content_area) # Add main content area to root

        self.inspector_panel.observe_node(None) # Initialize with no node selected
        self.preview_window.update_preview(None) # Initialize preview
        return root_layout

    def select_node(self, node_to_select):
        if self.selected_node == node_to_select:
            return

        if self.selected_node:
            self.selected_node.is_selected = False
        
        self.selected_node = node_to_select
        if self.selected_node:
            self.selected_node.is_selected = True
        
        print(f"Selected node: {self.selected_node.title if self.selected_node else 'None'}")
        if self.inspector_panel:
            self.inspector_panel.observe_node(self.selected_node) # Update inspector
        if self.preview_window:
            self.preview_window.update_preview(self.selected_node) # Update preview on selection

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

    def notify_parameter_changed(self, changed_node, param_name):
        print(f"Node '{changed_node.title}' parameter '{param_name}' changed.")
        
        # Auto Key: If auto key is enabled and we have a selected source node, create a keyframe
        if self.auto_key_enabled and isinstance(changed_node, SourceNode):
            self.create_keyframe_for_parameter(changed_node, param_name)
        
        # Force clear particles for immediate color feedback
        if param_name == "particle_color" and self.preview_window and changed_node == self.selected_node:
            print("Clearing existing particles due to color change")
            self.preview_window.particles.clear()
        
        if self.preview_window and changed_node == self.selected_node:
            if isinstance(changed_node, SourceNode) and param_name in ["emission_rate", "lifespan", "particle_color", "initial_velocity", "emitter_position"]:
                 self.preview_window.update_preview(changed_node)
            # For other node types or params, could have different handling

    def create_keyframe_for_parameter(self, node, param_name):
        """Create a keyframe at current_time for the given node parameter"""
        if not self.effect_ir:
            return
            
        # Get current parameter value
        current_value = node.get_parameter_value(param_name)
        if current_value is None:
            return
            
        # Create timeline path
        timeline_path = f"{node.node_id}/{param_name}"
        
        # Get or create AnimatedParameter
        animated_param = self.effect_ir.timelines.get(timeline_path)
        if animated_param is None:
            # Create new AnimatedParameter with just this keyframe
            from src.core.ir import AnimatedParameter, TimelineKeyframe
            animated_param = AnimatedParameter(keyframes=[
                TimelineKeyframe(time=self.current_time, value=current_value)
            ])
            self.effect_ir.add_or_update_timeline(timeline_path, animated_param)
        else:
            # Add keyframe to existing AnimatedParameter
            from src.core.ir import TimelineKeyframe
            new_keyframe = TimelineKeyframe(time=self.current_time, value=current_value)
            
            # Remove existing keyframe at this time if it exists
            animated_param.keyframes = [kf for kf in animated_param.keyframes if abs(kf.time - self.current_time) > 0.001]
            
            # Add new keyframe and re-sort
            animated_param.keyframes.append(new_keyframe)
            animated_param.keyframes.sort(key=lambda kf: kf.time)
        
        print(f"Created keyframe for {timeline_path} at T={self.current_time:.2f} with value {current_value}")
        
        # Update timeline display
        if hasattr(self, 'timeline_panel'):
            self.timeline_panel._redraw_timeline_markings(self.effect_ir.loop_duration)

    def create_manual_keyframe(self):
        """Manually create keyframes for all parameters of the selected node at current time"""
        if not self.selected_node or not isinstance(self.selected_node, SourceNode):
            print("No source node selected for manual keyframe")
            return
            
        # Create keyframes for all parameters
        for param in self.selected_node.parameters:
            self.create_keyframe_for_parameter(self.selected_node, param.name)
        
        print(f"Created manual keyframes for all parameters of '{self.selected_node.title}' at T={self.current_time:.2f}")

if __name__ == '__main__':
    SparcleApp().run() 