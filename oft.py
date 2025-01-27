
class OFT:
    def __init__(self):
        self.oft = [oftEntry()] * 10

class oftEntry:
    def __init__(self):
        self.buf = []
        self.position = -1
        self.size = 0
        self.descriptor = -1