class DirMissing(Exception):
    """docstring"""
    def __init__(self, message, errors=None):
        super().__init__(message)


class OutDirNotEmpty(Exception):
    """docstring"""
    def __init__(self, message, errors=None):
        super().__init__(message)


class WhyWouldYou(Exception):
    """docstring for WhyWouldYou."""

    def __init__(self, message, errors=None):
        super().__init__(message)
