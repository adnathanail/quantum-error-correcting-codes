from tests.utils import combs_of_strings


class TestCombsOfStrings:
    def test_2_qubit_states(self):
        assert combs_of_strings(("0", "1"), ("0", "1")) == ["00", "01", "10", "11"]

    def test_3_qubit_states(self):
        assert combs_of_strings(("0", "1"), ("0", "1"), ("0", "1")) == ["000", "001", "010", "011", "100", "101", "110", "111"]
