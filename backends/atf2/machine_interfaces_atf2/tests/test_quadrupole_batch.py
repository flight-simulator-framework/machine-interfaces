"""Offline batch read regressions; bypass the live-interface constructor."""
import unittest
from unittest.mock import patch
import numpy as np
from machine_interfaces_atf2.InterfaceATF2_Ext import InterfaceATF2_Ext

MODULE = "machine_interfaces_atf2.InterfaceATF2_Ext"


class TestBatchRead(unittest.TestCase):
    def setUp(self):
        self.machine = InterfaceATF2_Ext.__new__(InterfaceATF2_Ext)

    def test_dedup_missing_and_invalid(self):
        with patch(MODULE + ".caget_many", return_value=[2.0, None, "bad"]) as get:
            out = self.machine._pv_get_many(["a", "a", None, "b", "c"])
        get.assert_called_once_with(["a", "b", "c"], timeout=0.7, connection_timeout=0.7)
        self.assertEqual(out["a"], 2.0)
        self.assertTrue(np.isnan(out["b"]))
        self.assertTrue(np.isnan(out["c"]))

    def test_empty_and_failed_batch(self):
        with patch(MODULE + ".caget_many", side_effect=RuntimeError("offline")) as get:
            self.assertEqual(self.machine._pv_get_many([]), {})
            get.assert_not_called()
            self.assertTrue(np.isnan(self.machine._pv_get_many(["a"])["a"]))

    def test_order_and_current_fallback(self):
        m = self.machine
        m.quadrupoles = ["Q1", "Q2"]
        keys = ("pv_set_x", "pv_set_y", "pv_set_roll", "pv_read_enc_x", "pv_read_enc_y", "pv_read_enc_roll")
        m.qmag_pv = {n: {k: f"{n}:{k}" for k in keys} for n in m.quadrupoles}
        m._quadrupole_current_pv_name = lambda n: n
        m._quad_mover_pv_name = lambda n: n
        m.current_to_k1l = lambda n, value: value * 2
        m.update_tracking_model_with_clibmagnet = lambda **kwargs: None
        def read(names, **kwargs):
            values = {"Q2:currentWrite": None, "Q2:current": None,
                      "Q2:currentRead": 4.0, "Q1:currentWrite": 2.0,
                      "Q1:current": 3.0}
            return [values.get(n, 0.5) for n in names]
        with patch(MODULE + ".caget_many", side_effect=read) as get:
            result = m.get_quadrupoles(["Q2", "Q1"], include_pv_names=True)
        self.assertEqual(get.call_count, 2)
        self.assertEqual(get.call_args_list[1].args[0], ["Q2:currentRead"])
        self.assertEqual(result["names"], ["Q2", "Q1"])
        np.testing.assert_equal(result["ides"], [4., 2.])
        np.testing.assert_equal(result["iact"], [4., 3.])
        np.testing.assert_equal(result["bdes"], [8., 4.])
        np.testing.assert_equal(result["xact"], [.5, .5])


if __name__ == "__main__":
    unittest.main()
