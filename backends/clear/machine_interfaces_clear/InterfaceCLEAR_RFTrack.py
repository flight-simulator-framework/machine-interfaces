import numpy as np
import RF_Track as rft
from scipy.optimize import minimize
from machine_interfaces.Backend.State import State
from machine_interfaces.Interfaces.AbstractMachineInterface import AbstractMachineInterface
from machine_interfaces.Backend.EnergyChangeMethod import EnergyChangeMethod
from machine_interfaces_clear.clear_lattice import load_clear_lattice

CORRECTOR_CALIBRATION_TMM_PER_A = {
    'CA.DHG0130': -0.0623, 'CA.DVG0130': -0.0623, 'CA.DHG0225': -0.0623, 'CA.DVG0225': -0.0623,
    'CA.DHG0245': -0.1930, 'CA.DVG0245': -0.1930, 'CA.DHG0265': -0.1913, 'CA.DVG0265': -0.2067,
    'CA.DHG0320': -0.1936, 'CA.DVG0320': -0.1838, 'CA.DHG0385': -0.2007, 'CA.DVG0385': -0.1815,
    'CA.DHJ0540': -0.4039, 'CA.DVJ0540': -0.3378, 'CA.DHJ0590': -0.4144, 'CA.DVJ0590': -0.3592,
    'CA.DHJ0710': -0.4353, 'CA.DVJ0710': -0.3656, 'CA.DHJ0780': -0.4293, 'CA.DVJ0780': -0.3815,
    'CA.DHJ0840': -0.4803, 'CA.DVJ0840': -0.4261,
}
QUADRUPOLE_OFFSETS_MM = {
    'CA.QFD0350': (0.10, 0.04), 'CA.QDD0355': (-0.59, -1.09), 'CA.QFD0360': (1.29, -0.18),
    'CA.QFD0510': (0.25, 1.27), 'CA.QDD0515': (-0.42, 0.42), 'CA.QFD0520': (0.03, -3.11),
    'CA.QFD0760': (-0.23, -0.10), 'CA.QDD0765': (-0.11, -1.40), 'CA.QFD0770': (0.30, 0.22),
}
BPM_OFFSETS_MM = {
    'CA.BPM0530': (1.80, -8.93), 'CA.BPM0595': (2.92, -5.11), 'CA.BPM0690': (0.18, -5.91),
    'CA.BPM0820': (-2.38, -8.26), 'CA.BPM0890': (-0.77, -9.48),
}
INCOMING_BEAM = {'dx_mm': 0.023, 'dy_mm': -0.618, 'pitch_mrad': 0.165, 'yaw_mrad': -0.102}
DEFAULT_CORRECTORS_A = {
    'CA.DHG0265': 2.83, 'CA.DVG0265': -1.21, 'CA.DHG0320': -1.29, 'CA.DVG0320': 0.42, 'CA.DHG0385': -1.82,
    'CA.DVG0385': 0.77, 'CA.DHJ0540': 1.83, 'CA.DVJ0540': 2.04, 'CA.DHJ0590': -1.54, 'CA.DVJ0590': 3.80,
}

class InterfaceCLEAR_RFTrack(AbstractMachineInterface):
    def get_name(self):
        return 'CLEAR_RFT'

    def get_ITF(self, I):
        return 1.29404711e-2 - 2.59458259e-07 * I  # T/A

    def get_grad(self, I, Lquad=0.226):
        G_0 = I * self.get_ITF(I) / Lquad  # T/m
        return G_0

    @staticmethod
    def _gradient_sign(quadrupole_name):
        if "QFD" in quadrupole_name:
            return -1.0
        if "QDD" in quadrupole_name:
            return 1.0

    def get_current_from_grad(self, gradient, Lquad=0.226):
        integrated_gradient = float(gradient) * float(Lquad)
        a = float(self.get_ITF(0.0))
        b = float(a - self.get_ITF(1.0))
        if np.isclose(b, 0.0):
            return integrated_gradient / a
        discriminant = a * a - 4.0 * b * integrated_gradient
        if discriminant < 0.0: raise ValueError(f"Gradient {gradient:.6g} T/m is outside the calibration range")
        return float((a - np.sqrt(discriminant)) / (2.0 * b))

    @staticmethod
    def _replace_btv_monitors_with_screens(lattice):
        for element in list(lattice['*']):
            if not element.get_name().startswith("CA.BTV"):
                continue
            if hasattr(element, "get_bunch"):
                continue
            screen = rft.Screen()
            screen.set_name(element.get_name())
            screen.set_length(element.get_length())
            element.replace_with(screen)
                                                                                                # from real data we estimate 50um
    def __init__(self, population=300 * rft.pC, jitter=0.05, bpm_resolution=0.05, nsamples=1, nparticles=1000, machine_offsets=True):
        self.sigmaCut = 4.0
        self.Pref = 198 # MeV/c
        self.Q=-1
        self.population = population
        self.jitter = jitter
        self.nsamples = nsamples
        self.nparticles = nparticles
        self.electronmass=rft.electronmass
        self.is_simulation = True
        self.lattice = load_clear_lattice()
        for element in self.lattice["*ICT*"]:
            drift = rft.Drift(element.get_length())
            drift.set_name(element.get_name())
            element.replace_with(drift)
        for element in self.lattice["*SCT*"]:
            drift = rft.Drift(element.get_length())
            drift.set_name(element.get_name())
            element.replace_with(drift)
        self._replace_btv_monitors_with_screens(self.lattice)
        elements_in_lattice = list(self.lattice['*'])
        self.sequence = [element.get_name() for element in elements_in_lattice]
        self.start = self.sequence[0]
        self.end = self.sequence[-1]
        self.lattice.set_bpm_resolution(bpm_resolution)
        self.lattice.set_tt_nsteps(0)
        self.log = print
        self.bpms = [element.get_name() for element in self.lattice.get_bpms()]
        self.corrs = list(CORRECTOR_CALIBRATION_TMM_PER_A)
        self.screens = [element.get_name() for element in self.lattice.get_screens()]
        self.quadrupoles = [element.get_name() for element in self.lattice.get_quadrupoles()]
        self.sextupoles = []
        self.dfs_test_energy = 0.92 #0.963
        self.wfs_test_charge = 0.90
        self.__setup_beam0()
        self.lattice.align_elements()
        self.machine_offsets = machine_offsets
        self.bpm_offsets = BPM_OFFSETS_MM if machine_offsets else {}
        self.incoming_beam = dict(INCOMING_BEAM) if machine_offsets else dict.fromkeys(INCOMING_BEAM, 0.0)
        if machine_offsets:
            for name, (dx, dy) in QUADRUPOLE_OFFSETS_MM.items():
                self.lattice[name].set_offsets(dx * 1e-3, dy * 1e-3, 0.0, 0.0, 0.0, 0.0, "center")
        else:
            '''Uncomment lines below to scatter elements in the lattice.'''
            self.lattice.scatter_elements('bpm', 0.100, 0.100, 0, 0, 0, 0, 'center')
            self.lattice.scatter_elements('quadrupole', 0.100, 0.100, 0, 0, 0, 0, 'center')
        self.freq=2.997e9
        self.nr_quad=11
        self.Lquad=0.226 #magnetic length of the quadrupole in [m]
        self.nominal_K=0.7752883624676146 #3.35  # 1/m
        self.machine_name = "CLEAR"
        self.chosen_ict = "CA.BPM0890"
        # qfd520 = self.lattice["CA.QFD0520"]
        #                     # dx   # dy   #dz  # roll  # pitch # yaw
        # qfd520.set_offsets(0.0, 0.0, 0.0, 0, 0.0, 0.0, "center")

        self.aperture = 20e-3
        for element in self.lattice['*']:
            element.set_aperture(self.aperture, self.aperture, "circular") # in reality, CLEAR has 40mm, or 30-20mm diameter

        '''test of bpm invertion'''
        self.invert_bpm = False
        defaults = DEFAULT_CORRECTORS_A if machine_offsets else {}
        self.set_correctors(list(defaults), list(defaults.values()))
        self.quadrupole_scaling_factor = 0.5
        self.initial_quad_currents = self.get_quadrupoles()["bdes"].copy()

    def __setup_beam0(self):
        T = rft.Bunch6d_twiss()
        T.emitt_x = 12.7000 # mm.mrad normalised emittance
        T.emitt_y = 4.3400   # mm.mrad
        T.beta_x = 46.1766 # m
        T.beta_y = 109.1117  # m; back-propagated from QFD350 entrance
        T.alpha_x = 1.3126
        T.alpha_y = 7.2462
        T.sigma_t = 0#10*rft.ps # mm/c
        T.sigma_pt = 0#10 # permille
        T.mean_xp = 0.0
        T.mean_yp = 0.0
        sigmaCut = 5.0
        self.P0 = rft.Bunch6d (rft.electronmass, self.population,  self.Q, np.array([0.0, 0.0, 0.0, 0.0, 0.0, self.Pref]))
        self.B0 = rft.Bunch6d_QR(rft.electronmass, self.population, self.Q, self.Pref, T, self.nparticles, sigmaCut) # reference bunch
        self._beam_mode = "nominal"

    def __setup_beam1(self):
        # Beam for DFS - Reduced energy
        Pref = self.dfs_test_energy * self.Pref
        T = rft.Bunch6d_twiss()

        T.emitt_x = 12.7000 # mm.mrad normalised emittance
        T.emitt_y = 4.3400   # mm.mrad
        T.beta_x = 46.244900 # m
        T.beta_y = 109.143468  # m; back-propagated from QFD350 entrance
        T.alpha_x = 1.314308
        T.alpha_y = 7.248155

        T.sigma_t = 0#10*rft.ps # mm/c
        T.sigma_pt = 0#10 # permille
        T.mean_xp=0.0
        T.mean_yp=0.0
        self.B0 = rft.Bunch6d_QR(rft.electronmass, self.population, self.Q, Pref, T, self.nparticles, self.sigmaCut)
        self.P0 = rft.Bunch6d (rft.electronmass, self.population,  self.Q, np.array([ 0.0, 0.0, 0.0, 0.0, 0.0, Pref]))

    def __setup_beam2(self):
        # Beam for WFS - Reduced bunch charge
        population = self.wfs_test_charge * self.population
        T = rft.Bunch6d_twiss()

        T.emitt_x = 12.7000 # mm.mrad normalised emittance
        T.emitt_y = 4.3400   # mm.mrad
        T.beta_x = 46.244900 # m
        T.beta_y = 109.143468  # m; back-propagated from QFD350 entrance
        T.alpha_x = 1.314308
        T.alpha_y = 7.248155

        T.sigma_t = 0#10*rft.ps # mm/c
        T.sigma_pt = 0#10 # permille
        T.mean_xp=0.0
        T.mean_yp=0.0
        self.B0 = rft.Bunch6d_QR(rft.electronmass, population, self.Q, self.Pref, T, self.nparticles, self.sigmaCut)
        self.P0 = rft.Bunch6d (rft.electronmass, population,  self.Q, np.array([ 0.0, 0.0, 0.0, 0.0, 0.0, self.Pref]))

    def match_screen_name(self, name, candidates):
        name = str(name)
        candidates = [str(candidate) for candidate in candidates]
        matched = super().match_screen_name(name, candidates)
        if matched is not None:
            return matched
        stripped = name.rstrip("LH")
        for candidate in candidates:
            if candidate.rstrip("LH") == stripped:
                return candidate
        return None

    def _model_screen_names(self, screens):
        if screens is None:
            return None
        single = isinstance(screens, str)
        names = [screens] if single else list(screens)
        mapped = []
        for name in names:
            name = str(name)
            mapped.append(name if name in self.screens else name.rstrip("LH"))
        return mapped[0] if single else mapped

    def get_screens(self, names=None):
        if isinstance(names, str): names = [names]
        names = self._model_screen_names(names)
        hpixel = 0.001
        vpixel = 0.001
        selected_screens = [screen for screen in self.screens if names is None or screen in names]
        hpixel_list = []
        vpixel_list = []
        xb_list = []
        yb_list = []
        sigx_list = []
        sigy_list = []
        sigxy_list = []
        sum_list = []
        images = []
        hedges_all = []
        vedges_all = []
        screen_names = []
        s_list = []

        for screen_name in selected_screens:
            screen = self.lattice[screen_name]
            screen_names.append(screen_name)
            s_list.append(float(screen.get_S("entrance")))
            hpixel_list.append(hpixel)
            vpixel_list.append(vpixel)
            bunch = screen.get_bunch()
            m = bunch.get_phase_space('%x %y')
            x_mean = float(np.mean(m[:, 0]))
            y_mean = float(np.mean(m[:, 1]))
            x_centered = m[:, 0] - x_mean # deviation from center of the beam; if the beam centroid changes, this will stay the same
            y_centered = m[:, 1] - y_mean # it has information about the tilt of ellipse

            xb_list.append(float(np.mean(m[:, 0])))
            yb_list.append(float(np.mean(m[:, 1])))
            sigx_list.append(float(np.std(m[:, 0])))
            sigy_list.append(float(np.std(m[:, 1])))
            sigxy_list.append(float(np.mean(x_centered * y_centered)))
            sum_list.append(float(len(m[:, 0])))

            nx = int(np.ceil(np.ptp(m[:, 0]) / hpixel)) if np.ptp(m[:, 0]) > 0 else 1
            ny = int(np.ceil(np.ptp(m[:, 1]) / vpixel)) if np.ptp(m[:, 1]) > 0 else 1
            nx = int(np.clip(nx, 10, 400))
            ny = int(np.clip(ny, 10, 400))

            image, hedges, vedges = np.histogram2d(m[:, 0], m[:, 1], bins=(nx, ny))
            images.append(image)
            hedges_all.append(hedges)
            vedges_all.append(vedges)

        screens = {
            "names": screen_names,
            "hpixel": np.array(hpixel_list, dtype=float),
            "vpixel": np.array(vpixel_list, dtype=float),
            "x": np.array(xb_list, dtype=float),
            "y": np.array(yb_list, dtype=float),
            "sigx": np.array(sigx_list, dtype=float),
            "sigy": np.array(sigy_list, dtype=float),
            "sigxy": np.array(sigxy_list, dtype=float),
            "sum": np.array(sum_list, dtype=float),
            "hedges": hedges_all,
            "vedges": vedges_all,
            "images": images,
            "S": np.array(s_list, dtype=float),
        }

        return screens

    def get_emittance_at_screens(self, names=None):
        if isinstance(names, str): names = [names]
        names = self._model_screen_names(names)
        selected_screens = [screen for screen in self.screens if names is None or screen in names]
        fields = ("emitt_x", "emitt_y", "beta_x", "beta_y", "alpha_x", "alpha_y", "sigma_x", "sigma_y")
        screen_names = []
        s_list = []
        values = {field: [] for field in fields}

        for screen_name in selected_screens:
            screen = self.lattice[screen_name]
            if isinstance(screen, list):
                screen = screen[-1]
            bunch = screen.get_bunch()
            if bunch is None:
                continue
            info = bunch.get_info()
            screen_names.append(screen_name)
            s_list.append(float(screen.get_S("entrance")))
            for field in fields:
                values[field].append(float(getattr(info, field, np.nan)))

        emittance = {"names": screen_names, "S": np.array(s_list, dtype=float)}
        emittance.update({field: np.array(values[field], dtype=float) for field in fields})
        return emittance

    def __track_bunch(self):
        I0 = self.B0.get_info()
        dx, dy, pitch, yaw = np.add(self._jitter_offsets(I0), [self.incoming_beam[k] for k in ("dx_mm", "dy_mm", "pitch_mrad", "yaw_mrad")])
        dz, dt, roll = 0.0, 0.0, 0.0
        B0_offset = self.B0.displaced(dx, dy, dz, dt, roll, pitch, yaw)
        B1=self.lattice.track(B0_offset)
        I = B0_offset.get_info()

    def get_beam_factors(self):
        gamma_rel = np.sqrt((self.Pref / self.electronmass) ** 2 + 1.0)
        beta_rel = np.sqrt(1.0 - 1.0 / gamma_rel ** 2)
        beta_gamma = gamma_rel * beta_rel
        if not np.isfinite(beta_gamma) or beta_gamma <= 0:
            raise RuntimeError("Invalid beam factors")
        return gamma_rel, beta_rel, beta_gamma

    def scale_quadrupoles(self, scale=None):
        if scale is None:
            scale = self.quadrupole_scaling_factor
        scale = float(scale)
        if not np.isfinite(scale) or scale <= 0:
            raise ValueError("Quadrupole scaling factor must be finite and positive.")
        scaled_optics_currents = self.initial_quad_currents * scale
        self.set_quadrupoles(self.quadrupoles, scaled_optics_currents)

    def change_energy(self, method = EnergyChangeMethod.DEFAULT, which_method = 1):
        if method == EnergyChangeMethod.DEFAULT:
            self.__setup_beam1()
            self.__track_bunch()
            self._beam_mode = "energy_changed"
            dP_P = self.dfs_test_energy - 1.0
            return dP_P
        elif method == EnergyChangeMethod.QUADRUPOLE_SCALING:
            self.scale_quadrupoles()
            return 0.0
        elif method == EnergyChangeMethod.BOTH:
            if which_method == 1:
                return self.change_energy(method=EnergyChangeMethod.DEFAULT)
            if which_method == 2:
                self.scale_quadrupoles()
                return 0.0
            return

    def reset_energy(self, method = EnergyChangeMethod.DEFAULT, *, which_method=1):
        if method == EnergyChangeMethod.DEFAULT:
            self.__setup_beam0()
            self.__track_bunch()
            self._beam_mode = "nominal"
        elif method == EnergyChangeMethod.QUADRUPOLE_SCALING:
            return self.scale_quadrupoles(scale = 1.0)
        elif method == EnergyChangeMethod.BOTH:
            if which_method == 1:
                return self.reset_energy(method=EnergyChangeMethod.DEFAULT)
            if which_method == 2:
                return self.scale_quadrupoles(scale=1.0)
            return

    def change_intensity(self): #reduced charge
        self.__setup_beam2()
        self.__track_bunch()
        self._beam_mode = "intensity_changed"

    def reset_intensity(self):
        self.__setup_beam0()
        self.__track_bunch()
        self._beam_mode = "nominal"

    def _get_elements_positions(self, names=None):
        if isinstance(names, str):
            names = [names]
        selected = [name for name in self.sequence if names is None or name in names]
        return {
            "names": selected,
            "S": np.array([self.lattice[name].get_S("entrance") for name in selected], dtype=float),
            "L": np.array([self.lattice[name].get_length() for name in selected], dtype=float),
        }

    def get_sequence(self):
        return [name for element in self.sequence for name in ((element, element.replace("DH", "DV")) if element in self.corrs else (element,))]

    def _bpm_reading(self, bpm_name):
        return np.subtract(self.lattice[bpm_name].get_reading()[:2], self.bpm_offsets.get(bpm_name, (0.0, 0.0)))

    @staticmethod
    def _corrector_element(name):
        return name.replace("DVG", "DHG").replace("DVJ", "DHJ"), int("DV" in name)

    def get_hcorrectors_names(self):
        return [string for string in self.corrs if "DH" in string]

    def get_vcorrectors_names(self):
        return [string for string in self.corrs if "DV" in string]

    def get_elements_position(self,names):
        return [index for index, string in enumerate(self.sequence) if string in names]

    def get_icts(self, names=None):
        self.log("Reading ict's...")
        icts = {
            "names": self.bpms,
            "charge": np.array([bpm.get_total_charge() for bpm in self.lattice.get_bpms()])
        }

        if isinstance(names, str):
            names = [names]
        if names is not None:
            idx = [list(icts["names"]).index(s) for s in names if s in icts["names"]]  # requested order, like the real machine
            icts = {
                "names": [icts["names"][i] for i in idx],
                "charge": np.asarray(icts["charge"])[idx],
            }

        return icts

    def get_correctors(self,names=None):
        #self.log("Reading correctors' strengths...")
        bdes = np.zeros(len(self.corrs))
        for i,corrector in enumerate(self.corrs):
            element, plane = self._corrector_element(corrector)
            bdes[i] = self.lattice[element].get_strength()[plane] / CORRECTOR_CALIBRATION_TMM_PER_A[corrector]
        correctors = { "names": self.corrs, "bdes": bdes, "bact": bdes }

        if isinstance(names, str):
            names = [names]
        if names is not None:
            idx = [list(correctors["names"]).index(s) for s in names if s in correctors["names"]]  # requested order, like the real machine
            correctors = {
                "names": [correctors["names"][i] for i in idx],
                "bdes": np.asarray(correctors["bdes"])[idx],
                "bact": np.asarray(correctors["bact"])[idx],
            }

        return correctors

    def get_bpms(self, names=None):
        self.log('Reading bpms...')
        x = np.zeros((self.nsamples, len(self.bpms)))
        y = np.zeros_like(x)
        tmit = np.zeros_like(x)

        for i in range(self.nsamples):
            if self.jitter:
                self.__track_bunch()
            for j, bpm_name in enumerate(self.bpms):
                bpm = self.lattice[bpm_name]
                reading = self._bpm_reading(bpm_name)
                '''test of inverted bpm'''
                sign = -1.0 if (self.invert_bpm and bpm_name == "CA.BPM0890") else 1.0

                x[i, j] = sign * reading[0]
                y[i, j] = sign * reading[1]
                # x[i, j] = reading[0]
                # y[i, j] = reading[1]
                tmit[i, j] = bpm.get_total_charge()

        bpms = {"names": self.bpms, "x": x, "y": y, "tmit": tmit}

        if isinstance(names, str):
            names = [names]
        if names is not None:
            idx = [list(bpms["names"]).index(s) for s in names if s in bpms["names"]]  # requested order, like the real machine
            bpms = {
                "names": [bpms["names"][i] for i in idx],
                "x": np.asarray(bpms["x"])[:, idx],
                "y": np.asarray(bpms["y"])[:, idx],
                "tmit": np.asarray(bpms["tmit"])[:, idx],
            }

        return bpms

    def set_correctors(self, names, corr_vals):
        if isinstance(names, str):
            names = [names]
        if not isinstance(corr_vals, (list, tuple, np.ndarray)):
            corr_vals = [corr_vals]
        for corr, val in zip(names, corr_vals):
            element, plane = self._corrector_element(corr)
            strength = list(self.lattice[element].get_strength())
            strength[plane] = val * CORRECTOR_CALIBRATION_TMM_PER_A[corr]
            self.lattice[element].set_strength(*strength)
        self.__track_bunch()

    def vary_correctors(self, names, corr_vals):
        if isinstance(names, str):
            names = [names]
        if not isinstance(corr_vals, (list, tuple, np.ndarray)):
            corr_vals = [corr_vals]
        for corr, val in zip(names, corr_vals):
            element, plane = self._corrector_element(corr)
            delta = [0.0, 0.0]
            delta[plane] = val * CORRECTOR_CALIBRATION_TMM_PER_A[corr]
            self.lattice[element].vary_strength(*delta)
        self.__track_bunch()

    def load_machine_state(self, state):
        quadrupoles = state.get_quadrupoles()
        currents = quadrupoles["bdes"] if quadrupoles.get("value_unit") == "A" else quadrupoles.get("ides", quadrupoles["bdes"])
        quads = [(name, current) for name, current in zip(quadrupoles["names"], np.ravel(currents)) if name in self.quadrupoles]
        self.set_quadrupoles([name for name, _ in quads], [current for _, current in quads], track=False)
        self.initial_quad_currents = self.get_quadrupoles()["bdes"].copy()
        correctors = state.get_correctors()
        corrs = [(name, value) for name, value in zip(correctors["names"], np.ravel(correctors["bdes"])) if name in self.corrs]
        self.set_correctors([name for name, _ in corrs], [value for _, value in corrs])
        measured = state.get_orbit(self.bpms)
        measured = np.r_[measured["x"], measured["y"]]
        keys, jitter = ("dx_mm", "dy_mm", "pitch_mrad", "yaw_mrad"), self.jitter
        self.jitter = 0.0
        self.incoming_beam = dict(INCOMING_BEAM) if self.machine_offsets else dict.fromkeys(INCOMING_BEAM, 0.0)
        for element in self.lattice['*']:
            element.set_aperture(1.0, 1.0, "circular")

        def orbit():
            self.__track_bunch()
            readings = np.array([self._bpm_reading(bpm) for bpm in self.bpms], dtype=float)
            charge = np.array([self.lattice[bpm].get_total_charge() for bpm in self.bpms], dtype=float)
            readings[charge == 0] = np.nan
            return np.r_[readings[:, 0], readings[:, 1]]

        for _ in range(5):
            base, columns = orbit(), []
            for key, step in zip(keys, (0.1, 0.1, 0.01, 0.01)):
                self.incoming_beam[key] += step
                columns.append((orbit() - base) / step)
                self.incoming_beam[key] -= step
            J = np.column_stack(columns)
            ok = np.isfinite(measured) & np.isfinite(base) & np.all(np.isfinite(J), axis=1)
            correction = np.linalg.lstsq(np.vstack([J[ok], np.diag([0.5, 0.5, 2.0, 2.0])]), np.r_[(measured - base)[ok], np.zeros(4)], rcond=None)[0]
            for key, value in zip(keys, correction):
                self.incoming_beam[key] += value
        for element in self.lattice['*']:
            element.set_aperture(self.aperture, self.aperture, "circular")
        residual = measured - orbit()
        self.jitter = jitter
        self.__track_bunch()
        return float(np.sqrt(np.nanmean(residual ** 2)))

    def _build_bunch_from_guesses(self, emit_x, emit_y, beta_x0, beta_y0, alpha_x0, alpha_y0, energy_pref=None):
        T = rft.Bunch6d_twiss()
        T.emitt_x = float(emit_x)
        T.emitt_y = float(emit_y)
        T.beta_x = float(beta_x0)
        T.beta_y = float(beta_y0)
        T.alpha_x = float(alpha_x0)
        T.alpha_y = float(alpha_y0)
        T.sigma_t = 0#10*rft.ps # mm/c
        T.sigma_pt = 0#10 # permille
        T.mean_xp = 0.0
        T.mean_yp = 0.0
        Pref = self.Pref if energy_pref is None else float(energy_pref)
        return rft.Bunch6d_QR(rft.electronmass, self.population, self.Q, Pref, T, self.nparticles, self.sigmaCut)

    def _read_tracked_bunch_screen_sigmas(self, screens):
        screen_data = self.get_screens(names=screens)
        name_to_index = {name: i for i, name in enumerate(screen_data["names"])}

        sigx = np.full(len(screens), np.nan, dtype=float)
        sigy = np.full(len(screens), np.nan, dtype=float)

        for i, screen in enumerate(screens):
            idx = name_to_index.get(screen)
            if idx is None:
                continue
            sigx[i] = float(screen_data["sigx"][idx])
            sigy[i] = float(screen_data["sigy"][idx])

        return sigx, sigy

    def _predict_scan_response_full(self, quad_name, screens, quad_setting_values, emit_x, emit_y, beta_x0, beta_y0, alpha_x0, alpha_y0, quad_dx0=None, quad_dy0=None, quad_roll=None, energy_pref=None, stop_checker=None, reference_screen=None, start_quad=None, quad_settings=None):
        screens = self._model_screen_names(screens)
        reference_screen = self._model_screen_names(reference_screen)
        screens = list(screens)
        quad_setting_values = np.asarray(quad_setting_values, dtype=float)
        if reference_screen is None: reference_screen = screens[0]
        end_element_name = str(screens[-1])
        start_element_name = str(start_quad or quad_name)
        B0_original = self.B0
        lattice_reference = self.lattice
        self.lattice = lattice_reference.clone()
        if quad_settings:
            self.set_quadrupoles(list(quad_settings), list(quad_settings.values()), track=False)
        start_element = self.lattice[start_element_name]
        if isinstance(start_element, list):
            start_element = start_element[0]
        quad_element = self.lattice[quad_name]
        quad_element = quad_element[0] if isinstance(quad_element, list) else quad_element
        override_offsets = any(value is not None for value in (quad_dx0, quad_dy0, quad_roll))
        dx = 0.0 if quad_dx0 is None else float(quad_dx0)
        dy = 0.0 if quad_dy0 is None else float(quad_dy0)
        roll = 0.0 if quad_roll is None else float(quad_roll)
        n_settings, nscreens = len(quad_setting_values), len(screens)
        sigma_x = np.full((n_settings, nscreens), np.nan, dtype=float)
        sigma_y = np.full((n_settings, nscreens), np.nan, dtype=float)
        x_mean = np.full((n_settings, nscreens), np.nan, dtype=float)
        y_mean = np.full((n_settings, nscreens), np.nan, dtype=float)
        sigma_xy = np.full((n_settings, nscreens), np.nan, dtype=float)
        particles_xy = np.empty((n_settings, nscreens), dtype=object)
        twiss_fields = ("emitt_x", "emitt_y", "beta_x", "beta_y", "alpha_x", "alpha_y")
        twiss = {field: np.full((n_settings, nscreens), np.nan, dtype=float) for field in twiss_fields}

        try:
            if override_offsets:
                quad_element.set_offsets(dx, dy, 0.0, roll, 0.0, 0.0, "center")
            for k,quad_setting in enumerate(quad_setting_values):
                if callable(stop_checker) and stop_checker():
                    raise RuntimeError("__OPTIMIZATION_STOP__")
                self.set_quadrupoles([quad_name], [float(quad_setting)], track=False)

                end_element = self.lattice[end_element_name]
                if isinstance(end_element, list):
                    end_element = end_element[-1]

                temp_bunch = self._build_bunch_from_guesses(emit_x=float(emit_x), emit_y=float(emit_y), beta_x0=float(beta_x0), beta_y0=float(beta_y0), alpha_x0=float(alpha_x0), alpha_y0=float(alpha_y0), energy_pref=energy_pref)
                lattice_view = rft.Lattice_view(self.lattice, start_element, end_element)
                tracked_to_last_screen = lattice_view.track(temp_bunch)

                for si, screen_name in enumerate(screens):
                    screen_elem = self.lattice[screen_name]
                    if isinstance(screen_elem, list):
                        screen_elem = screen_elem[-1]
                    bunch_at_screen = screen_elem.get_bunch()
                    if bunch_at_screen is None and str(screen_name) == end_element_name:
                        bunch_at_screen = tracked_to_last_screen
                    m = bunch_at_screen.get_phase_space('%x %y')
                    particles_xy[k, si] = (m[:, 0].copy(), m[:, 1].copy())
                    if m is not None and len(m) > 0:
                        xs = m[:, 0]
                        ys = m[:, 1]
                        xm = float(np.mean(xs))
                        ym = float(np.mean(ys))
                        sigma_x[k, si] = float(np.std(xs))
                        sigma_y[k, si] = float(np.std(ys))
                        x_mean[k, si] = xm
                        y_mean[k, si] = ym
                        sigma_xy[k, si] = float(np.mean((xs - xm) * (ys - ym))) # covariance
                        info = bunch_at_screen.get_info()
                        for field in twiss_fields:
                            twiss[field][k, si] = float(getattr(info, field, np.nan))

        finally:
            self.lattice = lattice_reference
            self.B0 = B0_original
            self.__track_bunch()

        return {
            "sigma_x": sigma_x, "sigma_y": sigma_y,
            "x_mean": x_mean, "y_mean": y_mean,
            "sigma_xy": sigma_xy, "particles_xy": particles_xy,
            **twiss,
        }

    def predict_emittance_scan_response(self, quad_name, screens, quad_setting_values, emit_x, emit_y, beta_x0, beta_y0, alpha_x0, alpha_y0, stop_checker = None, reference_screen = None, start_quad=None, quad_settings=None):
        full = self._predict_scan_response_full(quad_name, screens, quad_setting_values, emit_x, emit_y, beta_x0, beta_y0, alpha_x0, alpha_y0, stop_checker=stop_checker, reference_screen=reference_screen, start_quad=start_quad, quad_settings=quad_settings)
        return full["sigma_x"], full["sigma_y"]

    def predict_emittance_scan_response_full(self, quad_name, screens, quad_setting_values, emit_x, emit_y, beta_x0, beta_y0, alpha_x0, alpha_y0, quad_dx0=None, quad_dy0=None, quad_roll=None, energy_pref=None, stop_checker=None, reference_screen=None, start_quad=None, quad_settings=None):
        return self._predict_scan_response_full(quad_name, screens, quad_setting_values, emit_x, emit_y, beta_x0, beta_y0, alpha_x0, alpha_y0, quad_dx0=quad_dx0, quad_dy0=quad_dy0, quad_roll=quad_roll, energy_pref=energy_pref, stop_checker=stop_checker, reference_screen=reference_screen, start_quad=start_quad, quad_settings=quad_settings)

    def get_phase_space_transport_to_screens(self, reference_screen=None, screens=None):
        screens = self._model_screen_names(screens)
        reference_screen = self._model_screen_names(reference_screen)
        if screens is None:
            screens = list(self.screens)
        if isinstance(screens, str):
            screens = [screens]
        screens = list(screens)

        if reference_screen is None:
            reference_screen = screens[0]

        original_bunch = self.B0

        result = {
            "reference_screen": str(reference_screen),
            "screens": [str(s) for s in screens],
            "x": {"R11": [], "R12": [], "R21": [], "R22": []},
            "y": {"R33": [], "R34": [], "R43": [], "R44": []},
        }

        try:
            start_element = self.lattice[reference_screen]
            if isinstance(start_element, list):
                start_element = start_element[-1]

            end_element = self.lattice[screens[-1]]
            if isinstance(end_element, list):
                end_element = end_element[-1]

            bx = np.array([
                [1.0, 0.0, 0.0, 0.0, 0.0, self.Pref],
                [0.0, 1.0, 0.0, 0.0, 0.0, self.Pref],
            ], dtype=float)

            bunch_x = rft.Bunch6d(rft.electronmass, 0.0, self.Q, bx)
            lattice_view = rft.Lattice_view(self.lattice, start_element, end_element)
            tracked_x = lattice_view.track(bunch_x)

            for screen in screens:
                screen_element = self.lattice[screen]
                if isinstance(screen_element, list):
                    screen_element = screen_element[-1]

                b = screen_element.get_bunch()
                if b is None and str(screen) == str(screens[-1]):
                    b = tracked_x

                ps = np.asarray(b.get_phase_space("%x %xp"), dtype=float)

                result["x"]["R11"].append(float(ps[0, 0]))
                result["x"]["R12"].append(float(ps[1, 0]))
                result["x"]["R21"].append(float(ps[0, 1]))
                result["x"]["R22"].append(float(ps[1, 1]))

            by = np.array([
                [0.0, 0.0, 1.0, 0.0, 0.0, self.Pref],
                [0.0, 0.0, 0.0, 1.0, 0.0, self.Pref],
            ], dtype=float)

            bunch_y = rft.Bunch6d(rft.electronmass, 0.0, self.Q, by)
            lattice_view = rft.Lattice_view(self.lattice, start_element, end_element)
            tracked_y = lattice_view.track(bunch_y)

            for screen in screens:
                screen_element = self.lattice[screen]
                if isinstance(screen_element, list):
                    screen_element = screen_element[-1]

                b = screen_element.get_bunch()
                if b is None and str(screen) == str(screens[-1]):
                    b = tracked_y

                ps = np.asarray(b.get_phase_space("%y %yp"), dtype=float)

                # [
                #     [x_of_particle_0, xp_of_particle_0],
                #     [x_of_particle_1, xp_of_particle_1],
                # ]

                result["y"]["R33"].append(float(ps[0, 0]))
                result["y"]["R34"].append(float(ps[1, 0]))
                result["y"]["R43"].append(float(ps[0, 1]))
                result["y"]["R44"].append(float(ps[1, 1]))

        finally:
            self.B0 = original_bunch
            self.__track_bunch()

        return result

    def get_R_matrix_scan(self, quad_name, screens, quad_setting_values):
        screens = self._model_screen_names(screens)
        screens = list(screens)
        quad_setting_values = np.asarray(quad_setting_values, dtype=float)
        original_quads = self.get_quadrupoles(names=[quad_name])
        original_quad_setting = float(original_quads["bdes"][0])
        end_element_name = str(screens[-1])

        n_settings = len(quad_setting_values)
        n_screens = len(screens)
        R11 = np.full((n_settings, n_screens), np.nan, dtype=float)
        R12 = np.full((n_settings, n_screens), np.nan, dtype=float)
        R33 = np.full((n_settings, n_screens), np.nan, dtype=float)
        R34 = np.full((n_settings, n_screens), np.nan, dtype=float)

        original_bunch = self.B0
        try:
            for k, quad_setting in enumerate(quad_setting_values):
                self.set_quadrupoles([quad_name], [float(quad_setting)], track=False)
                start_element = self.lattice[quad_name]
                if isinstance(start_element, list): start_element = start_element[0]
                end_element = self.lattice[end_element_name]
                if isinstance(end_element, list): end_element = end_element[-1]

                bx = np.array([
                    [1.0, 0.0, 0.0, 0.0, 0.0, self.Pref],  # x = 1, x' = 0
                    [0.0, 1.0, 0.0, 0.0, 0.0, self.Pref],  # x = 0, x' = 1
                ], dtype=float)

                bunch_x = rft.Bunch6d(rft.electronmass, 0.0, self.Q, bx)
                tracked_x = rft.Lattice_view(self.lattice, start_element, end_element).track(bunch_x)

                for si, screen_name in enumerate(screens):
                    screen_elem = self.lattice[screen_name]
                    if isinstance(screen_elem, list):
                        screen_elem = screen_elem[-1]
                    b_x = None
                    try:
                        b_x = screen_elem.get_bunch()  # Read the test particles cached at this screen.
                    except Exception:
                        b_x = None
                    if b_x is None and str(screen_name) == end_element_name:
                        b_x = tracked_x
                    if b_x is None:
                        continue
                    phase_space_x = np.asarray(b_x.get_phase_space("%x %xp"), dtype=float)
                    R11[k, si] = phase_space_x[0, 0]  # k: quad_setting index, si: screen index.
                    R12[k, si] = phase_space_x[1, 0]

                by = np.array([
                    [0.0, 0.0, 1.0, 0.0, 0.0, self.Pref],  # y = 1, y' = 0
                    [0.0, 0.0, 0.0, 1.0, 0.0, self.Pref],  # y = 0, y' = 1
                ], dtype=float)
                bunch_y = rft.Bunch6d(rft.electronmass, 0.0, self.Q, by)
                tracked_y = rft.Lattice_view(self.lattice, start_element, end_element).track(bunch_y)

                for si, screen_name in enumerate(screens):
                    screen_elem = self.lattice[screen_name]
                    if isinstance(screen_elem, list):
                        screen_elem = screen_elem[-1]
                    b_y = None
                    try:
                        b_y = screen_elem.get_bunch()  # Read the test particles cached at this screen.
                    except Exception:
                        b_y = None
                    if b_y is None and str(screen_name) == end_element_name:
                        b_y = tracked_y
                    if b_y is None:
                        continue
                    phase_space_y = np.asarray(b_y.get_phase_space("%y %yp"), dtype=float)
                    R33[k, si] = phase_space_y[0, 0]  # k: quad_setting index, si: screen index.
                    R34[k, si] = phase_space_y[1, 0]
        finally:
            self.set_quadrupoles([quad_name], [float(original_quad_setting)], track=False)
            self.B0 = original_bunch
            self.__track_bunch()

        return {"R11": R11, "R12": R12, "R33": R33, "R34": R34, "screens": screens, "quad_setting_values": quad_setting_values}

    def get_quadrupoles(self, names=None):
        #self.log("Reading quadrupoles' strengths...")
        bdes = np.zeros(len(self.quadrupoles), dtype=float)

        for i, quadrupole_name in enumerate(self.quadrupoles):
            elements = self.lattice[quadrupole_name]
            if not isinstance(elements, list):
                elements = [elements]

            current_values = []
            for element in elements:
                try:
                    gradient = float(element.get_gradient())
                    current = self.get_current_from_grad(
                        self._gradient_sign(quadrupole_name) * gradient,
                        element.get_length(),
                    )
                except Exception:
                    continue
                current_values.append(current)

            bdes[i] = current_values[0] if current_values else 0.0

        quadrupoles = {
            "names": self.quadrupoles,
            "bdes": bdes,
            "bact": bdes.copy(),
            "value_unit": "A",
        }

        if isinstance(names, str):
            names = [names]
        if names is not None:
            idx = [list(quadrupoles["names"]).index(s) for s in names if s in quadrupoles["names"]]  # requested order, like the real machine
            quadrupoles = {
                "names": [quadrupoles["names"][i] for i in idx],
                "bdes": np.asarray(quadrupoles["bdes"])[idx],
                "bact": np.asarray(quadrupoles["bact"])[idx],
                "value_unit": "A",
            }

        return quadrupoles

    def _get_elements_positions_show_beamline(self, names=None):
        if isinstance(names, str):
            names = [names]
        all_names = [name for name in self.sequence if names is None or name in names]

        return {
            "names": all_names,
            "S": np.array([self.lattice[name].get_S("entrance") for name in all_names], dtype=float),
        }

    def _give_elements_to_show_beamline(self, quad_selected):
        start_quad_element_name = quad_selected
        return start_quad_element_name

    def set_quadrupoles(self, names, currents_A, track=True):
        if isinstance(names, str):
            names = [names]
        if not isinstance(currents_A, (list, tuple, np.ndarray)):
            currents_A = [currents_A]
        if len(names) != len(currents_A):
            raise ValueError(f"len(names)={len(names)} != len(currents_A)={len(currents_A)}")

        for quadrupole_name, current_A in zip(names, currents_A):
            elements = self.lattice[quadrupole_name]
            if not isinstance(elements, list):
                elements = [elements]
            for element in elements:
                gradient = self._gradient_sign(quadrupole_name) * self.get_grad(float(current_A), element.get_length())
                element.set_gradient(gradient)
        if track:
            self.__track_bunch()

    def get_elements_indices(self, names):
        if isinstance(names, str):
            names = [names]
        name_to_index = {string: index for index, string in enumerate(self.sequence)}
        return [name_to_index.get(name, np.nan) for name in names]

    def get_beam_evolution(self, quad_name, screens, quad_setting, quad_value_unit, beam_parameters):
        if quad_value_unit != "A":
            raise ValueError("quad_value_unit must be 'A' for CLEAR.")

        tracking_results = self.predict_emittance_scan_response_full(quad_name=quad_name, screens = screens, quad_setting_values = [quad_setting], emit_x= beam_parameters["emit_x_norm"], emit_y = beam_parameters["emit_y_norm"], beta_x0 = beam_parameters["beta_x0"], beta_y0 = beam_parameters["beta_y0"], alpha_x0 = beam_parameters["alpha_x0"], alpha_y0 = beam_parameters["alpha_y0"]) # e.g result for one setting and 3 screens
        screen_names = self._model_screen_names(screens)
        screen_positions = []

        for name in screen_names:
            positions = self._get_elements_positions_show_beamline(name)
            screen_positions.append(positions["S"][-1])
        tracking_results["S"] = np.array(screen_positions, dtype=float)

        return tracking_results