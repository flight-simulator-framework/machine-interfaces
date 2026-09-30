from pathlib import Path

INTERFACES = [{'display_name': 'ESRF TL2',
  'module': 'machine_interfaces_esrf.InterfaceESRF_TL2',
  'class_name': 'InterfaceESRF_TL2',
  'clock_timezone': 'Europe/Paris',
  'beam_change': {},
  'settings': {'nsamples': 3},
  'units': {'corrector_strength': 'A', 'quadrupole_strength': 'A', 'bpm_position': 'm', 'sysid_target_excursion': 0.0005}},

  {'display_name': 'ESRF TL2 RF-Track',
   'module': 'machine_interfaces_esrf.InterfaceESRF_TL2_RFTrack',
   'class_name': 'InterfaceESRF_TL2_RFTrack',
   'clock_timezone': 'Europe/Paris',
   'beam_change': {},
   'settings': {'nsamples': 3},
   'units': {'corrector_strength': 'A', 'quadrupole_strength': 'A', 'bpm_position': 'm',
             'sysid_target_excursion': 0.5}},

  ]

BRANDING = (Path(__file__).parent / "assets" / 'esrf_logo.png',)
