import unittest
from disk import Disk
from oft import OFT
from inputBuffer import InputBuffer
from outputBuffer import OutputBuffer
from fs import FS


class TestFS(unittest.TestCase):

    def setUp(self):
        """Set up a fresh FS instance before each test."""
        self.fs = FS()


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

    # def testCloseFile(self):
    #     """Test destroying a file."""
    #     # Create a file
    #     self.fs.create("del")
    #
    #     # Destroy the file
    #     result = self.fs.close(0)
    #     self.assertEqual(result, "file del destroyed")
    #
    #     # Verify the file is no longer in the directory
    #     dir_index = self.fs.disk.searchDirectory("delete_me.txt")
    #     self.assertIsNone(dir_index)
    #
    # def test_open_after_destroy(self):
    #     """Test that attempting to open a destroyed file raises an exception."""
    #     # Create and destroy a file
    #     self.fs.disk.create("oldfile.txt")
    #     self.fs.disk.destroy("oldfile.txt")
    #
    #     # Attempt to open the file
    #     with self.assertRaises(Exception) as context:
    #         self.fs.open("oldfile.txt")
    #     self.assertEqual(str(context.exception), "File does not exist")

    def test_create_duplicate_file(self):
        """Test creating a file with a duplicate name raises an exception."""
        # Create a file
        self.fs.disk.create("dupl")

        # Attempt to create the same file again
        with self.assertRaises(Exception) as context:
            self.fs.disk.create("dupl")
        self.assertEqual(str(context.exception), "Duplicate file")




if __name__ == "__main__":
    unittest.main()
