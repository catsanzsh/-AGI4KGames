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
        self.speed = 8
        self.jump_height = 4
        self.dash_cooldown = 1.5
        self.can_dash = True
        self.teleport_ready = True
        self.reality_warp = False
        self.gravity = 0.5
        self.y_velocity = 0

    def input(self, key):
        if key == 'space':
            self.jump()
        if key == 'shift':
            self.warp_dash()
        if key == 'e':
            self.reality_shift()

    def jump(self):
        if self.grounded:
            self.y_velocity = self.jump_height

    def warp_dash(self):
        if self.can_dash:
            self.can_dash = False
            self.animate_position(
                self.position + (self.right*5),
                duration=0.15,
                curve=curve.in_expo
            )
            invoke(setattr, self, 'can_dash', True, delay=self.dash_cooldown)

    def reality_shift(self):
        if self.teleport_ready:
            self.teleport_ready = False
            self.color = color.cyan
            invoke(setattr, self, 'color', color.hex("#6A5ACD"), delay=0.1)
            self.position += self.right * 3
            invoke(setattr, self, 'teleport_ready', True, delay=2)

    @property
    def grounded(self):
        return self.intersects().hit

    def update(self):
        self.rotation_z += held_keys['d'] * 5
        self.rotation_z -= held_keys['a'] * 5
        self.x += held_keys['d'] * time.dt * self.speed
        self.x -= held_keys['a'] * time.dt * self.speed
        # Gravity
        self.y_velocity -= self.gravity
        self.y += self.y_velocity * time.dt
        if self.grounded and self.y_velocity < 0:
            self.y_velocity = 0
            self.y = self.intersects().entity.world_y + self.scale_y/2

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
