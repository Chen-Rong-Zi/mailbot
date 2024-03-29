class UpdateConfigError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'UpdateConfigError: {self.message}'

class BaseTokenError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'BaseTokenError: {self.message}'
