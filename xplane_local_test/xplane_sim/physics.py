from dataclasses import dataclass
import math

@dataclass
class SimState:
    lat: float = -23.4322     # Galeão de presente ;)
    lon: float = -46.4695
    alt_m: float = 30.0
    pitch_deg: float = 0.0
    roll_deg: float = 0.0
    yaw_deg: float = 90.0     # rumo leste
    v_ms: float = 50.0

def step_dynamics(s: SimState, ctrls, dt: float):
    # ctrls = [aileron, elevator, rudder, throttle]
    aileron, elevator, rudder, throttle = ctrls
    # parâmetros “brinquedo”
    max_roll_rate = 40.0      # deg/s @ |aileron|=1
    max_pitch_rate = 30.0     # deg/s
    max_yaw_rate = 15.0       # deg/s
    max_accel = 5.0           # m/s² @ throttle=1
    Cd = 0.015                # arrasto pseudo
    rho = 1.225
    mass = 1200.0

    # atitude
    s.roll_deg  += max_roll_rate  * aileron * dt
    s.pitch_deg += max_pitch_rate * (-elevator) * dt   # convenção: +elevator cabra => nariz sobe; invertido aqui
    s.yaw_deg   += max_yaw_rate   * rudder * dt
    s.yaw_deg = (s.yaw_deg + 360.0) % 360.0

    # velocidade
    drag = Cd * s.v_ms * s.v_ms
    s.v_ms += (max_accel * max(0.0, throttle) - drag / max(1.0, mass/10.0)) * dt
    s.v_ms = max(0.0, s.v_ms)

    # subir/descer por pitch (simplificado)
    climb_rate = s.v_ms * math.sin(math.radians(s.pitch_deg))
    s.alt_m += climb_rate * dt
    s.alt_m = max(0.0, s.alt_m)

    # avançar lat/lon pelo rumo e v horizontal
    vxy = s.v_ms * math.cos(math.radians(s.pitch_deg))
    R_earth = 6_371_000.0
    d_north = vxy * math.cos(math.radians(s.yaw_deg)) * dt
    d_east  = vxy * math.sin(math.radians(s.yaw_deg)) * dt
    s.lat += (d_north / R_earth) * (180.0 / math.pi)
    s.lon += (d_east  / (R_earth * math.cos(math.radians(s.lat)))) * (180.0 / math.pi)
