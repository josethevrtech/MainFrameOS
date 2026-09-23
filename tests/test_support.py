import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / 'packages/mainframeos-support/mainframeos-support'


class HardwareMatching(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.dmi = self.root / 'sys/class/dmi/id'
        self.dmi.mkdir(parents=True)
        for name, value in {'sys_vendor': 'HP', 'product_name': 'HP OmniBook 5 Laptop 16-bf0xxx', 'board_name': '8E33'}.items():
            (self.dmi / name).write_text(value + '\n')
        self.dt = self.root / 'proc/device-tree'
        self.dt.mkdir(parents=True)
        (self.dt / 'compatible').write_bytes(b'hp,omnibook-5\0lenovo,thinkpad-t14s\0qcom,x1p42100\0')

    def invoke(self, profiles=None):
        return subprocess.run([sys.executable, str(TOOL), '--root', str(self.root), '--profiles', str(profiles or ROOT / 'devices')], text=True, capture_output=True)

    def test_reference_matches_but_is_not_certified(self):
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['profile'], 'hp-omnibook5-8e33')
        self.assertFalse(report['release_ready'])

    def test_same_chip_wrong_board_rejected(self):
        (self.dmi / 'board_name').write_text('8E34')
        self.assertEqual(self.invoke().returncode, 2)

    def test_wrong_vendor_rejected(self):
        (self.dmi / 'sys_vendor').write_text('Lenovo')
        self.assertEqual(self.invoke().returncode, 2)

    def test_compatible_substring_does_not_match(self):
        (self.dt / 'compatible').write_bytes(b'hp,omnibook-50\0qcom,x1p42100\0')
        self.assertEqual(self.invoke().returncode, 2)

    def test_missing_identity_rejected(self):
        (self.dmi / 'product_name').unlink()
        self.assertEqual(self.invoke().returncode, 2)

    def test_invalid_utf8_rejected(self):
        (self.dt / 'compatible').write_bytes(b'\xff')
        self.assertEqual(self.invoke().returncode, 2)

    def test_ambiguous_profiles_fail(self):
        profiles = self.root / 'profiles'
        profiles.mkdir()
        text = (ROOT / 'devices/hp-omnibook5-8e33.json').read_text()
        (profiles / 'a.json').write_text(text)
        (profiles / 'b.json').write_text(text)
        self.assertEqual(self.invoke(profiles).returncode, 1)

    def test_malformed_profile_fails(self):
        profiles = self.root / 'profiles'
        profiles.mkdir()
        (profiles / 'bad.json').write_text('{')
        self.assertEqual(self.invoke(profiles).returncode, 1)

    def test_output_does_not_collect_serials(self):
        (self.dmi / 'product_serial').write_text('DO-NOT-PUBLISH')
        self.assertNotIn('DO-NOT-PUBLISH', self.invoke().stdout)


if __name__ == '__main__':
    unittest.main()
