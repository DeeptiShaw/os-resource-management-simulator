import unittest
from simulator import cpu, memory, banker, disk

class Tests(unittest.TestCase):
    def test_fcfs(self):
        self.assertAlmostEqual(cpu([5,3,8],'FCFS')['wait'],13/3)
    def test_single(self):
        self.assertEqual(cpu([1],'RR')['wait'],0)
    def test_bad_burst(self):
        with self.assertRaises(ValueError): cpu([0],'FCFS')
    def test_memory(self):
        self.assertEqual(memory([1,1,2],1,'LRU')['faults'],2)
    def test_bad_frames(self):
        with self.assertRaises(ValueError): memory([1],0,'FIFO')
    def test_safe(self):
        self.assertTrue(banker([1],[[1]],[[2]])['safe'])
    def test_unsafe(self):
        self.assertFalse(banker([0],[[1]],[[2]])['safe'])
    def test_bad_maximum(self):
        with self.assertRaises(ValueError): banker([1],[[2]],[[1]])
    def test_disk(self):
        self.assertEqual(disk(50,[50,60],'SSTF')['movement'],10)
    def test_bad_disk(self):
        with self.assertRaises(ValueError): disk(50,[200],'FCFS')

if __name__ == '__main__': unittest.main()
