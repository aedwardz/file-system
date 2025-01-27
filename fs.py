from disk import Disk
from inputBuffer import InputBuffer
from outputBuffer import OutputBuffer
from oft import OFT
class FS:
    def __init__(self):

        self.disk = Disk(100)
        self.oft = OFT()
        self.k = self.disk.k
        self.I = InputBuffer()
        self.O = OutputBuffer()

    def open(self, name):
        dirIndex = self.disk.searchDirectory(name)
        if not dirIndex:
            raise Exception('File does not exist')

        oftIndex = self.oft.searchFreeEntry()
        if oftIndex is None:
            raise Exception('Too many files open')

        self.oft[oftIndex].descriptor = dirIndex

        self.oft[oftIndex].position = 0
        b, i = self.disk.getFD(dirIndex)

        self.oft[oftIndex].size = self.disk[b][i].size

        return oftIndex














    def printDisk(self):
        for index, row in enumerate(self.disk.disk):
            print(f"Index {index}: {row}")













