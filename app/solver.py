# app/solver.py
from typing import List, Optional

def gather(nums: List[int]):
    out = []
    for first_num in range(len(nums)):
        for second_num in range(first_num + 1, len(nums)):
            card1, card2 = nums[first_num], nums[second_num]
            remaining = nums.copy()
            remaining.remove(card1)
            remaining.remove(card2)
            possible_vals = [
                [card1[0] + card2[0], f"({card1[1]} + {card2[1]})"],
                [card1[0] - card2[0], f"({card1[1]} - {card2[1]})"],
                [card2[0] - card1[0], f"({card2[1]} - {card1[1]})"],
                [card1[0] * card2[0], f"({card1[1]} * {card2[1]})"],
            ]
            if card2[0]: possible_vals.append([card1[0] / card2[0], f"({card1[1]} / {card2[1]})"])
            if card1[0]: possible_vals.append([card2[0] / card1[0], f"({card2[1]} / {card1[1]})"])
            for i in possible_vals:
                out.append([i] + remaining)
    return out


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
    nums = [[i, str(i)] for i in nums]
    stack = gather(nums)
    while len(stack) != 0:
        if len(stack[-1]) == 1:
            solution = stack.pop()[0]
            if 23.9999 <= solution[0] <= 24.0001:
                return solution[1]
        else:
            stack.extend(gather(stack.pop()))
    return None

if __name__ == "__main__":
    print(solve24([12, 11, 1, 6]))
    




