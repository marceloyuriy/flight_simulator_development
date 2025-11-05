"""
Interface REAL com o X-Plane
- Lê controles do X-Plane e publica no Message Bus
- Recebe estado do nosso modelo e envia para X-Plane
"""

import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.message_bus import MessageBus
from core.data_types import ControlInputs, AircraftState, Vector3

try:
    import XPlaneConnect as xpc

    XPLANE_AVAILABLE = True
    print("✅ XPlaneConnect disponível - modo REAL ativado")
except ImportError:
    XPLANE_AVAILABLE = False
    print("⚠️  XPlaneConnect não disponível - conectando ao MOCK")
    from sim_io.xplane_client import get_xplane_client


class XPlaneInterface:
    """
    Interface com X-Plane (real ou mock)
    """

    def __init__(self, message_bus: MessageBus, xplane_host: str = '127.0.0.1', xplane_port: int = 49000):
        self.bus = message_bus
        self.host = xplane_host
        self.port = xplane_port

        # Estado
        self.connected = False
        self.xp_client = None
        self.frame_count = 0

        # Para mock
        self.mock_controls = ControlInputs()
        self.mock_auto_pilot = False

        # Conecta ao X-Plane (se disponível)
        if XPLANE_AVAILABLE:
            self._connect_to_xplane()
        else:
            print("🔶 Executando em modo MOCK - controles simulados")
            self.connected = True  # Mock sempre "conectado"

        # Inscreve para receber estado do nosso modelo
        self.bus.subscribe("aircraft_state", self._handle_our_aircraft_state)

    def _connect_to_xplane(self):
        """Conecta com X-Plane real"""
        try:
            self.xp_client = xpc.XPlaneConnect(self.host, self.port)
            self.connected = True
            print(f"✅ Conectado ao X-Plane em {self.host}:{self.port}")
        except Exception as e:
            print(f"❌ Falha ao conectar com X-Plane: {e}")
            print("🔶 Continuando em modo MOCK")
            self.connected = False

    def update(self):
        """Chamado a cada frame - lê controles do X-Plane"""
        self.frame_count += 1

        if XPLANE_AVAILABLE and self.connected and self.xp_client:
            self._read_real_xplane_controls()
        else:
            self._generate_mock_controls()

    def _read_real_xplane_controls(self):
        """Lê controles do X-Plane real"""
        try:
            # Lê dados de controle do X-Plane
            ctrl_data = self.xp_client.getCTRL()

            # X-Plane retorna: [elevator, aileron, rudder, throttle, gear, flaps]
            controls = ControlInputs(
                elevator=ctrl_data[0],  # -1 to 1
                aileron=ctrl_data[1],  # -1 to 1
                rudder=ctrl_data[2],  # -1 to 1
                throttle=[ctrl_data[3]],  # 0 to 1
                flaps=ctrl_data[5]  # 0 to 1
            )

            # Publica controles no nosso sistema
            self.bus.publish("controls", controls)

            # Log a cada segundo para não poluir
            if self.frame_count % 60 == 0:
                print(f"🎮 X-Plane Controls: elev={controls.elevator:.2f}, thr={controls.throttle[0]:.2f}")

        except Exception as e:
            print(f"❌ Erro lendo controles do X-Plane: {e}")
            self.connected = False

    def _generate_mock_controls(self):
        """Gera controles mock para desenvolvimento sem X-Plane"""
        # Simula um piloto automático simples ou entrada manual
        if self.mock_auto_pilot:
            # Modo automático - voo reto e nivelado
            controls = ControlInputs(
                elevator=0.1,  # Leve subida
                aileron=0.0,
                rudder=0.0,
                throttle=[0.7],
                flaps=0.0
            )
        else:
            # Modo manual - controles variando suavemente
            import math
            time_s = self.frame_count / 60.0
            controls = ControlInputs(
                elevator=0.2 * math.sin(time_s * 0.5),  # Oscila suavemente
                aileron=0.1 * math.sin(time_s * 0.3),
                rudder=0.05 * math.sin(time_s * 0.2),
                throttle=[0.6 + 0.2 * math.sin(time_s * 0.1)],
                flaps=0.0
            )

        # Alterna entre manual e automático a cada 10 segundos
        if self.frame_count % 600 == 0:
            self.mock_auto_pilot = not self.mock_auto_pilot
            mode = "AUTOPILOT" if self.mock_auto_pilot else "MANUAL"
            print(f"🔀 Modo Mock: {mode}")

        # Publica controles mock
        self.bus.publish("controls", controls)

        # Log a cada 2 segundos
        if self.frame_count % 120 == 0:
            print(f"🎮 Mock Controls: elev={controls.elevator:.2f}, thr={controls.throttle[0]:.2f}")

    def _handle_our_aircraft_state(self, our_state: AircraftState):
        """Recebe estado do nosso modelo e envia para X-Plane"""
        if XPLANE_AVAILABLE and self.connected and self.xp_client:
            self._send_to_real_xplane(our_state)
        else:
            # Em modo mock, apenas mostra o estado
            if self.frame_count % 120 == 0:  # A cada 2 segundos
                print(
                    f"✈️  Nosso Estado: Altura={-our_state.position_ned.z:.0f}m, Vel={our_state.velocity_body.x:.1f}m/s")

    def _send_to_real_xplane(self, our_state: AircraftState):
        """Envia estado para X-Plane real"""
        try:
            # Converte nosso estado para formato X-Plane
            # X-Plane espera: [lat, lon, alt, pitch, roll, heading, gear]
            xplane_data = [
                0.0,  # Lat - usar referência local
                0.0,  # Lon - usar referência local
                -our_state.position_ned.z,  # Altitude (nosso Z é negativo para altura)
                our_state.attitude.y,  # Pitch (radianos)
                our_state.attitude.x,  # Roll (radianos)
                our_state.attitude.z,  # Heading (radianos)
                1  # Gear down
            ]

            # Envia para X-Plane
            self.xp_client.sendPOSI(xplane_data)

        except Exception as e:
            print(f"❌ Erro enviando estado para X-Plane: {e}")
            self.connected = False