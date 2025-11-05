"""
Modelo de dinâmica de voo SIMPLES para teste
Física básica baseada nas equações de movimento
"""

import numpy as np
from core.message_bus import MessageBus
from core.data_types import ControlInputs, AircraftState, Vector3, ForcesMoments


class SimpleFlightDynamics:
    """
    Modelo de física de voo simplificado
    Implementa equações de movimento básicas
    """

    def __init__(self, message_bus: MessageBus):
        self.bus = message_bus

        # Estado inicial da aeronave
        self.state = AircraftState(
            position_ned=Vector3(0, 0, -1000),  # 1000m de altura
            velocity_body=Vector3(50, 0, 0),  # 50 m/s para frente
            attitude=Vector3(0, 0, 0)  # Nivelado
        )

        # Parâmetros da aeronave (Cessna 172-like)
        self.mass = 1000.0  # kg
        self.gravity = 9.81  # m/s²
        self.wing_area = 16.2  # m²
        self.dt = 1 / 60.0  # Passo de tempo (60Hz)

        # Controles atuais
        self.current_controls = ControlInputs()

        # Inscreve para receber controles
        self.bus.subscribe("controls", self._handle_controls)

        print("✅ SimpleFlightDynamics inicializado")

    def _handle_controls(self, controls: ControlInputs):
        """Processa controles recebidos do piloto/X-Plane"""
        self.current_controls = controls

    def update(self):
        """Atualiza física - chamado a cada frame"""
        # Calcula forças e momentos
        forces_moments = self._calculate_forces_moments()

        # Integra equações de movimento
        self._integrate_equations_of_motion(forces_moments)

        # Atualiza valores derivados
        self.state.update_derived_values()

        # Publica estado atualizado
        self.bus.publish("aircraft_state", self.state)

        # Log a cada segundo
        if hasattr(self, 'frame_count'):
            self.frame_count += 1
        else:
            self.frame_count = 1

        if self.frame_count % 60 == 0:
            print(f"✈️  FlightDynamics: Altura={-self.state.position_ned.z:.0f}m, "
                  f"Vel={self.state.velocity_body.x:.1f}m/s, "
                  f"Pitch={self.state.attitude.y:.2f}rad")

    def _calculate_forces_moments(self) -> ForcesMoments:
        """Calcula forças e momentos atuando na aeronave"""
        # Força de sustentação (simplificada)
        lift = self._calculate_lift()

        # Força de arrasto (simplificada)
        drag = self._calculate_drag()

        # Força de propulsão
        thrust = self._calculate_thrust()

        # Força gravitacional
        gravity_force = self.mass * self.gravity

        # Converte forças para o sistema de coordenadas do corpo
        # Simplificação: assumindo ângulos pequenos
        pitch = self.state.attitude.y
        roll = self.state.attitude.x

        # Forças no sistema do corpo [X, Y, Z]
        Fx = thrust - drag  # Forward force
        Fy = 0.0  # Lateral force (simplificado)
        Fz = -lift  # Upward force (negative in body Z)

        # Momentos [L, M, N] - simplificado
        L = self.current_controls.aileron * 5000.0  # Rolling moment
        M = self.current_controls.elevator * 3000.0  # Pitching moment
        N = self.current_controls.rudder * 1000.0  # Yawing moment

        return ForcesMoments(
            force_body=Vector3(Fx, Fy, Fz),
            moment_body=Vector3(L, M, N)
        )

    def _calculate_lift(self) -> float:
        """Calcula força de sustentação"""
        # Coeficiente de sustentação simplificado
        CL0 = 0.3
        CL_alpha = 5.0  # por radiano

        alpha = self.state.alpha
        dynamic_pressure = 0.5 * 1.225 * self.state.velocity_body.x ** 2

        CL = CL0 + CL_alpha * alpha
        lift = CL * dynamic_pressure * self.wing_area

        return max(lift, 0)  # Não permite sustentação negativa

    def _calculate_drag(self) -> float:
        """Calcula força de arrasto"""
        # Coeficiente de arrasto simplificado
        CD0 = 0.03
        CD_alpha = 0.5  # por radiano

        alpha = self.state.alpha
        dynamic_pressure = 0.5 * 1.225 * self.state.velocity_body.x ** 2

        CD = CD0 + CD_alpha * alpha ** 2
        drag = CD * dynamic_pressure * self.wing_area

        return drag

    def _calculate_thrust(self) -> float:
        """Calcula força de propulsão"""
        max_thrust = 6000.0  # Newtons
        return self.current_controls.throttle[0] * max_thrust

    def _integrate_equations_of_motion(self, fm: ForcesMoments):
        """Integra as equações de movimento (Euler simples)"""
        # Acelerações lineares (F = ma)
        ax = fm.force_body.x / self.mass
        ay = fm.force_body.y / self.mass
        az = fm.force_body.z / self.mass

        # Atualiza velocidades lineares
        self.state.velocity_body.x += ax * self.dt
        self.state.velocity_body.y += ay * self.dt
        self.state.velocity_body.z += az * self.dt

        # Acelerações angulares (simplificado)
        I_roll = 2000.0  # Momento de inércia roll
        I_pitch = 3000.0  # Momento de inércia pitch
        I_yaw = 4000.0  # Momento de inércia yaw

        p_dot = fm.moment_body.x / I_roll
        q_dot = fm.moment_body.y / I_pitch
        r_dot = fm.moment_body.z / I_yaw

        # Atualiza velocidades angulares
        self.state.angular_rates.x += p_dot * self.dt
        self.state.angular_rates.y += q_dot * self.dt
        self.state.angular_rates.z += r_dot * self.dt

        # Atualiza ângulos de atitude (simplificado)
        self.state.attitude.x += self.state.angular_rates.x * self.dt
        self.state.attitude.y += self.state.angular_rates.y * self.dt
        self.state.attitude.z += self.state.angular_rates.z * self.dt

        # Atualiza posição (convertendo do sistema do corpo para NED)
        # Simplificação: assumindo ângulos pequenos
        u, v, w = self.state.velocity_body.x, self.state.velocity_body.y, self.state.velocity_body.z
        phi, theta, psi = self.state.attitude.x, self.state.attitude.y, self.state.attitude.z

        # Matriz de rotação simplificada (para ângulos pequenos)
        self.state.position_ned.x += (u * np.cos(psi) - v * np.sin(psi)) * self.dt
        self.state.position_ned.y += (u * np.sin(psi) + v * np.cos(psi)) * self.dt
        self.state.position_ned.z += w * self.dt  # Lembrete: Z positivo é para baixo no NED