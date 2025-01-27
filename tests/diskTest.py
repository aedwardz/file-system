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
        disk = Disk(blocks)
        self.assertEqual(disk.blocks, blocks)
        self.assertEqual(disk.k, ceil(192/ 32) + 1)
        self.assertEqual(len(disk.disk), blocks)
        print(disk[0])

    def test_initializeDisk(self):
        """
        Test that the initializeDisk method correctly sets up the disk array.
        """
        blocks = 10
        d = 64
        disk = Disk(blocks)

        # Check bitmap initialization
        self.assertEqual(len(disk.disk[0]), 512)

        # Check file descriptors initialization
        for i in range(1, disk.k):
            self.assertEqual(len(disk.disk[i]), 32)
            self.assertTrue(all(isinstance(fd, FileDescriptor) for fd in disk.disk[i]))

        #check directory block
        self.assertEqual(disk[disk.k],[(0,0) for i in range(512//8)])
        # Check uninitialized blocks remain 0
        for i in range(disk.k+1, blocks):
            self.assertEqual(disk.disk[i], 0)

    def testAllocate(self):
        blocks = 100
        disk = Disk(blocks)

        self.assertEqual(disk.disk[0].count(1), 8)
        disk.allocate_block()
        self.assertEqual(disk.disk[0].count(1), 9)


if __name__ == '__main__':
    unittest.main()
