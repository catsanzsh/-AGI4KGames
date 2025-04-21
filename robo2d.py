from ursina import *
from ursina.shaders import basic_lighting_shader
import random

class Astra(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='quad',
            texture='astro_fox',
            color=color.hex("#6A5ACD"),
            scale=(1,2,1),
            shader=basic_lighting_shader,
            position=(0,1,0),
            collider='box',
            **kwargs
        )
        self.max_speed = 18
        self.acceleration = 60
        self.deceleration = 40
        self.jump_power = 13
        self.gravity = 36
        self.y_velocity = 0
        self.x_velocity = 0
        self.grounded = False
        self.facing = 1
        self.rolling = False
        self.roll_speed = 22
        self.roll_decel = 20
        self.spindash_ready = False
        self.spindash_power = 0
        self.spindash_max = 32
        self.spindash_charge = 0

    def input(self, key):
        if key == 'space':
            self.jump()
        if key == 'down arrow' and self.grounded:
            self.rolling = True
            self.x_velocity = self.facing * self.roll_speed
        if key == 'shift' and self.grounded and held_keys['down arrow']:
            self.spindash_ready = True
        if key == 'shift up' and self.spindash_ready:
            self.spindash_ready = False
            self.rolling = True
            self.x_velocity = self.facing * max(self.spindash_charge, self.roll_speed)
            self.spindash_charge = 0

    def jump(self):
        if self.grounded:
            self.y_velocity = self.jump_power
            self.grounded = False

    def update(self):
        dt = time.dt
        move = held_keys['d'] - held_keys['a']
        if move:
            self.facing = 1 if move > 0 else -1
        # Spindash charge
        if self.spindash_ready:
            if self.spindash_charge < self.spindash_max:
                self.spindash_charge += 60 * dt
        # Rolling
        if self.rolling:
            self.x_velocity = lerp(self.x_velocity, 0, self.roll_decel * dt / self.roll_speed)
            if abs(self.x_velocity) < 2:
                self.rolling = False
        # Normal movement
        elif move:
            self.x_velocity += move * self.acceleration * dt
            if abs(self.x_velocity) > self.max_speed:
                self.x_velocity = self.max_speed * self.facing
        else:
            # Deceleration
            if abs(self.x_velocity) > 0:
                self.x_velocity -= self.deceleration * dt * (1 if self.x_velocity > 0 else -1)
                if abs(self.x_velocity) < 1:
                    self.x_velocity = 0
        # Gravity
        self.y_velocity -= self.gravity * dt
        # Horizontal move and collision
        self.x += self.x_velocity * dt
        # Vertical move and collision (step by step for better collision)
        step = self.y_velocity * dt
        steps = max(1, int(abs(step) // 0.1))
        collided = False
        for i in range(steps):
            self.y += step / steps
            hit = self.intersects()
            if hit.hit:
                if self.y_velocity < 0 and self.y > hit.entity.y:
                    self.y = hit.entity.world_y + self.scale_y/2
                    self.y_velocity = 0
                    self.grounded = True
                    collided = True
                    break
                else:
                    self.grounded = False
        if not collided:
            self.grounded = False
        # Animation (optional): flip sprite
        self.scale_x = abs(self.scale_x) * self.facing

app = Ursina()
window.color = color.black

# World setup
ground = Entity(
    model='cube', 
    scale=(50,1,50),
    texture='grass',
    collider='box',
    position=(0, -1, 0)
)
for i in range(20):
    Entity(
        model='cube',
        position=(random.randint(-20,20), 0.5, random.randint(-20,20)),
        scale=(2,2,2),
        texture='brick',
        collider='box'
    )

astra = Astra()
camera_rig = Entity()
camera.parent = camera_rig
camera.position = (0,15,-20)
camera.rotation_x = 30

def update():
    camera_rig.position = lerp(
        camera_rig.position,
        (astra.x, astra.y + 5, astra.z),
        time.dt * 8
    )

app.run()
