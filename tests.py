import unittest
from a1 import CommandInterface

# easier way for me to document my unit tests: 
# python3 -m unittest tests.py
class TestHeapGoCommand(unittest.TestCase):
    def setUp(self):
        self.ci = CommandInterface()

    def test_valid_input(self):
        result = self.ci.cmd_heapgo("5.5 [[('w', 2)]]")
        self.assertEqual(result, 1)

    def test_missing_gamestate(self):
        result = self.ci.cmd_heapgo("5.5")
        self.assertEqual(result, 0)

    def test_missing_komi(self):
        result = self.ci.cmd_heapgo("[[('w', 2)]]")
        self.assertEqual(result, 0)

    def test_random_text(self):
        result = self.ci.cmd_heapgo("abc [def ghi")
        self.assertEqual(result, 0)

    def test_komi_limit(self):
        result1 = self.ci.cmd_heapgo("-100 [[('w', 2)]]")
        result2 = self.ci.cmd_heapgo("100 [[('w', 2)]]")
        self.assertEqual(result1, 0)
        self.assertEqual(result2, 0)

    def test_gamestate_rigorous(self):
        onelist = self.ci.cmd_heapgo("5.5 [('w', 2)]")
        self.assertEqual(onelist, 0)

        no_tuple = self.ci.cmd_heapgo("5.5 [[0]]")
        self.assertEqual(no_tuple, 0)

        no_value = self.ci.cmd_heapgo("5.5 [[('w')]]")
        self.assertEqual(no_value, 0)

        no_color = self.ci.cmd_heapgo("5.5 [[('a', 4)]]")
        self.assertEqual(no_color, 0)

        out_of_range1 = self.ci.cmd_heapgo("5.5 [[('w', -0)]]")
        out_of_range2 = self.ci.cmd_heapgo("5.5 [[('w', 21)]]")
        self.assertEqual(out_of_range1, 0)
        self.assertEqual(out_of_range2, 0)

        heaps_11 = "5.5 " + str([[('w', 1)]] * 11)
        print(heaps_11)
        result1 = self.ci.cmd_heapgo(heaps_11)
        self.assertEqual(result1, 0)

        tokens_11 = "5.5 [" + str([('w', 1)] * 11) + "]"
        print(tokens_11)
        result2 = self.ci.cmd_heapgo(heaps_11)
        self.assertEqual(result2, 0)

    
if __name__ == "__main__":
    unittest.main()