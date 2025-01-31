
class OFT:
    def __init__(self):
        self.oft = [oftEntry() for i in range(3)]

    def __getitem__(self, item):
        return self.oft[item]

    def __setitem__(self, key, value):
        self.oft[key] = value

    def searchFreeEntry(self):
        """
        Searches the OFT for a free entry
        :return:
            index of the free entry if there is one,
            else None
        """
        for index, entry in enumerate(self.oft):
            if entry.position == -1:
                return index

        return None

class oftEntry():
    def __init__(self):
        self.buf = [0] * 512
        self.position = -1
        self.size = 0
        self.descriptor = -1
    def __repr__(self):
        if self.position == -1:
            return 'empty'
        else:
            return "occupied"
