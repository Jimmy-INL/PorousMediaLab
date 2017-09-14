from Lab import Lab
from DotDict import DotDict
import numpy as np
import DESolver
import Plotter
import pHcalc


class BatchLab(Lab):
    """The batch experiments simulations"""

    def __init__(self, tend, dt):
        super().__init__(tend, dt)
        self.N = 1

    def add_species(self, element, init_C):
        self.species[element] = DotDict({})
        self.species[element]['init_C'] = init_C
        self.species[element]['concentration'] = np.zeros((self.N, self.time.size))
        self.species[element]['alpha'] = np.zeros((self.N, self.time.size))
        self.species[element]['rates'] = np.zeros((self.N, self.time.size))
        self.species[element]['concentration'][:, 0] = self.species[element]['init_C']
        self.profiles[element] = self.species[element]['concentration'][:, 0]
        self.species[element]['int_transport'] = False
        self.dcdt[element] = '0'

    def integrate_one_timestep(self, i):
        if i == 1:
            self.pre_run_methods()
        self.reactions_integrate_scipy(i)
        if self.henry_law_equations:
            self.henry_equilibrium_integrate(i)
        if self.acid_base_components:
            self.acid_base_equilibrium_solve(i)

    def create_acid_base_system(self):
        self.add_species(element='pH', init_C=7)
        self.acid_base_system = pHcalc.System(
            *[c['pH_object'] for c in self.acid_base_components])

    def acid_base_update_concentrations(self, i):
        for component in self.acid_base_components:
            init_conc = 0
            alphas = component['pH_object'].alpha(
                self.species['pH']['concentration'][:, i])
            for idx in range(len(component['species'])):
                init_conc += self.species[component['species']
                                          [idx]]['concentration'][:, i]
            for idx in range(len(component['species'])):
                self.species[component['species'][idx]]['concentration'][:, i] = init_conc * alphas[idx]
                self.profiles[component['species'][idx]] = self.species[component['species'][idx]]['concentration'][:, i]
                self.species[component['species'][idx]]['alpha'][:, i] = alphas[idx]

    plot = Plotter.plot_depth_index
    plot_profiles = Plotter.all_plot_depth_index
    plot_fractions = Plotter.plot_fractions
    plot_rates = Plotter.plot_batch_rates
