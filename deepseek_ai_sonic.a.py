from ursina import *
from ursina.shaders import basic_lighting_shader
import random
import math
from collections import deque

class SonicVolumeDeepseekEngine:
    def __init__(self):
        self.app = Ursina()
        window.color = color.black  # Fixed: Access window directly from ursina module
        self.entities = []
        self.particle_systems = []
        self.audio_system = AudioSystem()
        self.physics = PhysicsSystem()
        self.time_scale = 1.0
        self.debug_mode = False
        
        # Engine configuration
        self.max_particles = 1000
        self.collision_precision = 0.1
        self.max_physics_steps = 5
        
        # Set up default camera
        self.camera_rig = Entity()
        camera.parent = self.camera_rig  # Fixed: Access camera directly
        camera.position = (0, 15, -20)
        camera.rotation_x = 30
        
        # Engine systems initialization
        self._init_lighting()
        self._init_input_system()
        
    def _init_lighting(self):
        self.directional_light = DirectionalLight(
            direction=(1, -1, 1),
            color=color.white,
            shadows=True
        )
        self.ambient_light = AmbientLight(color=color.rgba(100, 100, 100, 0.1))
        
    def _init_input_system(self):
        self.input_buffer = deque(maxlen=10)
        self.input_mappings = {
            'move_left': 'a',
            'move_right': 'd',
            'jump': 'space',
            'dash': 'shift',
            'special': 'e'
        }
        
    def create_entity(self, **kwargs):
        """Create a new game entity with default components"""
        entity = SonicEntity(**kwargs)
        self.entities.append(entity)
        return entity
    
    def create_particle_system(self, position, count=50, **kwargs):
        """Create a particle emitter"""
        if len(self.particle_systems) < self.max_particles:
            system = ParticleSystem(position, count, **kwargs)
            self.particle_systems.append(system)
            return system
        return None
    
    def update(self):
        """Main engine update loop"""
        dt = time.dt * self.time_scale
        
        # Process physics in fixed steps
        physics_steps = min(int(dt / (1/60)) + 1, self.max_physics_steps)
        for _ in range(physics_steps):
            self.physics.update(dt / physics_steps)
            
        # Update particles
        for system in self.particle_systems[:]:
            system.update(dt)
            if system.dead:
                self.particle_systems.remove(system)
                
        # Process input buffer
        self._process_input_buffer()
        
        # Debug rendering if enabled
        if self.debug_mode:
            self._render_debug()
    
    def _process_input_buffer(self):
        """Process buffered inputs"""
        while self.input_buffer:
            input_event = self.input_buffer.popleft()
            # Process input event here
            pass
    
    def _render_debug(self):
        """Render debug information"""
        for entity in self.entities:
            if hasattr(entity, 'collider') and entity.collider:
                entity.collider.debug = True
    
    def run(self):
        """Start the engine"""
        self.app.run()
        
    def set_time_scale(self, scale):
        """Adjust the global time scale"""
        self.time_scale = max(0.1, min(scale, 5.0))
        
    def play_sound(self, sound_name, volume=1.0, pitch=1.0):
        """Play a sound effect"""
        self.audio_system.play(sound_name, volume, pitch)

class SonicEntity(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity = Vec3(0, 0, 0)
        self.acceleration = Vec3(0, 0, 0)
        self.max_speed = 10
        self.friction = 0.9
        self.gravity = 0.5
        self.grounded = False
        self.jump_power = 8
        self.dash_power = 15
        self.dash_cooldown = 1.0
        self.can_dash = True
        self.health = 100
        self.invincible = False
        self.invincibility_time = 0
        
        # Sonic-specific properties
        self.ring_count = 0
        self.homing_attack_ready = True
        self.spin_dash_charged = 0
        self.boost_energy = 100
        
    def update(self):
        """Entity-specific update logic"""
        dt = time.dt
        
        # Apply physics
        self.velocity += self.acceleration * dt
        self.velocity.x *= self.friction
        self.velocity.z *= self.friction
        
        # Limit speed
        if self.velocity.length() > self.max_speed:
            self.velocity = self.velocity.normalized() * self.max_speed
            
        # Apply movement
        self.position += self.velocity * dt
        
        # Gravity
        if not self.grounded:
            self.velocity.y -= self.gravity
        else:
            self.velocity.y = 0
            
        # Update invincibility
        if self.invincible:
            self.invincibility_time -= dt
            if self.invincibility_time <= 0:
                self.invincible = False
                
    def jump(self):
        if self.grounded:
            self.velocity.y = self.jump_power
            self.grounded = False
            
    def dash(self, direction):
        if self.can_dash and self.boost_energy >= 10:
            self.velocity = direction.normalized() * self.dash_power
            self.boost_energy -= 10
            self.can_dash = False
            invoke(setattr, self, 'can_dash', True, delay=self.dash_cooldown)
            
    def homing_attack(self, target):
        if self.homing_attack_ready and target:
            direction = (target.position - self.position).normalized()
            self.velocity = direction * self.dash_power * 1.5
            self.homing_attack_ready = False
            invoke(setattr, self, 'homing_attack_ready', True, delay=0.5)
            
    def spin_dash(self, charge_rate=5.0):
        self.spin_dash_charged = min(100, self.spin_dash_charged + charge_rate * time.dt)
        
    def release_spin_dash(self):
        power = self.spin_dash_charged / 10
        self.velocity = self.forward * power
        self.spin_dash_charged = 0
        
    def take_damage(self, amount):
        if not self.invincible:
            self.health -= amount
            if self.health <= 0:
                self.die()
            else:
                self.invincible = True
                self.invincibility_time = 2.0
                # Flash effect
                self.blink(color.red, duration=0.1, loop=5)
                
    def die(self):
        """Handle entity death"""
        destroy(self)
        
    def collect_ring(self, amount=1):
        self.ring_count += amount
        if self.ring_count > 0 and self.health <= 0:
            self.ring_count = max(0, self.ring_count - 50)
            self.health = 100
            self.invincible = True
            self.invincibility_time = 3.0

class PhysicsSystem:
    def __init__(self):
        self.gravity = Vec3(0, -9.81, 0)
        self.colliders = []
        self.raycast_precision = 0.1
        self.max_collision_iterations = 5
        
    def add_collider(self, collider):
        self.colliders.append(collider)
        
    def remove_collider(self, collider):
        if collider in self.colliders:
            self.colliders.remove(collider)
            
    def update(self, dt):
        """Update physics simulation"""
        # In a full implementation, this would handle collision detection
        # and resolution for all entities with colliders
        pass
        
    def raycast(self, origin, direction, distance=100, ignore=None):
        """Cast a ray into the scene"""
        # Simplified raycast implementation
        direction = direction.normalized()
        current_pos = Vec3(origin)
        
        for _ in range(int(distance / self.raycast_precision)):
            current_pos += direction * self.raycast_precision
            
            for collider in self.colliders:
                if collider == ignore:
                    continue
                    
                if collider.intersects_point(current_pos):
                    return True, current_pos, collider
                    
        return False, None, None

class ParticleSystem:
    def __init__(self, position, count=50, 
                 color=color.white, 
                 size=0.1, 
                 lifetime=1.0, 
                 velocity=Vec3(0,1,0), 
                 spread=0.5):
        self.position = position
        self.particles = []
        self.lifetime = lifetime
        self.dead = False
        
        for _ in range(count):
            particle = {
                'position': Vec3(
                    position.x + random.uniform(-spread, spread),
                    position.y + random.uniform(-spread, spread),
                    position.z + random.uniform(-spread, spread)
                ),
                'velocity': Vec3(
                    velocity.x + random.uniform(-spread, spread),
                    velocity.y + random.uniform(-spread, spread),
                    velocity.z + random.uniform(-spread, spread)
                ),
                'size': size * random.uniform(0.5, 1.5),
                'color': color,
                'life': lifetime * random.uniform(0.8, 1.2),
                'max_life': lifetime * random.uniform(0.8, 1.2)
            }
            self.particles.append(particle)
            
    def update(self, dt):
        """Update all particles"""
        alive_particles = []
        
        for particle in self.particles:
            particle['life'] -= dt
            if particle['life'] > 0:
                particle['position'] += particle['velocity'] * dt
                alive_particles.append(particle)
                
        self.particles = alive_particles
        if not self.particles:
            self.dead = True

class AudioSystem:
    def __init__(self):
        self.sounds = {}
        self.current_music = None
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        
    def load_sound(self, name, path):
        self.sounds[name] = Audio(path, loop=False, autoplay=False)
        
    def play(self, name, volume=1.0, pitch=1.0):
        if name in self.sounds:
            sound = self.sounds[name]
            sound.volume = volume * self.sfx_volume
            sound.pitch = pitch
            sound.play()
            
    def play_music(self, name, loop=True):
        if name in self.sounds:
            if self.current_music:
                self.current_music.stop()
            self.current_music = self.sounds[name]
            self.current_music.loop = loop
            self.current_music.volume = self.music_volume
            self.current_music.play()

# Example usage
if __name__ == "__main__":
    engine = SonicVolumeDeepseekEngine()
    
    # Create a player entity
    player = engine.create_entity(
        model='sphere',
        color=color.blue,
        scale=(1,1,1),
        position=(0,5,0),
        collider='sphere'
    )
    
    # Create ground
    ground = engine.create_entity(
        model='cube',
        scale=(50,1,50),
        texture='grass',
        collider='box',
        position=(0,0,0)
    )
    
    # Add some obstacles
    for i in range(10):
        engine.create_entity(
            model='cube',
            position=(random.uniform(-20,20), 0.5, random.uniform(-20,20)),
            scale=(2,2,2),
            texture='brick',
            collider='box'
        )
    
    # Camera follow
    def update():
        engine.camera_rig.position = lerp(
            engine.camera_rig.position,
            (player.x, player.y + 5, player.z),
            time.dt * 8
        )
        
    engine.run()
