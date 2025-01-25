import unittest
from disk import Disk
from math import ceil
from fileDescriptor import FileDescriptor


class MyTestCase(unittest.TestCase):
    def test_initialization(self):
        """
        Test that the Disk class initializes the attributes correctly.
        """
        blocks = 100
        d = 64
        disk = Disk(blocks, d)
        self.assertEqual(disk.d, d)
        self.assertEqual(disk.blocks, blocks)
        self.assertEqual(disk.k, ceil(d / 32) + 1)
        self.assertEqual(len(disk.disk), blocks)

    def test_initializeDisk(self):
        """
        Test that the initializeDisk method correctly sets up the disk array.
        """
        blocks = 10
        d = 64
        disk = Disk(blocks, d)

        # Check bitmap initialization
        self.assertEqual(len(disk.disk[0]), 512)
        self.assertTrue(all(bit == 0 for bit in disk.disk[0]))

        # Check file descriptors initialization
        for i in range(1, disk.k):
            self.assertEqual(len(disk.disk[i]), 32)
            self.assertTrue(all(isinstance(fd, FileDescriptor) for fd in disk.disk[i]))

        # Check uninitialized blocks remain 0
        for i in range(disk.k, blocks):
            self.assertEqual(disk.disk[i], 0)

if __name__ == '__main__':
    unittest.main()
