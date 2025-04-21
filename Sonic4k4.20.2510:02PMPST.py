# test.py

from ursina import *
from ursina.shaders import basic_lighting_shader
import random
import math
from collections import deque

class Voxel(Entity):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(model='cube', color=color.white, position=position, collider='box')

class FangameAudioSystem:
    def __init__(self):
        print("Initializing Audio System")

    def play(self, sound_name, volume=1.0):
        print(f"Pretending to play sound: '{sound_name}' at volume {volume:.1f}")

class SonicFangameWorld:
    def __init__(self):
        self.app = Ursina()
        window.title = 'Sonic Fangame World Demo'
        window.borderless = False
        window.fullscreen = False
        window.exit_button.visible = False
        window.fps_counter.enabled = True

        self.entities = []
        self.rings = []
        self.enemies = []
        self.checkpoints = []
        self.ring_count = 0
        self.score = 0
        self.lives = 3
        self.time_scale = 1.0
        self.debug_mode = False

        self.audio = FangameAudioSystem()

        self.camera_rig = Entity()
        camera.parent = self.camera_rig
        camera.position = (0, 15, -20)
        camera.rotation_x = 30

        self._create_fangame_world()
        self._setup_controls()

        self.input_buffer = deque(maxlen=10)

        self.app.update = self._game_update

    def _setup_controls(self):
        self.controls = {
            'left': 'a', 'right': 'd',
            'up': 'w', 'down': 's',
            'jump': 'space', 'boost': 'left shift',
            'spin_dash': 'left ctrl', 'stomp': 'e',
            'camera_left': 'q', 'camera_right': 'r'
        }

    def _create_fangame_world(self):
        # Create voxel terrain
        for z in range(-10, 10):
            for x in range(-10, 10):
                voxel = Voxel(position=(x, 0, z))

        # Create rings
        for i in range(10):
            ring = Entity(model='torus', color=color.yellow, scale=(0.5,0.5,0.5), position=(random.randint(-5, 5), 1, random.randint(-5, 5)), collider='sphere', rotation=(90,0,0), shader=basic_lighting_shader, double_sided=True)
            self.rings.append(ring)

        # Create enemies
        for i in range(5):
            enemy = Entity(model='sphere', color=color.red, scale=(1,1,1), position=(random.randint(-5, 5), 1, random.randint(-5, 5)), collider='sphere', shader=basic_lighting_shader)
            self.enemies.append(enemy)

        # Create player
        self.character = FangameCharacter(position=(0, 3, 0))
        self.character.shader = basic_lighting_shader
        self.entities.append(self.character)

    def _game_update(self):
        dt = time.dt * self.time_scale
        if dt > 0.1: dt = 0.1

        self.character.game_update(dt, self.audio, self.enemies)

        # Update rings
        for ring in self.rings[:]:
            if self.character.intersects(ring).hit:
                self.rings.remove(ring)
                destroy(ring)
                self.ring_count += 1
                self.score += 10
                self.audio.play('ring', volume=0.3)

        # Update enemies
        for enemy in self.enemies[:]:
            if self.character.intersects(enemy).hit:
                if self.character.is_attacking():
                    self.enemies.remove(enemy)
                    destroy(enemy)
                    self.score += 10
                    self.audio.play('enemy_defeat', volume=0.5)

        # Update camera
        target_pos = self.character.world_position + Vec3(0, 2, 0)
        self.camera_rig.position = lerp(self.camera_rig.position, target_pos, dt * 4)

    def run(self):
        print("Starting the fangame world!")
        self.app.run()


class FangameCharacter(Entity):
    def __init__(self, **kwargs):
        super().__init__(model='sphere', color=color.blue, scale=(0.8, 0.8, 0.8), collider='sphere', **kwargs)

        self.base_speed = 10
        self.top_speed = 25
        self.acceleration = 15
        self.air_acceleration = 5
        self.deceleration = 10
        self.friction = 5
        self.gravity = 35
        self.air_control_factor = 0.6
        self.jump_height = 12
        self.max_fall_speed = -30

        self.velocity = Vec3(0,0,0)
        self.grounded = False
        self.ground_normal = Vec3(0,1,0)

    def game_update(self, dt, audio, enemies):
        # Update character movement
        move_input = Vec3(held_keys['d'] - held_keys['a'], 0, held_keys['w'] - held_keys['s']).normalized()

        cam_fwd = camera.forward
        cam_fwd.y = 0
        cam_fwd.normalize()
        cam_right = camera.right
        cam_right.y = 0
        cam_right.normalize()

        world_move_dir = (cam_fwd * move_input.z + cam_right * move_input.x).normalized()

        if move_input.length() > 0:
            self.rotation_y = lerp_angle(self.rotation_y, math.degrees(math.atan2(world_move_dir.x, world_move_dir.z)), dt * 10)

            accel = self.acceleration if self.grounded else self.air_acceleration
            current_vel_in_move_dir = self.velocity.dot(world_move_dir)

            if current_vel_in_move_dir < self.top_speed:
                new_velocity = self.velocity + world_move_dir * accel * dt
                self.velocity.x = new_velocity.x
                self.velocity.z = new_velocity.z

        # Apply gravity
        if not self.grounded:
            self.velocity.y -= self.gravity * dt

        # Move character
        self.position += self.velocity * dt

        # Check for ground collision
        ground_check = raycast(self.world_position + self.up * 0.1, self.down, distance=self.scale_y * 0.5 + 0.2, ignore=[self], debug=False)
        self.grounded = ground_check.hit

        if self.grounded:
            self.ground_normal = ground_check.world_normal
            self.y = ground_check.world_point.y + self.scale_y * 0.5
            if self.velocity.y < 0:
                self.velocity.y = 0

    def is_attacking(self):
        return False  # Implement attack logic here

if __name__ == '__main__':
    world = SonicFangameWorld()
    world.run()
