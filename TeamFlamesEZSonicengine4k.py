from ursina import *
from ursina.shaders import basic_lighting_shader
import random
import math
from collections import deque

class SonicAdventureEngine:
    def __init__(self):
        self.app = Ursina()
        window.title = 'Sonic Adventure Tech Demo'
        window.borderless = False
        window.fullscreen = False
        window.exit_button.visible = False
        window.fps_counter.enabled = True
        
        # Dreamcast-style visual setup
        window.color = color.rgb(50, 50, 70)
        self._setup_dreamcast_aesthetics()
        
        # Core systems
        self.entities = []
        self.particle_systems = []
        self.audio = AdventureAudioSystem()
        self.physics = AdventurePhysicsSystem()
        self.time_scale = 1.0
        self.debug_mode = False
        
        # Adventure-specific systems
        self.rings = []
        self.ring_count = 0
        self.score = 0
        self.lives = 3
        self.character = None
        self.current_mission = None
        
        # Camera setup
        self.camera_rig = Entity()
        camera.parent = self.camera_rig
        camera.position = (0, 15, -20)
        camera.rotation_x = 30
        
        # Demo level setup
        self._create_demo_level()
        
        # Input
        self.input_buffer = deque(maxlen=10)
        self._setup_controls()
        
    def _setup_dreamcast_aesthetics(self):
        """Configure Dreamcast-style visual elements"""
        # Dreamcast-style vertex lighting
        self.directional_light = DirectionalLight(
            direction=(1, -1, 1),
            color=color.rgb(255, 240, 220),
            shadows=False
        )
        
        # Dreamcast-style fog
        scene.fog_density = 0.01
        scene.fog_color = color.rgb(50, 50, 70)
        
        # Post-processing for Dreamcast look
        camera.clip_plane_far = 300
        camera.clip_plane_near = 0.1
        
    def _setup_controls(self):
        """Adventure-style control scheme"""
        self.controls = {
            'left': 'a',
            'right': 'd',
            'up': 'w',
            'down': 's',
            'jump': 'space',
            'action': 'e',
            'spin_dash': 'shift',
            'camera_left': 'q',
            'camera_right': 'e'
        }
        
    def _create_demo_level(self):
        """Create a simple Adventure-style level"""
        # Ground
        self.ground = Entity(
            model='plane',
            texture='white_cube',
            color=color.rgb(30, 120, 80),
            scale=(100, 1, 100),
            collider='box',
            position=(0, -0.5, 0)
        )
        
        # Checkpoint (Adventure-style)
        self.checkpoint = Entity(
            model='cube',
            color=color.yellow,
            scale=(2, 3, 2),
            position=(20, 0, 0),
            collider='box'
        )
        
        # Springs (SA1-style)
        self.spring = Entity(
            model='cylinder',
            color=color.red,
            scale=(1, 0.5, 1),
            position=(10, 0, 0),
            collider='mesh'
        )
        
        # Rings (Adventure-style)
        for _ in range(30):
            ring = Entity(
                model='torus',
                color=color.yellow,
                scale=(0.5, 0.1, 0.5),
                position=(
                    random.uniform(-30, 30),
                    1,
                    random.uniform(-30, 30)
                ),
                collider='mesh',
                rotation_x=90
            )
            self.rings.append(ring)
        
        # Enemy (SA1-style)
        self.enemy = Entity(
            model='sphere',
            color=color.rgb(200, 50, 50),
            scale=(1.5, 1.5, 1.5),
            position=(15, 0.75, 5),
            collider='sphere'
        )
        
        # Player character (Sonic)
        self.character = AdventureCharacter(
            model='sphere',
            color=color.blue,
            scale=(1, 1, 1),
            position=(0, 1, 0),
            collider='sphere'
        )
        self.entities.append(self.character)
        
    def update(self):
        """Main game loop"""
        dt = time.dt * self.time_scale
        
        # Update character
        self.character.update()
        
        # Check ring collisions
        for ring in self.rings[:]:
            if self.character.intersects(ring).hit:
                self.rings.remove(ring)
                destroy(ring)
                self.ring_count += 1
                self.audio.play('ring', volume=0.3)
                
        # Check enemy collision
        if self.character.intersects(self.enemy).hit:
            if not self.character.invincible:
                self._player_hit()
                
        # Check spring collision
        if self.character.intersects(self.spring).hit:
            self.character.velocity.y = 20  # High bounce
            self.audio.play('spring', volume=0.5)
            
        # Check checkpoint
        if self.character.intersects(self.checkpoint).hit:
            self.checkpoint.color = color.green
            self.audio.play('checkpoint', volume=0.4)
            
        # Camera follow with SA1-style smoothing
        self.camera_rig.position = lerp(
            self.camera_rig.position,
            (self.character.x, self.character.y + 5, self.character.z),
            time.dt * 6
        )
        
        # Simple camera rotation
        if held_keys[self.controls['camera_left']]:
            self.camera_rig.rotation_y += 100 * time.dt
        if held_keys[self.controls['camera_right']]:
            self.camera_rig.rotation_y -= 100 * time.dt
            
    def _player_hit(self):
        """Handle player getting hit by enemy"""
        if self.ring_count > 0:
            # SA1-style ring loss
            rings_lost = min(20, self.ring_count)
            self.ring_count -= rings_lost
            self.audio.play('ring_loss', volume=0.5)
            
            # Create lost rings
            for _ in range(rings_lost):
                ring = Entity(
                    model='torus',
                    color=color.yellow,
                    scale=(0.5, 0.1, 0.5),
                    position=self.character.position,
                    collider='mesh',
                    rotation_x=90
                )
                ring.velocity = Vec3(
                    random.uniform(-3, 3),
                    random.uniform(5, 10),
                    random.uniform(-3, 3)
                )
                self.rings.append(ring)
                destroy(ring, delay=5)
        else:
            # SA1-style death
            self.lives -= 1
            if self.lives <= 0:
                self._game_over()
            else:
                self.character.position = (0, 1, 0)
                self.audio.play('death', volume=0.7)
                
    def _game_over(self):
        """Handle game over state"""
        print("Game Over!")
        self.audio.play('game_over', volume=0.8)
        application.quit()
        
    def run(self):
        """Start the engine"""
        self.app.run()

class AdventureCharacter(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Movement properties
        self.speed = 8
        self.rotation_speed = 200
        self.jump_height = 8
        self.gravity = 1.5
        self.air_control = 0.5
        self.velocity = Vec3(0, 0, 0)
        
        # Adventure mechanics
        self.spin_dash_power = 0
        self.max_spin_dash = 100
        self.homing_available = False
        self.homing_target = None
        self.invincible = False
        self.invincibility_timer = 0
        self.boost_energy = 100
        
        # Animation state
        self.state = "idle"  # idle, running, jumping, spinning, falling
        
    def update(self):
        """Update character physics and state"""
        dt = time.dt
        
        # Apply gravity
        self.velocity.y -= self.gravity * dt
        
        # Ground check
        ground_ray = raycast(self.position, (0, -1, 0), distance=1.1)
        grounded = ground_ray.hit
        
        # Input handling
        move_dir = Vec3(0, 0, 0)
        if held_keys['a']:
            move_dir.x -= 1
        if held_keys['d']:
            move_dir.x += 1
        if held_keys['w']:
            move_dir.z += 1
        if held_keys['s']:
            move_dir.z -= 1
            
        # Normalize move direction
        if move_dir.length() > 0:
            move_dir = move_dir.normalized()
            
            # Rotate to face movement direction (SA1-style)
            target_angle = math.degrees(math.atan2(-move_dir.z, move_dir.x)) + 90
            self.rotation_y = lerp_angle(self.rotation_y, target_angle, time.dt * 5)
            
            # Apply movement
            move_speed = self.speed * (self.air_control if not grounded else 1)
            self.velocity.x = move_dir.x * move_speed
            self.velocity.z = move_dir.z * move_speed
            
            # Update state
            if grounded:
                self.state = "running"
        else:
            if grounded:
                self.state = "idle"
                
        # Jumping
        if grounded and held_keys['space']:
            self.velocity.y = self.jump_height
            self.state = "jumping"
            
        # Spin dash charging
        if grounded and held_keys['shift']:
            self.spin_dash_power = min(self.spin_dash_power + 50 * dt, self.max_spin_dash)
            self.state = "spinning"
            
        # Spin dash release
        if grounded and not held_keys['shift'] and self.spin_dash_power > 0:
            self.velocity = self.forward * (self.spin_dash_power / 10)
            self.spin_dash_power = 0
            
        # Homing attack
        if not grounded and held_keys['e'] and self.homing_available:
            self._perform_homing_attack()
            
        # Apply velocity
        self.position += self.velocity * dt
        
        # Update invincibility
        if self.invincible:
            self.invincibility_timer -= dt
            if self.invincibility_timer <= 0:
                self.invincible = False
                self.color = color.blue
                
    def _perform_homing_attack(self):
        """SA2-style homing attack"""
        if self.homing_target:
            direction = (self.homing_target.position - self.position).normalized()
            self.velocity = direction * 20
            self.homing_available = False
            invoke(setattr, self, 'homing_available', True, delay=1.0)
            
    def take_damage(self):
        """Handle character taking damage"""
        if not self.invincible:
            self.invincible = True
            self.invincibility_timer = 3
            self.color = color.red
            invoke(setattr, self, 'color', color.blue, delay=0.1)

class AdventurePhysicsSystem:
    def __init__(self):
        self.gravity = Vec3(0, -20, 0)
        self.colliders = []
        
    def add_collider(self, collider):
        self.colliders.append(collider)
        
    def raycast(self, origin, direction, distance=100, ignore=None):
        """Simple raycast implementation"""
        direction = direction.normalized()
        for i in range(int(distance * 10)):
            point = origin + direction * (i/10)
            for collider in self.colliders:
                if collider == ignore:
                    continue
                if collider.intersects_point(point):
                    return True, point, collider
        return False, None, None

class AdventureAudioSystem:
    def __init__(self):
        # In a real implementation, these would be actual sound files
        # For demo purposes, we'll just print the sound names
        self.sounds = {
            'ring': None,
            'spring': None,
            'checkpoint': None,
            'death': None,
            'game_over': None,
            'jump': None,
            'homing': None,
            'spin_dash': None
        }
        
    def play(self, sound_name, volume=1.0):
        """Play a sound effect"""
        if sound_name in self.sounds:
            print(f"Playing sound: {sound_name} at volume {volume}")

# Run the demo
if __name__ == "__main__":
    print("Starting Sonic Adventure Tech Demo...")
    print("Controls:")
    print("WASD: Move")
    print("Space: Jump")
    print("Shift: Spin Dash (hold to charge)")
    print("E: Homing Attack (when available)")
    print("Q/E: Rotate Camera")
    
    engine = SonicAdventureEngine()
    engine.run()
