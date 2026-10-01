import csv
import time
from pathlib import Path
import numpy as np
import pandas
from machine_interfaces.Interfaces.AbstractMachineInterface import AbstractMachineInterface
import pandas as pd
try:
    import tango
except ImportError:
    tango = None
# import ringcontrol.beamcontrol.orbitcorr as orbitcorr
# from ringcontrol.devices.constants import DevNames, AttNames, PropNames, Numeric
# import ringcontrol.devices.magnets as magnets

def get_unavailable_reason():
    if tango is None:
        return "ESRF interface requires the tango environment."
    return None

class InterfaceESRF_TL2(AbstractMachineInterface):
    def get_name(self):
        return 'ESRF_TL2_Ext'

    def __init__(self, nsamples=3, bg_shots=10.0, energy_delta=None, intensity_delta=None, text_unit=None):
        reason = get_unavailable_reason()
        if reason:
            raise RuntimeError(reason)
        self.screen_backgrounds = {}
        self.settle_time = 2
        self.energy_delta = 1.0 if energy_delta is None else energy_delta
        self.intensity_delta = intensity_delta
        self.text_unit = text_unit
        self.initial_energy_settings = {}
        self.initial_gridv = None
        self.chosen_ict = "tl2/d-ct/ict-1"
        self.nsamples = nsamples
        self.electronmass = 0.51099895 # MeV/c^2
        self.Pref = 6000
        self.machine_name = "ESRF_TL2"
        # self.tracking_interface = InterfaceESRF_TL2_RFTrack()
        self.is_simulation = False
        self.log = print
        self.quadrupole_scaling_factor = 0.5

        # Bpms and correctors in beamline order
        # sequence including -- bpms and correctors -- in beamline order with device names
        # sequence = [
        #     "tl2/ps-c1/cv0", "tl2/d-bpm/cv1", "tl2/ps-c1/cv1", "tl2/ps-c1/ch1", "tl2/ps-c1/ch2", "tl2/ps-c1/cv3", "tl2/ps-c1/ch3", "tl2/d-bpm/d2",
        #     "tl2/d-bpm/q5", "tl2/ps-c1/cv4", "tl2/ps-c1/ch4", "tl2/d-bpm/q6", "tl2/ps-c1/cv5", "tl2/ps-c1/ch5", "tl2/d-bpm/sx",
        #     "tl2/ps-c1/cv6", "tl2/ps-c1/ch6", "tl2/d-bpm/q8", "tl2/ps-c1/cv7", "tl2/ps-c1/ch7", "tl2/d-bpm/q12",
        #     "tl2/ps-c1/cv8", "tl2/ps-c1/ch8", "tl2/d-bpm/q14", "tl2/ps-c1/cv9", "tl2/d-bpm/s1pm"
        # ]
        # sequence including -- correctors and bpms -- in beamline order
        # sequence = [
        #     "COR.cv0", "BPM.cv1", "COR.cv1", "COR.ch1", "COR.ch2", "COR.cv3", "COR.ch3", "BPM.d2", "BPM.q5",
        #     "COR.cv4", "COR.ch4", "BPM.q6", "COR.cv5", "COR.ch5", "BPM.sx", "COR.cv6", "COR.ch6", "BPM.q8",
        #     "COR.cv7", "COR.ch7", "BPM.q12", "COR.cv8", "COR.ch8", "BPM.q14", "COR.cv9", "BPM.s1pm"
        # ]
        # sequence including correctors (COR), quadrupoles (MAG), dipoles (MAG) and bpms (BPM) -- in beamline order
        # sequence = [
            # "COR.cv0", "BPM.cv1", "COR.cv1", "COR.ch1", "MAG.qf1", "COR.ch2", "MAG.qd2", "MAG.d1", "MAG.qf3", "COR.cv3", "COR.ch3",
            # "MAG.d2", "BPM.d2", "MAG.qf4", "BPM.q5", "MAG.qd5", "COR.cv4", "COR.ch4", "BPM.q6", "MAG.qf6", "COR.cv5", "COR.ch5", "MAG.d3",
            # "BPM.sx", "COR.cv6", "COR.ch6", "MAG.qf7", "MAG.d4", "BPM.q8", "MAG.qd8", "COR.cv7", "COR.ch7", "MAG.qf9", "MAG.qd10", "MAG.qf11",
            # "MAG.d5", "BPM.q12", "MAG.qd12", "COR.cv8", "COR.ch8", "MAG.qf13", "BPM.q14", "MAG.qf14", "COR.cv9", "BPM.s1pm"
        # ]
        # sequence including correctors, quadrupoles and bpms -- in beamline order
        sequence = [
            "COR.cv0", "BPM.cv1", "COR.cv1", "COR.ch1", "MAG.qf1", "COR.ch2", "MAG.qd2", "MAG.qf3", "COR.cv3", "COR.ch3", "BPM.d2",
            "MAG.qf4", "BPM.q5", "MAG.qd5", "COR.cv4", "COR.ch4", "BPM.q6", "MAG.qf6", "COR.cv5", "COR.ch5", "BPM.sx",
            "COR.cv6", "COR.ch6", "MAG.qf7", "BPM.q8", "MAG.qd8", "COR.cv7", "COR.ch7", "MAG.qf9", "MAG.qd10", "MAG.qf11", "BPM.q12",
            "MAG.qd12", "COR.cv8", "COR.ch8", "MAG.qf13", "BPM.q14", "MAG.qf14", "COR.cv9", "BPM.s1pm"
        ]

        monitors = [
            "CV1", "D2", "Q5", "Q6", "SX", "Q8", "Q12", "Q14", "S1PM" # striplines
        ]

        correctors = [
            'CV0',
            'CH1', 'CV1',
            'CH2',
            'CH3', 'CV3',
            'CH4', 'CV4',
            'CH5', 'CV5',
            'CH6', 'CV6',
            'CH7', 'CV7',
            'CH8', 'CV8',
                   'CV9'
        ]

        quadrupoles = [
            "QF1", "QD2", "QF3", "QF4", "QD5", "QF6", "QF7", "QD8", "QF9", "QD10", "QF11", "QD12", "QF13", "QF14"
        ]
        vlm = [
            "D1", "D2", "D3", "D4", "D5" # visible light monitors
        ]
        screens = [
            "FS0", "FS1", "FS2", "FS3", "FS4", "FS5", "FS6", "FS7" # destructive screen measurements
        ]

        monitors = [f"BPM.{name.lower()}" for name in monitors]
        correctors = [f"COR.{name.lower()}" for name in correctors]
        quadrupoles = [f"MAG.{name.lower()}" for name in quadrupoles]

        self.screens = screens
        self.quadrupoles = quadrupoles
        self.vlm = vlm

        monitors_from_sequence = [element for element in sequence if element in monitors]
        bpm_ok = all(bpm in monitors for bpm in monitors_from_sequence)

        if not bpm_ok:
            bpms_unknown = [bpm for bpm in monitors_from_sequence if bpm not in monitors]
            self.log(f'Unknown bpms {bpms_unknown} removed from list')

        sequence_filtered = [
            element for element in sequence
            if element in monitors or element in correctors or element in self.quadrupoles or element in self.screens
        ]
        self.sequence = sequence_filtered
        self.bpms = [element for element in self.sequence if element in monitors]
        self.correctors = [element for element in self.sequence if element in correctors]
        self.corrs = self.correctors
        self.bpm_indexes = [index for index, string in enumerate(sequence) if string in self.bpms]

        # Bunch current monitors
        self.ict_names = self.bpms + [self.chosen_ict]

        #self.lattice = self.tracking_interface.lattice
        #self.start = self.tracking_interface.start
        #self.end = self.tracking_interface.end
        self.bg_shots = int(bg_shots)
        self.bpm_readout_names = monitors.copy()

    def _get_charge_reference(self):
        value = self.get_icts(names=self.chosen_ict)
        return value["charge"]

    def _get_elements_positions_show_beamline(self, names=None):
        if isinstance(names, str):
            names = [names]
        all_names = [name for name in self.tracking_interface.get_sequence() if names is None or name in names]

        return {
            "names": all_names,
            "S": np.array([self._get_tracking_element(name).get_S("entrance") for name in all_names], dtype=float),
        }

    @staticmethod
    def make_safe_float(value, default=np.nan):  # so even if japc address returns none, empty array or whatever, interface still works
        try:
            if value is None:
                return float(default)
            arr = np.asarray(value)
            if arr.size == 0:
                return float(default)
            return float(arr.flat[0])
        except Exception:
            return float(default)

    def get_beam_settings(self):
        return {
            "Text": float(tango.AttributeProxy('infra/t-whist/bunchclock/Text').read().w_value),
            "pulsev": float(tango.AttributeProxy('elin/beam/run/pulsev').read().w_value),
        }

    def change_intensity(self, delta=-1):
        delta = self.intensity_delta if delta is None else delta
        if delta is None or not np.isfinite(delta):
            raise ValueError("Set intensity_delta in V.")
        attribute = tango.AttributeProxy('elin/beam/run/pulsev')
        if self.initial_gridv is None:
            self.initial_gridv = float(attribute.read().w_value)
        target = self.initial_gridv+delta
        self._set_and_verify(lambda: attribute.write(target), lambda: attribute.read().w_value, target, description= "Grid voltage")

    def reset_intensity(self):
        if self.initial_gridv is not None:
            attribute = tango.AttributeProxy('elin/beam/run/pulsev')
            target = self.initial_gridv
            self._set_and_verify(lambda: attribute.write(target), lambda: attribute.read().w_value, target, description="Grid voltage")

    def change_energy(self, delta=None):
        delta = self.energy_delta if delta is None else delta
        if delta is None or not np.isfinite(delta) or abs(delta)>=5: # limit to 10ms Text variation
            raise ValueError("Delta value is wrong.")
        "Change energy with extraction time in the booster"
        "which is good because the dipoles ramp in TL2 and SY (booster) are synchronised"
        df = pd.read_csv("/machfs/kandre/rips_dipole_ramp.csv")
        timing = pd.read_csv("/opt/infra_rw/settings/Timing/operation_long.ts", header=None, names=["name", "current"], skiprows=6, sep=": ", engine="python")
        syext = pd.read_csv("/opt/infra_rw/settings/syext/operation.ts", header=None, names=["name", "current"], skiprows=6, sep=": ", engine="python")
        Eext = np.interp(144.2 - delta, df["step"]/1599*250, df["Dipole Output Current [Amp]"]) * 4.05776e-3
        print(rf"For a dt = {-delta:.2f} ms, the extraction energy is ~ {Eext:.3f} GeV eq. to dpp = {1e2*(1-Eext/6):.2f}%")
        factor =  1 - (1-Eext/6)
        self.log(f"Change energy by {delta} which change the energy to {Eext:.2f}GeV ({1e2*(1-Eext/6):.2f}%)..")
        try:
            # commented to not change the machine by mistake
            tango.AttributeProxy('infra/t-whist/bunchclock/Text').write((timing[timing["name"]=="infra/t-whist/bunchclock/Text"]["current"].values[0] + delta*1e3)*1e-6)
            tango.AttributeProxy('sy/ps-ke/1/current').write(syext[syext["name"]=="sy/ps-ke/1/current"]["current"].values[0] * factor)
            tango.AttributeProxy('sy/ps-bumper/1/current').write(syext[syext["name"]=="sy/ps-bumper/1/current"]["current"].values[0]* factor)
            tango.AttributeProxy('sy/ps-se/1/current').write(syext[syext["name"]=="sy/ps-se/1/current"]["current"].values[0]* factor)
            tango.AttributeProxy('sy/ps-bumper/2/current').write(syext[syext["name"]=="sy/ps-bumper/2/current"]["current"].values[0]* factor)
            tango.AttributeProxy('sy/ps-se/2-1/current').write(syext[syext["name"]=="sy/ps-se/2-1/current"]["current"].values[0]* factor)
            tango.AttributeProxy('sy/ps-bumper/3/current').write(syext[syext["name"]=="sy/ps-bumper/3/current"]["current"].values[0]* factor)
            time.sleep(self.settle_time)
        except Exception as e:
            self.log(f"ABORT : change_energy failed - {e}")
            self.reset_energy()
            raise
        return float(factor - 1)

    def reset_energy(self):
        "Reset extraction time to the nominal value from operation_long.ts"
        timing = pd.read_csv("/opt/infra_rw/settings/Timing/operation_long.ts", header=None, names=["name", "current"], skiprows=6, sep=": ", engine="python")
        syext = pd.read_csv("/opt/infra_rw/settings/syext/operation.ts", header=None, names=["name", "current"], skiprows=6, sep=": ", engine="python")
        self.log("Reset energy, with initial Text..")
        # commented to not change the machine by mistake
        tango.AttributeProxy('infra/t-whist/bunchclock/Text').write(timing[timing["name"]=="infra/t-whist/bunchclock/Text"]["current"].values[0]*1e-6)
        tango.AttributeProxy('sy/ps-ke/1/current').write(syext[syext["name"]=="sy/ps-ke/1/current"]["current"].values[0])
        tango.AttributeProxy('sy/ps-bumper/1/current').write(syext[syext["name"]=="sy/ps-bumper/1/current"]["current"].values[0])
        tango.AttributeProxy('sy/ps-se/1/current').write(syext[syext["name"]=="sy/ps-se/1/current"]["current"].values[0])
        tango.AttributeProxy('sy/ps-bumper/2/current').write(syext[syext["name"]=="sy/ps-bumper/2/current"]["current"].values[0])
        tango.AttributeProxy('sy/ps-se/2-1/current').write(syext[syext["name"]=="sy/ps-se/2-1/current"]["current"].values[0])
        tango.AttributeProxy('sy/ps-bumper/3/current').write(syext[syext["name"]=="sy/ps-bumper/3/current"]["current"].values[0])
        time.sleep(self.settle_time)
        self.log(f"Write {timing[timing['name']=='infra/t-whist/bunchclock/Text']['current'].values[0]*1e-6} to Text and {tango.AttributeProxy('infra/t-whist/bunchclock/Text').read().w_value} is read")

    def get_sequence(self):
        return self.sequence

    def get_hcorrectors_names(self):
        return [element for element in self.correctors if element.startswith("COR.ch")]

    def get_vcorrectors_names(self):
        return [element for element in self.correctors if element.startswith("COR.cv")]

    def get_elements_indices(self, names):
        if isinstance(names, str):
            names = [names]
        name_to_index = {string: index for index, string in enumerate(self.sequence)}
        return [name_to_index.get(name, np.nan) for name in names]

    def read_charge(self):
        "Read striplines charge and ICT for integrated charge"
        self.log("Reading ICT's... (charge from striplines, integrated charge from ict)")
        return {
            "names": self.bpms,
            "charge": tango.DeviceProxy('tl2/d-bpm/all').charge,
            "integrated_charge": tango.DeviceProxy('tl2/d-ct/ict-1').totalcharge,
        }

    def get_icts(self, names=None):
        selected_names = self.ict_names if names is None else ([names] if isinstance(names, str) else list(names))
        charges = None
        charge = []
        for name in selected_names:
            if name == self.chosen_ict:
                value = tango.DeviceProxy(self.chosen_ict).totalcharge
            else:
                index = self.bpm_readout_names.index(name)
                if charges is None:
                    charges = np.asarray(tango.DeviceProxy('tl2/d-bpm/all').charge, dtype=float)
                value = charges[index]
            charge.append(self.make_safe_float(value))
        return {"names": list(selected_names), "charge": np.asarray(charge, dtype=float)}

    def get_bpms(self, names=None):
        self.log('Reading bpms...')
        selected_names = self.bpms if names is None else ([names] if isinstance(names, str) else list(names))
        indices = [self.bpm_readout_names.index(name) for name in selected_names]
        data = {key: np.empty((self.nsamples, len(selected_names)), dtype=float) for key in ("x", "y", "tmit")}
        device = tango.DeviceProxy('tl2/d-bpm/all')
        attributes = {
            "x": "x_position",
            "y": "z_position",
            "tmit": "charge",
        }
        for sample in range(self.nsamples):
            for key, attribute in attributes.items():
                values = np.asarray(getattr(device, attribute), dtype=float)
                if values.shape != (len(self.bpm_readout_names),):
                    raise ValueError(f"{attribute}: unexpected BPM array shape {values.shape}") # 3 samples,
                data[key][sample] = values[indices]

            if sample < self.nsamples - 1:
                time.sleep(1.0)
        return {"names": selected_names, **data}

    def set_correctors(self, names, corr_vals):
        if isinstance(names, str):
            names = [names]
        if not isinstance(corr_vals, (list, tuple, np.ndarray)):
            corr_vals = [corr_vals]
        if len(names) != len(corr_vals):
            raise ValueError("len(names) != len(corr_vals)")
        for corrector, corr_val in zip(names, corr_vals):
            device_name = corrector.rsplit(".", 1)[-1].lower()
            tango.AttributeProxy(f'tl2/ps-c1/{device_name}/current').write(float(corr_val))
        return self._wait_for_corrector_readbacks(names, corr_vals)

    # def read_vlm(self):
    #     "Read VLMs pixels 488x648"
    #     fig, ax = plt.subplots(1, 4, figsize=(16, 6))
    #     a, b = [], []
    #     for idx, d in enumerate([1,2,4,5]):
    #         ax[idx].imshow(tango.DeviceProxy(f'tl2/d-ccd/dipole{d}').Image, aspect='equal', origin='lower', cmap="rainbow")
    #         ax[idx].set_title(f"VLM of dipole {d}")
    #         a.append(f"Dipole{d}"); b.append(tango.DeviceProxy(f'tl2/d-ccd/dipole{d}').Image)
    #     return {
    #         "names": a,
    #         "2d_array": b
    #     }

    @staticmethod
    def _read_settings(path):
        settings = {}
        for line in Path(path).read_text().splitlines()[6:]:
            if ": " in line:
                name, value = line.split(": ", 1)
                settings[name.strip()] = value.strip()
        return settings

    def reset_quadrupoles(self):
        settings = self._read_settings("/opt/infra_rw/settings/tl2/operation.ts")
        for name in self.quadrupoles:
            device_name = name.rsplit(".", 1)[-1].lower()
            attribute = f"tl2/ps/{device_name}/current"
            current = float(settings[attribute])
            tango.AttributeProxy(attribute).write(current)
        time.sleep(self.settle_time)

    def reset_correctors(self):
        tl2 = self._read_settings("/opt/infra_rw/settings/tl2/operation.ts")
        srinj = self._read_settings("/opt/infra_rw/settings/srinj-slowk/operation_restart.ts")
        for name in self.correctors:
            device_name = name.rsplit(".", 1)[-1].lower()
            attribute = f"tl2/ps-c1/{device_name}/current"
            settings = srinj if device_name in ("cv8", "cv9") else tl2
            current = float(settings[attribute])
            tango.AttributeProxy(attribute).write(current)
        time.sleep(self.settle_time)

    def get_correctors(self, names=None):
        self.log("Reading correctors' strengths...")
        selected_names = self.corrs if names is None else ([names] if isinstance(names, str) else list(names))

        bdes, bact = [], []
        for corrector in selected_names:
            device_name = corrector.rsplit(".", 1)[-1].lower()
            attribute = tango.AttributeProxy(f"tl2/ps-c1/{device_name}/current")
            reading = attribute.read()
            bdes.append(float(reading.w_value))
            bact.append(self.make_safe_float(reading.value))

        return {
            "names": list(selected_names),
            "bdes": np.asarray(bdes, dtype=float),
            "bact": np.asarray(bact, dtype=float),
        }

    def get_quadrupoles(self, names=None):
        selected_names = self.quadrupoles if names is None else ([names] if isinstance(names, str) else list(names))
        bdes, bact = [], []
        for name in selected_names:
            device_name = name.rsplit(".", 1)[-1].lower()
            reading = tango.AttributeProxy(f"tl2/ps/{device_name}/current").read()
            bdes.append(float(reading.w_value))
            bact.append(self.make_safe_float(reading.value))
        return {
            "names": list(selected_names),
            "bdes": np.asarray(bdes, dtype=float),
            "bact": np.asarray(bact, dtype=float),
            "value_unit": "A",
        }

    def set_quadrupoles(self, names, values=None):
        "Set quadrupole currents to values"
        if names == "all":
            names = self.quadrupoles
        elif isinstance(names, str):
            print(f"change {names} into {[names]}")
            names = [names]
        if not isinstance(values, (list, tuple, np.ndarray)):
            print(f"change {values} into {[values]}")
            values = [values]
        if len(names) != len(values):
            raise ValueError("len(names) != len(values)")
        for name, value in zip(names, values):
            device_name = name.rsplit(".", 1)[-1].lower()
            tango.AttributeProxy(f'tl2/ps/{device_name}/current').write(float(value))
        return self._wait_for_quadrupole_readbacks(names, values)

    def restore_quadrupoles_state(self, state):
        quadrupoles = state.get_quadrupoles()
        if quadrupoles.get("value_unit") != "A":
            raise ValueError("The application is trying to restore quadrupoles to a different unit than an Ampere.")
        super().restore_quadrupoles_state(state)

    def log_messages(self, console):
        self.log = console or print
                                                                                            # 50 ms
    def _wait_for_corrector_readbacks(self, names, targets, tolerance=0.1, timeout=10.0, acq_interval=0.05):
        targets = {name: float(target) for name, target in zip(names, targets)}
        pending = set(targets)
        last_values = {name: np.nan for name in targets}
        deadline = time.perf_counter() + timeout

        while pending and time.perf_counter() < deadline:
            for corrector in tuple(pending):
                try:
                    device_name = corrector.rsplit(".", 1)[-1].lower() # from COR.ch1 to ch1
                    reading = tango.AttributeProxy(f"tl2/ps-c1/{device_name}/current").read()
                    value = self.make_safe_float(reading.value)
                except Exception:
                    value = np.nan
                last_values[corrector] = value
                if np.isfinite(value) and abs(value - targets[corrector]) <= tolerance:
                    pending.remove(corrector)
            if pending:
                time.sleep(acq_interval)

        for corrector in pending:
            self.log(
                f"Warning: {corrector} did not reach target {targets[corrector]:.6g} "
                f"within {timeout:.2f}s. Last readback = {last_values[corrector]:.6g}"
            )
        return not pending

    def _wait_for_quadrupole_readbacks(self, names, targets, tolerance=0.1, timeout=10.0, acq_interval=0.05):
        targets = {name: float(target) for name, target in zip(names, targets)}
        pending = set(targets)
        last_values = {name: np.nan for name in targets}
        deadline = time.perf_counter() + timeout

        while pending and time.perf_counter() < deadline:
            for quadrupole in tuple(pending):
                try:
                    device_name = quadrupole.rsplit(".", 1)[-1].lower()
                    reading = tango.AttributeProxy(f"tl2/ps/{device_name}/current").read()
                    value = self.make_safe_float(reading.value)
                except Exception:
                    value = np.nan
                last_values[quadrupole] = value
                if np.isfinite(value) and abs(value - targets[quadrupole]) <= tolerance:
                    pending.remove(quadrupole)
            if pending:
                time.sleep(acq_interval)

        for quadrupole in pending:
            self.log(
                f"Warning: {quadrupole} did not reach target current {targets[quadrupole]:.6g} "
                f"within {timeout:.2f}s. Last readback = {last_values[quadrupole]:.6g}"
            )
        return not pending
