from pathlib import Path

QUADRUPOLE_SCALING = {
    'label': 'Change energy',
    'tooltip': 'Multiplicative factor for the quadrupole settings: 1.0 leaves them unchanged; '
               '0.9 scales them to 90% of their reference values.',
    'test': {'label': 'Scaling factor', 'attribute': 'quadrupole_scaling_factor', 'default': 0.5},
}

INTERFACES = [{'display_name': 'FACET2 Linac RFTrack',
  'module': 'machine_interfaces_facet2.InterfaceFACET2_Linac_RFTrack',
  'class_name': 'InterfaceFACET2_Linac_RFTrack',
  'clock_timezone': 'Europe/Zurich',
  'beam_change': {'methods': ['Change Pref', 'Quadrupole scaling'],
                  'method_ids': {
                      'Change Pref': 'default',
                      'Quadrupole scaling': 'quadrupole_scaling',
                  },
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
  'units': {'corrector_strength': 'gauss*m', 'bpm_position': 'mm', 'sysid_corrector_kick': 0.0001},
  'bounds': {'emit_x_norm': [0.5, 8.0],
             'beta_x0': [0.5, 12.0],
             'alpha_x0': [-5.0, 3.0],
             'emit_y_norm': [0.5, 8.0],
             'beta_y0': [0.5, 12.0],
             'alpha_y0': [-5.0, 5.0],
             'energy_pref': [100.0, 150.0]}},
 {'display_name': 'FACET2 Linac',
  'module': 'machine_interfaces_facet2.InterfaceFACET2_Linac',
  'class_name': 'InterfaceFACET2_Linac',
  'clock_timezone': 'America/Los_Angeles',
  'beam_change': {'methods': ['Change feedback-vernier setpoints', 'Quadrupole scaling'],
                  'method_settings': {
                      'Quadrupole scaling': {'energy': QUADRUPOLE_SCALING}},
                    'method_ids': {
                        'Change feedback-vernier setpoints': 'default',
                        'Quadrupole scaling': 'quadrupole_scaling',
                    },
                  'energy': {'label': 'Change energy',
                             'tooltip': 'Writes FACET2 BC11, BC14 and BC20 feedback-vernier setpoints. Reset '
                                        'returns all three to zero.',
                             'nominal': {'label': 'BC11 [MeV]',
                                         'attribute': 'bba_bc11_energy_offset_mev',
                                         'default': -3.0},
                             'test': {'label': 'BC14/20 [MeV]',
                                      'attribute': 'bba_downstream_energy_offset_mev',
                                      'default': -40.0}},
                  'intensity': {'label': 'Change intensity (UV waveplate)',
                                'tooltip': 'Offsets the FACET2 UV waveplate; charge is then measured and '
                                           'used as the new charge setpoint.',
                                'test': {'label': 'UVWP Δ [deg]',
                                         'attribute': 'bba_uvwp_offset_deg',
                                         'default': -2.5}}},
  'units': {'corrector_strength': 'gauss*m', 'bpm_position': 'mm', 'sysid_corrector_kick': 0.0001},
  'bounds': {'emit_x_norm': [0.5, 8.0],
             'beta_x0': [0.5, 12.0],
             'alpha_x0': [-5.0, 3.0],
             'emit_y_norm': [0.5, 8.0],
             'beta_y0': [0.5, 12.0],
             'alpha_y0': [-5.0, 5.0]}}]

BRANDING = tuple(Path(__file__).parent / "assets" / name for name in ('facet2_logo.png', 'slac_logo.png'))
