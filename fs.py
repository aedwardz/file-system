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

    def bufToBlock(self, i:int, block:int) -> None:
        """
        Copies the buffer at entry i of the OFT
        onto disk at the given block
        :param i:
        :param block:
        :return:
        """
        buf = self.oft[i].buf
        self.disk[block] = buf

    def blockToBuf(self, i:int, block:int) -> None:
        """
        copies the block b on the disk into the oft buf
        at the specified index i
        :param i:
            entry index
        :param block:
            disk block
        :return:
            None
        """
        self.oft[i].buf = self.disk[block]



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
        blockPointerindex = entry.position // 512
        b, x = self.disk.getFD(entry.descriptor)
        block = self.disk[b][x].blockPointers[blockPointerindex]
        self.bufToBlock(i, block)
        #update file size in descriptor

        self.disk[b][x].size = entry.size


        #mark oft entry as free by setting current position to -1
        self.oft[i].position = -1

        return f"File {i} closed"


    def seek(self, i, p) -> str:
        """
        Changes block and current position of a file
        :param i:
            OFT index
        :param p:
            New position to be set to
        :return:
            Success String
        """
        if p > self.oft[i].size:
            raise Exception('current position is past the end of the file')


        currentBlock = self.oft[i].position // 512

        newBlock = p // 512

        if currentBlock != newBlock:
            #copy current buffer back to disk
            self.bufToBlock(i, currentBlock)
            #copy new block onto the entry
            self.blockToBuf(i, newBlock)

        self.oft[i].position = p
        return f'Current position is {p}'



























