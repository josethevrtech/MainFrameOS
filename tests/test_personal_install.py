import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from personal_install import layout, menu, normalized, GIB, ESP, LINUX

class PersonalInstallPlanTests(unittest.TestCase):
    def setUp(self):
        self.original = dict(label='gpt', id='0bbfc627-cd2b-4b83-a8e6-0223c5dcfa4d',
            sectorsize=512, firstlba=2048, lastlba=2000409230,
            partitions=[dict(start=2048, size=4194304, type=ESP,
                uuid='40254019-b5da-42e1-bbbb-d1cfae362df5', name='Existing_EFI'),
                dict(start=4196352, size=1996212224, type=LINUX,
                uuid='85ddacd1-d548-4cc1-bb08-fff2ca1e7ae3', name='Existing')])
        self.new_uuid = 'aacb7eac-0156-4224-8501-b2e7b0ea5af5'

    def test_existing_partition_identity_and_end_preserved(self):
        before = copy.deepcopy(self.original)
        after = layout(before, 150 * GIB, self.new_uuid)
        self.assertEqual(before, self.original)
        self.assertEqual(after['partitions'][0], before['partitions'][0])
        old, shrunk, new = before['partitions'][1], after['partitions'][1], after['partitions'][2]
        self.assertEqual(old['start'], shrunk['start'])
        self.assertEqual(old['uuid'], shrunk['uuid'])
        self.assertEqual(old['start'] + old['size'], new['start'] + new['size'])
        self.assertEqual(shrunk['start'] + shrunk['size'], new['start'])
        self.assertEqual(new['size'] * 512, 150 * GIB)

    def test_unreviewed_layouts_rejected(self):
        for change in ('sector', 'extra', 'attrs', 'overlap', 'too-small'):
            t = copy.deepcopy(self.original)
            if change == 'sector': t['sectorsize'] = 4096
            if change == 'extra': t['partitions'].append(t['partitions'][0])
            if change == 'attrs': t['partitions'][1]['attrs'] = 'RequiredPartition'
            if change == 'overlap': t['partitions'][1]['start'] = 2048
            if change == 'too-small': t['partitions'][1]['size'] = 1024
            with self.assertRaises(RuntimeError): layout(t, 150 * GIB, self.new_uuid)

    def test_menu_uses_unique_internal_paths_and_root_uuid(self):
        entry, config = menu('BEE2-8C4C', self.new_uuid)
        self.assertIn('EFI/MainFrameOS-Internal/grub.cfg', entry)
        self.assertIn('root=UUID=' + self.new_uuid, config)
        self.assertNotIn('search --no-floppy --file', entry + config)
        with self.assertRaises(RuntimeError): menu('bad;command', self.new_uuid)

    def test_node_renaming_does_not_hide_geometry_changes(self):
        other = copy.deepcopy(self.original)
        other['device'] = '/dev/other'
        other['id'] = other['id'].upper()
        other['partitions'][0]['uuid'] = other['partitions'][0]['uuid'].upper()
        other['partitions'][0]['node'] = '/dev/other1'
        self.assertEqual(normalized(other), normalized(self.original))
        other['partitions'][1]['size'] -= 2048
        self.assertNotEqual(normalized(other), normalized(self.original))
