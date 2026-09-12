import io
import unittest
from contextlib import redirect_stdout, redirect_stderr

from a1 import CommandInterface

# easier way for me to document my unit tests:
# python3 -m unittest tests.py


def run(ci, cmd_name, cmd_args=""):
    """
    Run a command exactly the way the grader does (through process_command)
    and return (output_lines, status_string). This matters because
    process_command swallows exceptions and turns them into '= -1',
    so a command can crash and still look correct from the outside.
    """
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        ci.process_command(cmd_name, cmd_args)
    lines = out.getvalue().splitlines()
    return lines[:-1], lines[-1]


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
        result1 = self.ci.cmd_heapgo(heaps_11)
        self.assertEqual(result1, 0)

        tokens_11 = "5.5 [" + str([('w', 1)] * 11) + "]"
        result2 = self.ci.cmd_heapgo(tokens_11)
        self.assertEqual(result2, 0)


# ===========================================================================
# Additional heapgo cases
# ===========================================================================
class TestHeapGoBoundaries(unittest.TestCase):
    """The accepting side of every range. Rejection tests alone can pass
    with an off-by-one that rejects legal games too."""

    def setUp(self):
        self.ci = CommandInterface()

    def test_exactly_10_heaps_ok(self):
        self.assertEqual(self.ci.cmd_heapgo("0.5 " + str([[('w', 1)]] * 10)), 1)

    def test_exactly_10_tokens_ok(self):
        self.assertEqual(self.ci.cmd_heapgo("0.5 [" + str([('w', 1)] * 10) + "]"), 1)

    def test_token_value_endpoints_ok(self):
        self.assertEqual(self.ci.cmd_heapgo("0.5 [[('w', 1), ('b', 20)]]"), 1)

    def test_komi_endpoints_ok(self):
        self.assertEqual(self.ci.cmd_heapgo("-99.5 [[('w', 1)]]"), 1)
        self.assertEqual(self.ci.cmd_heapgo("99.5 [[('w', 1)]]"), 1)

    def test_negative_token_value_rejected(self):
        self.assertEqual(self.ci.cmd_heapgo("0.5 [[('w', -3)]]"), 0)

    def test_zero_heaps_rejected(self):
        # spec: "The number of heaps is between 1 and 10"
        self.assertEqual(self.ci.cmd_heapgo("0.5 []"), 0)

    def test_empty_heap_at_start_rejected(self):
        # spec: "Each heap contains from 1 to 10 tokens"
        self.assertEqual(self.ci.cmd_heapgo("0.5 [[]]"), 0)
        self.assertEqual(self.ci.cmd_heapgo("0.5 [[('w', 1)], []]"), 0)


class TestHeapGoMalformed(unittest.TestCase):
    """Input that must not crash the command. process_command masks crashes
    as '= -1', so these assert on the return value directly."""

    def setUp(self):
        self.ci = CommandInterface()

    def test_unclosed_bracket(self):
        self.assertEqual(self.ci.cmd_heapgo("0.5 [[('w', 2)]"), 0)

    def test_trailing_junk_after_gamestate(self):
        self.assertEqual(self.ci.cmd_heapgo("0.5 [[('w', 2)]] junk"), 0)

    def test_string_token_value(self):
        self.assertEqual(self.ci.cmd_heapgo("0.5 [[('w', '2')]]"), 0)

    def test_none_token_value(self):
        self.assertEqual(self.ci.cmd_heapgo("0.5 [[('w', None)]]"), 0)

    def test_float_token_value_rejected(self):
        # spec: "value n, an integer between 1 and 20"
        self.assertEqual(self.ci.cmd_heapgo("0.5 [[('w', 2.5)]]"), 0)

    def test_bool_token_value_rejected(self):
        # bool is a subclass of int, so 1 <= True <= 20 passes a naive check
        self.assertEqual(self.ci.cmd_heapgo("0.5 [[('w', True)]]"), 0)

    def test_three_element_token(self):
        self.assertEqual(self.ci.cmd_heapgo("0.5 [[('w', 2, 3)]]"), 0)

    def test_reversed_token_fields(self):
        self.assertEqual(self.ci.cmd_heapgo("0.5 [[(2, 'w')]]"), 0)

    def test_uppercase_color(self):
        self.assertEqual(self.ci.cmd_heapgo("0.5 [[('W', 2)]]"), 0)

    def test_token_as_list_not_tuple(self):
        self.assertEqual(self.ci.cmd_heapgo("0.5 [[['w', 2]]]"), 0)

    def test_dict_gamestate(self):
        self.assertEqual(self.ci.cmd_heapgo("0.5 [{'w': 2}]"), 0)

    def test_extra_nesting(self):
        self.assertEqual(self.ci.cmd_heapgo("0.5 [[[('w', 2)]]]"), 0)

    def test_no_args_at_all(self):
        self.assertEqual(self.ci.cmd_heapgo(""), 0)

    def test_komi_not_a_number(self):
        self.assertEqual(self.ci.cmd_heapgo("abc [[('w', 2)]]"), 0)

    def test_komi_nan_and_inf(self):
        self.assertEqual(self.ci.cmd_heapgo("nan [[('w', 2)]]"), 0)
        self.assertEqual(self.ci.cmd_heapgo("inf [[('w', 2)]]"), 0)
        self.assertEqual(self.ci.cmd_heapgo("-inf [[('w', 2)]]"), 0)

    def test_two_komi_values(self):
        self.assertEqual(self.ci.cmd_heapgo("0.5 1.5 [[('w', 2)]]"), 0)

    def test_extra_whitespace_is_fine(self):
        self.assertEqual(self.ci.cmd_heapgo("   0.5     [[('w', 2)]]   "), 1)

    def test_double_quoted_colors_accepted(self):
        self.assertEqual(self.ci.cmd_heapgo('0.5 [[("w", 2)]]'), 1)

    def test_gamestate_with_no_internal_spaces(self):
        self.assertEqual(self.ci.cmd_heapgo("0.5 [[('w',2),('b',3)]]"), 1)


class TestHeapGoResetsState(unittest.TestCase):
    """A new game must fully reset, and a rejected game must change nothing."""

    def setUp(self):
        self.ci = CommandInterface()

    def test_new_game_resets_scores_and_toplay(self):
        self.ci.cmd_heapgo("0.5 [[('w', 2)]]")
        self.ci.cmd_play("0")                       # black scores 2, toplay -> w
        self.ci.cmd_heapgo("1.5 [[('b', 3)]]")
        self.assertEqual(self.ci.black_score, 0)
        self.assertEqual(self.ci.white_score, 1.5)
        self.assertEqual(self.ci.to_play, 'b')

    def test_toplay_resets_to_black_on_new_game(self):
        self.ci.cmd_heapgo("0.5 [[('w', 2)]]")
        self.ci.cmd_toplay("w")
        self.ci.cmd_heapgo("0.5 [[('w', 2)]]")
        self.assertEqual(self.ci.to_play, 'b')

    def test_rejected_game_leaves_previous_game_intact(self):
        self.ci.cmd_heapgo("0.5 [[('w', 2)]]")
        run(self.ci, "heapgo", "7.5 [[('a', 2)]]")   # invalid colour -> = -1
        out, status = run(self.ci, "show")
        self.assertEqual(out, ["k 0.5 [[('w', 2)]]"])

    def test_rejected_game_leaves_scores_and_toplay_intact(self):
        # the board and komi may survive a rejected heapgo while the scores
        # and to_play do not, if they are assigned before validation finishes
        self.ci.cmd_heapgo("0.5 [[('w', 2), ('b', 3)]]")
        self.ci.cmd_play("0")                        # black scores 5, toplay -> w
        run(self.ci, "heapgo", "7.5 [[('a', 2)]]")   # invalid colour -> = -1
        out, status = run(self.ci, "score")
        self.assertEqual(out, ["b 5 w 0.5"])
        self.assertEqual(self.ci.to_play, 'w')

    def test_crashing_game_leaves_previous_game_intact(self):
        self.ci.cmd_heapgo("0.5 [[('w', 2)]]")
        self.ci.cmd_play("0")
        run(self.ci, "heapgo", "7.5 [[(")            # malformed -> = -1
        out, status = run(self.ci, "show")
        self.assertEqual(out, ["k 0.5 [[]]"])
        out, status = run(self.ci, "score")
        self.assertEqual(out, ["b 2 w 0.5"])


class TestKomiIsIntegerPlusHalf(unittest.TestCase):
    """spec: "The komi is an integer + 0.5 to avoid draws."
    Delete this class if you decide komi is any number in range instead."""

    def setUp(self):
        self.ci = CommandInterface()

    def test_half_komi_accepted(self):
        for k in ("0.5", "-0.5", "7.5", "-2.5", "99.5", "-99.5", "+3.5", "0.50"):
            with self.subTest(komi=k):
                self.assertEqual(self.ci.cmd_heapgo(k + " [[('w', 2)]]"), 1)

    def test_integer_komi_rejected(self):
        for k in ("0", "2", "-3", "7", "0.0", "5.000"):
            with self.subTest(komi=k):
                self.assertEqual(self.ci.cmd_heapgo(k + " [[('w', 2)]]"), 0)

    def test_other_fractions_rejected(self):
        for k in ("0.25", "1.75", "-2.3", "0.6"):
            with self.subTest(komi=k):
                self.assertEqual(self.ci.cmd_heapgo(k + " [[('w', 2)]]"), 0)

    def test_no_draw_is_possible(self):
        # the point of the +0.5: scores can never tie, so cmd_winner never
        # has to break one
        self.ci.cmd_heapgo("0.5 [[('b', 4)], [('w', 4)]]")
        self.ci.cmd_play("0")
        self.ci.cmd_play("1")
        out, status = run(self.ci, "winner")
        self.assertEqual(status, "= 1")
        self.assertEqual(out, ["w"])


# ===========================================================================
# show
# ===========================================================================
class TestShowCommand(unittest.TestCase):
    def setUp(self):
        self.ci = CommandInterface()

    def show(self):
        out, status = run(self.ci, "show")
        return out, status

    def test_show_before_any_game(self):
        out, status = self.show()
        self.assertEqual(status, "= -1")
        self.assertEqual(out, [])

    def test_show_basic(self):
        self.ci.cmd_heapgo("0.5 [[('w', 2)]]")
        self.assertEqual(self.show(), (["k 0.5 [[('w', 2)]]"], "= 1"))

    def test_show_negative_komi(self):
        self.ci.cmd_heapgo("-2.5 [[('b', 3), ('w', 1)]]")
        self.assertEqual(self.show(), (["k -2.5 [[('b', 3), ('w', 1)]]"], "= 1"))

    def test_show_normalises_input_spacing(self):
        self.ci.cmd_heapgo("0.5 [[('w',2),('b',3)]]")
        self.assertEqual(self.show(), (["k 0.5 [[('w', 2), ('b', 3)]]"], "= 1"))

    def test_show_normalises_double_quotes(self):
        self.ci.cmd_heapgo('0.5 [[("w", 2)]]')
        self.assertEqual(self.show(), (["k 0.5 [[('w', 2)]]"], "= 1"))

    def test_show_after_play(self):
        self.ci.cmd_heapgo("0.5 [[('w', 9), ('b', 12), ('w', 5)], [('b', 6), ('b', 9)]]")
        self.ci.cmd_play("0")
        self.assertEqual(
            self.show(),
            (["k 0.5 [[('w', 9), ('b', 12)], [('b', 6), ('b', 9)]]"], "= 1"))

    def test_show_empty_heaps_at_game_end(self):
        self.ci.cmd_heapgo("0.5 [[('b', 1)], [('w', 2)]]")
        self.ci.cmd_play("0")
        self.ci.cmd_play("1")
        self.assertEqual(self.show(), (["k 0.5 [[], []]"], "= 1"))

    def test_show_does_not_mutate_state(self):
        self.ci.cmd_heapgo("0.5 [[('w', 2)]]")
        first = self.show()
        second = self.show()
        self.assertEqual(first, second)

    def test_show_after_failed_play_unchanged(self):
        self.ci.cmd_heapgo("0.5 [[('w', 2)]]")
        run(self.ci, "play", "5")                   # out of range -> = -1
        self.assertEqual(self.show(), (["k 0.5 [[('w', 2)]]"], "= 1"))

    def test_show_ten_heaps(self):
        state = [[('b', 1)] for _ in range(10)]
        self.ci.cmd_heapgo("0.5 " + str(state))
        self.assertEqual(self.show(), ([f"k 0.5 {state}"], "= 1"))

    def test_show_integer_komi_formatting(self):
        # only matters if integer komi is accepted at all; komi is specified
        # as integer + 0.5, so "heapgo 2 ..." is arguably invalid input
        self.ci.cmd_heapgo("2 [[('w', 2)]]")
        out, status = self.show()
        self.assertIn(out, ([], ["k 2 [[('w', 2)]]"]))

    def test_show_ignores_extra_args(self):
        self.ci.cmd_heapgo("0.5 [[('w', 2)]]")
        out, status = run(self.ci, "show", "extra junk")
        self.assertEqual(out, ["k 0.5 [[('w', 2)]]"])
        self.assertEqual(status, "= 1")


if __name__ == "__main__":
    unittest.main()
