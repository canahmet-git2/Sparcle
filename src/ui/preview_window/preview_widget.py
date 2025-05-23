from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle, PushMatrix, PopMatrix, Rotate, Translate, Callback
from kivy.graphics.opengl import GL_SRC_ALPHA, GL_ONE, GL_ONE_MINUS_SRC_ALPHA, GL_ZERO, GL_SRC_COLOR, GL_ONE_MINUS_SRC_COLOR, GL_DST_COLOR, GL_DST_ALPHA, GL_ONE_MINUS_DST_COLOR, GL_ONE_MINUS_DST_ALPHA, glBlendFuncSeparate # Added missing ones
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.properties import ObjectProperty, ListProperty
from kivy.config import Config

# Assuming ir.py and particle_system.py are in src.core
# Adjust import paths if necessary based on your project structure
import sys
import os
# Add src directory to Python path to allow direct imports of core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from core.ir import EffectIR, EmitterProperties, EmitterParameter, SpriteAsset, SpriteDefinition
from core.particle_system import ParticleSystem, Particle

# Placeholder for actual texture loading, Kivy requires textures to be loaded
# typically via Image.texture or similar.
# We will handle actual texture loading later. For now, sprite_info might just store path.

class PreviewWidget(Widget):
    effect_ir = ObjectProperty(None)
    particle_system = ObjectProperty(None)
    
    # Store texture references here once loaded
    _sprite_textures = {} # Dict to hold {definition_id: KivyTexture}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.draw_background() # Draw the background first
        self.setup_effect()
        Clock.schedule_interval(self.update_simulation, 1.0 / 60.0)
        self.bind(size=self.redraw_background) # Redraw background if widget size changes

    def draw_background(self, *args):
        with self.canvas.before:
            self.canvas.before.clear()
            # Checkerboard background
            color1 = (0.4, 0.4, 0.4, 1) # Dark gray
            color2 = (0.5, 0.5, 0.5, 1) # Light gray
            step = 20 # Size of each checker square

            for y in range(0, int(self.height) + step, step):
                for x in range(0, int(self.width) + step, step):
                    idx = (x // step + y // step) % 2
                    Color(*(color1 if idx == 0 else color2))
                    Rectangle(pos=(x, y), size=(step, step))
    
    def redraw_background(self, *args):
        # This ensures the background is redrawn when the widget size changes.
        # We might need to be more sophisticated if there are other static elements
        # in canvas.before, but for now, clearing and redrawing is fine.
        self.draw_background()

    def setup_effect(self):
        self.effect_ir = EffectIR(loop_duration=5.0)

        # 1. Define Sprite Asset(s)
        # For now, let's assume a placeholder image. You'll need to create this image.
        # Kivy's image loading happens differently; this is just data for now.
        # The actual texture loading will happen in load_sprite_textures()
        asset1 = SpriteAsset(asset_id="particle_atlas_01", 
                             path="assets/placeholder_particle.png", # IMPORTANT: Create this image!
                             width=31, height=31) # UPDATED to actual image dimensions
        self.effect_ir.add_sprite_asset(asset1)

        # 2. Define Sprite Definition(s)
        spark_def = SpriteDefinition(
            definition_id="default_spark", 
            asset_id="particle_atlas_01", 
            region=(1, 1, 29, 29), # Reverted to 1px inset
            name="Default Spark"
        )
        self.effect_ir.add_sprite_definition(spark_def)
        
        # Attempt to load textures for defined sprites
        self.load_sprite_textures()

        # 3. Define Emitter Properties
        emitter_params = {
            "emission_rate": EmitterParameter(name="emission_rate", value=20.0),
            "lifespan_range": EmitterParameter(name="lifespan_range", value=(1.0, 2.5)),
            "sprite_definition_id": EmitterParameter(name="sprite_definition_id", value="default_spark"),
            "initial_direction_vector": EmitterParameter(name="initial_direction_vector", value=(0, 1)),
            "speed_range": EmitterParameter(name="speed_range", value=(100.0, 150.0)),
            "emission_angle_range_deg": EmitterParameter(name="emission_angle_range_deg", value=(-25.0, 25.0)),
            "size_range": EmitterParameter(name="size_range", value=(16.0, 32.0)), 
            "rotation_range_deg": EmitterParameter(name="rotation_range_deg", value=(0.0, 0.0)),
            "angular_velocity_range_dps": EmitterParameter(name="angular_velocity_range_dps", value=(0.0, 0.0)),
            "acceleration_vector": EmitterParameter(name="acceleration_vector", value=(0.0, -50.0)),
            "orient_to_velocity": EmitterParameter(name="orient_to_velocity", value=True),
            # Removed opacity_over_lifespan for this test
            # Removed particle_color_tint for this test
            "particle_color": EmitterParameter(name="particle_color", value=(1.0, 1.0, 1.0, 0.7)) # Fixed 70% white
        }
        
        source_emitter = EmitterProperties(
            emitter_id="emitter01",
            emitter_type="PointParticleEmitter",
            name="MyKivyEmitter",
            parameters=emitter_params,
            blending_mode="alpha"  # Focus on alpha mode
        )
        # Manually set emitter_position as it's not an EmitterParameter in this simplified setup
        # In a full node system, this would be a property of the emitter node.
        # For now, we'll make ParticleSystem use its own center if not found in parameters.
        # Or, we add it to parameters like other properties:
        emitter_params["emitter_position"] = EmitterParameter(name="emitter_position", value=(self.center_x, self.center_y))


        self.effect_ir.add_emitter(source_emitter)

        # 4. Create Particle System
        self.particle_system = ParticleSystem(
            effect_ir=self.effect_ir, 
            emitter_id="emitter01"
        )
        
        # Bind emitter_position to widget center (or allow it to be set)
        self.bind(center=self.update_emitter_position)
        self.update_emitter_position() # Initial set

    def load_sprite_textures(self):
        if not self.effect_ir:
            return
        for def_id, sprite_def in self.effect_ir.sprite_definitions.items():
            asset = self.effect_ir.get_sprite_asset(sprite_def.asset_id)
            if asset:
                try:
                    # CoreImage is used for loading, its texture is what we need.
                    # This path should be relative to the application's execution directory
                    # or an absolute path.
                    image = CoreImage(asset.path, nocache=True)
                    if image.texture:
                        # Get the subtexture (region)
                        # sprite_def.region is (x_tl, y_tl, w, h) from top-left
                        # Kivy's get_region expects (x_bl, y_bl, w, h) from bottom-left
                        rx, ry_tl, rw, rh = sprite_def.region
                        ry_bl = asset.height - ry_tl - rh # Convert y from top-left to bottom-left
                        
                        region_texture = image.texture.get_region(rx, ry_bl, rw, rh)
                        
                        # Avoid sampling outside the sprite region which causes white borders in Screen mode
                        region_texture.wrap = 'clamp_to_edge'
                        region_texture.mag_filter = 'nearest'
                        region_texture.min_filter = 'nearest'
                        
                        self._sprite_textures[def_id] = region_texture
                        print(f"Successfully loaded texture for: {def_id} from {asset.path}")
                    else:
                        print(f"Error: Could not get texture from image: {asset.path} for sprite {def_id}")
                except Exception as e:
                    print(f"Error loading image {asset.path} for sprite {def_id}: {e}")
            else:
                print(f"Error: Asset {sprite_def.asset_id} not found for sprite {def_id}")


    def update_emitter_position(self, *args):
        if self.effect_ir and self.particle_system: # Check if particle_system exists
            emitter = self.effect_ir.get_emitter("emitter01")
            if emitter:
                # Update the base value of the emitter_position parameter
                emitter.set_param_value("emitter_position", self.center)
                # print(f"Emitter position updated to: {self.center}")


    def update_simulation(self, dt):
        if self.particle_system:
            current_time = Clock.get_time() # Or manage a specific timeline time
            self.particle_system.update(dt, current_time)
            self.canvas.clear() # Clear previous frame
            self.draw_particles()

    def draw_particles(self):
        if not self.particle_system or not self.effect_ir:
            return

        # Get the current emitter (assuming one for now)
        emitter = self.effect_ir.get_emitter(self.particle_system.emitter_id)
        if not emitter:
            return

        current_blend_mode = emitter.blending_mode
        
        # Store Kivy's default blend func to restore later
        # Kivy default is (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) for both color and alpha
        default_src_rgb = GL_SRC_ALPHA
        default_dst_rgb = GL_ONE_MINUS_SRC_ALPHA
        default_src_alpha = GL_SRC_ALPHA
        default_dst_alpha = GL_ONE_MINUS_SRC_ALPHA

        with self.canvas:
            # We need to use a Callback to make raw OpenGL calls at the right time in Kivy's graphics pipeline.
            if current_blend_mode == "additive":
                # Common non-PMA Additive: Src*SrcAlpha + Dst*1
                Callback(lambda instr: glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE, GL_SRC_ALPHA, GL_ONE))
            elif current_blend_mode == "alpha": # Standard non-PMA alpha blending
                # Result = Src*SrcAlpha + Dst*(1-SrcAlpha)
                Callback(lambda instr: glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA))
            elif current_blend_mode == "multiply":
                # Multiply: Dst * Src (DstRGB * SrcRGB, DstAlpha * SrcAlpha)
                Callback(lambda instr: glBlendFuncSeparate(GL_DST_COLOR, GL_ZERO, GL_DST_ALPHA, GL_ZERO))
            elif current_blend_mode == "screen":
                # Screen with source pre-multiplied by its alpha: Src*SrcA + Dst*(1-SrcColor)
                # This darkens any fully transparent RGB so they don't lighten the background.
                Callback(lambda instr: glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_COLOR, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA))
            # Add other blend modes here if needed

            for p in self.particle_system.get_alive_particles():
                sprite_def_id = p.sprite_definition_id
                texture = self._sprite_textures.get(sprite_def_id)

                if not texture:
                    # Fallback: draw a small red dot if texture not found
                    Color(1, 0, 0, 1) # Red, Opaque
                    PushMatrix()
                    Translate(p.position[0] - 2, p.position[1] - 2) # Center the dot
                    # No rotation for a simple dot
                    Rectangle(size=(4, 4)) # Small 4x4 dot
                    PopMatrix()
                    if sprite_def_id and sprite_def_id not in self._sprite_textures:
                         # Print warning only once per missing texture to avoid spam
                        # print(f"Warning: Texture not found for {sprite_def_id}. Drawing fallback.")
                        # self._sprite_textures[sprite_def_id] = None # Mark as checked to avoid spam
                        pass
                    continue

                # If texture found, draw it
                sprite_definition = self.effect_ir.get_sprite_definition(sprite_def_id)
                if not sprite_definition: # Should not happen if texture was found by its ID
                    continue 

                # Calculate drawing origin based on pivot
                # SpriteDefinition region is (x,y,w,h), texture.size is (w,h) of the region
                draw_w, draw_h = texture.size[0], texture.size[1]
                
                # Scale particle size relative to base texture size - this needs refinement.
                # For now, let particle.size directly be the screen size.
                display_size_w = p.size 
                display_size_h = p.size * (draw_h / draw_w if draw_w != 0 else 1.0)


                # Pivot is normalized (0-1) relative to sprite definition region
                # Origin for Kivy rotation is relative to the particle's bottom-left after translation
                origin_x = display_size_w * sprite_definition.pivot[0]
                origin_y = display_size_h * sprite_definition.pivot[1]
                
                pos_x = p.position[0] - origin_x
                pos_y = p.position[1] - origin_y

                # Apply tint if present (TEMPORARILY REMOVED FOR TESTING)
                # final_color = list(p.color)
                # if self.particle_system and self.particle_system.emitter_properties:
                #     tint = self.particle_system.emitter_properties.get_param_value("particle_color_tint", None)
                #     if tint:
                #         final_color[0] *= tint[0]
                #         final_color[1] *= tint[1]
                #         final_color[2] *= tint[2]
                #         # final_color[3] *= tint[3] # Usually don't tint alpha, particle's own alpha is king

                Color(p.color[0], p.color[1], p.color[2], p.color[3]) # Use p.color directly for this test
                PushMatrix()
                Translate(pos_x, pos_y)
                Rotate(angle=p.rotation, origin=(origin_x, origin_y))
                Rectangle(texture=texture, size=(display_size_w, display_size_h))
                PopMatrix()
            
            # Restore default blending mode after drawing all particles for this emitter
            Callback(lambda instr: glBlendFuncSeparate(default_src_rgb, default_dst_rgb, default_src_alpha, default_dst_alpha))

if __name__ == '__main__':
    from kivy.app import App
    from kivy.uix.slider import Slider # Will be used later, good to have for now
    Config.set('input', 'mouse', 'mouse,disable_multitouch') # Disable multitouch emulation for mouse

    class PreviewApp(App):
        def build(self):
            root_layout = BoxLayout(orientation='horizontal')
            
            preview_widget = PreviewWidget(size_hint=(0.7, 1))
            
            controls_layout = BoxLayout(orientation='vertical', size_hint=(0.3, 1), padding=10, spacing=5)

            # Blend Mode Control
            controls_layout.add_widget(Label(text='Blend Mode:', size_hint_y=None, height=30))
            blend_mode_spinner = Spinner(
                text=preview_widget.effect_ir.get_emitter("emitter01").blending_mode, # Initial value
                values=("alpha", "additive", "multiply", "screen"), # Added screen
                size_hint_y=None,
                height=40
            )
            def on_blend_mode_change(spinner, text):
                if preview_widget.effect_ir and preview_widget.effect_ir.get_emitter("emitter01"):
                    preview_widget.effect_ir.get_emitter("emitter01").blending_mode = text
            
            blend_mode_spinner.bind(text=on_blend_mode_change)
            controls_layout.add_widget(blend_mode_spinner)

            # Placeholder for more controls
            controls_layout.add_widget(Widget()) #占位符 

            root_layout.add_widget(preview_widget)
            root_layout.add_widget(controls_layout)

            # Create a placeholder image if it doesn't exist for the demo to run
            if not os.path.exists("assets/placeholder_particle.png"):
                os.makedirs("assets", exist_ok=True)
                try:
                    from PIL import Image as PILImage, ImageDraw as PILImageDraw
                    img = PILImage.new('RGBA', (64, 64), (0,0,0,0)) # Transparent
                    draw = PILImageDraw.Draw(img)
                    # Simple white circle
                    draw.ellipse((4, 4, 60, 60), fill=(255,255,255,255))
                    img.save("assets/placeholder_particle.png")
                    print("Created placeholder_particle.png in assets/")
                except ImportError:
                    print("Pillow not installed. Cannot create placeholder image. Please create assets/placeholder_particle.png manually (e.g. a 64x64 white circle).")
                except Exception as e_img:
                    print(f"Error creating placeholder image: {e_img}")


            return root_layout

    PreviewApp().run() 