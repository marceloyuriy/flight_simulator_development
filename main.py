"""
Arquivo principal do simulador de voo
Integra todos os módulos
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.message_bus import MessageBus
from core.simulation_orchestrator import SimulationOrchestrator
from interfaces.xplane_interface import XPlaneInterface
from dynamics.flight_dynamics import SimpleFlightDynamics
from sim_io.xplane_backend import get_xpc

def main():
    print("🚀 SIMULADOR DE VOO - DESENVOLVIMENTO")
    print("=" * 60)

    # 1. Criar Message Bus
    bus = MessageBus()

    # 2. Criar Orchestrator (30Hz para desenvolvimento)
    orchestrator = SimulationOrchestrator(bus, frame_rate=30)

    # 3. Criar módulos
    print("\n📦 INICIALIZANDO MÓDULOS:")

    xplane_interface = XPlaneInterface(bus)
    flight_dynamics = SimpleFlightDynamics(bus)

    # 4. Registrar módulos
    orchestrator.register_module(xplane_interface)
    orchestrator.register_module(flight_dynamics)

    print(f"\n🔧 CONFIGURAÇÃO:")
    print(f"   - Frame rate: {orchestrator.frame_rate}Hz")
    print(f"   - Módulos ativos: {orchestrator.list_modules()}")

    print("\n🎮 CONTROLES:")
    print("   - Se X-Plane estiver rodando: use joystick/teclado no X-Plane")
    print("   - Caso contrário: controles automáticos mock serão usados")

    print("\n📊 SAÍDA:")
    print("   - Estado da aeronave mostrado a cada 2 segundos")
    print("   - Log de controles mostrado periodicamente")

    print("\n⏱️  EXECUTANDO POR 30 SEGUNDOS...")
    print("   Pressione Ctrl+C para parar mais cedo")
    print("-" * 60)

    # Executar simulação
    try:
        orchestrator.run(duration=30.0)
    except KeyboardInterrupt:
        print("\n⏹️  Interrompido pelo usuário")

    # Estatísticas finais
    stats = orchestrator.get_stats()
    print(f"\n📈 ESTATÍSTICAS FINAIS:")
    for key, value in stats.items():
        print(f"   - {key}: {value}")


if __name__ == "__main__":
    main()