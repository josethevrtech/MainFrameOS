import json
import struct
import sys
import tempfile
import unittest
import uuid
import zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build import digest
from usb_support import verify_image, esp_offset, cache_inputs, verify_cache, verify_firmware_provenance

class USBIntegrityTests(unittest.TestCase):
    def test_modified_image_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'image'; p.write_bytes(b'original')
            expected = digest(p)
            self.assertEqual(verify_image(p, expected), expected)
            p.write_bytes(b'modified')
            with self.assertRaises(ValueError): verify_image(p, expected)

    def test_gpt_crc_and_esp_location(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'image'
            data = bytearray(512*128)
            entry = bytearray(128)
            entry[:16] = uuid.UUID('c12a7328-f81f-11d2-ba4b-00a0c93ec93b').bytes_le
            struct.pack_into('<QQ', entry, 32, 40, 100)
            data[1024:1152] = entry
            header = bytearray(512); header[:8] = b'EFI PART'
            struct.pack_into('<I', header, 12, 92)
            struct.pack_into('<QIII', header, 72, 2, 1, 128, zlib.crc32(entry))
            struct.pack_into('<I', header, 16, zlib.crc32(header[:92]))
            data[512:1024] = header; p.write_bytes(data)
            self.assertEqual(esp_offset(p), 40*512)
            data[1050] ^= 1; p.write_bytes(data)
            with self.assertRaises(ValueError): esp_offset(p)
            data[1050] ^= 1; data[530] ^= 1; p.write_bytes(data)
            with self.assertRaises(ValueError): esp_offset(p)

    def test_cache_rejects_changed_bootstrap_and_base(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); recipe = p/'recipe'; recipe.write_text('FROM base')
            expected = cache_inputs(recipe, 'bootstrap-a', 'base-a')
            (p/'image-id').write_text('image-a')
            (p/'inputs.json').write_text(json.dumps({'inputs':expected,'image':'image-a'}))
            verify_cache(p, expected)
            for bootstrap, base in [('bootstrap-b','base-a'),('bootstrap-a','base-b')]:
                with self.assertRaises(ValueError): verify_cache(p, cache_inputs(recipe, bootstrap, base))

    def test_firmware_requires_provenance_and_exact_hashes(self):
        state = dict(origin='local device', device_profile='test', revision='local inventory',
                     license_status='unresolved', redistribution_allowed=False, files={'fw':'sha'})
        verify_firmware_provenance(state, {'fw':'sha'})
        with self.assertRaises(ValueError): verify_firmware_provenance(state, {'fw':'different'})
        del state['revision']
        with self.assertRaises(ValueError): verify_firmware_provenance(state, {'fw':'sha'})
