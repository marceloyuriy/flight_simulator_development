# core/message_bus.py

class MessageBus:
    def __init__(self):
        # Dicionário: tópico -> lista de funções inscritas
        self.subscribers = {}

    def subscribe(self, topic, callback):
        """Inscreve uma função para receber mensagens de um tópico"""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
        print(f"✅ Nova inscrição no tópico: {topic}")

    def publish(self, topic, message):
        """Publica uma mensagem para todos inscritos no tópico"""
        if topic in self.subscribers:
            for callback in self.subscribers[topic]:
                try:
                    callback(message)  # Chama cada função inscrita
                except Exception as e:
                    print(f"❌ Erro ao entregar mensagem: {e}")
            print(f"📤 Mensagem publicada em '{topic}': {message}")
        else:
            print(f"⚠️  Tópico '{topic}' sem inscritos")