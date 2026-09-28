import importlib.util, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('receiver',Path(__file__).resolve().parents[1]/'tools/frame-input-bridge/receiver.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Fake:
 def __init__(self):self.events=[]
 def key(self,*x):self.events.append(('key',*x))
 def emit(self,*x):self.events.append(('event',*x))
 def release(self):self.events.append(('release',))
class Protocol(unittest.TestCase):
 def setUp(self):self.k=Fake();self.m=Fake()
 def test_route(self):
  for line in ['K 30 1','K 30 0','B 272 1','M -4 7','W 0 -1']:m.dispatch(line,self.k,self.m)
  self.assertEqual(self.k.events,[('key',30,1),('key',30,0)])
  self.assertEqual(self.m.events,[('key',272,1),('event',2,0,-4),('event',2,1,7),('event',2,8,-1)])
 def test_invalid_cannot_inject(self):
  for line in ['K 0 1','K 256 1','K 30 2','B 30 1','B 277 1','M 9999 0','W 0 121','Q','K 30 1 extra']:
   with self.assertRaises(ValueError):m.dispatch(line,self.k,self.m)
  self.assertEqual(self.k.events+self.m.events,[])
 def test_release_and_heartbeat(self):
  m.dispatch('R',self.k,self.m);self.assertEqual(self.k.events,self.m.events)
  self.assertEqual(m.dispatch('P',self.k,self.m),'P')
class HeldKeys(unittest.TestCase):
 def test_held_keys_release_once(self):
  d=m.Device.__new__(m.Device);d.held=set();events=[];d.emit=lambda *x:events.append(x)
  d.key(30,1);d.key(30,1);d.key(31,1);d.release();d.release()
  self.assertEqual(len(events),4)
  self.assertEqual(d.held,set())
  self.assertIn((1,30,0),events);self.assertIn((1,31,0),events)
if __name__ == '__main__': unittest.main()
