"""Changing the ring origin must preserve physical device identities."""
import unittest
import numpy as np

from machine_interfaces_atf2.DR_ATF2.ATF_DR_RFTrack_lattice import build_atf_dr_lattice
from machine_interfaces_atf2.DR_ATF2.ATF_DR_RFTrack_correction import ATFDRRingCorrection


class RingOriginTests(unittest.TestCase):
    def test_rotated_native_elements_are_exactly_one_cyclic_permutation(self):
        for mode in ('disabled', 'equilibrium'):
            original = build_atf_dr_lattice(rf_mode=mode)
            baseline = [(e.get_name(), e.get_length()) for e in original['*']][1:-1]
            for entry in ('KII.1', 'KII.2', 'KIX.1', 'QF1R.2'):
                with self.subTest(mode=mode, entry=entry):
                    moved = build_atf_dr_lattice(start_at=entry, rf_mode=mode)
                    actual = [(e.get_name(), e.get_length()) for e in moved['*']][1:-1]
                    index = [n for n, length in baseline].index(entry)
                    self.assertEqual(actual, baseline[index:] + baseline[:index])
                    self.assertAlmostEqual(moved.get_length(), original.get_length(), places=10)

    def test_first_injection_bpm_keeps_source_identity(self):
        ring = build_atf_dr_lattice(start_at='KII.1')
        names = [e.get_name() for e in ring.get_bpms()]
        self.assertEqual(names[0], 'MB22R')
        self.assertEqual(len(names), len(set(names)))
        with self.assertRaises(ValueError):
            build_atf_dr_lattice(start_at='KII')

    def test_same_perturbation_gives_same_orbit_at_each_named_bpm(self):
        observations = []
        for entry in (None, 'KII.1'):
            solver = ATFDRRingCorrection(build_atf_dr_lattice(start_at=entry))
            solver._set_corrector_kick(solver._single_element('ZV1R'), [0., 1e-6])
            solver.set_skew_strength('SD1R.1$SKEW', .0001)
            orbit = solver.find_closed_orbit()
            observations.append(dict(zip(orbit.bpm_names, orbit.bpm_positions)))
        self.assertEqual(set(observations[0]), set(observations[1]))
        for name in observations[0]:
            np.testing.assert_allclose(observations[0][name], observations[1][name], atol=1e-7,
                                       err_msg=name)


if __name__ == '__main__':
    unittest.main()
