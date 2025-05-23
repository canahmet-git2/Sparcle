from dataclasses import dataclass, field
from typing import List, Tuple, Any, Optional
import uuid
import random
import math

# Attempt to import EmitterProperties and EffectIR for type hinting and potential use.
# This might require adjustments based on actual file structure and circular dependencies.
try:
    from .ir import EmitterProperties, EffectIR, AnimatedParameter, TimelineKeyframe
except ImportError:
    # Fallback for standalone execution or if ir.py is not yet in the exact path
    # Define placeholder classes if imports fail, to allow basic structure definition
    print("Warning: Could not import from .ir. Using placeholder classes for EmitterProperties and EffectIR.")
    @dataclass
    class EmitterPropertiesPlaceholder:
        emitter_id: str = "placeholder_emitter"
        parameters: dict = field(default_factory=dict)
        def get_param_value(self, param_name: str, default: Any = None) -> Any:
            return self.parameters.get(param_name, default)

    EmitterProperties = EmitterPropertiesPlaceholder # type: ignore

    @dataclass
    class EffectIRPlaceholder:
        timelines: dict = field(default_factory=dict)
        def get_animated_param_value(self, emitter_id: str, param_name: str, time: float) -> Any:
            # Simplified: try to get from timelines, or return a default if not found
            path = f"{emitter_id}/{param_name}"
            if path in self.timelines and hasattr(self.timelines[path], 'get_value_at_time'):
                return self.timelines[path].get_value_at_time(time, None)
            return None # Or some other sensible default
            
    EffectIR = EffectIRPlaceholder # type: ignore


@dataclass
class Particle:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    position: Tuple[float, float] = (0.0, 0.0)
    velocity: Tuple[float, float] = (0.0, 0.0)
    acceleration: Tuple[float, float] = (0.0, 0.0) # Optional simple physics
    color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0) # RGBA
    size: float = 5.0
    age: float = 0.0  # Current age in seconds
    lifespan: float = 2.0  # Total lifespan in seconds
    is_alive: bool = True
    rotation: float = 0.0  # In degrees
    angular_velocity: float = 0.0 # In degrees per second

    # Fields for "over lifetime" behavior
    initial_size: float = 5.0 # Size at birth
    initial_color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0) # Color at birth

    size_curve: Optional[List[Tuple[float, float]]] = None # List of (time_norm, size_multiplier)
    opacity_curve: Optional[List[Tuple[float, float]]] = None # List of (time_norm, opacity_value)
    color_curve: Optional[List[Tuple[float, Tuple[float, float, float, float]]]] = None # List of (time_norm, rgba_color)

    # Sprite information
    sprite_definition_id: Optional[str] = None

    # Behavior flags
    orient_to_velocity: bool = False

    def update(self, dt: float):
        if not self.is_alive:
            return

        self.age += dt
        if self.age >= self.lifespan:
            self.is_alive = False
            return

        # Update velocity with acceleration
        self.velocity = (
            self.velocity[0] + self.acceleration[0] * dt,
            self.velocity[1] + self.acceleration[1] * dt
        )
        # Update position with velocity
        self.position = (
            self.position[0] + self.velocity[0] * dt,
            self.position[1] + self.velocity[1] * dt
        )
        # Update rotation
        self.rotation = (self.rotation + self.angular_velocity * dt) % 360

        # Orient to velocity if flag is set
        if self.orient_to_velocity:
            if self.velocity[0] != 0 or self.velocity[1] != 0: # Check for non-zero velocity
                self.rotation = math.degrees(math.atan2(self.velocity[1], self.velocity[0]))

        # Affect over lifetime
        if self.lifespan > 0: # Avoid division by zero if lifespan is 0
            norm_age = min(1.0, max(0.0, self.age / self.lifespan))
        else:
            norm_age = 1.0 # Consider it at the end of its life if lifespan is zero

        # Apply size curve (as multiplier to initial_size)
        if self.size_curve:
            current_size_multiplier = _interpolate_scalar_curve(self.size_curve, norm_age)
            self.size = self.initial_size * current_size_multiplier
        # else: self.size remains initial_size or set directly if no curve logic is used for size elsewhere

        # Determine current base color (from color_curve or initial_color)
        current_base_color_rgb = (self.initial_color[0], self.initial_color[1], self.initial_color[2])
        current_base_alpha = self.initial_color[3]

        if self.color_curve:
            interpolated_color = _interpolate_color_curve(self.color_curve, norm_age)
            current_base_color_rgb = (interpolated_color[0], interpolated_color[1], interpolated_color[2])
            current_base_alpha = interpolated_color[3] # Color curve defines full RGBA
        
        # Apply opacity curve (modulates the alpha of the current_base_color)
        if self.opacity_curve:
            current_opacity = _interpolate_scalar_curve(self.opacity_curve, norm_age)
            final_alpha = current_base_alpha * current_opacity # Modulate if color curve also had alpha
                                                              # Or directly use current_opacity if that logic is preferred
                                                              # For now, let opacity_curve be the dominant controller of final alpha if it exists.
            final_alpha = current_opacity # Let opacity curve directly set final alpha if present
        else:
            final_alpha = current_base_alpha
        
        self.color = (current_base_color_rgb[0], current_base_color_rgb[1], current_base_color_rgb[2], final_alpha)


class ParticleSystem:
    def __init__(self, 
                 effect_ir: Optional[EffectIR] = None, 
                 emitter_id: Optional[str] = None,
                 max_particles: int = 1000):
        self.particles: List[Particle] = []
        self.effect_ir: Optional[EffectIR] = effect_ir
        self.emitter_id: Optional[str] = emitter_id
        self.max_particles: int = max_particles
        self._emission_debt: float = 0.0 # For fractional particle emission

        self.emitter_properties: Optional[EmitterProperties] = None
        if self.effect_ir and self.emitter_id:
            self.emitter_properties = self.effect_ir.get_emitter(self.emitter_id) # type: ignore
            if not self.emitter_properties:
                 print(f"Warning: Emitter '{self.emitter_id}' not found in EffectIR.")
        
        if not self.emitter_properties and not isinstance(self.effect_ir, EffectIRPlaceholder): # Avoid warning if using placeholder
            print(f"Warning: ParticleSystem initialized without valid EmitterProperties for emitter_id '{self.emitter_id}'. Emission may not work as expected.")


    def _get_param_value_at_time(self, param_name: str, time: float, default: Any) -> Any:
        if self.effect_ir and self.emitter_id:
            # This uses the get_animated_param_value from EffectIR, which handles base vs animated
            val = self.effect_ir.get_animated_param_value(self.emitter_id, param_name, time)
            # print(f"DEBUG PS: Param '{param_name}' at T={time:.2f}, RawVal: {val}, Default: {default}")
            if val is not None:
                return val
        
        # Fallback to base EmitterProperties if EffectIR not available or param not animated
        if self.emitter_properties:
            val = self.emitter_properties.get_param_value(param_name, default)
            # print(f"DEBUG PS: Param '{param_name}' (base), Val: {val}, Default: {default}")
            return val
        
        # print(f"DEBUG PS: Param '{param_name}' returning default: {default}")
        return default

    def emit_particle(self, current_time: float):
        if len(self.particles) >= self.max_particles:
            return

        # Get initial properties from EmitterProperties, potentially animated via EffectIR
        initial_pos = self._get_param_value_at_time("emitter_position", current_time, (0.0, 0.0))

        # Lifespan
        lifespan_val = self._get_param_value_at_time("lifespan_range", current_time, None)
        if isinstance(lifespan_val, tuple) and len(lifespan_val) == 2:
            particle_lifespan = random.uniform(lifespan_val[0], lifespan_val[1])
        else:
            particle_lifespan = self._get_param_value_at_time("lifespan", current_time, 2.0)
        particle_lifespan = max(0.001, particle_lifespan) # Ensure lifespan is positive

        # Velocity
        direction_vec_val = self._get_param_value_at_time("initial_direction_vector", current_time, (0.0, 1.0)) # Default up
        speed_range_val = self._get_param_value_at_time("speed_range", current_time, (50.0, 150.0))
        emission_angle_range_deg_val = self._get_param_value_at_time("emission_angle_range_deg", current_time, (0.0, 0.0))

        speed = random.uniform(speed_range_val[0], speed_range_val[1])
        emission_angle_offset_deg = random.uniform(emission_angle_range_deg_val[0], emission_angle_range_deg_val[1])
        
        # Normalize direction_vec_val
        dir_x, dir_y = direction_vec_val
        len_dir = math.sqrt(dir_x**2 + dir_y**2)
        if len_dir == 0: # Avoid division by zero, default to (0,1) if zero vector
            norm_dir_x, norm_dir_y = 0.0, 1.0
        else:
            norm_dir_x, norm_dir_y = dir_x / len_dir, dir_y / len_dir
            
        base_angle_rad = math.atan2(norm_dir_y, norm_dir_x)
        final_angle_rad = base_angle_rad + math.radians(emission_angle_offset_deg)
        
        initial_vel = (
            speed * math.cos(final_angle_rad),
            speed * math.sin(final_angle_rad)
        )

        # Initial Size (base for size_over_lifespan curve)
        size_val = self._get_param_value_at_time("size_range", current_time, None)
        if isinstance(size_val, tuple) and len(size_val) == 2:
            born_size = random.uniform(size_val[0], size_val[1])
        else:
            born_size = self._get_param_value_at_time("particle_size", current_time, 5.0)
        
        # Initial Color (base for color/opacity_over_lifespan curves)
        born_color = self._get_param_value_at_time("particle_color", current_time, (1.0, 1.0, 1.0, 1.0))

        # Rotation
        rot_val = self._get_param_value_at_time("rotation_range_deg", current_time, None)
        if isinstance(rot_val, tuple) and len(rot_val) == 2:
            initial_rotation = random.uniform(rot_val[0], rot_val[1])
        else:
            initial_rotation = self._get_param_value_at_time("initial_rotation_deg", current_time, 0.0)

        # Angular Velocity
        ang_vel_val = self._get_param_value_at_time("angular_velocity_range_dps", current_time, None)
        if isinstance(ang_vel_val, tuple) and len(ang_vel_val) == 2:
            initial_angular_velocity = random.uniform(ang_vel_val[0], ang_vel_val[1])
        else:
            initial_angular_velocity = self._get_param_value_at_time("initial_angular_velocity_dps", current_time, 0.0)
            
        # Acceleration
        particle_acceleration = self._get_param_value_at_time("acceleration_vector", current_time, (0.0, 0.0))

        # Fetch "over lifetime" curve data
        p_size_curve = self._get_param_value_at_time("size_over_lifespan", current_time, None)
        p_opacity_curve = self._get_param_value_at_time("opacity_over_lifespan", current_time, None)
        p_color_curve = self._get_param_value_at_time("color_over_lifespan", current_time, None)

        # Fetch Sprite Definition ID
        p_sprite_definition_id = self._get_param_value_at_time("sprite_definition_id", current_time, None)

        # Fetch Behavior Flags
        p_orient_to_velocity = self._get_param_value_at_time("orient_to_velocity", current_time, False)

        particle = Particle(
            position=initial_pos,
            velocity=initial_vel,
            acceleration=particle_acceleration,
            lifespan=particle_lifespan,
            # color and size will be set by curves, using initial_color/initial_size as base
            initial_color=born_color,
            initial_size=born_size,
            size=born_size, # Set initial effective size
            color=born_color, # Set initial effective color
            rotation=initial_rotation,
            angular_velocity=initial_angular_velocity,
            size_curve=p_size_curve if isinstance(p_size_curve, list) else None,
            opacity_curve=p_opacity_curve if isinstance(p_opacity_curve, list) else None,
            color_curve=p_color_curve if isinstance(p_color_curve, list) else None,
            sprite_definition_id=p_sprite_definition_id if isinstance(p_sprite_definition_id, str) else None,
            orient_to_velocity=p_orient_to_velocity if isinstance(p_orient_to_velocity, bool) else False
        )
        self.particles.append(particle)

    def update(self, dt: float, current_time: float):
        # 1. Emit new particles
        if self.emitter_properties:
            emission_rate = self._get_param_value_at_time("emission_rate", current_time, 10.0)
            num_to_emit_float = emission_rate * dt + self._emission_debt
            num_to_emit_int = math.floor(num_to_emit_float)
            self._emission_debt = num_to_emit_float - num_to_emit_int

            for _ in range(num_to_emit_int):
                if len(self.particles) < self.max_particles:
                    self.emit_particle(current_time) 
                else:
                    break # Stop emitting if max particles reached
        
        # 2. Update existing particles
        # Iterate backwards if removing items, or create a new list
        # For now, just update and then filter
        for p in self.particles:
            p.update(dt)
            # TODO: Apply affectors or update properties over lifetime based on timelines
            # e.g., color_over_life, size_over_life from emitter/effect_ir

        # 3. Remove dead particles
        self.particles = [p for p in self.particles if p.is_alive]

    def get_alive_particles(self) -> List[Particle]:
        # This could simply return self.particles if removal is handled in update.
        # Or, if filtering is preferred here:
        return [p for p in self.particles if p.is_alive]

    def __repr__(self):
        return f"<ParticleSystem emitter_id='{self.emitter_id}' particles={len(self.particles)} alive={len(self.get_alive_particles())}>"

# --- Interpolation Helper Functions ---

def _interpolate_scalar_curve(curve_points: List[Tuple[float, float]], normalized_time: float) -> float:
    if not curve_points:
        return 1.0 # Default to 1.0 (no change) if no curve

    curve_points.sort(key=lambda p: p[0]) # Ensure sorted by time

    if normalized_time <= curve_points[0][0]:
        return curve_points[0][1]
    if normalized_time >= curve_points[-1][0]:
        return curve_points[-1][1]

    for i in range(len(curve_points) - 1):
        p1 = curve_points[i]
        p2 = curve_points[i+1]
        if p1[0] <= normalized_time < p2[0]:
            if p2[0] == p1[0]: # Avoid division by zero if times are identical
                return p1[1]
            t_ratio = (normalized_time - p1[0]) / (p2[0] - p1[0])
            return p1[1] + (p2[1] - p1[1]) * t_ratio
    
    return curve_points[-1][1] # Should ideally be caught by checks above

def _interpolate_color_curve(curve_points: List[Tuple[float, Tuple[float,float,float,float]]], normalized_time: float) -> Tuple[float,float,float,float]:
    if not curve_points:
        return (1.0, 1.0, 1.0, 1.0) # Default to white if no curve

    curve_points.sort(key=lambda p: p[0]) # Ensure sorted by time

    if normalized_time <= curve_points[0][0]:
        return curve_points[0][1]
    if normalized_time >= curve_points[-1][0]:
        return curve_points[-1][1]

    for i in range(len(curve_points) - 1):
        p1_time, p1_color = curve_points[i]
        p2_time, p2_color = curve_points[i+1]
        if p1_time <= normalized_time < p2_time:
            if p2_time == p1_time: # Avoid division by zero
                return p1_color
            t_ratio = (normalized_time - p1_time) / (p2_time - p1_time)
            interpolated_rgba = tuple(c1 + (c2 - c1) * t_ratio for c1, c2 in zip(p1_color, p2_color))
            return interpolated_rgba # type: ignore
            
    return curve_points[-1][1] # Should ideally be caught by checks above

if __name__ == '__main__':
    print("Running Particle System Demo...")

    # Create a mock EffectIR and EmitterProperties for testing
    # This simulates what the main application would provide
    mock_ir = EffectIR() # Using placeholder if ir.py not found
    
    # Define some base parameters for the emitter
    emitter_params_data = {
        "emission_rate": {"name": "emission_rate", "value": 50.0}, # particles per second
        "lifespan_range": {"name": "lifespan_range", "value": (1.5, 3.0)}, # seconds (ranged)
        "particle_color": {"name": "particle_color", "value": (1.0, 0.5, 0.0, 0.8)}, # Initial base color (e.g. orange, semi-transparent)
        "sprite_definition_id": {"name": "sprite_definition_id", "value": "spark_01"}, # Link to a sprite definition
        
        # Velocity related parameters
        "initial_direction_vector": {"name": "initial_direction_vector", "value": (0, 1)}, # Base direction (up)
        "speed_range": {"name": "speed_range", "value": (50.0, 100.0)}, # Speed in px/sec
        "emission_angle_range_deg": {"name": "emission_angle_range_deg", "value": (-30.0, 30.0)}, # Emission cone 60 deg wide

        "emitter_position": {"name": "emitter_position", "value": (300, 100)}, # px
        "size_range": {"name": "size_range", "value": (5.0, 10.0)}, # (ranged)

        "rotation_range_deg": {"name": "rotation_range_deg", "value": (0.0, 0.0)}, # Set to 0 if orient_to_velocity is true
        "angular_velocity_range_dps": {"name": "angular_velocity_range_dps", "value": (0.0, 0.0)},# Set to 0 if orient_to_velocity is true
        "acceleration_vector": {"name": "acceleration_vector", "value": (0.0, -20.0)}, # Gentle downward gravity
        "orient_to_velocity": {"name": "orient_to_velocity", "value": True}, # Enable orient to velocity

        # --- "Over Lifetime" Parameters ---
        "size_over_lifespan": {"name": "size_over_lifespan", "value": [
            (0.0, 0.2), # At birth, 20% of initial_size
            (0.1, 1.0), # Quickly grow to full initial_size
            (0.7, 0.8), # Slowly shrink
            (1.0, 0.0)  # Disappear at end of life
        ]},
        "opacity_over_lifespan": {"name": "opacity_over_lifespan", "value": [
            (0.0, 0.0), # Fully transparent at birth
            (0.1, 1.0), # Fade in quickly
            (0.8, 1.0), # Stay opaque
            (1.0, 0.0)  # Fade out at end of life
        ]},
        "color_over_lifespan": {"name": "color_over_lifespan", "value": [
            (0.0, (1.0, 0.0, 0.0, 1.0)), # Red
            (0.5, (1.0, 1.0, 0.0, 1.0)), # Yellow
            (1.0, (0.0, 0.0, 1.0, 0.5))  # Blue, semi-transparent (but opacity_curve may override alpha)
        ]}
    }
    
    # If using the actual ir.EmitterParameter, structure would be:
    # from .ir import EmitterParameter
    # emitter_params_actual = {k: EmitterParameter(name=k, value=v["value"]) for k, v in emitter_params_data.items()}
    # For placeholder, direct dict is fine if EmitterPropertiesPlaceholder expects it
    
    source_emitter_props = EmitterProperties( # type: ignore
        emitter_id="test_emitter_01",
        # parameters=emitter_params_actual # If using actual EmitterParameter
        parameters={k: v["value"] for k, v in emitter_params_data.items()} # Simplified for placeholder
    )
    
    if not isinstance(mock_ir, EffectIRPlaceholder): # If actual EffectIR is available
        mock_ir.emitters.append(source_emitter_props) # Add emitter to IR so ParticleSystem can find it.
    else: # If using placeholder, we manually set it up or ensure ParticleSystem can handle it
        mock_ir.get_emitter = lambda eid: source_emitter_props if eid == "test_emitter_01" else None # type: ignore


    # Create an animated parameter for emission_rate for fun
    # rate_anim = AnimatedParameter() # This would require AnimatedParameter to be available
    # rate_anim.add_keyframe(TimelineKeyframe(time=0.0, value=5.0))
    # rate_anim.add_keyframe(TimelineKeyframe(time=1.0, value=100.0))
    # rate_anim.add_keyframe(TimelineKeyframe(time=2.0, value=5.0))
    # mock_ir.add_or_update_timeline("test_emitter_01/emission_rate", rate_anim) # If add_or_update_timeline exists

    # Initialize Particle System
    ps = ParticleSystem(effect_ir=mock_ir, emitter_id="test_emitter_01", max_particles=500)
    print(f"Initialized Particle System: {ps}")
    if ps.emitter_properties:
        print(f"Emitter props found: {ps.emitter_properties.parameters}") # type: ignore
    else:
        print("Warning: Emitter properties not found in ParticleSystem during __main__ test.")


    total_sim_time = 3.0  # seconds
    dt = 1.0 / 60.0    # time step (60 FPS)
    current_time = 0.0

    print(f"\nSimulating for {total_sim_time} seconds with dt={dt:.4f}...")
    max_particles_seen = 0

    while current_time < total_sim_time:
        ps.update(dt, current_time)
        alive_count = len(ps.get_alive_particles())
        max_particles_seen = max(max_particles_seen, alive_count)
        
        if current_time == 0 or (int(current_time / dt) % 30 == 0) : # Print every 30 frames approx
             print(f"Time: {current_time:.2f}s, Particles Alive: {alive_count}, Total in system: {len(ps.particles)}")
        
        # Example of accessing particle data (e.g., for rendering)
        # if alive_count > 0 and (int(current_time / dt) % 60 == 0):
        #     first_particle = ps.get_alive_particles()[0]
        #     print(f"  First particle sample: Pos={first_particle.position}, Age={first_particle.age:.2f}, Color={first_particle.color}, Size={first_particle.size:.2f}, SpriteID={first_particle.sprite_definition_id}")

        current_time += dt
        if not ps.emitter_properties and not isinstance(mock_ir, EffectIRPlaceholder) and current_time > dt*5 : # Break early if no props after a few steps
            print("Error: EmitterProperties not loading correctly in test. Aborting simulation.")
            break


    print(f"\nSimulation finished. Max particles simultaneously alive: {max_particles_seen}")
    print(f"Final particle count: {len(ps.get_alive_particles())}")

    # Further test: What if no emitter_properties is found?
    print("\nTesting ParticleSystem with non-existent emitter ID:")
    ps_no_emitter = ParticleSystem(effect_ir=mock_ir, emitter_id="non_existent_emitter", max_particles=100)
    print(ps_no_emitter)
    ps_no_emitter.update(dt, 0.0) # Should not emit anything, run silently
    print(f"Particles after update with bad emitter: {len(ps_no_emitter.get_alive_particles())}")

    print("\nParticle System Demo Complete.") 