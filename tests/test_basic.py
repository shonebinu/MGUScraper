import unittest


class TestBasic(unittest.TestCase):
    def test_true_equals_true(self):
        self.assertTrue(True, "True is not equal to True")


if __name__ == "__main__":
    unittest.main()
