INTERFACE_SETUP = {
    "ATF2": [
        {
            "display_name": "ATF2 Damping Ring",
            "module": "machine_interfaces.Interfaces.ATF2.InterfaceATF2_DR",
            "class_name": "InterfaceATF2_DR",
            "clock_timezone": "Asia/Tokyo",
            "beam_change": {
                "energy": {
                    "label": "Change energy",
                    "tooltip": "The frequency offset of RAMP/PL4 is used to calculate dP/P.",
                    "test": {"label": "Δf [kHz]", "attribute": "energy_frequency_offset_khz", "default": 4.0},
                },
                "intensity": {
                    "label": "Change intensity",
                    "tooltip": "Sets the test laser-intensity factor. Reset restores the laser setting captured when the interface was opened.",
                    "test": {"label": "Test factor", "attribute": "test_laser_intensity", "default": 0.125},
                },
            },
            "settings": {"nsamples": 3},
            "units":
            {
                "corrector_strength":"T*mm",
                "bpm_position": "mm",
                "sysid_corrector_kick": 0.01
            },
            "bounds": {
                "emit_x_norm": [1.0, 10.0],
                "beta_x0": [1.0, 12.0],
                "alpha_x0": [-10.0, 3.0],
                "emit_y_norm": [0.005, 0.15],
                "beta_y0": [0.5, 8.0],
                "alpha_y0": [-4.0, 6.0],
                "energy_pref": [1000.0, 2000.0],
            }
        },
        {
            "display_name": "ATF2 Damping Ring RFTrack",
            "module": "machine_interfaces.Interfaces.ATF2.InterfaceATF2_DR_RFTrack",
            "class_name": "InterfaceATF2_DR_RFTrack",
            "clock_timezone": "Europe/Zurich",
            "beam_change": {
                "energy": {"label": "Change energy", "tooltip": "Multiplies RFTrack reference momentum Pref for the DFS measurement.", "test": {"label": "Pref factor", "attribute": "dfs_test_energy", "default": 0.98}},
                "intensity": {"label": "Change intensity", "tooltip": "Multiplies the RFTrack bunch charge for the WFS measurement.", "test": {"label": "Charge factor", "attribute": "wfs_test_charge", "default": 0.90}},
            },
            "settings": {"jitter":0.0, "bpm_resolution":0.0, "nsamples":1},
            "units":
                {
                    "corrector_strength": "T*mm",
                    "bpm_position": "mm",
                    "sysid_corrector_kick": 0.01
                },
            "bounds": {
                "emit_x_norm": [1.0, 10.0],
                "beta_x0": [1.0, 12.0],
                "alpha_x0": [-10.0, 3.0],
                "emit_y_norm": [0.005, 0.15],
                "beta_y0": [0.5, 8.0],
                "alpha_y0": [-4.0, 6.0],
                "energy_pref": [1000.0, 2000.0],
            }
        },
        {
            "display_name": "ATF2 Extraction Line",
            "module": "machine_interfaces.Interfaces.ATF2.InterfaceATF2_Ext",
            "class_name": "InterfaceATF2_Ext",
            "clock_timezone": "Asia/Tokyo",
            "beam_change": {
                "energy": {
                    "label": "Change energy",
                    "tooltip": "The frequency offset of RAMP/PL4 is used to calculate dP/P.",
                    "test": {"label": "Δf [kHz]", "attribute": "energy_frequency_offset_khz", "default": 4.0},
                },
                "intensity": {
                    "label": "Change intensity",
                    "tooltip": "Sets the nominal and test laser-intensity factors used for WFS.",
                    "nominal": {"label": "Nominal factor", "attribute": "nominal_laser_intensity", "default": 0.1},
                    "test": {"label": "Test factor", "attribute": "test_laser_intensity", "default": 0.125},
                },
            },
            "settings": {"nsamples": 3},
            "units":
                {
                    "corrector_strength": "T*mm",
                    "bpm_position": "mm",
                    "sysid_corrector_kick": 0.01,
                    "em_sigma_unit": "mm"
                },
            "bounds":
                {
                    "emit_x_norm": [0.5, 8.0],
                    "beta_x0": [0.2, 5.0],
                    "alpha_x0": [-4.0, 2.0],
                    "emit_y_norm": [0.005, 0.12],
                    "beta_y0": [2.0, 20.0],
                    "alpha_y0": [-8.0, 2.0],
                    "energy_pref": [1000.0, 2000.0],
                }
        },
        {
            "display_name": "ATF2 Extraction Line RFTrack",
            "module": "machine_interfaces.Interfaces.ATF2.InterfaceATF2_Ext_RFTrack",
            "class_name": "InterfaceATF2_Ext_RFTrack",
            "clock_timezone": "Europe/Zurich",
            "beam_change": {
                "energy": {"label": "Change energy", "tooltip": "Multiplies RFTrack reference momentum Pref for the DFS measurement.", "test": {"label": "Pref factor", "attribute": "dfs_test_energy", "default": 0.98}},
                "intensity": {"label": "Change intensity", "tooltip": "Multiplies the RFTrack bunch charge for the WFS measurement.", "test": {"label": "Charge factor", "attribute": "wfs_test_charge", "default": 0.90}},
            },
            "settings": {"jitter":0.0, "bpm_resolution":0.00, "nsamples":1},
            "units":
                {
                    "corrector_strength": "T*mm",
                    "bpm_position": "mm",
                    "sysid_corrector_kick": 0.01,
                    "em_sigma_unit": "mm"

                },

        "bounds": {
            "emit_x_norm": [5, 10.0],
            "beta_x0": [0.001, 60.0],
            "alpha_x0": [-15.0, 15.0],
            "emit_y_norm": [0.01, 5.0],
            "beta_y0": [0.001, 60.0],
            "alpha_y0": [-15, 15.0],
            "energy_pref": [1000.0, 2000.0],
        }

        },

        {
            "display_name": "ATF2 Linac",
            "module": "machine_interfaces.Interfaces.ATF2.InterfaceATF2_Linac",
            "class_name": "InterfaceATF2_Linac",
            "clock_timezone": "Asia/Tokyo",
            "beam_change": {
                "energy": {
                    "label": "Change energy",
                    "tooltip": "Writes CM1L RF phase. Nominal is restored after the DFS measurement.",
                    "nominal": {"label": "Nominal [deg]", "attribute": "phase_kl1", "default": 0.0},
                    "test": {"label": "Test [deg]", "attribute": "cm1l_test_phase", "default": 5.0},
                },
                "intensity": {"label": "Change intensity (RF gun laser)", "tooltip": "Sets the test laser-intensity factor. Reset restores the captured laser setting.", "test": {"label": "Test factor", "attribute": "test_laser_intensity", "default": 0.15}},
            },
            "settings": {"nsamples":3},
            "units":
                {
                    "corrector_strength": "T*mm",
                    "bpm_position": "mm",
                    "sysid_corrector_kick": 0.01
                },
            "bounds": {
                "emit_x_norm": [1e-4, 0.05],
                "beta_x0": [0.05, 5.0],
                "alpha_x0": [-6.0, 2.0],
                "emit_y_norm": [1e-4, 0.05],
                "beta_y0": [0.2, 8.0],
                "alpha_y0": [-15.0, 2.0],
                "energy_pref": [1000.0, 2000.0],
            }
        },
        {
            "display_name": "ATF2 Linac Beam Transport",
            "module": "machine_interfaces.Interfaces.ATF2.InterfaceATF2_LinacBT",
            "class_name": "InterfaceATF2_LinacBT",
            "clock_timezone": "Asia/Tokyo",
            "beam_change": {},
            "settings": {"nsamples": 3},
            "units":
                {
                    "corrector_strength": "T*mm",
                    "bpm_position": "mm",
                    "sysid_corrector_kick": 0.01
                },
            "bounds": {
                "emit_x_norm": [1e-4, 0.05],
                "beta_x0": [0.05, 5.0],
                "alpha_x0": [-6.0, 2.0],
                "emit_y_norm": [1e-4, 0.05],
                "beta_y0": [0.2, 8.0],
                "alpha_y0": [-15.0, 2.0],
                "energy_pref": [1000.0, 2000.0],
            }
        },
        {
            "display_name": "ATF2 Linac RFTrack",
            "module": "machine_interfaces.Interfaces.ATF2.InterfaceATF2_Linac_RFTrack",
            "class_name": "InterfaceATF2_Linac_RFTrack",
            "clock_timezone": "Europe/Zurich",
            "beam_change": {
                "energy": {"label": "Change energy", "tooltip": "Multiplies RFTrack reference momentum Pref for the DFS measurement.", "test": {"label": "Pref factor", "attribute": "dfs_test_energy", "default": 0.98}},
                "intensity": {"label": "Change intensity", "tooltip": "Multiplies the RFTrack bunch charge for the WFS measurement.", "test": {"label": "Charge factor", "attribute": "wfs_test_charge", "default": 0.90}},
            },
            "settings": {"jitter": 0.00, "bpm_resolution": 0.00},
            "units":
                {
                    "corrector_strength": "T*mm",
                    "bpm_position": "mm",
                    "sysid_corrector_kick": 0.01
                },
            "bounds": {
                "emit_x_norm": [1e-4, 0.05],
                "beta_x0": [0.05, 5.0],
                "alpha_x0": [-6.0, 2.0],
                "emit_y_norm": [1e-4, 0.05],
                "beta_y0": [0.2, 8.0],
                "alpha_y0": [-15.0, 2.0],
                "energy_pref": [1000.0, 2000.0],
            }
        },
    ],

    "FACET2": [
        {
            "display_name": "FACET2 Linac RFTrack",
            "module": "machine_interfaces.Interfaces.FACET2.InterfaceFACET2_Linac_RFTrack",
            "class_name": "InterfaceFACET2_Linac_RFTrack",
            "clock_timezone": "Europe/Zurich",
            "beam_change": {
                "energy": {"label": "Change energy", "tooltip": "Multiplies RFTrack reference momentum Pref for the DFS measurement.", "test": {"label": "Pref factor", "attribute": "dfs_test_energy", "default": 0.98}},
                "intensity": {"label": "Change intensity", "tooltip": "Multiplies the RFTrack bunch charge for the WFS measurement.", "test": {"label": "Charge factor", "attribute": "wfs_test_charge", "default": 0.90}},
            },
            "settings": {"jitter":0.0, "bpm_resolution":0.0, "nsamples":1},
            "units":
                {
                    "corrector_strength": "gauss*m",
                    "bpm_position": "mm",
                    "sysid_corrector_kick": 0.0001
                },
            "bounds": {
                "emit_x_norm": [0.5, 8.0],
                "beta_x0": [0.5, 12.0],
                "alpha_x0": [-5.0, 3.0],
                "emit_y_norm": [0.5, 8.0],
                "beta_y0": [0.5, 12.0],
                "alpha_y0": [-5.0, 5.0],
            }
        },
        {
            "display_name": "FACET2 Linac",
            "module": "machine_interfaces.Interfaces.FACET2.InterfaceFACET2_Linac",
            "class_name": "InterfaceFACET2_Linac",
            "clock_timezone": "America/Los_Angeles",
            "beam_change": {
                "energy": {
                    "label": "Change energy",
                    "tooltip": "Writes FACET2 BC11, BC14 and BC20 feedback-vernier setpoints. Reset returns all three to zero.",
                    "nominal": {"label": "BC11 [MeV]", "attribute": "bba_bc11_energy_offset_mev", "default": -3.0},
                    "test": {"label": "BC14/20 [MeV]", "attribute": "bba_downstream_energy_offset_mev", "default": -40.0},
                },
                "intensity": {"label": "Change intensity (UV waveplate)", "tooltip": "Offsets the FACET2 UV waveplate; charge is then measured and used as the new charge setpoint.", "test": {"label": "UVWP Δ [deg]", "attribute": "bba_uvwp_offset_deg", "default": -2.5}},
            },
            "settings": {"nsamples":10},
            "units":
                {
                    "corrector_strength": "gauss*m",
                    "bpm_position": "mm",
                    "sysid_corrector_kick": 0.0001
                },
            "bounds": {
                "emit_x_norm": [0.5, 8.0],
                "beta_x0": [0.5, 12.0],
                "alpha_x0": [-5.0, 3.0],
                "emit_y_norm": [0.5, 8.0],
                "beta_y0": [0.5, 12.0],
                "alpha_y0": [-5.0, 5.0],
            }
        },],

    "CLEAR": [
        {
            "display_name": "CLEAR",
            "module": "machine_interfaces.Interfaces.CLEAR.InterfaceCLEAR",
            "class_name": "CLEAR_real_machine",
            "clock_timezone": "Europe/Zurich",
            "beam_change": {
                "energy": {
                    "label": "Change energy",
                    "tooltip": "Writes MKS11 PhaseSh_SP. Nominal is restored after the DFS measurement.",
                    "nominal": {"label": "Nominal [deg]", "attribute": "rf_phase_nominal", "default": 125.0},
                    "test": {"label": "Test [deg]", "attribute": "rf_phase_test", "default": 145.0},
                },
                "intensity": {
                    "label": "Quadrupole scaling",
                    "tooltip": "Multiply the quadrupole currents captured when the interface was opened by this factor. Restore those currents afterward.",
                    "test": {"label": "Scaling factor", "attribute": "quadrupole_scaling_factor", "default": 0.5},
                    "labels": {
                        "mode": "Quadrupole scaling",
                        "status": "Quadrupole scaling",
                        "quantity": "Quadrupole scaling",
                        "short": "Quadrupole scaling",
                        "correction": "Quadrupole scaling correction",
                        "weight": "Quadrupole scaling weight",
                        "weight_tooltip": "Weight of the orbit-response change caused by scaling quadrupole currents. Higher values prioritize reducing this difference.",
                        "plot_title": "Quadrupole scaling (Residual to response matrix reference)",
                        "measuring": "Measuring orbit with scaled quadrupoles",
                        "changed": "Quadrupole currents scaled",
                        "directory": "quadrupole scaling",
                        "data_loaded": "Quadrupole Scaling Data Loaded",
                        "same_settings": "Orbit and quadrupole scaling measurements have the same settings.",
                        "restore_error": "Could not confirm the machine returned to its nominal RF phase and initial quadrupole currents.",
                        "restore_start": "Restoring RF phase and quadrupole settings from machine status...",
                        "restore_done": "RF phase and quadrupole settings restored!",
                        "jitter_tooltip": "Use upstream BPMs to estimate incoming beam jitter and subtract it from downstream BPM readings. With energy changes or quadrupole scaling, real orbit changes may be mistaken for jitter and over-subtracted.",
                    },
                },
            },
            "settings": {"nsamples":3},
            "units":
                {
                    "corrector_strength": "A",
                    "quadrupole_strength": "A",
                    "bpm_position": "mm",
                    "sysid_corrector_kick": 1,
                    "sysid_target_excursion": 5.0,
                    "bba_max_h_strength": 9.99,
                    "bba_max_v_strength": 9.99,
                },
            "bounds": {
                "emit_x_norm": [0.0, 50.0],
                "beta_x0": [0.001, 200.0],
                "alpha_x0": [-100.0, 100.0],
                "emit_y_norm": [0.0, 50.0],
                "beta_y0": [0.001, 200.0],
                "alpha_y0": [-100.0, 100.0],
                "energy_pref": [150.0, 250.0],
            }
        },
        {
            "display_name": "CLEAR RFTrack",
            "module": "machine_interfaces.Interfaces.CLEAR.InterfaceCLEAR_RFTrack",
            "class_name": "InterfaceCLEAR_RFTrack",
            "clock_timezone": "Europe/Zurich",
            "beam_change": {
                "energy": {"label": "Change energy", "tooltip": "Multiplies RFTrack reference momentum Pref for the DFS measurement.", "test": {"label": "Pref factor", "attribute": "dfs_test_energy", "default": 0.90}},
                "intensity": {"label": "Change intensity", "tooltip": "Multiplies the RFTrack bunch charge for the WFS measurement.", "test": {"label": "Charge factor", "attribute": "wfs_test_charge", "default": 0.90}},
            },
            "settings": {"jitter": 0.0, "bpm_resolution": 0.0, "nsamples": 1},
            "units":
                {
                    "corrector_strength": "gauss*m",
                    "bpm_position": "mm",
                    "sysid_corrector_kick": 0.01,
                    "bba_max_h_strength": 9.99,
                    "bba_max_v_strength": 9.99,
                },
            "bounds": {
                "emit_x_norm": [0.0, 50.0],
                "beta_x0": [0.001, 200.0],
                "alpha_x0": [-100.0, 100.0],
                "emit_y_norm": [0.0, 50.0],
                "beta_y0": [0.001, 200.0],
                "alpha_y0": [-100.0, 100.0],
                "energy_pref": [150.0, 250.0],
            }
        },
    ],
}


INTENSITY_LABELS = {
    "mode": "Changed intensity",
    "status": "Wakefield",
    "quantity": "Wakefield",
    "short": "WFS",
    "correction": "Wakefield-Free Steering",
    "weight": "Wakefield weight",
    "weight_tooltip": "<html><head/><body><p>Weight of the WFS term. </p><p>Higher value makes the correction prioritize reducing intensity-dependent orbit changes. </p></body></html>",
    "plot_title": "Wakefield (Residual to response matrix reference)",
    "measuring": "Measuring wakefield",
    "changed": "Intensity changed)",
    "directory": "wakefield",
    "data_loaded": "WFS Data Loaded",
    "same_settings": "Orbit and Changed intensity measurements have the same settings.",
    "restore_error": "Could not confirm the machine returned to its nominal energy/intensity.",
    "restore_start": "Restoring energy and intensity from machine status...",
    "restore_done": "Energy and intensity restored!"
}


def get_intensity_labels(interface=None):
    interface_type = type(interface)
    for interfaces in INTERFACE_SETUP.values():
        for settings in interfaces:
            if (settings.get("module") == interface_type.__module__
                    and settings.get("class_name") == interface_type.__name__):
                labels = settings.get("beam_change", {}).get("intensity", {}).get("labels", {})
                return {**INTENSITY_LABELS, **labels}
    return dict(INTENSITY_LABELS)
