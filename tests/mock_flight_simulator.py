from core.message_bus import MessageBus
from core.simulation_orchestrator import SimulationOrchestrator
from core.data_types import ControlInputs, AircraftState


# ==================== MÓDULOS MOCK (SIMULADOS) ====================

class MockXPlaneInterface:
    """Simula a interface com o X-Pline - gera controles aleatórios"""

    def __init__(self, message_bus):
        self.bus = message_bus
        self.contador = 0

    def update(self):
        """Chamado a cada frame pelo Orchestrator"""
        self.contador += 1

        # A cada 30 frames (0.5 segundo a 60Hz), simula um input do piloto
        if self.contador % 30 == 0:
            # Gera controles aleatórios para simular piloto
            import random
            controles = ControlInputs(
                elevator=random.uniform(-1, 1),
                aileron=random.uniform(-0.5, 0.5),
                throttle=[random.uniform(0, 1)]
            )

            print(f"🎮 MockXPlane: Piloto mexeu nos controles! Elevador: {controles.elevator:.2f}")
            self.bus.publish("controls", controles)


class MockFlightDynamics:
    """Simula a física de voo - processa controles e calcula novo estado"""

    def __init__(self, message_bus):
        self.bus = message_bus
        self.estado = AircraftState(x=0, y=0, z=-1000)  # Começa a 1000m de altura
        self.velocidade = 50.0  # m/s

        # Se inscreve para receber controles
        self.bus.subscribe("controls", self.processar_controles)

    def processar_controles(self, controles):
        """Chamado quando chegam novos controles do piloto"""
        print(f"✈️  FlightDynamics: Recebidos controles - processando física...")

        # Simulação BEM simples da física:
        # - Elevador controla subida/descida
        # - Aileron controla inclinação
        self.estado.z += controles.elevator * 10  # Sobe/desce baseado no elevador
        self.estado.roll = controles.aileron * 0.5  # Inclina baseado no aileron

        # Atualiza velocidade baseado no throttle
        self.velocidade = 30 + controles.throttle[0] * 40

        print(f"   ↳ Nova altura: {-self.estado.z:.0f}m, Velocidade: {self.velocidade:.0f}m/s")

    def update(self):
        """Chamado a cada frame - atualiza estado contínuo"""
        # Movimento para frente baseado na velocidade
        self.estado.x += self.velocidade * (1 / 60)  # Avança baseado na velocidade

        # Publica o estado atualizado
        self.bus.publish("aircraft_state", self.estado)


class MockDataRecorder:
    """Simula um gravador de dados - registra tudo que acontece"""

    def __init__(self, message_bus):
        self.bus = message_bus
        self.dados = []

        # Se inscreve em TUDO para registrar
        self.bus.subscribe("controls", self.registrar_controles)
        self.bus.subscribe("aircraft_state", self.registrar_estado)

    def registrar_controles(self, controles):
        self.dados.append(f"CONTROLES: elevador={controles.elevator:.2f}")

    def registrar_estado(self, estado):
        self.dados.append(f"ESTADO: x={estado.x:.1f}, altura={-estado.z:.1f}m")

    def update(self):
        """Chamado a cada frame"""
        # A cada 60 frames (1 segundo), mostra estatísticas
        if len(self.dados) % 60 == 0 and len(self.dados) > 0:
            print(f"📊 DataRecorder: Registrados {len(self.dados)} eventos")

            # Mostra os últimos 3 eventos como exemplo
            ultimos = self.dados[-3:] if len(self.dados) >= 3 else self.dados
            for evento in ultimos:
                print(f"   📝 {evento}")


# ==================== PROGRAMA PRINCIPAL ====================

def main():
    print("🎯 INICIANDO DEMONSTRAÇÃO DO SIMULADOR COMPLETO")
    print("=" * 50)

    # 1. Criar o sistema de mensagens
    bus = MessageBus()

    # 2. Criar o orchestrator (maestro)
    orchestrator = SimulationOrchestrator(bus, frame_rate=60)

    # 3. Criar todos os módulos
    xplane_interface = MockXPlaneInterface(bus)
    flight_dynamics = MockFlightDynamics(bus)
    data_recorder = MockDataRecorder(bus)

    # 4. Registrar módulos no orchestrator
    orchestrator.register_module(xplane_interface)
    orchestrator.register_module(flight_dynamics)
    orchestrator.register_module(data_recorder)

    print("\n🧩 MÓDULOS REGISTRADOS:")
    print(f"   - {xplane_interface.__class__.__name__}")
    print(f"   - {flight_dynamics.__class__.__name__}")
    print(f"   - {data_recorder.__class__.__name__}")

    print("\n🔧 CONFIGURAÇÃO:")
    print(f"   - Frame rate: {orchestrator.frame_rate}Hz")
    print(f"   - Frame period: {orchestrator.frame_period:.4f}s")

    print("\n🚀 INICIANDO SIMULAÇÃO (5 segundos)...")
    print("   Pressione Ctrl+C para parar mais cedo")
    print("-" * 50)

    # 5. Rodar a simulação por 5 segundos
    import threading

    # Timer para parar automaticamente após 5 segundos
    stop_timer = threading.Timer(5.0, orchestrator.stop)
    stop_timer.start()

    # 6. INICIAR O LOOP PRINCIPAL!
    orchestrator.run()

    print("\n📈 ESTATÍSTICAS FINAIS:")
    print(f"   - Frames processados: {orchestrator.frame_count}")
    print(f"   - Tempo simulado: {orchestrator.frame_count / 60:.1f} segundos")


if __name__ == "__main__":
    main()