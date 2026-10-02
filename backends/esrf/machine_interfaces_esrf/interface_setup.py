from pathlib import Path

QUADRUPOLE_SCALING = {
    'label': 'Change energy',
    'tooltip': 'Multiplicative factor for the quadrupole settings: 1.0 leaves them unchanged; '
               '0.9 scales them to 90% of their reference values.',
    'test': {'label': 'Scaling factor', 'attribute': 'quadrupole_scaling_factor', 'default': 0.5},
}

INTERFACES = [{'display_name': 'ESRF TL2',
  'module': 'machine_interfaces_esrf.InterfaceESRF_TL2',
  'class_name': 'InterfaceESRF_TL2',
  'clock_timezone': 'Europe/Paris',
  'beam_change': {'methods': ['Change booster extraction time', 'Quadrupole scaling'],
                  'method_settings': {
                      'Quadrupole scaling': {'energy': QUADRUPOLE_SCALING}},
                  'energy': {'label': 'Change energy',
                             'tooltip': 'Offsets the booster extraction time and scales the extraction '
                                        'magnet currents accordingly. Reset restores the nominal settings '
                                        'from the operation files.',
                             'test': {'label': 'Timing offset [ms]',
                                      'attribute': 'energy_delta',
                                      'default': 1.0}},
                  'intensity': {'label': 'Change intensity',
                                'tooltip': 'Offsets the gun grid voltage (pulsev) by the specified number of '
                                           'volts. Reset restores the voltage captured before the first change.',
                                'test': {'label': 'Grid voltage offset [V]',
                                         'attribute': 'intensity_delta',
                                         'default': -1.0}}},
  'settings': {'nsamples': 3},
  'units': {'corrector_strength': 'A', 'quadrupole_strength': 'A', 'bpm_position': 'm', 'sysid_target_excursion': 0.0005}},

  {'display_name': 'ESRF TL2 RF-Track',
   'module': 'machine_interfaces_esrf.InterfaceESRF_TL2_RFTrack',
   'class_name': 'InterfaceESRF_TL2_RFTrack',
   'clock_timezone': 'Europe/Paris',
   'beam_change': {'methods': ['Change Pref', 'Quadrupole scaling'],
                   'method_settings': {
                       'Quadrupole scaling': {'energy': QUADRUPOLE_SCALING}},
                   'energy': {'label': 'Change energy',
                              'tooltip': 'Multiplies RFTrack reference momentum Pref for the DFS measurement.',
                              'test': {'label': 'Pref factor',
                                       'attribute': 'dfs_test_energy',
                                       'default': 0.98}},
                   'intensity': {'label': 'Change intensity',
                                 'tooltip': 'Multiplies the RFTrack bunch charge for the WFS measurement.',
                                 'test': {'label': 'Charge factor',
                                          'attribute': 'wfs_test_charge',
                                          'default': 0.9}}},
   'settings': {'nsamples': 3},
   'units': {'corrector_strength': 'A', 'quadrupole_strength': 'A', 'bpm_position': 'm',
             'sysid_target_excursion': 0.5}},

  ]

BRANDING = (Path(__file__).parent / "assets" / 'esrf_logo.png',)
