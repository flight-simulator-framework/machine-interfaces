import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

from poetry.core.factory import Factory
from poetry.core.masonry.builders.wheel import WheelBuilder


ROOT = Path(__file__).resolve().parents[1]
MACHINES = ("clear", "atf2", "facet2", "esrf")


class BackendPackagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temporary.name)
        cls.wheels = {}
        for name, directory in [("core", ROOT), *((name, ROOT / "backends" / name) for name in MACHINES)]:
            cls.wheels[name] = WheelBuilder(Factory().create_poetry(directory)).build(cls.output)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def discover(self, machines):
        with tempfile.TemporaryDirectory() as directory:
            for name in ("core", *machines):
                with zipfile.ZipFile(self.wheels[name]) as archive:
                    archive.extractall(directory)
            code = """
import importlib.util
import json
from pathlib import Path
import sys
sys.path.insert(0, sys.argv[1])
from machine_interfaces.Interfaces.interface_setup import INTERFACE_SETUP, ACCELERATOR_BRANDING
print(json.dumps({
    'machines': sorted(INTERFACE_SETUP),
    'visible': [name for name in ('clear', 'atf2', 'facet2', 'esrf') if importlib.util.find_spec('machine_interfaces_' + name)],
    'assets_exist': all(Path(path).is_file() for paths in ACCELERATOR_BRANDING.values() for path in paths),
    'adapters_exist': all(importlib.util.find_spec(entry['module']) is not None for entries in INTERFACE_SETUP.values() for entry in entries),
    'heavy_imports': sorted(set(sys.modules) & {'RF_Track', 'epics', 'tango', 'pyda', 'pyda_japc'}),
}))
"""
            result = subprocess.run([sys.executable, "-I", "-S", "-c", code, directory], check=True, capture_output=True, text=True)
            return json.loads(result.stdout)

    def test_core_works_without_any_machine(self):
        result = self.discover(())
        self.assertEqual(result["machines"], [])
        self.assertEqual(result["visible"], [])

    def test_each_machine_is_independently_discoverable(self):
        for machine in MACHINES:
            with self.subTest(machine=machine):
                result = self.discover((machine,))
                self.assertEqual(result["machines"], [machine.upper()])
                self.assertEqual(result["visible"], [machine])
                self.assertTrue(result["assets_exist"])
                self.assertTrue(result["adapters_exist"])
                self.assertEqual(result["heavy_imports"], [])

    def test_multiple_machines_can_be_installed_together(self):
        result = self.discover(MACHINES)
        self.assertEqual(result["machines"], sorted(name.upper() for name in MACHINES))
        self.assertEqual(result["visible"], list(MACHINES))
        self.assertEqual(result["heavy_imports"], [])

    def test_wheels_only_contain_their_own_package(self):
        for name, wheel in self.wheels.items():
            with self.subTest(package=name), zipfile.ZipFile(wheel) as archive:
                package = "machine_interfaces" if name == "core" else "machine_interfaces_" + name
                for member in archive.namelist():
                    self.assertTrue(member.startswith(package + "/") or (member.split("/")[0].startswith(package + "-") and member.split("/")[0].endswith(".dist-info")), member)
                    self.assertNotIn("__pycache__", member)
                metadata = archive.read(next(member for member in archive.namelist() if member.endswith("/METADATA"))).decode()
                self.assertNotIn("file://", metadata)
                self.assertNotIn("git+", metadata)
                if name == "core":
                    for dependency in ("rf-track", "pyepics", "pytao", "cpymad", "pytango", "pyda"):
                        self.assertNotIn("Requires-Dist: " + dependency, metadata)

    def test_model_data_is_bundled(self):
        required = {
            "clear": ("Setup_files/twissinit.tfs", "cameras.json"),
            "atf2": ("Ext_ATF2/atf2_full_twiss.tfs", "DR_ATF2/ATF_DR_lattice.madx", "libmagnet/Makefile"),
            "facet2": ("FACET2/FACET-II-Wakes.lat.bmad", "FACET2/tao.init"),
            "esrf": ("Setup_files/rips_dipole_ramp.csv",),
        }
        for name, paths in required.items():
            with self.subTest(package=name), zipfile.ZipFile(self.wheels[name]) as archive:
                for path in paths:
                    self.assertIn(f"machine_interfaces_{name}/{path}", archive.namelist())


if __name__ == "__main__":
    unittest.main()
