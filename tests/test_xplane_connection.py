# tests/test_xpc_mock_integration.py
import xplaneconnect as xpc
def test_loop():
    xpc.openUDP()
    p0 = xpc.getPOSI()
    xpc.sendCTRL([0.2, -0.1, 0.0, 0.8])
    p1 = xpc.getPOSI()
    assert len(p0) == 6 and len(p1) == 6