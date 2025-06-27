import unittest
from Test_EDIFiles import Test834Message


def load_tests_in_order():
    suite = unittest.TestSuite()

    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(Test834Message))

    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(load_tests_in_order())
