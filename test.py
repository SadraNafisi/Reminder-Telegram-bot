import unittest
from pattern import is_outdated, is_time_expired
from translation import translate_with_regex
from datetime import datetime
class pattern_test(unittest.TestCase):
    def test_is_outdated(self):
        self.assertTrue(is_outdated('2000/10/10'))
        self.assertFalse(is_outdated(datetime.now().date()))
        self.assertFalse(is_outdated('2050/10/10'))
    def test_is_time_expired(self):
        # self.assertTrue(is_time_expired('2024/5/23','12:23:23'))
        self.assertFalse(is_time_expired(datetime.now().date(),datetime.now().time()))

class translation_test(unittest.TestCase):
    def test_translate_with_regex(self):
        # self.assertEqual(translate_with_regex('The following word is ^*that*^','fa'),'کلمه زیر that است')
if __name__ == '__main__':
    unittest.main()
