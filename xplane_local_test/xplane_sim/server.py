import asyncio, json, time
from typing import Dict, Any
from xplane_local_test.xplane_sim.physics import SimState, step_dynamics
from xplane_local_test.xplane_sim.datarefs import DREFS

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 49009  # mesmo padrão do XPC para evitar surpresas

class XPCSim:
    def __init__(self):
        self.state = SimState()   # posição/atitude/velocidade
        self.ctrls = [0.0, 0.0, 0.0, 0.0]  # aileron, elevator, rudder, throttle
        self.drefs: Dict[str, Any] = {k: v.copy() if isinstance(v, list) else v for k, v in DREFS.items()}
        self._last = time.perf_counter()

    def handle(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        op = msg.get("op")
        if op == "ping":
            return {"ok": True, "data": "pong"}
        if op == "getPOSI":
            # compatível com XPC: [lat, lon, alt_msl_m, pitch, roll, true_hdg_deg]
            data = [self.state.lat, self.state.lon, self.state.alt_m,
                    self.state.pitch_deg, self.state.roll_deg, self.state.yaw_deg]
            return {"ok": True, "data": data}
        if op == "sendCTRL":
            # [aileron, elevator, rudder, throttle] em -1..1 (throttle 0..1)
            self.ctrls = msg["ctrls"]
            return {"ok": True}
        if op == "setDREF":
            dref, values = msg["dref"], msg["values"]
            self.drefs[dref] = values
            return {"ok": True}
        if op == "getDREF":
            dref = msg["dref"]
            return {"ok": True, "data": self.drefs.get(dref, None)}
        if op == "sendXPCCommand":
            # aceite e faça no-ops por enquanto
            return {"ok": True}
        return {"ok": False, "error": f"Unknown op {op}"}

    def tick(self):
        now = time.perf_counter()
        dt = max(1e-3, min(0.05, now - self._last))  # dt limitado para estabilidade
        self._last = now
        step_dynamics(self.state, self.ctrls, dt)

async def physics_loop(sim: XPCSim):
    while True:
        sim.tick()
        await asyncio.sleep(0.02)  # 50 Hz

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, sim: XPCSim):
    while True:
        line = await reader.readline()
        if not line:
            break
        try:
            msg = json.loads(line.decode("utf-8"))
            out = sim.handle(msg)
        except Exception as e:
            out = {"ok": False, "error": repr(e)}
        writer.write((json.dumps(out) + "\n").encode("utf-8"))
        await writer.drain()
    writer.close()
    await writer.wait_closed()

async def main(host=DEFAULT_HOST, port=DEFAULT_PORT):
    sim = XPCSim()
    server = await asyncio.start_server(lambda r, w: handle_client(r, w, sim), host, port)
    print(f"[XPC-MOCK] Rodando em {host}:{port}")
    async with server:
        await asyncio.gather(server.serve_forever(), physics_loop(sim))

if __name__ == "__main__":
    asyncio.run(main())
