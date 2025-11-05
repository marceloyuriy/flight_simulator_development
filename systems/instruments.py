# systems/instruments.py
@dataclass
class InstrumentData:
    """Contrato: Instruments → XPlaneInterface, DataRecorder"""
    airspeed_indicator: float = 0.0  # m/s
    altimeter: float = 0.0  # m
    vertical_speed: float = 0.0  # m/s
    attitude_indicator: tuple = (0.0, 0.0)  # (roll, pitch) rad
    heading_indicator: float = 0.0  # rad
    turn_coordinator: float = 0.0
    slip_ball: float = 0.0
    engine_instruments: Dict = None

    def __post_init__(self):
        if self.engine_instruments is None:
            self.engine_instruments = {'rpm': 0.0, 'temp': 0.0}


class Instruments:
    def __init__(self, message_bus):
        self.bus = message_bus

        # ASSINA estes tópicos:
        self.bus.subscribe('aircraft_state', self.handle_aircraft_state)
        self.bus.subscribe('systems_state', self.handle_systems_state)

    def update(self):
        # LÓGICA: Calcula valores dos instrumentos
        instrument_data = self.calculate_instruments()

        # PUBLICA neste tópico:
        self.bus.publish('instrument_data', instrument_data)