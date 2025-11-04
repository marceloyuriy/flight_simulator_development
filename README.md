## Este é um projeto de desenvolvimento de um simulador de voo baseado em python como backend e Xplane 11 como frontend

# Arquitetura do simulador 
+--------------------------+
|   Serviço de I/O (Hardware)  |
| (Joystick, Manete, etc.) |
| (Ref: 1.4.4 Data Acquisition [cite: 221])|
+--------------------------+
       |
       | publica -> TÓPICO: "PILOT_INPUT"
       v
+-------------------------------------------------------------------------+
|                        BARRAMENTO DE MENSAGENS (UDP / ZeroMQ)           |
+-------------------------------------------------------------------------+
^      ^                                       |                        |
|      | publica -> TÓPICO: "AIRCRAFT_STATE"       |                        |
|      |                                       |                        |
| +--------------------------+                 v                        v
| |   Serviço EOM (Cérebro)  |        +-------------------+    +----------------------+
| |  (Ref: 1.4.1 EOM [cite: 220])    | | Serviço Visual  |    | Serviço de Instrumentos|
| | * Carrega Modelos Plugáveis: |        |  (X-Plane)      |    |  (Pygame / OpenGL)   |
| |   - Aero (Cessna/GEV)      |        | (Ref: 1.4.7 )|    | (Ref: 1.4.11 [cite: 222]) |
| |   - Motor                  |        +-------------------+    +----------------------+
| |   - Trem de Pouso          |                 ^                        ^
| | (Ref: 1.4.2, 1.4.3, 1.4.5) |                 |                        |
| +--------------------------+                 | assina                 | assina
|      ^                                       +------------------------+
|      | assina
|      |
+------+----------------+----------------+
| TÓPICO: "PILOT_INPUT" | TÓPICO: "ENV_DATA" | TÓPICO: "SIM_COMMAND"
+-----------------------+----------------+-----------------------+
       ^                       ^                ^
       | publica               | publica        | publica
       |                       |                |
+-------------------+ +---------------------+ +----------------------+
| Serviço de I/O    | | Serviço de Ambiente | | Serviço do Instrutor |
| (já mostrado)     | | (Ref: 1.4.6 [cite: 217])| | (IOS) (Ref: 1.4.10 [cite: 219])|
+-------------------+ +---------------------+ +----------------------+

# Estrutura de arquivos 
/simulador_voo/
|
|-- /services/
|   |
|   |-- /eom_service/            # O CÉREBRO: Roda a física
|   |   |-- main.py              # Loop principal: assina inputs, integra EOMs, publica estado
|   |   |-- eom_integrator.py    # As EOMs de 6-DOF (baseado no Cap. 3 do livro [cite: 39, 124])
|   |   |-- /models/             # <-- SUA ESCALABILIDADE ESTÁ AQUI
|   |   |   |-- fdm_interface.py # Classe base abstrata para modelos
|   |   |   |-- aero_cessna.py   # Implementação 1: Aerodinâmica simples
|   |   |   |-- aero_gev.py      # Implementação 2: Aerodinâmica de Efeito Solo
|   |   |   |-- propulsion.py    # Modelo do motor (Ref: 1.4.3 [cite: 228])
|   |   |   `-- landing_gear.py  # Modelo do trem de pouso (Ref: 1.4.5 [cite: 234])
|   |
|   |-- /io_service/             # HARDWARE: Lê joystick/manete
|   |   |-- main.py              # Loop principal: lê hardware, publica no tópico "PILOT_INPUT"
|   |   `-- hardware_reader.py   # (Usa a biblioteca 'inputs' ou 'pygame')
|   |
|   |-- /visual_service/         # VISUAL: Conecta ao X-Plane
|   |   |-- main.py              # Loop principal: assina "AIRCRAFT_STATE", envia para X-Plane
|   |   `-- xplane_connector.py  # (Usa a biblioteca XPC)
|   |
|   |-- /environment_service/    # MUNDO: Fornece dados de clima e terreno
|   |   |-- main.py              # Loop principal: publica no tópico "ENV_DATA"
|   |   |-- weather_model.py     # (Simples: densidade, vento) (Ref: 1.4.6 )
|   |   `-- terrain_reader.py    # (Lê AGL do X-Plane para o seu GEV)
|   |
|   |-- /instructor_service/     # IOS: Controla a simulação
|   |   |-- main.py              # (Pode ser um app web Flask/FastAPI)
|   |   `-- web_routes.py        # (Envia comandos "SIM_COMMAND": pause, reposicione, falhe)
|   |
|   `-- /instrument_service/     # INSTRUMENTOS: (Opcional)
|       |-- main.py              # Loop principal: assina "AIRCRAFT_STATE" e "NAV_DATA"
|       `-- pfd.py               # (Renderiza um PFD com Pygame/OpenGL) (Ref: 1.4.11 [cite: 222])
|
|-- /common/
|   |-- message_bus.py         # Abstração para ZeroMQ ou UDP
|   `-- data_structures.py     # Dataclasses Python para "AircraftState", "PilotInput"
|
|-- config/
|   |-- settings.ini           # (IPs, portas, modelo de FDM a ser carregado)
|
`-- run_services.py            # Script para iniciar todos os serviços
