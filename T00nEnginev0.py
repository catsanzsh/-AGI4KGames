import math

from ursina import raycast
from ursina.camera import clamp
 

def _find_homing_target(self):
    best_target = None
    min_dist_sq = self.homing_range * self.homing_range

    for enemy in self.potential_targets:
        if not enemy.enabled:
            continue

        direction_to_enemy = enemy.world_position - self.world_position
        dist_sq = direction_to_enemy.length_squared()

        if 0.1 < dist_sq < min_dist_sq:
            dir_normalized = direction_to_enemy.normalized()
            dot_product = self.forward.dot(dir_normalized)
            angle = math.degrees(math.acos(clamp(dot_product, -1, 1)))

            if angle < self.homing_angle_limit:
                # Line-of-sight check
                los_check = raycast(self.world_position + self.up * 0.1, dir_normalized, distance=dist_sq**0.5, ignore=[self])
                if not los_check.hit or los_check.entity == enemy:
                    min_dist_sq = dist_sq
                    best_target = enemy

    return best_target
