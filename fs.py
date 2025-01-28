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

    def create(self, name):
        return self.disk.create(name)

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
        if self.disk[b][i].size == 0:
            self.disk[b][i].blockPointers.append(self.disk.allocate_block())
        else:
            blockPointers = self.disk[b][i].blockPointers


            self.oft[oftIndex].buf = self.disk[blockPointers[0]]

        return oftIndex

    def close(self, i):
        """
        Closes a file on the OFT
        :param i:
        :return:
        """
        #copy buffer to disk
        entry = self.oft[i]
        block = entry.descriptor.blockPointers[0]
        self.disk[block] = entry.buf

        #update file size in descriptor

        b, i = self.disk.getFD(entry.descriptor)
        self.disk[b][i].size = entry.size


        #mark oft entry as free by setting current position to -1
        self.oft[i].position = -1

        return f"File {i} closed"




























