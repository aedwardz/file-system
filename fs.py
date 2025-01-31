from disk import Disk

from oft import OFT
class FS:
    def __init__(self):

        self.disk = Disk(64)
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

    def create(self, name:str):
        self.disk.create(name)
        return f"File {name} created"


    def destroy(self, name:str):
        return self.disk.destroy(name)


    def isOpen(self, name:str) ->bool:
        #get the file descriptor of the file
        #check if that descriptor is in the oft
        #if it is in, check the position that it is -1
        #if not, return False
        index = self.disk.searchDirectory(name)
        if not index:
            return False

        for entry in self.oft.oft:
            if entry.descriptor == index and entry.position != -1:
                return True

        return False

    def open(self, name:str):
        if self.isOpen(name):
            raise Exception("Error: file is already open")
        dirIndex = self.disk.searchDirectory(name)
        if not dirIndex:
            raise Exception('Error: File does not exist')

        oftIndex = self.oft.searchFreeEntry()
        if oftIndex is None:
            raise Exception('Error: Too many files open')

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

    def close(self, i:int):
        """
        Closes a file on the OFT
        :param i:
        :return:
        """
        #copy buffer to disk
        entry = self.oft[i]
        if entry.position == -1:
            raise Exception('Error: File is not open')
        blockPointerindex = entry.position // 512
        b, x = self.disk.getFD(entry.descriptor)
        block = self.disk[b][x].blockPointers[blockPointerindex]
        self.bufToBlock(i, block)
        #update file size in descriptor

        self.disk[b][x].size = entry.size


        #mark oft entry as free by setting current position to -1
        self.oft[i].position = -1

        return f"File {i+1} closed"

    def read(self, i: int, m: int, n: int) -> str:
        """
        Reads n bytes from the open file at OFT index i into memory M starting at location m.
        :param i: OFT index of the open file
        :param m: Starting location in memory M
        :param n: Number of bytes to read
        :return: Success message with the number of bytes read
        """


        entry = self.oft[i]
        if entry.position == -1:
            raise Exception("Error: File not open")
        blocks = self.disk.getFDBlocks(entry.descriptor)
        bpIndex = entry.position // 512
        startPos = entry.position
        startingBlock = blocks[bpIndex]
        offset = entry.position % 512
        mIndex = m
        bytesRead = 0
        trueData = 0
        for block in blocks[bpIndex:]:
            if block != startingBlock:
                self.blockToBuf(i, block)
            for j in range(offset, 512):
                byte = self.oft[i].buf[j]
                self.M[mIndex] = byte
                bytesRead += 1
                if byte != 0:
                    trueData += 1
                if bytesRead == n:
                    self.oft[i].position = startPos + n
                    return f"{trueData} bytes read from {i+1}"
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
        if entry.position == -1:
            raise Exception('Error: File must be opened first')
        blocks = self.disk.getFDBlocks(entry.descriptor)
        bpIndex = entry.position // 512  # Block index in file
        startPos = entry.position  # Track the initial position
        startingBlock = blocks[bpIndex] if bpIndex < len(blocks) else None
        if not startingBlock:
            if len(blocks) == 3:
                return "Maximum file storage reached"
            else:
                b, x = self.disk.getFD(entry.descriptor)
                self.disk[b][x].blockPointers.append(self.disk.allocate_block())
                blocks = self.disk.getFDBlocks(entry.descriptor)
                startingBlock = blocks[bpIndex]
                self.bufToBlock(i, blocks[bpIndex-1])
                self.blockToBuf(i, blocks[bpIndex])


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
                return f"{n} bytes written to {i+1}"

            if offset == 512:
                #switch buffers
                offset = 0
                self.bufToBlock(i, startingBlock)
                bpIndex += 1
                if bpIndex == len(blocks):
                    if len(blocks) == 3:
                        if self.oft[i].position > self.oft[i].size:
                            size = self.oft[i].size = self.oft[i].position
                            b, x = self.disk.getFD(self.oft[i].descriptor)
                            self.disk[b][x].size = size
                            self.oft[i].size = size
                        return f"{bytesWritten} bytes written to {i+1}"
                    else:
                        b, x = self.disk.getFD(entry.descriptor)
                        self.disk[b][x].blockPointers.append(self.disk.allocate_block())
                        blocks = self.disk.getFDBlocks(entry.descriptor)
                        startingBlock = blocks[bpIndex]
                        self.blockToBuf(i, startingBlock)

    def write_memory(self, m:int, s:str):
        """
        Writes a string to self.M
        :param m: starting index of self.M
        :param s: string
        :return: None
        """
        mIndex = m
        for char in s:
            self.M[mIndex] = char
            mIndex += 1
        return f"{len(s)} bytes written to M"

    def read_memory(self, m:int, n:int):

        for i in range(m, m+n):
            if self.M[i] == 0:
                continue
            print(self.M[i], end= " ")
        print()

    def seek(self, i:int, p:int) -> str:
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
            raise Exception('Error: current position is past the end of the file')

        blocks = self.disk.getFDBlocks(self.oft[i].descriptor)
        currIndex = self.oft[i].position // 512
        if currIndex >= len(blocks):
            newBlock = blocks[p // 512]
            self.blockToBuf(i, newBlock)
            self.oft[i].position = p
            return f'Current position is {p}'

        else:
            currentBlock = blocks[self.oft[i].position // 512]


            newBlock = blocks[p // 512]

            if currentBlock != newBlock:
                #copy current buffer back to disk
                self.bufToBlock(i, currentBlock)
                #copy new block onto the entry
                self.blockToBuf(i, newBlock)

            self.oft[i].position = p
            return f'Current position is {p}'

    def directory(self):
        dirBlocks = self.disk.getFDBlocks(0)
        for block in dirBlocks:
            for i in range(len(self.disk[block])):
                name = self.disk[block][i][0]
                if name != 0:
                    index = self.disk[block][i][1]

                    b, x = self.disk.getFD(index)
                    size = self.disk[b][x].size
                    print(f"{name}-{size}", end=" ")
        print()