class DBError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class InvalidArgument(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
