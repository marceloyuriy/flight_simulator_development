import os, json, socket

_HOST = os.getenv("XPC_HOST", "127.0.0.1")
_PORT = int(os.getenv("XPC_PORT", "49009"))
_sock = None
_f = None

def openUDP(ip=_HOST, port=_PORT):
    global _sock, _f
    _sock = socket.create_connection((ip, port), timeout=2.0)
    _f = _sock.makefile("rwb")
    return _sock

def closeUDP():
    global _sock, _f
    try:
        if _f: _f.close()
        if _sock: _sock.close()
    finally:
        _sock = None
        _f = None

def _rpc(payload):
    if _f is None:
        openUDP()
    _f.write((json.dumps(payload) + "\n").encode("utf-8"))
    _f.flush()
    line = _f.readline()
    if not line:
        raise RuntimeError("XPC-MOCK: conexão encerrada")
    resp = json.loads(line.decode("utf-8"))
    if not resp.get("ok", False):
        raise RuntimeError(f"XPC error: {resp.get('error')}")
    return resp.get("data")

# ---- API compatível mínima ----
def getPOSI():
    return _rpc({"op": "getPOSI"})

def sendCTRL(ctrls):
    # aceitamos lista [aileron, elevator, rudder, throttle]
    _rpc({"op": "sendCTRL", "ctrls": list(ctrls)})

def setDREF(dref, values):
    _rpc({"op": "setDREF", "dref": dref, "values": list(values)})

def getDREF(dref):
    return _rpc({"op": "getDREF", "dref": dref})

def sendXPCCommand(cmd):
    _rpc({"op": "sendXPCCommand", "cmd": cmd})
