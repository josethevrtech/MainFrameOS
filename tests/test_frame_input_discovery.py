import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
from types import SimpleNamespace

spec = importlib.util.spec_from_file_location('discovery', Path(__file__).resolve().parents[1]/'tools/frame-input-bridge/ssh-mdns.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Discovery(unittest.TestCase):
 def test_changes_route_not_trusted_identity(self):
  args=['-T','-o','StrictHostKeyChecking=yes','-i','/key','steamos@frame.local','python3','/receiver.py']
  result=m.command(args,lambda host:'10.42.0.25')
  self.assertEqual(result[:3],['/usr/bin/ssh','-o','HostKeyAlias=frame.local'])
  self.assertEqual(result[-3: ],['steamos@10.42.0.25','python3','/receiver.py'])
  self.assertIn('StrictHostKeyChecking=yes',result)
  self.assertEqual(args[-3],'steamos@frame.local')
 def test_existing_ip_target_unchanged(self):
  args=['steamos@192.168.0.76','python3','/receiver.py']
  self.assertEqual(m.command(args,lambda h:self.fail('unexpected discovery')),['/usr/bin/ssh',*args])
 def test_rejects_shelllike_names_and_missing_user(self):
  for target in ['steamos@frame;evil.local','-oProxyCommand=bad@frame.local','frame.local']:
   with self.assertRaises(ValueError):m.command([target,'python3','/receiver.py'])
 def test_rejects_wrong_or_nonlocal_response(self):
  for reply in ['other.local\t10.42.0.5','frame.local\t127.0.0.1','frame.local\t224.0.0.1','frame.local\t0.0.0.0','frame.local\t8.8.8.8','frame.local\t10.0.0.2\nextra']:
   with patch.object(m.subprocess,'run',return_value=SimpleNamespace(stdout=reply)):
    with self.assertRaises(ValueError):m.resolve_ipv4('frame.local')
 def test_accepts_private_address_and_bounds_resolver(self):
  with patch.object(m.subprocess,'run',return_value=SimpleNamespace(stdout='frame.local\t10.42.0.25')) as run:
   self.assertEqual(m.resolve_ipv4('frame.local'),'10.42.0.25')
   self.assertEqual(run.call_args.kwargs['timeout'],5)
if __name__=='__main__':unittest.main()
