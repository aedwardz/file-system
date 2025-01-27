class FileDescriptor:
    def __init__(self,  is_directory=False):
        self.size = -1
        self.blockPointers = []
        self.isDirectory = is_directory

    def __repr__(self):
        if self.size == -1:
            return 'Free'
        else:
            return f"FD size{self.size}"

class DirectoryDescriptor:
    def __init__(self):
        self.name = None
        self.index = None