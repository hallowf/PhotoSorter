class DirMissing(Exception):
    """docstring"""
    pass

class OutDirNotEmpty(Exception):
    """docstring"""
    pass

class WhyWouldYou(Exception):
    """docstring for WhyWouldYou."""

    def __init__(self, arg):
        super(WhyWouldYou, self).__init__()
        self.arg = arg
