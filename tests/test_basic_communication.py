"""
Teste BÁSICO de comunicação - Verifica apenas o essencial
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.message_bus import MessageBus
from core.data_types import ControlInputs, AircraftState


def test_basic_message_bus():
    """Teste mais simples do Message Bus"""
    print("🧪 TESTE BÁSICO DE COMUNICAÇÃO")
    print("=" * 50)

    # 1. Criar Message Bus
    bus = MessageBus()

    # Variáveis para verificar recebimento
    received_controls = []
    received_states = []

    # 2. Criar callbacks de teste
    def handle_controls(controls):
        received_controls.append(controls)
        print(f"✅ CONTROLES RECEBIDOS: elevator={controls.elevator:.2f}")

    def handle_states(state):
        received_states.append(state)
        print(f"✅ ESTADO RECEBIDO: altitude={state.altitude:.1f}m")

    # 3. Inscrever nos tópicos
    bus.subscribe("controls", handle_controls)
    bus.subscribe("aircraft_state", handle_states)

    # 4. Publicar mensagens de teste
    print("\n📤 PUBLICANDO MENSAGENS DE TESTE:")

    # Publica controles
    controls = ControlInputs(elevator=0.5, aileron=0.2, throttle=[0.8])
    bus.publish("controls", controls)

    # Publica estado
    state = AircraftState(altitude=1500.0, airspeed=75.0)
    bus.publish("aircraft_state", state)

    # 5. Verificar resultados
    print("\n📊 VERIFICANDO RESULTADOS:")
    print(f"   - Controles recebidos: {len(received_controls)}")
    print(f"   - Estados recebidos: {len(received_states)}")

    # Verificações
    success = True

    if len(received_controls) == 0:
        print("❌ FALHA: Nenhum controle foi recebido")
        success = False
    else:
        print("✅ Controles: Comunicação OK")

    if len(received_states) == 0:
        print("❌ FALHA: Nenhum estado foi recebido")
        success = False
    else:
        print("✅ Estados: Comunicação OK")

    if success:
        print("\n🎉 TESTE BÁSICO PASSOU! Comunicação fundamental está funcionando.")
    else:
        print("\n💥 TESTE BÁSICO FALHOU! Há problemas na comunicação.")

    return success


def test_data_types():
    """Testa se os data types básicos funcionam"""
    print("\n🧪 TESTANDO DATA TYPES BÁSICOS:")
    print("-" * 40)

    try:
        # Testa ControlInputs
        controls = ControlInputs(elevator=0.3, aileron=-0.1, throttle=[0.7])
        print(f"✅ ControlInputs criado: elevator={controls.elevator}")

        # Testa AircraftState
        state = AircraftState(altitude=1000.0, airspeed=60.0)
        state.update_derived_values()
        print(f"✅ AircraftState criado: altitude={state.altitude}, airspeed={state.airspeed}")

        print("🎉 Data Types básicos funcionando!")
        return True

    except Exception as e:
        print(f"❌ Erro nos Data Types: {e}")
        return False


if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DE VERIFICAÇÃO")
    print("=" * 50)

    # Executa testes
    data_types_ok = test_data_types()
    communication_ok = test_basic_message_bus()

    print("\n" + "=" * 50)
    print("📈 RESULTADO FINAL:")

    if data_types_ok and communication_ok:
        print("🎉 TODOS OS TESTES BÁSICOS PASSARAM!")
        print("   O sistema de comunicação está funcionando.")
    else:
        print("💥 ALGUNS TESTES FALHARAM!")
        print("   Verifique as implementações.")