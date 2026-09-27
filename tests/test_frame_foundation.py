import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


xr = load('frame_xr')
kernel = load('frame_kernel')


class FrameFoundationTests(unittest.TestCase):
    def test_prepare_uses_pinned_objects_inside_ignored_build_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            (root / '.gitignore').write_text('build/\n')
            upstream = root / 'upstream'
            upstream.mkdir()
            subprocess.run(['git', 'init', '-q', str(upstream)], check=True)
            (upstream / 'src/xrt/drivers/remote').mkdir(parents=True)
            original = upstream / 'src/xrt/drivers/remote/test.c'
            original.write_text('original\n')
            subprocess.run(['git', '-C', str(upstream), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(upstream), '-c', 'user.name=Test',
                            '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'fixture'], check=True)
            pin = subprocess.check_output(['git', '-C', str(upstream), 'rev-parse', 'HEAD'], text=True).strip()
            tree = subprocess.check_output(['git', '-C', str(upstream), 'rev-parse', 'HEAD^{tree}'], text=True).strip()
            original.write_text('unrecorded working-tree modification\n')
            recipe = root / 'recipe'
            recipe.mkdir()
            (recipe / 'fix.patch').write_text('--- a/src/xrt/drivers/remote/test.c\n'
                '+++ b/src/xrt/drivers/remote/test.c\n@@ -1 +1 @@\n-original\n+patched\n')
            (recipe / 'generate-optics.py').write_text(
                'import sys\nfrom pathlib import Path\nPath(sys.argv[2]).write_text("generated")\n')
            optics = root / 'optics.json'
            optics.write_text('{}')
            lock = root / 'lock.json'
            lock.write_text(json.dumps({'schema_version': 1, 'commit': pin, 'tree': tree,
                'patches': ['fix.patch'], 'files': {p.name: xr.sha(p) for p in recipe.iterdir()},
                'optics': {'sha256': xr.sha(optics)}}))
            destination = root / 'build/prepared'
            with patch.object(xr, 'LOCK', lock), patch.object(xr, 'RECIPE', recipe):
                xr.prepare(upstream, optics, destination)
                xr.verify(destination)
            self.assertEqual((destination / 'src/xrt/drivers/remote/test.c').read_text(), 'patched\n')
            self.assertEqual(original.read_text(), 'unrecorded working-tree modification\n')

    def test_recipe_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            recipe = root / 'patch'
            recipe.write_text('changed')
            lock = root / 'lock.json'
            lock.write_text(json.dumps({'schema_version': 1, 'files': {'patch': '0' * 64}}))
            with patch.object(xr, 'LOCK', lock), patch.object(xr, 'RECIPE', root):
                with self.assertRaisesRegex(ValueError, 'recipe input changed'):
                    xr.inputs()

    def test_added_removed_or_modified_sources_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'source.c'
            source.write_text('original')
            record = {'lock_sha256': xr.sha(xr.LOCK), 'commit': xr.inputs()['commit'],
                      'files': xr.inventory(root)}
            (root / '.mainframeos-source.json').write_text(json.dumps(record))
            xr.verify(root)
            source.write_text('changed')
            with self.assertRaisesRegex(ValueError, 'changed after reconstruction'):
                xr.verify(root)
            source.unlink()
            with self.assertRaises(ValueError):
                xr.verify(root)
            source.write_text('original')
            (root / 'unexpected.c').write_text('extra')
            with self.assertRaises(ValueError):
                xr.verify(root)

    def test_source_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'escape').symlink_to('/etc/passwd')
            with self.assertRaisesRegex(ValueError, 'symlink'):
                xr.inventory(root)

    def test_existing_destination_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sentinel = root / 'keep'
            sentinel.write_text('do not overwrite')
            with self.assertRaisesRegex(ValueError, 'must not exist'):
                xr.prepare(root, root / 'absent-optics', root)
            self.assertEqual(sentinel.read_text(), 'do not overwrite')

    def test_kernel_module_drift_requires_review(self):
        reference = json.loads(kernel.REFERENCE.read_text())
        self.assertFalse(kernel.compare(reference, reference)['changed'])
        observed = {**reference, 'modules': {**reference['modules'], 'extra.ko': 'new'}}
        result = kernel.compare(reference, observed)
        self.assertTrue(result['changed'])
        self.assertEqual(set(result['changes']), {'modules'})
        self.assertFalse(result['automatic_adoption'])

    def test_recorded_kernel_config_matches_reference(self):
        reference = json.loads(kernel.REFERENCE.read_text())
        self.assertEqual(kernel.sha(ROOT / 'kernels/frame/reference.config'), reference['config_sha256'])


if __name__ == '__main__':
    unittest.main()
