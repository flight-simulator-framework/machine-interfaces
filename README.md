# Machine Interfaces

Connect Flight Simulator applications to an accelerator control system or a simulation. Each interface implements the common set of methods used by the applications.

This repository provides a shared interface API and four accelerator-specific backend packages:

- `machine-interfaces`: shared interface API and application utilities.
- `machine-interfaces-clear`: CLEAR interfaces.
- `machine-interfaces-atf2`: ATF2 interfaces.
- `machine-interfaces-facet2`: FACET2 interfaces.
- `machine-interfaces-esrf`: ESRF interfaces.

Accelerator-specific packages are located in `backends/<machine>` and provide interfaces to the control system or simulation. Installed packages register their interfaces through the `flight_simulator.interfaces` entry-point group. The selector displays only installed machines. Importing the registry does not connect to any machine.

# Installation

For deployment on a control-room computer, follow the instructions for [CLEAR](backends/clear/clear_deploy.md), [ATF2](backends/atf2/atf2_deploy.md), [ESRF](backends/esrf/esrf_deploy.md) or [FACET2](backends/facet2/facet2_deploy.md).


## Connecting a new machine

The abstract base class is `AbstractMachineInterface`; `State` is the data container shared by acquisition, response-matrix calculation, correction and emittance applications, while the machine interface itself is used for communication with the machine (simulated or real).

## Required subclass methods

These ten methods have `@abstractmethod` in the current base class and must be implemented before Python will instantiate a subclass.

| Method | Required behavior |
|---|---|
| `get_name()` | Return the machine/backend name used in application labels and output-directory names. |
| `get_sequence()` | Return the beamline-ordered list of element names. Names used in BPM/corrector inventories must be consistent with it. Matrix/correction code uses sequence order and `list.index`. |
| `get_correctors(names=None)` | Return corrector names, desired values and actual/readback values. |
| `get_bpms(names=None)` | Return BPM names and two-dimensional position/intensity arrays. |
| `get_icts(names=None)` | Return ICT names and charge readings. An empty correctly shaped result can represent no ICTs. |
| `set_correctors(names, values)` | Set the requested absolute corrector values using the backend's documented units and synchronization.|
| `change_energy()` | Apply the configured DFS test energy condition. |
| `reset_energy()` | Restore the backend's nominal/captured energy condition. |
| `change_intensity()` | Apply the configured WFS test intensity condition. |
| `reset_intensity()` | Restore the backend's nominal/captured intensity condition. |

The following two methods are not declared abstract, but the inherited `get_state()` calls them and a usable subclass must provide them:

- `get_hcorrectors_names()` returns the horizontal corrector names.
- `get_vcorrectors_names()` returns the vertical corrector names.

Energy methods used by SysID and BBA must accept the `method` keyword argument. For target-dispersion correction, `change_energy()` must return the relative momentum change used to calculate the target orbit difference.

## Data dictionaries

All fields must describe the same devices in the same order. `names` is an ordered sequence of device names. Convert scalar hardware responses to arrays with the expected dimensions, including when only one device or one sample is selected.

| Device type | Fields | Shapes and meaning                                                                                                                                                                                                           |
|-------------|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Correctors  | `names`, `bdes`, `bact` | `N` names and two arrays of length `N`; `bdes`: desired/setpoint, `bact`: actual/readback strengths.                                                                                                                         |
| BPMs        | `names`, `x`, `y`, `tmit` | `N` names; arrays shaped `(nsamples, N)`. Return positions in millimetres to match the application calculations and declare `units.bpm_position` as `mm` in the interface registration. |
| ICTs        | `names`, `charge` | `N` names and charge array of length `N`.                                                                                                                                                                                    |
| Quadrupoles | `names`, `bdes`, `bact` | Existing mover interfaces add position/roll arrays such as `xdes`, `xact`, `ydes`, `yact`, `rolldes`, `rollact`.                                                                                                             |
| Sextupoles  | `names`, `bdes`, `bact` | Same as quadrupoles.                                                                                                                                                                                                         |
| Screens     | `names`, `hpixel`, `vpixel`, `x`, `y`, `sigx`, `sigy`, `sum`, `hedges`, `vedges`, `images`, `S` | Scalar arrays of length `N`; one image and horizontal/vertical edge array per screen. `x`/`y` are centroids, `sigx`/`sigy` RMS sizes, `sum` intensity, and `S` longitudinal position. Edge and image orientation must agree. |

The base supplies empty quadrupole and sextupole dictionaries with empty arrays. Its empty screen dictionary supplies every listed key, using empty arrays or lists as appropriate. It does not supply default corrector, BPM or ICT reads.

## Methods required by each application

### Response matrix

`ComputeResponseMatrix_GUI.py`, its QM variant and the random-excitation variant calculate matrices from saved acquisition files. They do not require a live machine interface merely to load and process existing data. They require the shared State format and the relevant response data.

For the paired-excitation logic, data filenames are `DATA_<corrector>_p<index>.pkl` (positive corrector kick) and `DATA_<corrector>_m<index>.pkl` (negative corrector kick).

The system-identification application below produces these machine snapshots.

### System identification

Corrector SysID needs:

- `set_correctors()` and `get_correctors()` apply corrector kicks and acquire readbacks.
- `get_bpms()` returns BPM readbacks.
- `get_hcorrectors_names()` and `get_vcorrectors_names()` return the horizontal and vertical corrector names.
- `change_energy()` and `reset_energy()` apply and restore the energy condition for off-energy response matrix acquisition.
- `change_intensity()` and `reset_intensity()` apply and restore the bunch-charge condition for changed-intensity response matrix acquisition.
- `get_icts()` returns charge readings included in the acquired machine snapshots.

QM SysID additionally needs `get_quadrupole_movers_names()`, `get_quadrupoles(names)` with mover readback/setpoint arrays, and `apply_qmag_xyroll(names, x, y, roll, wait=True)`.

### Beam-based alignment

Corrector BBA needs the same methods as System Identification, an ordered device sequence and `get_target_dispersion()` for target-dispersion correction. Return zero target dispersion for Dispersion Free Steering.

Optional QM BBA additionally uses mover names, mover state and `apply_qmag_xyroll(...)`. Some plots optionally use `get_twiss_at_screen`.

### Orbit bump

Orbit bump requires corrector reads and writes, BPM acquisition, device ordering and machine snapshots. Applying a bump does not call the energy or intensity methods, although subclasses must still implement all abstract methods.


### Emittance measurement

Emittance measurement needs:

- `get_quadrupoles()` and `set_quadrupoles()` read and change quadrupole settings during a scan. Quadrupole readbacks are also used to update the RFTrack model from the machine state.
- `get_screens()` returns screen images, beam positions, sizes and other acquisition quantities.
- `get_sequence()` returns the ordered device sequence.

Screen movement methods are optional. The scan calls `extract_screen()` during cleanup when the backend provides it. The current scan does not require or call `insert_screen()`.

Scan ranges are entered in amperes. If a quadrupole's `value_unit` is not `A`, the scan requires `current_to_k1l(quad_name, current_A)` for conversion. `k1l_to_current(quad_name, value)` is used for displayed/stored current values when available.


## Next steps to create a new machine interface

Create a separate adapter package with an `interface_setup.py` exporting an `INTERFACES` list and a `BRANDING` tuple of logo paths (or an empty tuple). Register that module under `[project.entry-points."flight_simulator.interfaces"]` in its `pyproject.toml`, using the accelerator name as the key. See `backends/clear` for the package layout.

An example of an entry is:

```python
{
    "display_name": "New accelerator",
    "module": "machine_interfaces_newaccelerator.InterfaceNewAccelerator",
    "class_name": "InterfaceNewAccelerator",
    "settings": {"nsamples": 3},
    "units": {
        "corrector_strength": "A",
        "bpm_position": "mm",
        "sysid_corrector_kick": 0.01
    }
}
```

The values are an example structure only; choose real units and appropriate kicks for the new machine. The module path must match the implementation.

1. Provide device inventories, beamline order, acquisition methods, corrector setters and the required energy/intensity methods. Follow the documented data shapes, device ordering and units.
2. Register the interface and its constructor settings in the adapter package’s `INTERFACES` list so that it appears in the selector when that package is installed.

## Shared application utilities

This repository also provides the common modules used by the applications:

- `machine_interfaces/Backend/State.py`: machine snapshots, device selection, orbit summaries and snapshot persistence.
- `machine_interfaces/Backend/SaveOrLoad.py`: saving and loading device selections and measurement sessions.
- `machine_interfaces/Backend/LogConsole.py`: application log dialog.
- `machine_interfaces/Backend/ActuatorMode.py`: corrector and quadrupole-mover modes.
- `machine_interfaces/Knobs/jitter_subtraction.py`: estimation and subtraction of correlated beam motion using upstream BPMs.
