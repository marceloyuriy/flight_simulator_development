"""
Teste de integração completo do sistema de comunicação
Verifica se Message Bus, Data Types e Orchestrator estão funcionando juntos
"""

import time
from core.message_bus import MessageBus
from core.simulation_orchestrator import SimulationOrchestrator
from core.data_types import ControlInputs, AircraftState, Vector3


class TestCommunication:
    """Testa se a comunicação entre módulos está funcionando"""

    def __init__(self):
        self.controls_received = []
        self.states_received = []
        self.message_sequence = []

    def test_complete_flow(self):
        """Testa o fluxo completo de comunicação"""
        print("🧪 INICIANDO TESTE DE INTEGRAÇÃO COMPLETA")
        print("=" * 60)

        # 1. Criar Message Bus
        bus = MessageBus()

        # 2. Criar módulos de teste
        control_publisher = ControlPublisher(bus)
        state_processor = StateProcessor(bus)
        data_validator = DataValidator(bus, self)

        # 3. Criar e configurar Orchestrator
        orchestrator = SimulationOrchestrator(bus, frame_rate=10)  # 10Hz para teste rápido

        # 4. Registrar módulos
        orchestrator.register_module(control_publisher)
        orchestrator.register_module(state_processor)
        orchestrator.register_module(data_validator)

        print(f"\n🔧 CONFIGURAÇÃO DO TESTE:")
        print(f"   - Frame rate: {orchestrator.frame_rate}Hz")
        print(f"   - Duração: 2 segundos")
        print(f"   - Módulos: {orchestrator.list_modules()}")

        # 5. Executar teste por 2 segundos
        print("\n🚀 EXECUTANDO TESTE...")
        orchestrator.run(duration=2.0)

        # 6. Verificar resultados
        self._verify_results()

    def _verify_results(self):
        """Verifica se o teste foi bem-sucedido"""
        print("\n📊 RESULTADOS DO TESTE:")
        print(f"   - Controles recebidos: {len(self.controls_received)}")
        print(f"   - Estados recebidos: {len(self.states_received)}")
        print(f"   - Sequência de mensagens: {len(self.message_sequence)} eventos")

        # Verificações
        success = True

        # Verifica se houve comunicação
        if len(self.controls_received) == 0:
            print("❌ FALHA: Nenhum controle foi recebido")
            success = False
        else:
            print("✅ CONTROLES: Comunicação funcionando")

        if len(self.states_received) == 0:
            print("❌ FALHA: Nenhum estado foi recebido")
            success = False
        else:
            print("✅ ESTADOS: Comunicação funcionando")

        # Verifica sequência correta
        if "CONTROL_PUBLISHED" not in self.message_sequence:
            print("❌ FALHA: Controles não foram publicados")
            success = False

        if "CONTROL_RECEIVED" not in self.message_sequence:
            print("❌ FALHA: Controles não foram recebidos")
            success = False

        if "STATE_PUBLISHED" not in self.message_sequence:
            print("❌ FALHA: Estados não foram publicados")
            success = False

        if "STATE_RECEIVED" not in self.message_sequence:
            print("❌ FALHA: Estados não foram recebidos")
            success = False

        if success:
            print("\n🎉 TODOS OS TESTES PASSARAM! Sistema de comunicação está funcionando.")
        else:
            print("\n💥 ALGUNS TESTES FALHARAM! Verifique a implementação.")

        return success


class ControlPublisher:
    """Publica controles de teste"""

    def __init__(self, bus):
        self.bus = bus
        self.frame_count = 0

    def update(self):
        """Publica controles a cada 5 frames"""
        self.frame_count += 1

        if self.frame_count % 5 == 0:
            controls = ControlInputs(
                elevator=0.3,
                aileron=-0.2,
                throttle=[0.8],
                flaps=0.1
            )
            self.bus.publish("controls", controls)
            test_instance.message_sequence.append("CONTROL_PUBLISHED")


class StateProcessor:
    """Processa controles e publica estados"""

    def __init__(self, bus):
        self.bus = bus
        self.state = AircraftState()
        self.bus.subscribe("controls", self._handle_controls)

    def _handle_controls(self, controls):
        """Processa controles recebidos"""
        test_instance.controls_received.append(controls)
        test_instance.message_sequence.append("CONTROL_RECEIVED")

        # Simula processamento de física
        self.state.position_ned.x += 10.0
        self.state.velocity_body.x = 50.0 + controls.throttle[0] * 20

    def update(self):
        """Publica estado atualizado"""
        self.bus.publish("aircraft_state", self.state)
        test_instance.message_sequence.append("STATE_PUBLISHED")


class DataValidator:
    """Valida dados recebidos"""

    def __init__(self, bus, test_instance):
        self.bus = bus
        self.test_instance = test_instance
        self.bus.subscribe("aircraft_state", self._validate_state)

    def _validate_state(self, state):
        """Valida estado recebido"""
        self.test_instance.states_received.append(state)
        self.test_instance.message_sequence.append("STATE_RECEIVED")

        # Valida dados básicos
        assert isinstance(state, AircraftState), "Estado não é do tipo AircraftState"
        assert hasattr(state, 'position_ned'), "Estado não tem position_ned"
        assert hasattr(state, 'velocity_body'), "Estado não tem velocity_body"


# Instância global para o teste
test_instance = TestCommunication()

if __name__ == "__main__":
    test_instance.test_complete_flow()