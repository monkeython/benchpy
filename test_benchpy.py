import collections
import time
import unittest

import benchpy

class BenchmarkTestCase(unittest.TestCase):

    def test_statistics(self):
        for __ in range(5):
            with benchpy.benchmarked(name='test'):
                time.sleep(0.2)
        stats = benchpy.benchmarked.statistics()
        self.assertIn('test', stats[None])

    def test_decorator(self):
        @benchpy.benchmarked()
        def t():
            pass

        for __ in range(10):
            t()

        self.assertEquals(10, len(benchpy.benchmarked.results[None]['t']))

    def test_context_manager(self):
        with benchpy.benchmarked(name='test'):
            pass

        self.assertEquals(1, len(benchpy.benchmarked.results[None]['test']))

        with self.assertRaises(ValueError):
            with benchpy.benchmarked():
                pass

    def tearDown(self):
        benchpy.benchmarked.results = collections.defaultdict(dict)

if __name__ == '__main__':
    unittest.main()
