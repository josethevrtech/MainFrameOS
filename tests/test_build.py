import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('builder', ROOT / 'scripts/build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class SourceIntegrity(unittest.TestCase):
    def test_cached_tamper_rejected_without_download(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'source'
            path.write_text('modified')
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                builder.fetch('https://example.invalid/source', path, '0' * 64)

    def test_verified_cache_reused_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'source'
            path.write_text('locked')
            builder.fetch('https://example.invalid/source', path, builder.digest(path))
            self.assertEqual(path.read_text(), 'locked')

    def test_plain_http_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'HTTPS'):
                builder.fetch('http://example.invalid/source', Path(tmp) / 'absent', '0' * 64)

    def test_unknown_package_rejected_before_container_execution(self):
        with self.assertRaisesRegex(ValueError, 'unknown package'):
            builder.build_package({}, '../other')


if __name__ == '__main__':
    unittest.main()
