from functools import wraps

from .exceptions import UnsupportedYearException


def supported_years(*years):
    """
    Decorator verifies requested year is available from the specified years
    argument.
    """
    def inner(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            year = kwargs.get('year', self.default_year)
            if int(year) not in years:
                raise UnsupportedYearException('geography is not available in %s' % year)
            return func(self, *args, **kwargs)
        return wrapper
    return inner
