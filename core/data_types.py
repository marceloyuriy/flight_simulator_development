# core/data_types.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

# Vetor 3D genérico
@dataclass(frozen=True)
class Vector3:
    x: float
    y: float
    z: float

# Entradas de controle normalizadas [-1,1] quando aplicável
@dataclass(frozen=True)
class ControlInputs:
    throttle: float          # [0,1]
    elevator: float          # [-1,1]
    aileron: float           # [-1,1]
    rudder: float            # [-1,1]
    flaps: float = 0.0       # [0,1]
    gear: float = 1.0        # [0,1] (baixado=1)

# Estado da aeronave (convenção corpo e Euler)
@dataclass
class AircraftState:
    # Posição em NED [m]
    position_ned: Vector3
    # Velocidades no corpo [m/s] (u,v,w)
    velocity_body: Vector3
    # Taxas angulares no corpo [rad/s] (p,q,r)
    rates_body: Vector3
    # Ângulos de Euler [rad] (phi, theta, psi)
    euler: Vector3
    # Massa [kg] e momentos de inércia principais [kg m^2]
    mass: float
    inertia_principal: Tuple[float, float, float]  # (Ixx, Iyy, Izz)

# 💥 ESTA É A QUE FALTAVA
@dataclass
class ForcesMoments:
    # Forças no corpo [N] (X, Y, Z)
    forces: Vector3
    # Momentos no corpo [N·m] (L, M, N)
    moments: Vector3

__all__ = [
    "Vector3",
    "ControlInputs",
    "AircraftState",
    "ForcesMoments",
]
