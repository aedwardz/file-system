from disk import Disk
from inputBuffer import InputBuffer
from outputBuffer import OutputBuffer
from oft import OFT
class FS:
    def __init__(self):

        self.disk = Disk(100)
        self.oft = OFT()
        self.k = self.disk.k
        self.M = [0] * 512

    def bufToBlock(self, i:int, block:int) -> None:
        """
        Copies the buffer at entry i of the OFT
        onto disk at the given block
        :param i:
        :param block:
        :return:
        """
        buf = self.oft[i].buf
        self.disk[block] = buf.copy()

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
        self.oft[i].buf = self.disk[block].copy()

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

    def read(self, i: int, m: int, n: int) -> str:
        """
        Reads n bytes from the open file at OFT index i into memory M starting at location m.
        :param i: OFT index of the open file
        :param m: Starting location in memory M
        :param n: Number of bytes to read
        :return: Success message with the number of bytes read
        """


        entry = self.oft[i]
        blocks = self.disk.getFDBlocks(entry.descriptor)
        bpIndex = entry.position // 512
        startPos = entry.position
        startingBlock = blocks[bpIndex]
        offset = entry.position % 512
        mIndex = m
        bytesRead = 0

        for block in blocks[bpIndex:]:
            if block != startingBlock:
                self.blockToBuf(i, block)
            for j in range(offset, 512):
                byte = self.oft[i].buf[j]
                self.M[mIndex] = byte
                bytesRead += 1
                if bytesRead == n:
                    self.oft[i].position = startPos + n
                    return "all bytes read"
                mIndex += 1
            offset = 0
            self.bufToBlock(i, block)





    def write(self, i: int, m: int, n: int) -> str:
        """
        Writes n bytes from memory M starting at location m into the open file at OFT index i,
        starting at the current position. A file can have a maximum of 3 allocated blocks.
        :param i: OFT index of the open file
        :param m: Starting location in memory M
        :param n: Number of bytes to write
        :return: Success message with the number of bytes written or an error if max blocks exceeded.
        """

        entry = self.oft[i]
        blocks = self.disk.getFDBlocks(entry.descriptor)
        bpIndex = entry.position // 512  # Block index in file
        startPos = entry.position  # Track the initial position
        startingBlock = blocks[bpIndex] if bpIndex < len(blocks) else None
        offset = entry.position % 512  # Offset within block
        mIndex = m
        bytesWritten = 0

        while bytesWritten < n:
            self.oft[i].buf[offset] = self.M[mIndex]
            offset += 1
            self.oft[i].position += 1
            mIndex += 1
            bytesWritten += 1
            if bytesWritten == n:
                if self.oft[i].position > self.oft[i].size:
                    size = self.oft[i].size = self.oft[i].position
                    b, x = self.disk.getFD(self.oft[i].descriptor)
                    self.disk[b][x].size = size
                    self.oft[i].size = size
                return f"{n} bytes written"

            if offset == 512:
                #switch buffers
                offset = 0
                self.bufToBlock(i, startingBlock)
                bpIndex += 1
                if bpIndex == len(blocks):
                    if len(blocks) == 3:
                        return f"{bytesWritten} bytes written"
                    else:
                        b, x = self.disk.getFD(entry.descriptor)
                        self.disk[b][x].blockPointers.append(self.disk.allocate_block())
                        blocks = self.disk.getFDBlocks(entry.descriptor)
                        startingBlock = blocks[bpIndex]
                        self.blockToBuf(i, startingBlock)










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



























