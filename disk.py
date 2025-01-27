from fileDescriptor import FileDescriptor
from math import ceil
BLOCK_SIZE = 512
class Disk:
    def __init__(self, blocks:int):
        self.k = ceil(192/32) + 1
        self.blocks = blocks
        self.disk = [0] * blocks
        self.initializeDisk()

    def allocate_block(self):
        """Find a free block in the bitmap and allocate it."""
        # print(self.disk[0])
        for i in range(len(self.disk[0])):

            if self.disk[0][i] == 0:  # Free block
                self.disk[0][i] = 1  # Mark as used
                return i  # Return the bitmap index
        raise ValueError("No free blocks available.")


    def deallocate_block(self, block_index):
        """Free a previously allocated block."""
        if self.disk[0][block_index] == 1:  # Block is in use
            self.disk[0][block_index] = 0  # Mark as free
        else:
            raise ValueError(f"Block {block_index} is already free.")

    def initializeDisk(self) -> None:
        """
        Initializes the disk split up into the bitMap, File Descriptors, and the block content
        """
        self.disk[0] = [0] * 512
        for i in range(1, self.k):
            self.disk[i] = [FileDescriptor() for j in range(32)]

        for i in range(self.k):
            self.disk[0][i] = 1
        self.create_directory()

    def getFD(self, fdIndex):
        """Retrieve a file descriptor by index."""
        fdNum = 0
        #       #new file descriptor
        for i in range(1, self.k):
            for fd in self.disk[i]:
                if fdNum == fdIndex:
                    return i, fdNum
                fdNum += 1


    def create_directory(self):
        """Create a new directory."""
        # Find a free file descriptor block

        fd = self.disk[1][0]
          # Free descriptor
        fd.size = 0
        fd.is_directory = True
        fd.blockPointers.append(self.allocate_block()) # Allocate a block for children metadata
        block = fd.blockPointers[0]
        self.disk[block] = [(0,0) for i in range(512//8)]

    def searchDirectory(self, name):
        """

        :param name: name of the file to be searched for
        :return:
            returns None if file not found in directory
            reuturns the descriptor index if found
        """

        dirBlocks = self.disk[1][0].blockPointers
        for b in dirBlocks:
            for entry in self.disk[b]:
                if entry[0] == name:
                    return entry[1]
        return None


    def create(self, name):
        # search directory first
        directoryBlocks = self.disk[1][0].blockPointers
        for block in directoryBlocks:
            entries = self.disk[block]
            for entry in entries:
                if entry[0] == name:
                    raise Exception('Duplicate file')

        fdNum = -1
        #       #new file descriptor
        assigned = False
        for i in range(1, self.k):
            if not assigned:
                for fd in self.disk[i]:
                    fdNum += 1
                    if fd.size == -1:
                        fd.size = 0
                        assigned = True
                        break

        if not assigned:
            raise Exception("too many files")

        for block in directoryBlocks:
            entries = self.disk[block]
            for i in range(len(entries)):
                if entries[i][0] == 0:
                    entries[i] = (name, fdNum)
                    break

    def freeDescriptor(self, num):
        count = 0
        freed = False
        for b in range(1, self.k):
            if not freed:
                for fd in range(len(self.disk[b])):
                    if count == num:
                        self.disk[b][fd].size = -1
                        for block in self.disk[b][fd].blockPointers:
                            self.deallocate_block(block)
                        self.disk[b][fd].blockPointers = []
                        freed = True
                        break
                    count += 1

    def destroy(self, name):
        dirBlocks = self.disk[1][0].blockPointers
        #search directory for name

        for b in dirBlocks:
            for i in range(len(self.disk[b])):
                #if found, mark entry as free
                if self.disk[b][i][0] == name:
                    self.freeDescriptor(self.disk[b][i][1])
                    self.disk[b][i] = (0,0)
                    return f"file {name} destroyed"

        raise Exception('file does not exist')

    def __getitem__(self, item):
        return self.disk[item]

    def __setitem__(self, key, value):
        self.disk[key] = value

    def __len__(self):
        return len(self.disk)