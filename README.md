# Machine Interfaces

Connect Flight Simulator applications to an accelerator control system or a simulation. An interface translates machine-specific commands and measurements into the common operations used by the applications: reading BPMs and magnet settings, changing actuators, recording machine states and controlling beam energy or intensity.

The repository contains interfaces for ATF2, CLEAR and FACET2, including live-machine and RFTrack implementations.


The available choices are registered in `machine_interfaces/Interfaces/interface_setup.py`; `machine_interfaces/Backend/SelectInterface.py` provides the selection window.

## Connecting a new machine

The virtual class is `AbstractMachineInterface`; `State` is the data container shared by acquisition, response-matrix calculation, correction and emittance applications, while the machine interface itself is used for communication with the machine (simulated or real).

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

## Data dictionaries

All fields must describe the same devices in the same order. `names` is an ordered sequence of device names. Convert scalar hardware responses to arrays with the expected dimensions, including when only one device or one sample is selected.

| Device type | Fields | Shapes and meaning                                                                                                                                                                                                           |
|-------------|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Correctors  | `names`, `bdes`, `bact` | `N` names and two arrays of length `N`; `bdes`: desired/setpoint, `bact`: actual/readback strengths.                                                                                                                         |
| BPMs        | `names`, `x`, `y`, `tmit` | `N` names; arrays shaped `(nsamples, N)`. Positions would be best in mm.                                                                                                                                                     |
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

* `set_correctors()` and `get_correctors()` - in order to perform corrector kicks and acquiring readbacks.


* `get_bpms()` returns BPMs readbacks


* `get_hcorrectors_names()` and `get_vcorrectors_names()` - return list of names with horizontal and vertical correctors


* `change_energy()`, `reset_energy()` - ways to change and reset energy for off-energy response matrix acquisition


* `change_intensity()`, `reset_intensity()` - ways to change and reset bunch charge for changed intensity response matrix acquisition


* `get_icts()` - returns transmission evolution in order to track if the transmission is not lost

QM SysID additionally needs `get_quadrupole_movers_names()`, `get_quadrupoles(names)` with mover readback/setpoint arrays, and `apply_qmag_xyroll(names, x, y, roll, wait=True)`.

### Beam-based alignment

Corrector BBA needs the same methods as `System Identification`, ordered sequence, `get_target_dispersion` in case of target-dispersion correction (can be set to 0 in case of Dispersion Free Steering).

Optional QM BBA additionally uses mover names, mover state and `apply_qmag_xyroll(...)`. Some plots optionally use `get_twiss_at_screen`.

### Orbit bump

This application needs the same methods as `System Identification`.


### Emittance measurement

Emittance measurement needs:

* `get_quadrupoles()`, `set_quadrupoles()` - used mainly for quadrupole scan. It is also useful when downloading the status of the machine to update the RF - Track model.
* `get_screens()` - used as well during quadrupole scan. They record images, coupling, beam positions and other quantities.
And, the ordered device sequence as well.
* `insert_screen()`, `extract_screen()` - methods to directly call to interact with screens moving in and out of the beamline.

Scan ranges are entered in amperes. If a quadrupole's `value_unit` is not `A`, the scan requires `current_to_k1l(quad_name, current_A)` for conversion. `k1l_to_current(quad_name, value)` is used for displayed/stored current values when available.


## Next steps to create a new machine interface

The first step is modifying the `machine_interfaces/Interfaces/interface_setup.py`, grouped by accelerator.

An example of an entry is:

```python
{
    "display_name": "New accelerator",
    "module": "machine_interfaces.Interfaces.NewAccelerator.InterfaceNewAccelerator",
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
2. Register the interface and its constructor settings in `machine_interfaces/Interfaces/interface_setup.py` so that it appears in the selector.

## Shared application utilities

This repository also provides the common modules used by the applications:

- `machine_interfaces/Backend/State.py`: machine snapshots, device selection, orbit summaries and snapshot persistence.
- `machine_interfaces/Backend/SaveOrLoad.py`: saving and loading device selections and measurement sessions.
- `machine_interfaces/Backend/LogConsole.py`: application log dialog.
- `machine_interfaces/Backend/ActuatorMode.py`: corrector and quadrupole-mover modes.
- `machine_interfaces/Knobs/jitter_subtraction.py`: estimation and subtraction of correlated beam motion using upstream BPMs.

## Installation

Use Python 3.11 or newer and Poetry 2 or newer. From the repository directory, install the dependencies:

```bash
poetry update rf-track --lock
poetry install --extras "rftrack epics madx tao"
```

The Python package is named `machine_interfaces`. For example:

```python
from machine_interfaces.Interfaces.CLEAR.InterfaceCLEAR_RFTrack import InterfaceCLEAR_RFTrack
```

## ATF2 magnet-current calibration

ATF2 emittance scans and magnet-current conversion require the native `libmagnet` library. Install a C compiler, GNU Fortran (`gfortran`) and `make`, then build it from the sources in this repository:

```bash
cd "machine_interfaces/Machine specifics, user implementations/ATF2/libmagnet"
make CFLAG=-fPIC
```

On macOS, also run:

```bash
gfortran -dynamiclib -o libmagnet.dylib *.o
```

On Linux, `make` produces `libmagnet.so`. Keep the resulting library in this directory; applications using the editable package will find it automatically. A prebuilt library must match the operating system and CPU architecture. To use a library stored elsewhere, set `ATF2_MAG_KI_LIB` to its absolute path. Compiled libraries and object files are excluded from Git.
