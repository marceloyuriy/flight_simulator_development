# sim_io/xplane_mock.py
from __future__ import annotations
import math, time, threading
from typing import List, Dict, Any, Optional

def _clamp(x, lo, hi): return max(lo, min(hi, x))

class XPlaneConnect:
    """
    Mock compatível com a API do XPlaneConnect suficiente para desenvolvimento local.
    Métodos cobertos: connect, close, getPOSI, sendPOSI, sendCTRL, getDREFs, getDREF, sendDREF, pauseSim.
    Também expõe step(dt) para avanço manual da simulação.
    """

    def __init__(self, addr: str="127.0.0.1", port: int=49009, timeout: float=1.0):
        self.addr, self.port, self.timeout = addr, port, timeout
        # Estado mínimo do "avião"
        self.state = {
            "lat": -3.7327,     # Fortaleza-ish, graus
            "lon": -38.5267,
            "alt": 100.0,       # m MSL
            "pitch": 0.0,       # deg
            "roll": 0.0,        # deg
            "yaw": 90.0,        # deg (rumo Leste)
            "gear": 1.0,
            "v_true": 40.0,     # m/s
        }
        # Superfícies/atuadores
        self.ctrl = {
            "elevator": 0.0, "aileron": 0.0, "rudder": 0.0,
            "throttle": 0.2, "flaps": 0.0, "speedbrakes": 0.0
        }
        # DREFs conhecidos (espelhados com o estado) + drefs arbitrários
        self._drefs: Dict[str, List[float]] = {
            "sim/operation/pause": [0.0],
            "sim/flightmodel/position/latitude":  [self.state["lat"]],
            "sim/flightmodel/position/longitude": [self.state["lon"]],
            "sim/flightmodel/position/elevation": [self.state["alt"]],  # m
            "sim/flightmodel/position/psi":       [self.state["yaw"]],  # deg
            "sim/flightmodel/position/theta":     [self.state["pitch"]],
            "sim/flightmodel/position/phi":       [self.state["roll"]],
            "sim/cockpit2/engine/actuators/throttle_ratio_all": [self.ctrl["throttle"]],
            "sim/joystick/yoke_pitch_ratio":  [self.ctrl["elevator"]],
            "sim/joystick/yoke_roll_ratio":   [self.ctrl["aileron"]],
            "sim/joystick/yoke_heading_ratio":[self.ctrl["rudder"]],
        }
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_t = None

    # --- utilidades internas -------------------------------------------------
    def _sync_drefs_from_state(self):
        self._drefs["sim/flightmodel/position/latitude"][0]  = self.state["lat"]
        self._drefs["sim/flightmodel/position/longitude"][0] = self.state["lon"]
        self._drefs["sim/flightmodel/position/elevation"][0] = self.state["alt"]
        self._drefs["sim/flightmodel/position/psi"][0]       = self.state["yaw"]
        self._drefs["sim/flightmodel/position/theta"][0]     = self.state["pitch"]
        self._drefs["sim/flightmodel/position/phi"][0]       = self.state["roll"]
        self._drefs["sim/cockpit2/engine/actuators/throttle_ratio_all"][0] = self.ctrl["throttle"]
        self._drefs["sim/joystick/yoke_pitch_ratio"][0]   = self.ctrl["elevator"]
        self._drefs["sim/joystick/yoke_roll_ratio"][0]    = self.ctrl["aileron"]
        self._drefs["sim/joystick/yoke_heading_ratio"][0] = self.ctrl["rudder"]

    def _physics_step(self, dt: float):
        """Modelo bobinho mas estável para depuração. Substitua pelo seu dynamics depois."""
        if self._drefs.get("sim/operation/pause", [0])[0] >= 0.5:
            return
        # ganhos de “pilotagem”
        p_rate = 30.0 * self.ctrl["elevator"]   # deg/s
        r_rate = 50.0 * self.ctrl["aileron"]
        y_rate = 25.0 * self.ctrl["rudder"]
        self.state["pitch"] += p_rate * dt
        self.state["roll"]  += r_rate * dt
        self.state["yaw"]   += y_rate * dt

        # velocidade: throttle empurra, arrasto quadrático simplificado
        t = _clamp(self.ctrl["throttle"], 0.0, 1.0)
        thrust = 20.0 * t
        drag   = 0.015 * (self.state["v_true"]**2)
        acc    = (thrust - drag) / 50.0
        self.state["v_true"] = max(0.0, self.state["v_true"] + acc*dt)

        # cinemática aproximada
        spd = self.state["v_true"]
        pitch_rad = math.radians(self.state["pitch"])
        yaw_rad   = math.radians(self.state["yaw"])
        climb     = spd * math.sin(pitch_rad)
        vxy       = spd * math.cos(pitch_rad)
        vx = vxy * math.cos(yaw_rad)
        vy = vxy * math.sin(yaw_rad)
        # converter m -> graus (aproximação)
        m_per_deg_lat = 111_320.0
        m_per_deg_lon = 111_320.0 * math.cos(math.radians(self.state["lat"]))
        self.state["lat"] += (vy / m_per_deg_lat) * dt
        self.state["lon"] += (vx / m_per_deg_lon) * dt if m_per_deg_lon != 0 else 0.0
        self.state["alt"] = max(0.0, self.state["alt"] + climb * dt)

        self._sync_drefs_from_state()

    # --- API “igual” à do XPlaneConnect -------------------------------------
    def connect(self):
        # No mock, não há nada a fazer. Mantemos compatibilidade com client real.
        return True

    def close(self):
        self.stop_auto_step()

    # POSI: [lat, lon, alt_msl, pitch, roll, yaw, gear]
    def getPOSI(self, ac: int = 0) -> List[float]:
        return [
            self.state["lat"], self.state["lon"], self.state["alt"],
            self.state["pitch"], self.state["roll"], self.state["yaw"],
            self.state["gear"]
        ]

    def sendPOSI(self, posi: List[float], ac: int = 0):
        lat, lon, alt, pitch, roll, yaw, gear = posi
        self.state.update({
            "lat": float(lat), "lon": float(lon), "alt": float(alt),
            "pitch": float(pitch), "roll": float(roll), "yaw": float(yaw),
            "gear": float(gear)
        })
        self._sync_drefs_from_state()

    # CTRL: [elevator, aileron, rudder, throttle, gear, flaps, ac, speedbrakes]
    def sendCTRL(self, ctrl: List[float], ac: int = 0):
        e, a, r, t, g, f, _ac, sb = ctrl
        self.ctrl["elevator"] = _clamp(float(e), -1, 1)
        self.ctrl["aileron"]  = _clamp(float(a), -1, 1)
        self.ctrl["rudder"]   = _clamp(float(r), -1, 1)
        self.ctrl["throttle"] = _clamp(float(t),  0, 1)
        # gear: 0 up, 1 down, -1 toggle (aqui ignoramos o toggle)
        if g in (-1, 0, 1): self.state["gear"] = float(1 if g == 1 else 0)
        self.ctrl["flaps"]       = _clamp(float(f), 0, 1)
        self.ctrl["speedbrakes"] = _clamp(float(sb), -0.5, 1.5)
        self._sync_drefs_from_state()

    def getDREFs(self, drefs: List[str]) -> List[List[float]]:
        out = []
        for d in drefs:
            if d in self._drefs:
                out.append(list(self._drefs[d]))
            else:
                # se desconhecido, cria “slot” e retorna 0.0
                self._drefs[d] = [0.0]
                out.append([0.0])
        return out

    def getDREF(self, dref: str) -> List[float]:
        return self.getDREFs([dref])[0]

    def sendDREF(self, dref: str, values: List[float]):
        self._drefs[dref] = list(values)
        # sincroniza espelhos importantes
        if dref == "sim/operation/pause":
            self._drefs[dref][0] = 1.0 if values[0] else 0.0
        self._sync_drefs_from_state()

    def pauseSim(self, pause: int):
        self._drefs["sim/operation/pause"] = [1.0 if pause else 0.0]

    # stepping manual/automático
    def step(self, dt: float):
        self._physics_step(dt)

    def start_auto_step(self, dt: float = 0.02):
        if self._running: return
        self._running, self._last_t = True, time.perf_counter()
        def _loop():
            while self._running:
                now = time.perf_counter()
                dt_local = min(0.05, now - self._last_t) if self._last_t else dt
                self._last_t = now
                self._physics_step(dt_local if dt_local > 0 else dt)
                time.sleep(dt)
        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()

    def stop_auto_step(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.2)
        self._thread = None
