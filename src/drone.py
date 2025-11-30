import math
import time
from src.geometry import get_distance, get_bearing, move_point

class DroneInterceptor:
    def __init__(self):
        # ICN Airport Coordinates
        self.lat = 37.4602
        self.lon = 126.4407
        self.alt = 0
        
        # Physics State
        self.speed = 800  # m/s (approx Mach 2.3)
        self.heading = 0  # Degrees
        self.active = False
        
        # PN Guidance State
        self.prev_los_angle = None
        self.last_update_time = time.time()
        self.nav_constant = 4.0  # N value
        
    def launch(self):
        self.active = True
        self.lat = 37.4602
        self.lon = 126.4407
        self.heading = 0 
        self.prev_los_angle = None
        self.last_update_time = time.time()
        print(f"Drone launched from ICN at {self.lat}, {self.lon}")

    def update(self, target_lat, target_lon, target_alt):
        if not self.active:
            return None

        current_time = time.time()
        total_dt = current_time - self.last_update_time
        self.last_update_time = current_time

        # 초기화 로직: 첫 업데이트 시 타겟 방향으로 정렬
        dist_to_target = get_distance(self.lat, self.lon, target_lat, target_lon)
        if self.prev_los_angle is None or total_dt > 1.0:
            los_angle = get_bearing(self.lat, self.lon, target_lat, target_lon)
            self.heading = los_angle
            self.prev_los_angle = los_angle
            return self._get_state(dist_to_target)

        # [수정 핵심] Sub-stepping: 정밀 유도를 위해 시간을 0.01초 단위로 쪼개서 계산
        SIM_STEP = 0.01
        remaining_time = total_dt
        
        while remaining_time > 0:
            step = min(remaining_time, SIM_STEP)
            
            # 1. 기하학적 정보 계산
            # (Note: 타겟 위치는 고정되어 있다고 가정. 실제로는 타겟도 움직여야 하지만 
            #  드론이 훨씬 빠르므로(800m/s vs 250m/s) 드론만 정밀하게 움직여도 충분함)
            dist_curr = get_distance(self.lat, self.lon, target_lat, target_lon)
            los_angle = get_bearing(self.lat, self.lon, target_lat, target_lon)
            
            # 2. PN 유도
            if self.prev_los_angle is not None:
                diff = los_angle - self.prev_los_angle
                if diff > 180: diff -= 360
                elif diff < -180: diff += 360
                
                # 매우 짧은 step이라도 rate는 초당 변화율로 환산
                los_rate = diff / step if step > 0 else 0
                
                # 가속 명령
                turn_rate = self.nav_constant * los_rate
                max_turn_rate = 30.0
                turn_rate = max(min(turn_rate, max_turn_rate), -max_turn_rate)
                
                self.heading += turn_rate * step
                self.heading = (self.heading + 360) % 360
            
            self.prev_los_angle = los_angle
            
            # 3. 위치 업데이트
            dist_step = self.speed * step
            self.lat, self.lon = move_point(self.lat, self.lon, dist_step, self.heading)
            
            # 고도 제어 (비례 제어)
            alt_error = target_alt - self.alt
            self.alt += alt_error * 2.0 * step # 게인 값을 높여서 더 빨리 고도 맞춤
            
            remaining_time -= step
            
            # [종료 조건] 명중 판정 시 즉시 루프 탈출 (불필요한 Overshoot 방지)
            if dist_curr < 5.0:
                break

        final_dist = get_distance(self.lat, self.lon, target_lat, target_lon)
        return self._get_state(final_dist)

    def _get_state(self, dist=0):
        return {
            "lat": self.lat,
            "lon": self.lon,
            "alt": self.alt,
            "heading": self.heading,
            "speed": self.speed,
            "distance_to_target": dist,
            "active": self.active
        }
