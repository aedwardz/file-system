import unittest
from oft import OFT


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.oft = OFT()


    def testSearchEmpty(self):
        self.assertEqual(self.oft.searchFreeEntry(), 0)

    def testSearchFull(self):
        for entry in self.oft.oft:
            entry.position = 0

        self.assertIsNone(self.oft.searchFreeEntry())


if __name__ == '__main__':
    unittest.main()
