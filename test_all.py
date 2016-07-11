
import unittest


class TestNothing(unittest.TestCase):

    def test_abc(self):
        self.assertEqual('foo'.upper(), 'FOO')


if __name__ == '__main__':
    unittest.main()
