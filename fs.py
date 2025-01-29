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
        Writes n bytes from memory M starting at position m to the open file at OFT index i.
        Returns the number of bytes written.
        """
        # Check if file is open
        if self.oft[i].position == -1:
            raise Exception("File is not open")

        entry = self.oft[i]
        bytes_written = 0
        max_file_size = 3 * 512  # Maximum file size in basic version (3 blocks)

        while bytes_written < n and entry.position < max_file_size:
            # Calculate position within current buffer
            offset = entry.position % 512
            remaining_in_block = 512 - offset

            # Calculate bytes to write in this iteration
            bytes_to_write = min(n - bytes_written, remaining_in_block,
                                 max_file_size - entry.position)

            # Copy bytes from memory to buffer
            for j in range(bytes_to_write):
                try:
                    entry.buf[offset + j] = self.M[m + bytes_written + j]
                except IndexError:
                    break  # Stop if we exceed memory bounds

            # Update positions and counters
            entry.position += bytes_to_write
            bytes_written += bytes_to_write

            # Update file size if we've extended it
            if entry.position > entry.size:
                entry.size = entry.position
                # Update descriptor size immediately
                b, fd_idx = self.disk.getFD(entry.descriptor)
                self.disk[b][fd_idx].size = entry.size

            # If buffer is full, flush to disk and load next block
            if (entry.position % 512) == 0 and entry.position < max_file_size:
                # Write current buffer to disk
                current_block_idx = (entry.position // 512) - 1
                b, fd_idx = self.disk.getFD(entry.descriptor)
                desc = self.disk[b][fd_idx]

                # Allocate new block if needed
                if current_block_idx + 1 >= len(desc.blockPointers):
                    if len(desc.blockPointers) >= 3:
                        break  # Max blocks reached
                    new_block = self.disk.allocate_block()
                    desc.blockPointers.append(new_block)

                # Write current buffer to disk
                current_block = desc.blockPointers[current_block_idx]
                self.bufToBlock(i, current_block)

                # Load next block into buffer
                next_block = desc.blockPointers[current_block_idx + 1]
                self.blockToBuf(i, next_block)

        # Final buffer flush if we're at end of file
        if entry.position % 512 != 0:
            current_block_idx = entry.position // 512
            b, fd_idx = self.disk.getFD(entry.descriptor)
            current_block = self.disk[b][fd_idx].blockPointers[current_block_idx]
            self.bufToBlock(i, current_block)

        return f"Wrote {bytes_written} bytes to file {i}"






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



























