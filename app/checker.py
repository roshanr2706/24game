# app/checker.py
from typing import List, Tuple

def check_expression(nums: List[int], expression: str) -> Tuple[bool, str]:
    """Validate a user-submitted expression for the 24 game.

    Input
    -----
    nums: List[int]
        Exactly four integers, the allowed card values.
    expression: str
        A candidate arithmetic expression string.

    Rules
    -----
    - Only +, -, *, / and parentheses are allowed (no functions/variables)
    - Must use exactly the provided numbers, each once (no concatenation like 12)
    - Division by zero is invalid
    - Must evaluate exactly to 24

    Output
    ------
    (ok, message): Tuple[bool, str]
        ok=True with message "Correct!" if valid and equals 24.
        Otherwise ok=False with an explanatory message (syntax, numbers mismatch, result not 24, etc.).

    Examples
    --------
    > check_expression([1,3,4,6], "(6/(1-3/4))")
    (True, "Correct!")
    > check_expression([1,3,4,6], "6/(1-3/4)")
    (True, "Correct!")
    > check_expression([2,2,2,2], "(2+2+2) * 2")
    (False, "Result is 12.0 (not 24).")
    """
    # TODO: Parse safely (no eval), enforce allowed tokens, multiset-match the integers,
    # evaluate with exact arithmetic, and return detailed feedback.
    raise NotImplementedError("TODO: implement check_expression")