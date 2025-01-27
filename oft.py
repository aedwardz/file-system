
class OFT:
    def __init__(self):
        self.oft = [oftEntry()] * 192

    def __getitem__(self, item):
        return self.oft[item]

    def __setitem__(self, key, value):
        self.oft[key] = value

    def searchFreeEntry(self):
        for index, entry in enumerate(self.oft):
            if entry.position == -1:
                return index

        return None



class oftEntry:
    def __init__(self):
        self.buf = []
        self.position = -1
        self.size = 0
        self.descriptor = -1
