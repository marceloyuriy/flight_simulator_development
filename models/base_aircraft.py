class BaseAircraft:
    def __init__(self, config):
        self.state = AircraftState()
        self.mass_props = MassProperties(config)
        self.aero_model = AerodynamicModel(config)
        self.propulsion = PropulsionModel(config)

    def calculate_forces_moments(self):
        aero_forces = self.aero_model.calculate(self.state)
        prop_forces = self.propulsion.calculate(self.state)
        return aero_forces + prop_forces

    def update_state(self, new_state):
        self.state = new_state