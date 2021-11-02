import unittest
import download_utilities as du

class GetSec_ReturnsCorrectFloat(unittest.TestCase):
    # get_sec should receive a string in 'x:xx.xxx' format, and return a float.
    def test_1(self):
        self.assertEqual(du.get_sec('1:55.487'), 115.487)
    def test_2(self):
        self.assertEqual(du.get_sec('0:52.912'), 52.912)

if __name__ == '__main__':
    unittest.main()