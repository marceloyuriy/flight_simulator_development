# systems/aerodynamics.py
class Aerodynamics:
    def __init__(self, message_bus, config):
        self.bus = message_bus

        # ASSINA estes tópicos:
        self.bus.subscribe('aircraft_state', self.handle_aircraft_state)
        self.bus.subscribe('environment', self.handle_environment)

    def update(self):
        # LÓGICA: Calcula forças e momentos aerodinâmicos
        forces_moments = self.calculate_aerodynamic_forces()

        # PUBLICA neste tópico:
        self.bus.publish('aerodynamic_forces', forces_moments)

    def calculate_aerodynamic_forces(self) -> ForcesMoments:
        # Usa aircraft_state e environment para calcular
        lift = 0.5 * self.environment.density * self.state.airspeed ** 2 * self.S * self.CL
        drag = 0.5 * self.environment.density * self.state.airspeed ** 2 * self.S * self.CD
        # ... cálculos completos
        return ForcesMoments(force_body=[-drag, 0, -lift],
                             moment_body=[L, M, N])