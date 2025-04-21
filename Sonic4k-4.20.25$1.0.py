# test.py
# Meow! Patched by CATSDK ~nya!

from ursina import *
from ursina.shaders import basic_lighting_shader
import random
import math
from collections import deque

# --- CATSDK Patch: Added a placeholder Audio System ---
# Purrrfect! This will pretend to play sounds so the game doesn't get sad.
class FangameAudioSystem:
    def __init__(self):
        print("Purrr... Initializing cute little Audio System!") # Meow! Just letting you know it's here.

    def play(self, sound_name, volume=1.0):
        # Instead of crashing, we'll just purr about the sound!
        print(f"~Meow~ Pretending to play sound: '{sound_name}' at volume {volume:.1f}")
        # If you had actual sound files, you'd load and play them here! Nya~
        # Example using Ursina's Audio (if you have files):
        # try:
        #     sound = Audio(sound_name, loop=False, autoplay=True, volume=volume)
        # except Exception as e:
        #     print(f"Could not play '{sound_name}', maybe the file is missing? Rawr! {e}")
        pass # Keeps the game running smoothly!

class SonicFangameWorld:
    def __init__(self):
        self.app = Ursina()
        window.title = 'Sonic Fangame World Demo - Patched by CATSDK! Meow!'
        window.borderless = False
        window.fullscreen = False
        window.exit_button.visible = False
        window.fps_counter.enabled = True

        # Visual setup inspired by various fangames
        window.color = color.rgb(100, 150, 255)  # Bright blue sky, nya!
        self._setup_fangame_aesthetics()

        # Core systems
        self.entities = []
        self.rings = []
        self.enemies = []
        self.checkpoints = []
        self.ring_count = 0
        self.score = 0
        self.lives = 3
        self.time_scale = 1.0
        self.debug_mode = False

        # --- CATSDK Patch: Instantiated the placeholder Audio System ---
        self.audio = FangameAudioSystem() # Yay! Now we have our pretend audio player.
        # self.physics = FangamePhysicsSystem() # Physics seems handled inside character, purrfect!

        # Camera setup with smoothing
        self.camera_rig = Entity()
        camera.parent = self.camera_rig
        camera.position = (0, 15, -20)
        camera.rotation_x = 30

        # Create the world, meow!
        self._create_fangame_world()
        self._setup_controls()

        # Input buffer for advanced input combos
        self.input_buffer = deque(maxlen=10)

        # Bind game loop
        self.app.update = self._game_update

    def _setup_fangame_aesthetics(self):
        # Directional light
        self.directional_light = DirectionalLight(
            direction=(1, -1, 1),
            color=color.rgb(255, 250, 230),
            shadows=False # Shadows can be demanding, maybe turn on later? Purrr.
        )
        # Fog
        scene.fog_density = 0.005
        scene.fog_color = color.rgb(100, 150, 255)
        # Clip planes
        camera.clip_plane_far = 500
        camera.clip_plane_near = 0.1

    def _setup_controls(self):
        self.controls = {
            'left': 'a', 'right': 'd',
            'up': 'w', 'down': 's',
            'jump': 'space', 'boost': 'left shift',
            'spin_dash': 'left ctrl', 'stomp': 'e',
            'camera_left': 'q', 'camera_right': 'r'
        }

    def _create_fangame_world(self):
        # Ground
        # Meow! 'white_cube' is a built-in Ursina texture, so no external png needed here! Purrrfect.
        ground = Entity(
            model='plane', texture='white_cube',
            color=color.rgb(50, 200, 100), # Nice green grass!
            scale=(200,1,200), collider='box',
            position=(0,-0.5,0), texture_scale=(20,20)
        )
        self.entities.append(ground)

        # Checkpoints
        for i in range(3):
            cp = Entity(
                model='cube', color=color.yellow,
                scale=(2,3,2), position=(40*(i+1),0,0),
                collider='box',
                shader=basic_lighting_shader # Let's make things look a little nicer, nya!
            )
            self.checkpoints.append(cp)

        # Springs
        spring_defs = [
            (color.red, 20, (15,0,0)),
            (color.blue, 30, (25,0,0)),
            (color.yellow, 40, (35,0,0))
        ]
        for clr, power, pos in spring_defs:
            # Using a cylinder model might need collider='mesh', which can be slow.
            # Let's use a simple box collider adjusted to fit, purrr.
            s = Entity(model='cube', color=clr, scale=(1.5,0.5,1.5), # Using cube for simpler collision
                       position=pos, collider='box', # Box collider is usually faster!
                       shader=basic_lighting_shader)
            s.spring_power = power
            self.entities.append(s)

        # Rings
        patterns = [
            [(x,1,0) for x in range(0,50,3)],
            [(math.cos(a)*10+30,1,math.sin(a)*10)
             for a in [math.radians(x) for x in range(0,360,15)]],
            [(x,1,5 if x%10<5 else -5) for x in range(20,70,2)]
        ]
        for pattern in patterns:
            for pos in pattern:
                # Using a mesh collider for rings is okay, they are small! Nya!
                r = Entity(model='torus', color=color.yellow,
                           scale=(0.5,0.5,0.5), # Let's make the torus a bit thicker!
                           position=pos,
                           collider='sphere', # Sphere collider might be more efficient for rings!
                           rotation=(90,0,0), # Rotate it correctly!
                           shader=basic_lighting_shader,
                           double_sided=True) # So we can see it from both sides!
                self.rings.append(r)

        # Enemies (Badniks! Hiss!)
        enemy_defs = [
            (color.red, 1, 10, (25,0.5,0)),
            (color.blue,1.5,20,(40,0.75,5)),
            (color.purple,2,30,(55,1,-5))
        ]
        for clr, scale, points, pos in enemy_defs:
            e = Entity(model='sphere', color=clr,
                       scale=(scale,scale,scale), position=pos,
                       collider='sphere', # Sphere collider is purrfect for spheres!
                       shader=basic_lighting_shader)
            e.points = points
            self.enemies.append(e)

        # Platforms
        plat_defs = [(0,5,10,5,1,5),(0,10,20,3,1,3),(10,7,15,8,1,1)]
        for x,y,z,sx,sy,sz in plat_defs:
            p = Entity(model='cube', color=color.rgb(200,150,100),
                       scale=(sx,sy,sz), position=(x,y,z),
                       collider='box', # Box collider is good!
                       shader=basic_lighting_shader)
            self.entities.append(p)

        # Ramp
        ramp = Entity(model='cube', color=color.rgb(180,140,100),
                      scale=(10,1,5), position=(60,0,0),
                      rotation_z=-30, collider='box', # Box might be okay, but mesh is more accurate for ramps
                      shader=basic_lighting_shader)
                      # Consider collider='mesh' if collision feels weird, nya!
        self.entities.append(ramp)

        # Player Kitty!
        self.character = FangameCharacter(position=(0,3,0))
        self.character.shader = basic_lighting_shader # Make the kitty shiny!
        self.entities.append(self.character)

    def _game_update(self):
        dt = time.dt * self.time_scale
        if dt > 0.1: # Prevent huge jumps if lagging, purrr
            dt = 0.1

        # Update the kitty!
        self.character.game_update(dt, self.audio, self.enemies) # Pass dependencies needed

        # Rings collection
        for ring in self.rings[:]:
            if self.character.intersects(ring).hit:
                self.rings.remove(ring)
                destroy(ring)
                self.ring_count += 1
                self.score += 10
                self.audio.play('ring', volume=0.3) # Pretend play! Meow!

        # Enemy interaction
        for enemy in self.enemies[:]:
            if self.character.intersects(enemy).hit:
                if self.character.is_attacking(): # Check if kitty is attacking!
                    self.enemies.remove(enemy)
                    destroy(enemy)
                    self.score += enemy.points
                    self.audio.play('enemy_defeat', volume=0.5) # Pretend play!
                    self._create_explosion_effect(enemy.position)
                    # Give kitty a little bounce! Nya!
                    if not self.character.grounded:
                        self.character.velocity.y = self.character.jump_height * 0.6
                    self.character.homing_available = True # Can home again after hitting!
                elif not self.character.invincible:
                    self._player_hit()
                    break # Only process one hit per frame, purrr.

        # Springs interaction
        for ent in self.entities:
            if hasattr(ent, 'spring_power') and self.character.intersects(ent).hit:
                 # Check if kitty hits it from above or side, not below! Purrr.
                 if self.character.velocity.y <= 0 or abs(self.character.y - (ent.y + ent.scale_y/2)) < 0.5:
                     self.character.velocity.y = ent.spring_power
                     self.character.position.y = ent.y + ent.scale_y/2 + self.character.scale_y/2 # Prevent sticking
                     self.audio.play('spring', volume=0.5) # Pretend play!

        # Checkpoints interaction
        for cp in self.checkpoints:
            # Check if the checkpoint hasn't been activated yet (is still yellow)
            if cp.color == color.yellow and self.character.intersects(cp).hit:
                cp.color = color.lime # Changed to lime green, nya!
                self.audio.play('checkpoint', volume=0.4) # Pretend play!
                self.character.spawn_point = cp.world_position + Vec3(0,1,0) # Save spawn slightly above

        # Camera follow logic
        target_pos = self.character.world_position + Vec3(0, 2, 0) # Look slightly above the kitty
        # Smooth follow using lerp
        self.camera_rig.position = lerp(self.camera_rig.position, target_pos, dt * 4)

        # Keep camera distance based on speed, purrr!
        current_speed = Vec3(self.character.velocity.x, 0, self.character.velocity.z).length()
        target_dist = 15 + current_speed * 0.3 # Zoom out when faster! Nya!
        target_dist = clamp(target_dist, 15, 35) # Min/Max distance
        camera.z = lerp(camera.z, -target_dist, dt*2)

        # Manual Camera rotation input
        if held_keys[self.controls['camera_left']]:
            self.camera_rig.rotation_y += 100 * dt # Smoother rotation, purrr
        if held_keys[self.controls['camera_right']]:
            self.camera_rig.rotation_y -= 100 * dt

        # Speed effects, meow!
        if self.character.is_boosting and random.random() < 0.4: # A bit more frequent!
            self._create_speed_effect()

        # Update ring physics if any were lost
        for ring in self.rings:
            if hasattr(ring, 'velocity'): # Only update rings that were dropped
                ring.velocity.y -= self.character.gravity * dt * 2 # Rings fall faster!
                ring.position += ring.velocity * dt
                # Basic ground collision for dropped rings, nya!
                if ring.y < 0:
                    ring.y = 0
                    ring.velocity = Vec3(0,0,0) # Stop bouncing

    def _create_explosion_effect(self, position):
        # Little poof effect! Nya!
        for _ in range(8): # Less particles maybe?
            p = Entity(model='quad', # Using quads might be cheaper!
                       color=random.choice([color.orange, color.yellow, color.white]),
                       scale=random.uniform(0.2, 0.5),
                       position=position + Vec3(random.uniform(-0.2,0.2), random.uniform(-0.2,0.2), random.uniform(-0.2,0.2)),
                       billboard=True) # Always face the camera! Purrrfect!
            p.animate_scale(p.scale * 0.1, duration=random.uniform(0.3, 0.6), curve=curve.linear)
            p.animate_color(p.color.tint(-0.5), duration=0.5) # Fade out
            destroy(p, delay=random.uniform(0.3, 0.6))

    def _create_speed_effect(self):
        # Trailing speed lines, meow!
        pos = self.character.world_position - self.character.forward * 0.6 + self.character.right * random.uniform(-0.3, 0.3)
        pos.y += random.uniform(0.1, 0.6) # Spread them out vertically a bit
        p = Entity(model='quad', color=color.cyan.tint(0.3), # Slightly transparent cyan
                   scale=(random.uniform(0.5, 1.5), 0.05), # Thin lines
                   position=pos,
                   billboard=True) # Face the camera
        p.animate_scale_x(0.1, duration=0.3, curve=curve.linear)
        destroy(p, delay=0.3)

    def _player_hit(self):
        if self.invincible: # Can't get hit if invincible! Nya!
            return

        self.audio.play('hurt', volume=0.6) # Play hurt sound!
        self.character.invincible = True # Grant temporary invincibility! Purrr.
        self.character.invincibility_timer = 1.5 # For 1.5 seconds
        self.character.blink(duration=1.5) # Make kitty blink!

        if self.ring_count > 0:
            lost_rings = min(self.ring_count, 20) # Lose up to 20 rings
            self.ring_count -= lost_rings
            self.score -= lost_rings * 5 # Lose some score too maybe? Meow?
            if self.score < 0: self.score = 0

            self.audio.play('ring_loss', volume=0.5) # Pretend play!

            # Scatter rings! Nya!
            for i in range(lost_rings):
                angle = math.radians(random.uniform(0, 360))
                dist = random.uniform(1, 3)
                vel_y = random.uniform(4, 8)
                vel_xz = random.uniform(2, 5)

                r = Entity(model='torus', color=color.yellow,
                           scale=(0.5,0.5,0.5), # Same thicker rings
                           position=self.character.world_position + Vec3(0,0.5,0),
                           rotation=(90,0,0),
                           collider='sphere', # Keep sphere collider
                           shader=basic_lighting_shader,
                           double_sided=True)

                r.velocity = Vec3(math.cos(angle) * vel_xz, vel_y, math.sin(angle) * vel_xz)
                # Make these temporary rings, not collectible again? Or collectable for less points?
                # For now, just make them vanish. Nya!
                r.fade_out(duration=3)
                destroy(r, delay=3.1)
        else:
            # No rings, kitty takes a big hit!
            self.lives -= 1
            self.character.velocity = Vec3(0, 5, 0) # Little bounce up
            if self.lives <= 0:
                self._game_over()
            else:
                # Respawn sequence
                self.audio.play('death', volume=0.7) # Pretend play!
                # Maybe add a small delay/fade out before respawning? Purrr.
                invoke(self.respawn_player, delay=1.5) # Respawn after a short delay


    def respawn_player(self):
         self.character.position = self.character.spawn_point
         self.character.velocity = Vec3(0,0,0)
         self.character.visible = True
         self.character.invincible = True # Invincible after respawn too!
         self.character.invincibility_timer = 2.0
         self.character.blink(duration=2.0)
         # Reset boost maybe?
         self.character.boost_energy = self.character.max_boost

    def _game_over(self):
        print(f"Game Over! Nya... Final Score: {self.score}")
        self.audio.play('game_over', volume=0.8) # Pretend play!
        # Maybe show a game over screen instead of quitting? Purrr.
        Text(text=f"Game Over!\nScore: {self.score}", origin=(0,0), scale=3, background=True)
        self.character.visible = False # Hide the kitty
        # application.quit() # Maybe don't quit right away?

    def run(self):
        print("Starting the cute fangame world! Meow!")
        self.app.run()


class FangameCharacter(Entity):
    def __init__(self, **kwargs):
        super().__init__(model='sphere', color=color.blue, # Kitty is blue!
                         scale=(0.8, 0.8, 0.8), # Slightly smaller kitty?
                         collider='sphere', **kwargs)
        # Movement Stats! Nya!
        self.base_speed = 10 # A bit faster!
        self.top_speed = 25
        self.acceleration = 15 # Accelerate faster on ground
        self.air_acceleration = 5 # Slower acceleration in air
        self.deceleration = 10 # Stop faster
        self.friction = 5 # Ground friction
        self.gravity = 35 # Stronger gravity, more Sonic-like! Purrr.
        self.air_control_factor = 0.6 # How much control in the air
        self.jump_height = 12
        self.max_fall_speed = -30 # Terminal velocity! Nya!

        self.velocity = Vec3(0,0,0)
        self.grounded = False
        self.ground_normal = Vec3(0,1,0) # What direction the ground is facing

        # Mechanics! Meow!
        self.spin_dash_charge = 0
        self.max_spin_dash_charge = 120
        self.min_spin_dash_speed = 15
        self.spin_dash_speed_factor = 0.3

        self.boost_energy = 100
        self.max_boost = 100
        self.boost_speed_multiplier = 1.8 # How much faster boost makes you
        self.boost_cost_per_second = 30
        self.boost_recharge_per_second = 10
        self.boost_min_activation = 10 # Need some boost to start

        self.stomp_speed = -25
        self.homing_speed = 35
        self.homing_range = 20 # How far kitty can see enemies!
        self.homing_angle_limit = 70 # Cone in front for homing target

        # State flags
        self.is_boosting = False
        self.is_charging_spin_dash = False
        self.is_rolling = False # General rolling state
        self.is_stomping = False
        self.is_homing = False
        self.homing_available = False # Can only home once per jump usually
        self.just_jumped = False # To prevent double jumps instantly

        # Invincibility! Nya!
        self.invincible = False
        self.invincibility_timer = 0

        # State machine (simple version)
        self.state = 'idle' # idle, walking, running, jumping, rolling, spinning, boosting, stomping, homing
        self.spawn_point = self.position + Vec3(0,1,0) # Start spawn point slightly above initial position

        # Store audio system reference
        self.audio = None
        # Store potential homing targets
        self.potential_targets = []


    def is_attacking(self):
        # Kitty is attacking if rolling, stomping, or homing! Nya!
        return self.is_rolling or self.is_stomping or self.is_homing

    def game_update(self, dt, audio, enemies):
        # Store references! Purrr.
        self.audio = audio
        self.potential_targets = enemies

        # --- Ground Check ---
        # Cast slightly downwards from kitty's center
        ground_check = raycast(self.world_position + self.up * 0.1, self.down, distance=self.scale_y * 0.5 + 0.2, ignore=[self], debug=False)
        self.grounded = ground_check.hit

        if self.grounded:
            self.ground_normal = ground_check.world_normal
            # Snap to ground if needed, slightly adjust position
            self.y = ground_check.world_point.y + self.scale_y * 0.5
            # Reset vertical velocity if we just landed
            if self.velocity.y < 0:
                self.velocity.y = 0
            # Allow homing again after landing
            self.homing_available = True
            self.is_homing = False # No longer homing if grounded
            self.is_stomping = False # No longer stomping if grounded
            if self.just_jumped: self.just_jumped = False # Can jump again

            # Cancel stomp state if we hit ground
            if self.state == 'stomping':
                self.state = 'idle' # Or maybe a little 'land' animation? Purr.
                # Add small landing effect?
        else:
            self.ground_normal = Vec3(0,1,0) # Assume flat ground normal if airborne
            # Apply Gravity
            self.velocity.y -= self.gravity * dt
            # Clamp fall speed
            if self.velocity.y < self.max_fall_speed:
                self.velocity.y = self.max_fall_speed
            # Can't charge spindash in air
            if self.is_charging_spin_dash:
                self._release_spin_dash() # Release if kitty falls off edge while charging
                self.is_charging_spin_dash = False

        # --- Handle Input ---
        move_input = Vec3(held_keys[self.controls['right']] - held_keys[self.controls['left']],
                           0,
                           held_keys[self.controls['up']] - held_keys[self.controls['down']]).normalized()

        # --- Camera Relative Movement ---
        # Get camera's forward direction on the XZ plane
        cam_fwd = camera.forward
        cam_fwd.y = 0
        cam_fwd.normalize()
        cam_right = camera.right
        cam_right.y = 0
        cam_right.normalize()

        # Calculate world direction based on input and camera
        world_move_dir = (cam_fwd * move_input.z + cam_right * move_input.x).normalized()

        # --- State Updates & Movement Logic ---

        # Stop boosting if button released or out of energy
        if self.is_boosting and (not held_keys[self.controls['boost']] or self.boost_energy <= 0):
            self.is_boosting = False
            self.audio.play('boost_end') # Pretend sound

        # Boosting depletes energy, otherwise recharge
        if self.is_boosting:
            self.boost_energy -= self.boost_cost_per_second * dt
            if self.boost_energy <= 0:
                self.boost_energy = 0
                self.is_boosting = False # Force stop if empty
        elif self.grounded: # Only recharge boost on ground! Nya!
            self.boost_energy = min(self.max_boost, self.boost_energy + self.boost_recharge_per_second * dt)

        # Start Boosting
        if self.grounded and held_keys[self.controls['boost']] and move_input.length() > 0 and self.boost_energy > self.boost_min_activation and not self.is_boosting:
            self.is_boosting = True
            self.is_rolling = True # Boosting often involves rolling! Purrr.
            self.audio.play('boost_start') # Pretend sound

        # Spin Dash Charging
        if self.grounded and held_keys[self.controls['spin_dash']] and not self.is_rolling:
            if not self.is_charging_spin_dash: # First frame of charging
                self.audio.play('spindash_charge') # Pretend sound
                self.velocity = Vec3(0,0,0) # Stop moving while charging
            self.is_charging_spin_dash = True
            self.spin_dash_charge = min(self.max_spin_dash_charge, self.spin_dash_charge + 90 * dt) # Charge up!
            self.state = 'spinning'
            # Make kitty face forward based on last direction or camera?
            # For now, just stay facing current direction.

        # Release Spin Dash
        if self.is_charging_spin_dash and not held_keys[self.controls['spin_dash']]:
           self._release_spin_dash()

        # Handle movement direction and speed
        current_speed_xz = Vec3(self.velocity.x, 0, self.velocity.z).length()
        target_speed = self.top_speed

        if self.is_boosting:
            target_speed *= self.boost_speed_multiplier

        # Apply acceleration / deceleration
        if move_input.length() > 0 and not self.is_charging_spin_dash:
            # Rotate kitty to face movement direction
            target_angle = math.degrees(math.atan2(world_move_dir.x, world_move_dir.z))
            # Use shortest angle lerp! Purrrrfect!
            self.rotation_y = lerp_angle(self.rotation_y, target_angle, dt * 10)

            # Acceleration differs in air vs ground
            accel = self.acceleration if self.grounded else self.air_acceleration
            current_vel_in_move_dir = self.velocity.dot(world_move_dir)

            # Only accelerate if below target speed or moving against direction
            if current_vel_in_move_dir < target_speed:
                 new_velocity = self.velocity + world_move_dir * accel * dt
                 # Clamp speed if needed? Might feel better without strict clamp during accel.
                 self.velocity.x = new_velocity.x
                 self.velocity.z = new_velocity.z
                 # Limit speed if not boosting (but allow boost to exceed)
                 if not self.is_boosting:
                     vel_xz = Vec3(self.velocity.x, 0, self.velocity.z)
                     if vel_xz.length() > self.top_speed:
                         vel_xz = vel_xz.normalized() * self.top_speed
                         self.velocity.x = vel_xz.x
                         self.velocity.z = vel_xz.z


            # Air control adjustment - allows changing direction mid-air
            if not self.grounded:
                 # Project current velocity onto new direction and lerp
                 proj_vel = world_move_dir * max(0, current_vel_in_move_dir) # Velocity along the new direction
                 side_vel = self.velocity - proj_vel # Velocity perpendicular to new direction
                 # Blend towards the new direction
                 self.velocity = lerp(self.velocity, proj_vel + side_vel, dt * self.air_control_factor * 5)


            # Update state based on speed
            if self.grounded:
                if self.is_rolling: self.state = 'rolling'
                elif self.is_boosting: self.state = 'boosting'
                elif current_speed_xz > self.base_speed * 0.8: self.state = 'running'
                else: self.state = 'walking'

        elif self.grounded and not self.is_charging_spin_dash and not self.is_rolling: # No input, grounded, not charging/rolling
             # Apply friction / deceleration
             speed_reduction = (self.deceleration + self.friction) * dt
             if current_speed_xz > speed_reduction:
                 decel_factor = (current_speed_xz - speed_reduction) / current_speed_xz
                 self.velocity.x *= decel_factor
                 self.velocity.z *= decel_factor
             else:
                 self.velocity.x = 0
                 self.velocity.z = 0
             self.state = 'idle'

        # Jumping
        if self.grounded and held_keys[self.controls['jump']] and not self.just_jumped and not self.is_charging_spin_dash:
            self.velocity.y = self.jump_height
            self.grounded = False
            self.state = 'jumping'
            self.audio.play('jump') # Pretend sound
            self.homing_available = True # Can home after jumping!
            self.just_jumped = True # Prevent immediate re-jump next frame
            self.is_rolling = False # Jumping usually uncurls kitty!

        # Stomping! Nya!
        if not self.grounded and held_keys[self.controls['stomp']] and not self.is_stomping and not self.is_homing:
            self.is_stomping = True
            self.velocity.y = self.stomp_speed
            self.velocity.x = 0 # Stop horizontal movement during stomp
            self.velocity.z = 0
            self.state = 'stomping'
            self.audio.play('stomp') # Pretend sound

        # Homing Attack! Pew Pew!
        if not self.grounded and held_keys[self.controls['jump']] and self.homing_available and not self.is_stomping and self.state != 'jumping': # Check state to avoid double jump triggering homing
            target = self._find_homing_target()
            if target:
                direction = (target.world_position - self.world_position).normalized()
                self.velocity = direction * self.homing_speed
                self.is_homing = True
                self.state = 'homing'
                self.audio.play('homing_attack') # Pretend sound
                self.homing_available = False # Used homing attack
            else:
                # Maybe a little jump dash if no target? Or just ignore?
                # Let's ignore for now, purrr.
                pass

        # Rolling state management
        # Automatically roll if speed is high and grounded? Or require input?
        # Let's keep it simple: boosting or spin-dashing makes you roll.
        # Stop rolling if speed drops too low while grounded and not boosting/spin-dashing.
        if self.is_rolling and self.grounded and not self.is_boosting and not self.is_charging_spin_dash and current_speed_xz < self.base_speed * 0.5:
            self.is_rolling = False


        # --- Apply Velocity ---
        # Handle slopes! Nya! Project velocity onto the ground plane if grounded.
        if self.grounded and not self.just_jumped: # Don't interfere right after jumping
            # Project velocity onto the plane defined by the ground normal
            projected_velocity = self.velocity - self.ground_normal * self.velocity.dot(self.ground_normal)
            self.velocity = projected_velocity

            # Add a small downward force to help stick to slopes?
            # self.velocity -= self.ground_normal * self.gravity * dt * 0.5

        # Actual movement application (using move function handles collisions better)
        move_amount = self.velocity * dt
        self.position += move_amount
        # Using Ursina's built-in collision handling by moving the entity


        # --- Invincibility Timer ---
        if self.invincible:
            self.invincibility_timer -= dt
            if self.invincibility_timer <= 0:
                self.invincible = False
                self.invincibility_timer = 0
                self.color = color.blue # Restore original color! Meow!
                self.alpha = 1 # Restore alpha

    def _release_spin_dash(self):
         # Release spin dash only if charged enough! Nya!
         if self.spin_dash_charge > 10: # Minimum charge needed
             speed = self.min_spin_dash_speed + self.spin_dash_charge * self.spin_dash_speed_factor
             # Use the direction the character is facing!
             self.velocity = self.forward * speed
             self.audio.play('spindash_release') # Pretend sound
             self.is_rolling = True # Start rolling!
             self.state = 'rolling'
         self.spin_dash_charge = 0
         self.is_charging_spin_dash = False

    def _find_homing_target(self):
        best_target = None
        min_dist_sq = self.homing_range * self.homing_range # Check within range

        for enemy in self.potential_targets:
            if not hasattr(enemy, 'position'): continue # Skip if enemy has no position (already destroyed?)

            direction_to_enemy = enemy.world_position - self.world_position
            dist_sq = direction_to_enemy.length_squared()

            if dist_sq < min_dist_sq:
                # Check if target is generally in front of the player
                # Using dot product with kitty's forward direction
                dir_normalized = direction_to_enemy.normalized()
                dot_product = self.forward.dot(dir_normalized)

                # Convert dot product to angle (approx)
                angle = math.degrees(math.acos(clamp(dot_product, -1, 1)))

                if angle < self.homing_angle_limit: # Check if within homing cone
                    min_dist_sq = dist_sq
                    best_target = enemy

        return best_target

    # Meow! Add a blink function for invincibility!
    def blink(self, duration=1.0):
        self.animate_alpha(0, duration=duration/10, loop=True, curve=curve.linear_boomerang)
        # Need to stop the animation later
        invoke(setattr, self, 'alpha', 1, delay=duration)


if __name__ == '__main__':
    world = SonicFangameWorld()
    world.run()
