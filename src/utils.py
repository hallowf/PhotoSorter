def threadsafe_generator(f):
    def g(*a, **kw):
        return ThreadsafeIter(f(*a, **kw))
    return g

class ThreadsafeIter():
    def __init__(self, it):
        self.it = it
        self.lock = threading.lock()

    def __iter__(self):
        return self

    def next(self):
        with self.lock:
            return self.it.next()
