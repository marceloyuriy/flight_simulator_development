# core/simulation_orchestrator.py

import time
from typing import List, Any


class SimulationOrchestrator:
    """
    Maestro que coordena todos os módulos do simulador
    Garante execução em tempo real e ordem determinística
    """

    def __init__(self, message_bus, frame_rate: int = 60):
        # Dependências
        self.message_bus = message_bus

        # Configuração de tempo
        self.frame_rate = frame_rate
        self.frame_period = 1.0 / frame_rate  # Ex: 0.016666s para 60Hz

        # Gerenciamento de módulos
        self.modules: List[Any] = []  # Lista de todos os módulos registrados

        # Controle de execução
        self.is_running = False
        self.frame_count = 0
        self.simulation_time = 0.0

        print(f"🎮 Simulation Orchestrator criado!")
        print(f"   - Frame rate: {frame_rate}Hz")
        print(f"   - Frame period: {self.frame_period:.4f}s")

    def register_module(self, module) -> bool:
        """
        Registra um módulo para ser atualizado a cada frame
        Retorna True se bem-sucedido
        """
        # Verifica se o módulo tem o método update()
        if not hasattr(module, 'update'):
            print(f"❌ ERRO: {module.__class__.__name__} não tem método 'update()'")
            return False

        if not callable(module.update):
            print(f"❌ ERRO: 'update' em {module.__class__.__name__} não é chamável")
            return False

        # Adiciona à lista de módulos
        self.modules.append(module)
        print(f"✅ Módulo registrado: {module.__class__.__name__}")
        return True

    def run(self, duration: float = None):
        """
        Inicia o loop principal de simulação
        duration: tempo total de simulação em segundos (None = executa até parar)
        """
        self.is_running = True
        self.frame_count = 0
        self.simulation_time = 0.0

        print("🚀 INICIANDO SIMULAÇÃO")
        print(f"   - Módulos ativos: {len(self.modules)}")
        print(f"   - Duração: {'INFINITA' if duration is None else f'{duration}s'}")
        print("-" * 50)

        start_wall_time = time.time()

        try:
            while self.is_running:
                # Marca início do frame para controle de tempo
                frame_start_time = time.time()

                # 🎯 ATUALIZAÇÃO DE TODOS OS MÓDULOS
                self._update_all_modules()

                # 📊 CONTAGEM E TEMPO
                self.frame_count += 1
                self.simulation_time = self.frame_count * self.frame_period

                # ⏰ CONTROLE DE TEMPO REAL
                self._enforce_real_time(frame_start_time)

                # 📝 LOG DE PROGRESSO
                self._log_progress(frame_start_time)

                # 🛑 VERIFICAÇÃO DE DURAÇÃO
                if duration and self.simulation_time >= duration:
                    print(f"⏰ Duração de {duration}s alcançada - parando simulação")
                    break

        except KeyboardInterrupt:
            print("\n⏹️  Simulação interrompida pelo usuário (Ctrl+C)")
        except Exception as e:
            print(f"\n💥 Erro durante simulação: {e}")
        finally:
            self.stop()

    def _update_all_modules(self):
        """Atualiza todos os módulos registrados"""
        for module in self.modules:
            try:
                module.update()
            except Exception as e:
                print(f"❌ Erro em {module.__class__.__name__}.update(): {e}")

    def _enforce_real_time(self, frame_start_time: float):
        """Garante que o frame respeite o tempo real"""
        frame_elapsed = time.time() - frame_start_time

        # Se executou mais rápido que o período do frame, espera o resto
        if frame_elapsed < self.frame_period:
            time.sleep(self.frame_period - frame_elapsed)
        else:
            # Frame demorou mais que o esperado - potencial problema de performance
            delay = frame_elapsed - self.frame_period
            print(f"⚠️  Frame {self.frame_count} atrasado: +{delay * 1000:.1f}ms")

    def _log_progress(self, frame_start_time: float):
        """Faz logging do progresso da simulação"""
        frame_elapsed = time.time() - frame_start_time

        # A cada segundo de simulação (em tempo de parede)
        if self.frame_count % self.frame_rate == 0:
            wall_time_elapsed = time.time() - frame_start_time
            efficiency = (self.frame_period / frame_elapsed) * 100 if frame_elapsed > 0 else 100

            print(f"📊 Frame {self.frame_count} | "
                  f"Tempo simulação: {self.simulation_time:.1f}s | "
                  f"Eficiência: {efficiency:.1f}%")

    def stop(self):
        """Para a simulação gracefulmente"""
        self.is_running = False
        print("\n🛑 SIMULAÇÃO PARADA")
        print(f"   - Frames processados: {self.frame_count}")
        print(f"   - Tempo simulado: {self.simulation_time:.2f}s")
        print(f"   - Módulos ativos: {len(self.modules)}")

    def get_stats(self) -> dict:
        """Retorna estatísticas da simulação"""
        return {
            'frames_processed': self.frame_count,
            'simulation_time': self.simulation_time,
            'active_modules': len(self.modules),
            'frame_rate': self.frame_rate,
            'frame_period': self.frame_period
        }

    def list_modules(self) -> List[str]:
        """Retorna lista dos nomes dos módulos registrados"""
        return [module.__class__.__name__ for module in self.modules]