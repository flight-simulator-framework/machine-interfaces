from importlib.metadata import entry_points

INTERFACE_SETUP = {}
ACCELERATOR_BRANDING = {}

for registration in sorted(entry_points(group="flight_simulator.interfaces"), key=lambda entry: entry.name):
    if registration.name in INTERFACE_SETUP:
        raise RuntimeError(f"Multiple interface packages registered for {registration.name}")
    setup = registration.load()
    INTERFACE_SETUP[registration.name] = setup.INTERFACES
    ACCELERATOR_BRANDING[registration.name] = setup.BRANDING


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


def get_intensity_labels(interface=None, energy_method=None):
    interface_type = type(interface)
    for interfaces in INTERFACE_SETUP.values():
        for settings in interfaces:
            if (settings.get("module") == interface_type.__module__
                    and settings.get("class_name") == interface_type.__name__):
                beam_change = settings.get("beam_change", {})
                profile = beam_change.get("method_settings", {}).get(energy_method, {})
                intensity = profile.get("intensity", beam_change.get("intensity", {}))
                labels = intensity.get("labels", {})
                return {**INTENSITY_LABELS, **labels}
    return dict(INTENSITY_LABELS)
