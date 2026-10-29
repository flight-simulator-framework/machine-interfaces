"""Pure excitation-amplitude rules shared by SysID and tuning scans.

These functions do not read instruments or write magnets. The caller owns
current bounds, restoration, cancellation and the meaning of response units.
"""
import numpy as np


def finite_abs_max(values):
    arr = np.asarray(values, dtype=float).ravel()
    arr = arr[np.isfinite(arr)]
    return float(np.max(np.abs(arr))) if arr.size else 0.0


def update_amplitude(current_amp, observed, target, max_range):
    """Original SysID update rule, before its 80/20 smoothing."""
    if not np.isfinite(observed) or observed <= 0.0:
        new_amp = current_amp * 1.5
    else:
        scale = target / observed if target > 0 else 1.0
        new_amp = current_amp * max(0.8, min(scale, 2.0))
    if max_range > 0:
        new_amp = min(new_amp, max_range)
    return max(float(new_amp), 1e-6)


def next_excitation_amplitude(current_amp, observed, target, max_range):
    """SysID's smoothed next amplitude; caller must enforce supply limits."""
    return 0.8 * update_amplitude(current_amp, observed, target, max_range) + 0.2 * current_amp
