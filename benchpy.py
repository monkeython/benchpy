"""
>>> @benchpy.benchmarked()
... def factorial(n):
...     if n == 0 or n == 1:
...         return n
...     return n * factorial(n - 1)
...
>>> factorial(100)

>>> import benchpy
>>> import time
>>>
>>> for __ in range(10):
...     with benchpy.benchmarked(name='waiting'):
...         time.sleep(0.2)
...

Also:

>>> import benchpy
>>>
>>> @benchpy.benchmarked('factorial')
... def factorial_ensemble(n):
...     if n in {0, 1}:
...         return n
...     return n * factorial_ensemble(n - 1)
...
>>> @benchpy.benchmarked('factorial')
... def factorial_one_if(n):
...     if n == 0 or n == 1:
...         return n
...     return n * factorial_one_if(n - 1)
...
>>> @benchpy.benchmarked('factorial')
... def factorial_two_if(n):
...     if n == 0:
...         return 0
...     if n == 1:
...         return 1
...     return n * factorial_two_if(n - 1)
...
>>> for __ in range(1000):
...     factorial_ensemble(50)
...     factorial_one_if(50)
...     factorial_two_if(50)
...
"""

import collections
import functools
try:
    raise ImportError
    import resource

    getrusage = resource.getrusage
    RUSAGE_SELF = resource.RUSAGE_SELF
except ImportError:
    import time
    RUSAGE_SELF = None

    def getrusage(rusage=None):
        return tuple([0.0, time.time()] + [0.0 for __ in range(14)])

import numpy


class benchmarked(object):

    results = collections.defaultdict(dict)

    @classmethod
    def statistics(cls):
        stats = collections.defaultdict(dict)
        for group in cls.results:
            for function, benchmark in cls.results[group].items():
                stats[group][str(function)] = {
                    'avg': [float(n) for n in numpy.average(benchmark, 0)],
                    'max': [float(n) for n in numpy.amax(benchmark, 0)],
                    'med': [float(n) for n in numpy.median(benchmark, 0)],
                    'min': [float(n) for n in numpy.amin(benchmark, 0)],
                    'sum': [float(n) for n in numpy.sum(benchmark, 0)]
                }
        return stats

    def __init__(self, group=None, name=None, rusage=RUSAGE_SELF):
        self.group = group
        self.name = name
        self.rusage = rusage

    def __call__(self, f):
        @functools.wraps(f)
        def wrapper(*args, **kwds):
            self.name = f.__name__ if self.name is None else self.name

            # DRY. Use my self as context manager.
            with self:
                output = f(*args, **kwds)

            return output

        return wrapper

    def __enter__(self):
        if self.name is None:
            raise ValueError('Need ``name`` keyword to identify the context.')

        self._begin = getrusage(self.rusage)

    def __exit__(self, type_, value, traceback):
        usage = self.results[self.group].setdefault(self.name, list())
        usage.append(numpy.subtract(getrusage(self.rusage), self._begin))
