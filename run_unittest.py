from unit_test import MyselfTestCase, MyselfTestCase_Async

from unittest import TestSuite, TestLoader, TextTestRunner

if __name__ == "__main__":
    test_suit = TestSuite()
    
    # myself.py
    test_suit.addTest(TestLoader().loadTestsFromTestCase(MyselfTestCase))
    test_suit.addTest(TestLoader().loadTestsFromTestCase(MyselfTestCase_Async))

    with open("unittest_result.log", mode="w") as log_file:
        TextTestRunner(stream=log_file, verbosity=2).run(test_suit)