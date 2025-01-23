from fileDescriptor import FileDescriptor
from math import ceil
BLOCK_SIZE = 512
class Disk:
    def __init__(self, blocks:int, d:int):
        self.d = d
        self.k = ceil(d/32) + 1
        self.blocks = blocks
        self.disk = [0] * blocks
        self.initializeDisk()

    def initializeDisk(self) -> None:
        """
        Initializes the disk split up into the bitMap, File Descriptors, and the block content
        """
        self.disk[0] = [0] * self.blocks
        for i in range(1, self.k):
            self.disk[i] = [FileDescriptor() for j in range(32)]








if __name__ == "__main__":
    #
    d = Disk(100, 200)
    for row in d.disk:
        print(row)

