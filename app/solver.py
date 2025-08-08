# app/solver.py
from typing import List, Optional

def solve24(nums: List[int]) -> Optional[str]:
    """Return an expression string that evaluates exactly to 24 using the
    four integers in `nums` each exactly once with + - * / and parentheses.
    ----------
    - len(nums) == 4
    - Each number must be used exactly once (order doesn't matter)
    - Allowed operators: +, -, *, /
    - Division by zero is invalid
    - Exact equality to 24 

    Returns
    -------
    - str expression if a solution exists (e.g., "(6/(1-3/4))")
    - None if unsolvable

    Example
    --------
    > solve24([4, 7, 8, 8])
    "(7 - (8/8)) * 4"  # for example; any valid equivalent is fine
    > solve24([1, 1, 1, 1])
    None
    """
    # TODO: Implement search over permutations, operator choices, and parenthesizations
    # using exact arithmetic. Return the first valid expression string or None.
    raise NotImplementedError("TODO: implement solve24")