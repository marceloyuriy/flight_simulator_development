# sim_io/xplane_backend.py
import os

def get_xpc():
    use_mock = os.getenv("USE_XPC_MOCK", "1") in ("1", "true", "True")
    if use_mock:
        from sim_io.xplane_mock import XPlaneConnect
        return XPlaneConnect()
    try:
        import xpc  # pacote oficial do XPlaneConnect
        return xpc.XPlaneConnect()
    except Exception:
        from sim_io.xplane_mock import XPlaneConnect
        return XPlaneConnect()
