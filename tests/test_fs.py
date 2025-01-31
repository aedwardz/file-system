import unittest
from disk import Disk
from oft import OFT, oftEntry
from fs import FS


class TestFS(unittest.TestCase):

    def setUp(self):
        """Set up a fresh FS instance before each test."""
        self.fs = FS()

    def testBufToBlock(self):
        self.fs.create('tone')

        self.fs.oft[1].buf = [1,2,3,4]

        self.fs.bufToBlock(1, 10)

        self.assertEqual(self.fs.disk[10], [1,2,3,4])

    def testBlockToBuf(self):
        i = 1
        b = 10

        self.fs.disk[b] = [1,2,3,4]
        self.fs.blockToBuf(i, b)
        self.assertEqual(self.fs.oft[i].buf, [1,2,3,4])





    def testAllocateWhenOpen(self):
        self.fs.create('tone')
        b, i = self.fs.disk.getFD(self.fs.disk.searchDirectory('tone'))
        self.assertEqual(0, self.fs.disk[b][i].size)
        self.fs.open('tone')
        b, i = self.fs.disk.getFD(self.fs.disk.searchDirectory('tone'))
        self.assertEqual(1, len(self.fs.disk[b][i].blockPointers))

    def testCopyBuffer(self):
        self.fs.create('jen')
        b, i = self.fs.disk.getFD(self.fs.disk.searchDirectory('jen'))
        self.fs.disk[b][i].blockPointers.append(self.fs.disk.allocate_block())
        self.fs.disk[b][i].size = 1
        content = [1]
        block = self.fs.disk[b][i].blockPointers[0]
        print(block)

        self.fs.disk[block] = content
        print(self.fs.disk[block])
        entryNum = self.fs.open('jen')
        print(self.fs.oft[entryNum].buf)
        self.assertEqual(content, self.fs.oft[entryNum].buf)

    def test_open_file_not_exist(self):
        """Test that opening a non-existent file raises an exception."""
        with self.assertRaises(Exception) as context:
            self.fs.open("non")
        self.assertEqual(str(context.exception), "File does not exist")

    def test_open_too_many_files(self):
        """Test that opening too many files raises an exception."""
        # Create the maximum number of OFT entries
        for i in range(len(self.fs.oft.oft)):
            self.fs.oft[i].position = 0  # Mark all OFT entries as in use

        self.fs.disk.create('file')
        # Attempt to open a file
        with self.assertRaises(Exception) as context:
            self.fs.open("file")
        self.assertEqual(str(context.exception), "Too many files open")
    #
    def test_open_valid_file(self):
        """Test that opening a valid file returns the correct OFT index."""
        # Create a file in the directory
        fs = FS()
        fs.disk.create("test")

        # Open the file
        oft_index = fs.open("test")

        # Verify that the OFT entry is updated
        self.assertEqual(fs.oft[oft_index].position, 0)
        self.assertEqual(fs.oft[oft_index].descriptor,
                         fs.disk.searchDirectory("test"))
    #
    def test_create_and_open_file(self):
        """Test creating and then opening a file."""
        # Create a new file
        self.fs.disk.create("new")

        # Verify that the file is in the directory
        dir_index = self.fs.disk.searchDirectory("new")
        self.assertIsNotNone(dir_index)

        # Open the newly created file
        oft_index = self.fs.open("new")
        self.assertEqual(self.fs.oft[oft_index].descriptor, dir_index)

    def test_create_duplicate_file(self):
        """Test creating a file with a duplicate name raises an exception."""
        # Create a file
        self.fs.disk.create("dupl")

        # Attempt to create the same file again
        with self.assertRaises(Exception) as context:
            self.fs.disk.create("dupl")
        self.assertEqual(str(context.exception), "Duplicate file")


    def testCloseOneFile(self):
        self.fs.create("tone")
        self.fs.open('tone')
        self.fs.close(0)

        self.assertTrue([True if x.position == -1 else False for x in self.fs.oft])

    def testBasicRead(self):
        self.fs.create("tone")
        b, i = self.fs.disk.getFD(self.fs.disk.searchDirectory("tone"))
        self.fs.disk[b][i].blockPointers.append(self.fs.disk.allocate_block())
        self.fs.disk[b][i].size = 1
        block = self.fs.disk[b][i].blockPointers[0]

        self.fs.disk[block][0] = 1
        self.fs.disk[block][1] = 2
        self.fs.disk[block][2] = 3
        self.fs.disk[block][3] = 4
        self.fs.disk[block][4] = 5
        self.fs.open('tone')
        self.assertEqual(self.fs.read(0, 0, 5), "5 bytes read from 1")
        expected = [1,2,3,4, 5] + [0 for i in range(512-5)]
        self.assertEqual(len(expected), 512)
        self.assertEqual(self.fs.M, expected)
        self.assertEqual(self.fs.oft[0].position, 5)
    def testReadBetweenBuffers(self):
        self.fs.create("tone")
        b, i = self.fs.disk.getFD(self.fs.disk.searchDirectory("tone"))
        self.fs.disk[b][i].blockPointers.append(self.fs.disk.allocate_block())
        self.fs.disk[b][i].blockPointers.append(self.fs.disk.allocate_block())
        self.fs.disk[b][i].size = 1
        block1 = self.fs.disk[b][i].blockPointers[0]
        block2 = self.fs.disk[b][i].blockPointers[1]


        self.fs.disk[block1]  = [0 for i in range(512-5)] + [1,2,3,4,5]
        self.fs.disk[block2] = [6,7,8,9,10] + [0 for i in range(512-5)]
        self.fs.open('tone')
        self.fs.oft[0].position = 507
        self.assertEqual(self.fs.read(0,0,10), "10 bytes read from 1")
        self.assertEqual(self.fs.M, [1,2,3,4,5,6,7,8,9,10] + [0 for i in range(502)])

    def testBasicWrite(self):
        self.fs.create("tone")
        self.fs.open("tone")

        # Prepare data in memory M to write
        self.fs.M = [1, 2, 3, 4, 5] + [0 for _ in range(512 - 5)]

        # Write 5 bytes from memory M starting at index 0
        self.assertEqual(self.fs.write(0, 0, 5), "5 bytes written to 1")

        # Ensure that position has been updated
        self.assertEqual(self.fs.oft[0].position, 5)

        # Ensure the data was correctly written to disk
        b, i = self.fs.disk.getFD(self.fs.disk.searchDirectory("tone"))
        block = self.fs.disk[b][i].blockPointers[0]

        expected = [1, 2, 3, 4, 5] + [0 for _ in range(512 - 5)]
        self.assertEqual(self.fs.oft[0].buf, expected)

        # Ensure file size is updated correctly
        self.assertEqual(self.fs.oft[0].size, 5)

    def testWriteUnopenedFile(self):
        self.fs.create('tone')
        self.fs.write_memory(0, "hello")

        with self.assertRaises(Exception):
            self.fs.write(0,0,5)
    def testWriteBetweenBuffers(self):
        self.fs.create("tone")
        self.fs.open("tone")

        # Prepare data in memory M to write
        self.fs.M = [5] * 512
        self.fs.oft[0].position = 1
        blocks = self.fs.disk.getFDBlocks(self.fs.oft[0].descriptor)
        print(blocks)
        # Write 5 bytes from memory M starting at index 0
        self.assertEqual(self.fs.write(0, 0, 512), "512 bytes written to 1")
        blocks = self.fs.disk.getFDBlocks(self.fs.oft[0].descriptor)
        print(blocks)

        # Ensure that position has been updated
        self.assertEqual(self.fs.oft[0].position, 513)
        # print(self.fs.disk[8])
        self.assertEqual(self.fs.disk[blocks[0]], [0] + [5 for i in range(511)])
        self.assertEqual(self.fs.oft[0].buf, [5] + [0 for i in range(511)])

        self.assertEqual(self.fs.oft[0].size, 513)
    def testFullWrite(self):
        self.fs.create('tone')
        self.fs.open('tone')
        self.fs.M = [5 for i in range(512)]
        self.fs.write(0,0,512)
        self.fs.write(0, 0, 512)
        self.fs.write(0,0,500)
        self.fs.write(0,0,30)
        entry = self.fs.oft[0]
        print(entry.size)
        self.assertEqual(entry.size, 1536)
        self.assertEqual(self.fs.write(0,0,5), "Maximum file storage reached")


    def testSeek(self):
        self.fs.create("tone")
        self.fs.open("tone")
        self.fs.write_memory(0,"h"*512)
        self.fs.write(0,0,512)
        self.fs.write(0, 0, 512)
        self.assertEqual(self.fs.seek(0, 3), "Current position is 3")


        with self.assertRaises(Exception):
            self.fs.seek(0,1400)

    def testSeek(self):
        self.fs.create("tone")
        self.fs.open("tone")
        self.fs.write_memory(0, "h" * 512)
        self.fs.write(0, 0, 300)
        self.assertEqual(self.fs.seek(0, 279), "Current position is 279")
    def testDirectory(self):
        self.fs.create("tone")
        self.fs.create("is")
        self.fs.create('tired')
        print()
        print("Before write")
        self.fs.directory()
        self.fs.write_memory(0, "hello")
        self.fs.open('tone')
        print("\nAfter Writing 5 bytes:")
        self.fs.write(0, 0, 5)
        self.fs.directory()





if __name__ == "__main__":
    unittest.main()
