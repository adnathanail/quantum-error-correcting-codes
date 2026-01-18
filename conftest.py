import pytest

# Let pytest make assertion errors nice, even when the assert isn't in the test file
pytest.register_assert_rewrite("tests.utils")
