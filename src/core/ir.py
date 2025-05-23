from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional
from kivy.event import EventDispatcher # Import EventDispatcher
from kivy.properties import NumericProperty, ObjectProperty, DictProperty # Added DictProperty

# Re-using ParamType from main.py for consistency, though it might live elsewhere eventually
# For now, assume it's accessible or we'll duplicate/move it later.
# from main import ParamType # This will cause circular import if not handled carefully.
# For now, let's define a simplified version or placeholder if direct import is an issue.

class ParamTypePlaceholder: # Placeholder to avoid direct import for now
    FLOAT = float
    INT = int
    STRING = str
    BOOLEAN = bool
    COLOR = tuple 
    VECTOR2 = tuple
    # ... add others as needed by IR

@dataclass
class EmitterParameter:
    name: str
    # param_type: ParamTypePlaceholder # Or a more generic type system for IR
    value: Any
    # Potentially add timeline_id if this parameter is animated

@dataclass
class EmitterProperties:
    emitter_id: str
    emitter_type: str # e.g., "PointEmitter", "LineEmitter" - for future expansion
    name: str = "Default Emitter"
    parameters: Dict[str, EmitterParameter] = field(default_factory=dict)
    # Example parameters that a source node might manage:
    # emission_rate: float = 10.0
    # lifespan: float = 2.0
    # particle_color: Tuple[float, float, float, float] = (1.0, 1.0, 0.0, 1.0)
    # initial_velocity: Tuple[float, float] = (0.0, 100.0)
    # emitter_position: Tuple[float, float] = (0.0, 0.0)

    # For now, parameters will be stored in the dict above.
    # The direct attributes are commented out as they'd be represented in the dict.

    def get_param_value(self, param_name: str, default: Any = None) -> Any:
        # This will return the BASE value, not the animated one.
        if param_name in self.parameters:
            return self.parameters[param_name].value
        return default

    def set_param_value(self, param_name: str, value: Any):
        # This sets the BASE value.
        if param_name in self.parameters:
            self.parameters[param_name].value = value
        else:
            # For now, create if not exists, as set_parameter_value in NodeWidget does this
            self.parameters[param_name] = EmitterParameter(name=param_name, value=value)
            print(f"Info: Parameter '{param_name}' created for emitter '{self.emitter_id}' with value {value}.")


@dataclass
class TimelineKeyframe:
    time: float # In seconds
    value: Any
    interpolation_mode: str = "linear" # Default to linear

@dataclass
class AnimatedParameter:
    # parameter_path: str # e.g., "emitter_id/param_name"
    # No longer needed if AnimatedParameter is stored directly in EmitterProperties or looked up by its key in EffectIR.timelines
    keyframes: List[TimelineKeyframe] = field(default_factory=list)

    def __post_init__(self):
        # Ensure keyframes are sorted by time upon initialization and modification
        self.sort_keyframes()

    def add_keyframe(self, keyframe: TimelineKeyframe):
        self.keyframes.append(keyframe)
        self.sort_keyframes()
    
    def sort_keyframes(self):
        self.keyframes.sort(key=lambda kf: kf.time)

    def get_value_at_time(self, time: float, default_value: Any) -> Any:
        if not self.keyframes:
            return default_value

        # self.sort_keyframes() # No longer needed here if sorted on modification

        if time < self.keyframes[0].time:
            # For times before the first keyframe, use the first keyframe's value (hold)
            return self.keyframes[0].value 

        if time >= self.keyframes[-1].time:
            # For times at or after the last keyframe, use the last keyframe's value (hold)
            return self.keyframes[-1].value

        # Find the two keyframes to interpolate between
        for i in range(len(self.keyframes) - 1):
            kf1 = self.keyframes[i]
            kf2 = self.keyframes[i+1]
            
            if kf1.time <= time < kf2.time:
                # Determine interpolation mode ( defaulting to kf1.interpolation_mode)
                interp_mode = kf1.interpolation_mode

                if interp_mode == "step":
                    return kf1.value
                
                # Linear interpolation (default)
                if kf2.time == kf1.time: # Avoid division by zero
                    return kf1.value
                t_ratio = (time - kf1.time) / (kf2.time - kf1.time)

                # Numeric interpolation (float, int)
                if isinstance(kf1.value, (int, float)) and isinstance(kf2.value, (int, float)):
                    return kf1.value + (kf2.value - kf1.value) * t_ratio
                
                # Tuple/List interpolation (for Color, Vector2, etc.)
                elif isinstance(kf1.value, (tuple, list)) and isinstance(kf2.value, (tuple, list)) and len(kf1.value) == len(kf2.value):
                    try:
                        interpolated_tuple = tuple(v1 + (v2 - v1) * t_ratio for v1, v2 in zip(kf1.value, kf2.value))
                        return interpolated_tuple
                    except TypeError: # In case tuple elements are not numbers
                        return kf1.value # Fallback to step
                
                return kf1.value # Default fallback: step interpolation for other types
        
        return default_value # Should not be reached if logic above is correct


@dataclass
class SpriteAsset:
    asset_id: str # Unique ID for this asset, e.g., "atlas_01"
    path: str     # File path to the image, e.g., "assets/particles.png"
    width: int    # Width of the image in pixels
    height: int   # Height of the image in pixels

@dataclass
class SpriteDefinition:
    definition_id: str # Unique ID for this sprite definition, e.g., "sparkle_frame_01"
    asset_id: str      # ID of the SpriteAsset this definition belongs to
    # UV coordinates defining the region within the asset image
    # (x, y, width, height) in pixels, from top-left of the asset image
    region: Tuple[int, int, int, int] 
    # Optional: pivot point (normalized, 0-1 relative to region, default center)
    pivot: Tuple[float, float] = (0.5, 0.5) 
    # Optional: name for easier lookup in editor, if different from definition_id
    name: Optional[str] = None 


class EffectIR(EventDispatcher):
    version = ObjectProperty("0.1.0") # Can be ObjectProperty for strings/other objects
    loop_duration = NumericProperty(5.0) # Use Kivy NumericProperty
    
    # emitters list might also become a Kivy ListProperty if we need to observe its changes directly
    # For now, keep it as a Python list, changes managed by add_emitter/get_emitter

    # Using DictProperty for timelines so Kivy can observe changes if we modify the dict itself.
    # Key: parameter_path (e.g., "emitter_id/param_name"), Value: AnimatedParameter instance
    timelines = DictProperty({}) 

    emitters: List[EmitterProperties] = field(default_factory=list) # Made this a field for clarity
    sprite_assets: List[SpriteAsset] = field(default_factory=list)
    sprite_definitions: Dict[str, SpriteDefinition] = field(default_factory=dict)

    def __init__(self, **kwargs):
        super().__init__(**kwargs) # Call EventDispatcher constructor
        self.emitters = [] # Initialize as plain list for now
        self.timelines = {} # Re-initialize if not relying on DictProperty solely for init
        self.sprite_assets = []
        self.sprite_definitions = {}

    def add_emitter(self, emitter_props: EmitterProperties):
        self.emitters.append(emitter_props)
        # If emitters were a ListProperty, you might do: self.emitters.append(emitter_props)
        # and that could trigger bindings if needed.

    def get_emitter(self, emitter_id: str) -> EmitterProperties | None:
        for emitter in self.emitters:
            if emitter.emitter_id == emitter_id:
                return emitter
        return None

    def get_animated_param_value(self, emitter_id: str, param_name: str, time: float) -> Any:
        emitter = self.get_emitter(emitter_id)
        if not emitter:
            print(f"DEBUG EffectIR: Emitter '{emitter_id}' not found")
            return None # Emitter not found

        base_value = emitter.get_param_value(param_name) # Get the non-animated base value as default
        print(f"DEBUG EffectIR: Base value for '{emitter_id}/{param_name}': {base_value}")

        param_path = f"{emitter_id}/{param_name}"
        print(f"DEBUG EffectIR: Looking for timeline path '{param_path}' at time {time:.2f}")
        print(f"DEBUG EffectIR: Available timelines: {list(self.timelines.keys())}")
        
        if param_path in self.timelines:
            animated_param = self.timelines[param_path]
            print(f"DEBUG EffectIR: Found animated parameter with {len(animated_param.keyframes)} keyframes")
            for i, kf in enumerate(animated_param.keyframes):
                print(f"  Keyframe {i}: time={kf.time:.2f}, value={kf.value}")
            
            # Ensure keyframes are sorted by time - ideally do this when keyframes are added/modified
            # For simplicity now, we might sort here or assume sorted.
            # animated_param.keyframes.sort(key=lambda kf: kf.time) # Costly if done every call
            result = animated_param.get_value_at_time(time, default_value=base_value)
            print(f"DEBUG EffectIR: Animated value at T={time:.2f}: {result}")
            return result
        
        print(f"DEBUG EffectIR: No animation found for '{param_path}', returning base value: {base_value}")
        return base_value # No animation found for this parameter, return its base value

    def add_or_update_timeline(self, parameter_path: str, timeline: AnimatedParameter):
        timeline.sort_keyframes()
        self.timelines[parameter_path] = timeline
        # This should trigger Kivy bindings if anything is bound to the timelines DictProperty directly
        # or to specific keys if Kivy supports that deeply.

    def add_sprite_asset(self, asset: SpriteAsset):
        # Check for duplicate asset_id if necessary
        if any(sa.asset_id == asset.asset_id for sa in self.sprite_assets):
            print(f"Warning: SpriteAsset with id '{asset.asset_id}' already exists. Overwriting not implemented.")
            return # Or raise error, or update
        self.sprite_assets.append(asset)

    def get_sprite_asset(self, asset_id: str) -> Optional[SpriteAsset]:
        for asset in self.sprite_assets:
            if asset.asset_id == asset_id:
                return asset
        return None

    def add_sprite_definition(self, definition: SpriteDefinition):
        if definition.definition_id in self.sprite_definitions:
            print(f"Warning: SpriteDefinition with id '{definition.definition_id}' already exists. Overwriting.")
        # Optionally, verify that definition.asset_id refers to an existing SpriteAsset
        if not self.get_sprite_asset(definition.asset_id):
            print(f"Error: Cannot add SpriteDefinition '{definition.definition_id}'. Asset '{definition.asset_id}' not found.")
            return
        self.sprite_definitions[definition.definition_id] = definition

    def get_sprite_definition(self, definition_id: str) -> Optional[SpriteDefinition]:
        return self.sprite_definitions.get(definition_id)

# Example Usage would remain similar, but instantiation of EffectIR is now of an EventDispatcher
if __name__ == '__main__':
    ir = EffectIR(loop_duration=3.0)
    # ir.version = "0.1.1" # This would now use Kivy property setting

    source_emitter_props = EmitterProperties(
        emitter_id="source01",
        emitter_type="PointParticleEmitter",
        name="My Fountain",
        parameters={
            "emission_rate": EmitterParameter(name="emission_rate", value=25.0),
            "lifespan": EmitterParameter(name="lifespan", value=1.5),
            "particle_color": EmitterParameter(name="particle_color", value=(0.2, 0.8, 1.0, 1.0)),
            "initial_velocity": EmitterParameter(name="initial_velocity", value=(0, 50)),
            "emitter_position": EmitterParameter(name="emitter_position", value=(10, -5))
        }
    )
    ir.add_emitter(source_emitter_props)
    print(f"IR loop duration: {ir.loop_duration}")
    ir.loop_duration = 4.5 # This will trigger Kivy property change events
    print(f"Updated IR loop duration: {ir.loop_duration}")

    print(ir)
    # To see events, you'd bind to it: ir.bind(loop_duration=my_callback_func)

    # Accessing a value:
    rate = source_emitter_props.get_param_value("emission_rate")
    print(f"Emission rate: {rate}")

    # Setting a value:
    source_emitter_props.set_param_value("emission_rate", 30.0)
    rate_updated = source_emitter_props.get_param_value("emission_rate")
    print(f"Updated emission rate: {rate_updated}")

    # Create mock animation for emission_rate of source01
    rate_anim = AnimatedParameter()
    rate_anim.add_keyframe(TimelineKeyframe(time=0.0, value=5.0))
    rate_anim.add_keyframe(TimelineKeyframe(time=1.0, value=50.0, interpolation_mode="step")) # Step example
    rate_anim.add_keyframe(TimelineKeyframe(time=2.0, value=50.0))
    rate_anim.add_keyframe(TimelineKeyframe(time=3.0, value=10.0))
    rate_anim.add_keyframe(TimelineKeyframe(time=4.0, value=5.0))
    ir.add_or_update_timeline("source01/emission_rate", rate_anim)

    # Test getting animated value
    times_to_test = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
    for t in times_to_test:
        animated_rate = ir.get_animated_param_value("source01", "emission_rate", time=t)
        lifespan = ir.get_animated_param_value("source01", "lifespan", time=t) # Should return base value
        print(f"Time: {t:.1f}s, Animated Emission Rate: {animated_rate}, Lifespan: {lifespan}") 

    # --- Sprite Asset and Definition Example ---
    print("\n--- Sprite Asset Demo ---")
    asset1 = SpriteAsset(asset_id="particle_atlas_01", path="textures/particles.png", width=1024, height=1024)
    ir.add_sprite_asset(asset1)
    print(f"Added asset: {ir.get_sprite_asset('particle_atlas_01')}")

    spark_def = SpriteDefinition(
        definition_id="spark_white_01", 
        asset_id="particle_atlas_01", 
        region=(0, 0, 64, 64), # x,y,w,h from top-left of particle_atlas_01
        name="White Spark"
    )
    smoke_def = SpriteDefinition(
        definition_id="smoke_puff_01", 
        asset_id="particle_atlas_01", 
        region=(64, 0, 128, 128),
        pivot=(0.5, 0.7) # Pivot towards bottom center for smoke rising
    )
    ir.add_sprite_definition(spark_def)
    ir.add_sprite_definition(smoke_def)

    # Test get
    retrieved_spark = ir.get_sprite_definition("spark_white_01")
    print(f"Retrieved spark: {retrieved_spark}")
    if retrieved_spark:
        print(f"  Spark belongs to asset: {retrieved_spark.asset_id}")

    # Test adding definition for non-existent asset
    bad_def = SpriteDefinition(definition_id="bad_one", asset_id="non_existent_atlas", region=(0,0,10,10))
    ir.add_sprite_definition(bad_def) # Should print an error
    print(f"Attempted to add bad_def, current defs: {list(ir.sprite_definitions.keys())}") 