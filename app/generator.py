# app/generator.py
from typing import List, Optional, Tuple
from . import solver
import random

def generate_puzzle(seed: Optional[int] = None) -> List[int]:

    """Draw a 4-number 'hand' (1..13 each) for the 24 game.

    Parameters
    ----------
    seed : Optional[int]
        Optional RNG seed for reproducibility.
    require_solvable : bool
        If True, keep drawing until a solvable hand is found (or max_tries hit).
    max_tries : int
        Upper bound on attempts when require_solvable is True.

    Returns
    -------
    (nums, solvable): (List[int], bool)
        nums: List of four integers in [1,13]
        solvable: whether the returned hand is solvable according to `solve24`.

    Examples
    --------
    > nums, ok = generate_puzzle(seed=42, require_solvable=False)
    > len(nums) == 4 and all(1 <= x <= 13 for x in nums)
    True
    """
    # TODO: Implement RNG-based draw of 4 numbers in 1..13 and (optionally)
    # loop until `solve24(nums)` indicates solvable. Return (nums, is_solvable).
    if seed != None:
        random.seed(seed)
    cards = [random.randint(1, 13) for _ in range(4)]
    while solver.solve24(cards) == None:
        cards = [random.randint(1, 13) for _ in range(4)]
    return cards

if __name__ == "__main__":
    print(generate_puzzle())
