## Este é um projeto de desenvolvimento de um simulador de voo baseado em python como backend e Xplane 11 como frontend

# Arquitetura do simulador 

┌─────────────────────────────────────────────────────────────────┐
│                    FLIGHT SIMULATION ORCHESTRATOR               │
├─────────────────────────────────────────────────────────────────┤
│  +----------------+    +----------------+    +----------------+  │
│  |   X-Plane      |    |   Instructor   |    |    Data        |  │
│  |   Interface    |    |   Station      |    |   Recorder     |  │
│  +----------------+    +----------------+    +----------------+  │
└─────────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
▼ Message Bus (UDP/TCP) ▼
        │                   │                   │
┌───────┴───────┐ ┌───────┴───────┐ ┌─────────┴─────────┐
│   CORE        │ │   SYSTEMS     │ │    VISUAL &       │
│   DYNAMICS    │ │   SIMULATION  │ │    SENSORY        │
├───────────────┤ ├───────────────┤ ├───────────────────┤
│• Flight Model │ │• Aerodynamics │ │• Visual System    │
│• Equations of │ │• Engine Model │ │• Motion Cueing    │
│  Motion       │ │• Gear Model   │ │• Sound System     │
│• Mass Props   │ │• Navigation   │ │• Control Loading  │
│• Atmosphere   │ │• Instruments  │ │                   │
└───────────────┘ │• FCS          │ └───────────────────┘
                  │• Weather      │
                  └───────────────┘

#Estrutura de pastas
ground_effect_vehicle_sim/
├── 📁 core/
│   ├── 🐍 simulation_orchestrator.py
│   ├── 🐍 message_bus.py
│   ├── 🐍 real_time_clock.py
│   └── 🐍 data_types.py
├── 📁 dynamics/
│   ├── 🐍 flight_dynamics.py
│   ├── 🐍 equations_of_motion.py
│   ├── 🐍 mass_properties.py
│   └── 🐍 atmosphere_model.py
├── 📁 systems/
│   ├── 🐍 aerodynamics.py
│   ├── 🐍 propulsion.py
│   ├── 🐍 landing_gear.py
│   ├── 🐍 navigation.py
│   ├── 🐍 instruments.py
│   ├── 🐍 flight_controls.py
│   └── 🐍 weather.py
├── 📁 interfaces/
│   ├── 🐍 xplane_interface.py
│   ├── 🐍 instructor_station.py
│   ├── 🐍 data_recorder.py
│   └── 🐍 control_loading.py
├── 📁 visual_systems/
│   ├── 🐍 motion_cueing.py
│   ├── 🐍 sound_system.py
│   └── 🐍 visualization.py
├── 📁 config/
│   ├── 🛠️ vehicle_configs/
│   │   ├── 🛠️ cessna_172.yaml
│   │   ├── 🛠️ pipistrel_virus.yaml
│   │   └── 🛠️ ground_effect_vehicle.yaml
│   ├── 🛠️ simulation_config.yaml
│   └── 🛠️ network_config.yaml
├── 📁 models/
│   ├── 🐍 base_aircraft.py
│   ├── 🐍 cessna_172.py
│   ├── 🐍 pipistrel_virus.py
│   └── 🐍 custom_gev.py
├── 📁 utils/
│   ├── 🐍 numerical_integration.py
│   ├── 🐍 coordinate_transforms.py
│   ├── 🐍 data_interpolation.py
│   └── 🐍 validation_tools.py
├── 📁 tests/
│   ├── 🧪 test_dynamics.py
│   ├── 🧪 test_aerodynamics.py
│   └── 🧪 test_integration.py
├── 📁 docs/
│   ├── 📚 architecture.md
│   └── 📚 api_reference.md
├── 🐍 main.py
├── 🐍 requirements.txt
└── 📜 README.md
