# -*- coding: latin-1 -*-

from __future__ import division  # use "//" to do integer division

from farquharwheat import model
from farquharwheat import parameters

"""
    farquharwheat.simulation
    ~~~~~~~~~~~~~~~~~~~~~~~~

    The module :mod:`farquharwheat.simulation` is the front-end to run the Farquhar-Wheat :mod:`model <farquharwheat.model>`.

    :copyright: Copyright 2014-2015 INRA-ECOSYS, see AUTHORS.
    :license: see LICENSE for details.

"""


class SimulationError(Exception):
    pass


class SimulationInputsError(SimulationError):
    pass


class Simulation(object):
    """The Simulation class permits to initialize and run a simulation.
    """

    def __init__(self, update_parameters=None):

        #: The inputs of Farquhar-Wheat.
        #:
        #: `inputs` is a dictionary of dictionaries:
        #:     {(plant_index, axis_label, metamer_index, organ_label, element_label): {element_input_name: element_input_value, ...}, ...}
        #: See :meth:`Model.run <farquharwheat.model.run>`
        #: for more information about the inputs.
        self.inputs = {}

        #: The outputs of Farquhar-Wheat.
        #:
        #: `outputs` is a dictionary of dictionaries:
        #:     {(plant_index, axis_label, metamer_index, organ_label, element_label): {element_output_name: element_output_value, ...}, ...}
        #: See :meth:`Model.run <farquharwheat.model.run>`
        #: for more information about the outputs.
        self.outputs = {}

        #: Update parameters if specified
        if update_parameters:
            parameters.__dict__.update(update_parameters)

    def initialize(self, inputs):
        """
        Initialize :attr:`inputs` from `inputs`.

        :param dict inputs: Dictionary of two dictionaries :
                    - `elements` : The inputs by element.
                    - `axes` : The inputs by axis.
              `inputs` must be a dictionary with the same structure as :attr:`inputs`.

            See :meth:`Model.run <farquharwheat.model.run>`
               for more information about the inputs.
        """
        self.inputs.clear()
        self.inputs.update(inputs)

    def run(self, Ta, ambient_CO2, RH, Ur):
        """
        Compute Farquhar variables for each element in :attr:`inputs` and put
        the results in :attr:`outputs`.

        :param float Ta: air temperature at t (degree Celsius)
        :param float ambient_CO2: air CO2 at t (�mol mol-1)
        :param float RH: relative humidity at t (decimal fraction)
        :param float Ur: wind speed at the top of the canopy at t (m s-1)
        """

        self.outputs.update({inputs_type: {} for inputs_type in self.inputs['elements'].keys()})

        for (element_id, element_inputs) in self.inputs['elements'].items():

            axis_id = element_id[:2]
            organ_label = element_id[3]

            axe_label = axis_id[1]
            if axe_label != 'MS':  # Calculation only for the main stem
                continue
            # In case it is an HiddenElement, we need temperature calculation. Cases of Visible Element without geomtry proprety (because too small) don't have photosynthesis calculation neither.
            if element_inputs['height'] is None:
                Ag, An, Rd, Tr, gs = 0., 0., 0., 0., 0.
                Ts = self.inputs['axes'][axis_id]['SAM_temperature']
            else:
                PARa = element_inputs['PARa']  #: Amount of absorbed PAR per unit area (�mol m-2 s-1)
                height_canopy = self.inputs['axes'][axis_id]['height_canopy']

                if parameters.MODEL_VERSION in ['SurfacicProteins', 'SurfacicProteins_Retroinhibition']:
                    surfacic_photosynthetic_proteins = model.calculate_surfacic_photosynthetic_proteins(element_inputs['proteins'],
                                                                                                        element_inputs['green_area'])

                    SLN_nonstruct_Farquhar = model.calculate_surfacic_nonstructural_nitrogen_Farquhar(surfacic_photosynthetic_proteins)

                    option_Retroinhibition = False
                    surfacic_WSC = None  # TODO: rename by non structural carbohydrates because starch is not water-soluble.
                    if parameters.MODEL_VERSION == 'SurfacicProteins_Retroinhibition':
                        option_Retroinhibition = True
                        surfacic_WSC = model.calculate_surfacic_WSC(element_inputs['sucrose'], element_inputs['starch'], element_inputs['fructan'], element_inputs['green_area'])

                    Ag, An, Rd, Tr, Ts, gs = model.run(SLN_nonstruct_Farquhar,
                                                       option_Retroinhibition,
                                                       surfacic_WSC,
                                                       element_inputs['width'],
                                                       element_inputs['height'],
                                                       PARa, Ta, ambient_CO2,
                                                       RH, Ur, organ_label, height_canopy)
                elif parameters.MODEL_VERSION == 'Barillot2016':
                    surfacic_nitrogen = model.calculate_surfacic_nitrogen(element_inputs['nitrates'],
                                                                          element_inputs['amino_acids'],
                                                                          element_inputs['proteins'],
                                                                          element_inputs['Nstruct'],
                                                                          element_inputs['green_area'])
                    option_Retroinhibition = False
                    surfacic_WSC = 0.  # Not used if option_Retoinhibition = False

                    Ag, An, Rd, Tr, Ts, gs = model.run(surfacic_nitrogen,
                                                       option_Retroinhibition,
                                                       surfacic_WSC,
                                                       element_inputs['width'],
                                                       element_inputs['height'],
                                                       PARa, Ta, ambient_CO2,
                                                       RH, Ur, organ_label, height_canopy)
                else:
                    raise NameError('MODEL_VERSION is not none. MODEL_VERSION must be Barillot2016 or SurfacicProteins or SurfacicProteins_Retroinhibition.')

            element_outputs = {'Ag': Ag, 'An': An, 'Rd': Rd,
                               'Tr': Tr, 'Ts': Ts, 'gs': gs,
                               'width': element_inputs['width'], 'height': element_inputs['height']}

            self.outputs[element_id] = element_outputs
