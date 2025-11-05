import os
import time
import threading
import importlib
import pytest

# garante que o mock está instalado (pip install -e ./xpc-mock)
xpcm = importlib.import_module("xpc_mock")
XPC = xpcm.XPlaneConnectMock

def test_smoke_init():
    xpc = XPC()
    assert hasattr(xpc, "getDREF")
    assert hasattr(xpc, "sendDREF")
    assert hasattr(xpc, "getPOSI")
    assert hasattr(xpc, "sendPOSI")
    assert hasattr(xpc, "sendCTRL")

def test_dref_roundtrip():
    xpc = XPC()
    assert xpc.getDREF("sim/cockpit2/controls/yoke_roll_ratio") == [0.0]
    rc = xpc.sendDREF("sim/cockpit2/controls/yoke_roll_ratio", 0.42)
    assert rc == 0
    assert xpc.getDREF("sim/cockpit2/controls/yoke_roll_ratio") == [0.42]

def test_posi_roundtrip():
    xpc = XPC()
    rc = xpc.sendPOSI([ -22.90, -43.17, 5_000, 2.0, 1.0, 180.0 ])
    assert rc == 0
    lat, lon, alt, pitch, roll, yaw = xpc.getPOSI()
    assert (lat, lon, alt, pitch, roll, yaw) == (-22.90, -43.17, 5000.0, 2.0, 1.0, 180.0)

def test_ctrl_roundtrip():
    xpc = XPC()
    rc = xpc.sendCTRL([0.7, 0.1, -0.05, 0.0, 1.0, 0.25])
    assert rc == 0

def test_thread_safety_drefs():
    xpc = XPC()
    keys = [f"sim/custom/test/{i}" for i in range(50)]
    def worker(idx):
        k = keys[idx]
        for v in range(100):
            xpc.sendDREF(k, float(v))
            assert xpc.getDREF(k) == [float(v)]

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(len(keys))]
    for t in threads: t.start()
    for t in threads: t.join()

def test_perf_getDREF_fast_enough():
    xpc = XPC()
    xpc.sendDREF("sim/cockpit2/controls/throttle_ratio", 0.33)
    n = 50_000
    t0 = time.perf_counter()
    for _ in range(n):
        xpc.getDREF("sim/cockpit2/controls/throttle_ratio")
    dt = time.perf_counter() - t0
    avg_us = (dt / n) * 1e6
    # alvo generoso: < 50 µs/call numa máquina comum em modo debug; ajuste se quiser ser mais rígido
    assert avg_us < 50, f"Mock lento ({avg_us:.1f} µs/call)"
