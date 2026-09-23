import importlib.util
from pathlib import Path
import tempfile
import json
import sys
from unittest.mock import patch
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('builder', ROOT / 'scripts/build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
sys.modules['build'] = builder
kernel_spec = importlib.util.spec_from_file_location('kernel_builder', ROOT / 'scripts/kernel.py')
kernel_builder = importlib.util.module_from_spec(kernel_spec)
kernel_spec.loader.exec_module(kernel_builder)


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

    def test_deleted_recipe_input_cannot_survive_next_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, work = Path(tmp) / 'source', Path(tmp) / 'work'
            source.mkdir()
            (source / 'PKGBUILD').write_text('source=(removed.patch)')
            (source / 'removed.patch').write_text('old patch')
            builder.stage_recipe(source, work)
            (source / 'removed.patch').unlink()
            builder.stage_recipe(source, work)
            self.assertFalse((work / 'removed.patch').exists())
            self.assertEqual((work / 'PKGBUILD').read_text(), 'source=(removed.patch)')

    def test_stale_builder_rejected_by_package_and_kernel_entrypoints(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'build-support').mkdir()
            recipe = root / 'build-support/Containerfile'
            recipe.write_text('FROM locked')
            (root / 'builder.json').write_text(json.dumps({
                'containerfile_sha256': builder.digest(recipe), 'bootstrap_sha256': 'old'}))
            lock = {'bootstrap': {'sha256': 'new'}, 'kernel_candidate': {}}
            lockfile = root / 'lock.json'
            lockfile.write_text(json.dumps(lock))
            with patch.object(builder, 'ROOT', root), patch.object(builder, 'BUILD', root), \
                 patch.object(kernel_builder, 'LOCK', lockfile), \
                 patch.object(builder, 'container') as container:
                with self.assertRaisesRegex(ValueError, 'bootstrap lock changed'):
                    builder.build_package(lock, 'mainframeos-support')
                with self.assertRaisesRegex(ValueError, 'bootstrap lock changed'):
                    kernel_builder.main()
                container.assert_not_called()


if __name__ == '__main__':
    unittest.main()
