# kvec_file.py - File representation in KVEC


class KVFile(object):
    pass


class KVSrcFile(KVFile):
    pass


class KVFortranFile(KVSrcFile):
    def __init__(self, filename, srclines):
        self.filename = filename
        self.srclines = srclines
        self.compilecmd = None
        self.log = []

