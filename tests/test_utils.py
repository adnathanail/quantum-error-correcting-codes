from tests.utils import combs_of_strings, flip, flip_bit_at_index


class TestCombsOfStrings:
    def test_2_qubit_states(self):
        assert combs_of_strings(("0", "1"), ("0", "1")) == ["00", "01", "10", "11"]

    def test_3_qubit_states(self):
        assert combs_of_strings(("0", "1"), ("0", "1"), ("0", "1")) == ["000", "001", "010", "011", "100", "101", "110", "111"]


class TestFlip:
    def test_flip(self):
        assert flip("0") == "1"
        assert flip("1") == "0"


class TestFlipBitAtIndex:
    def test_flip_bit_at_index(self):
        assert flip_bit_at_index("0000000", 2) == "0000100"
        assert flip_bit_at_index("1010101", 3) == "1011101"
        assert flip_bit_at_index("1111000", 6) == "0111000"
