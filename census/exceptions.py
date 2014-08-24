class APIKeyError(Exception):
    """Invalid API Key"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class CensusException(Exception):
    pass


class UnsupportedYearException(Exception):
    pass
