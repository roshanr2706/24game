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

    # parsed = []
    # operations = ["+", "-", "*", "/"]
    # current_exp = ""
    # for i in expression.replace(" ", ""):
    #     if i == "(":
    #         parsed.append(current_exp)
    #         current_exp = ""
    #     elif i == ")":
    #         parsed.append(current_exp)
    #         current_exp = ""
    #     else:
    #         current_exp += i
    # parsed.append(current_exp)
    # print(parsed)
    # i = 0
    # while len(parsed) > 0:
    #     if len(parsed[i]) > 1:
    #         for i in operations:
    #             chunk = parsed[i].split(i)
    #             if len(chunk) > 1:
    #                 match i:
    #                     case "+":

    #                         chunk[0] + chunk[1]
    #                     case "-":
    #                         pass
    #                     case "*":
    #                         pass
    #                     case "/":
    #                         pass
    #                 print(chunk)
    # expression = "(" + expression + ")"
    # bracket_loc_stack = []  # stack for bracket positions
    # Op_stack = []
    # Num_stack = []
    # i = 0
    # while i < len(expression):
    #     if expression[i] == "(":
    #         bracket_loc_stack.append(i)
    #     elif expression[i] == ")":
    #         loc = bracket_loc_stack.pop()
            

    #         expression = expression[:loc] + f"aso" + expression[i + 1:]
    #         i = loc
        # elif expression[i] == "*":
        #     Div_mult_loc_queue.append(["*", i])
        # elif expression[i] == "/":
        #     Div_mult_loc_queue.append(["/", i])
        # elif expression[i] == "+":
        #     Sub_add_loc_queue.append(["+", i])
        # elif expression[i] == "-":
        #     Sub_add_loc_queue.append(["-", i])
        
        
        # elif expression[i].isdigit():
        #     if (expression[i + 1])
        #     if expression[i] in nums:
        #         nums.remove(expression[i])
        #     else:
        #         return (False, "Incorrect, numbers mismatched")
    #     i += 1
    # print(expression)

    # Shunting Yard

    output_queue = []
    operator_stack = []
    operations = {"+" : 2, "-" : 2, "*" : 1, "/" : 1}
    was_num = False
    for i in expression:
        if i.isdigit():
            if was_num:
                output_queue[-1] = output_queue[-1] + i
            else:
                output_queue.append(i)
                was_num = True
        elif i in operations.keys():
            was_num = False
            while len(operator_stack) > 0 and operator_stack[-1] in operations.keys() and operations[operator_stack[-1]] <= operations[i]:
                output_queue.append(operator_stack.pop())
            operator_stack.append(i)
        elif i == "(":
            was_num = False
            operator_stack.append(i)
        elif i == ")":
            was_num = False
            while len(operator_stack) > 0 and operator_stack[-1] != "(":
                output_queue.append(operator_stack.pop())
            if len(operator_stack) == 0:
                return (False, "Brackets mismatched")
            else:
                operator_stack.pop()
    output_queue.extend(operator_stack[::-1])

    print(output_queue)

    # Evaluating Post-fix expression
    i = 0
    while i < len(output_queue):
        if output_queue[i] in operations.keys():
            match output_queue.pop(i):
                case "+":
                    output_queue.insert(i - 2, output_queue.pop(i - 2) + output_queue.pop(i - 2))
                    i -= 2
                case "-":
                    output_queue.insert(i - 2, output_queue.pop(i - 2) - output_queue.pop(i - 2))
                    i -= 2
                case "*":
                    output_queue.insert(i - 2, output_queue.pop(i - 2) * output_queue.pop(i - 2))
                    i -= 2
                case "/":
                    output_queue.insert(i - 2, output_queue.pop(i - 2) / output_queue.pop(i - 2))
                    i -= 2
        else:
            output_queue[i] = int(output_queue[i])
            if output_queue[i] in nums:
                nums.remove(output_queue[i])
            else:
                return (False, "Numbers mismatched")
        i += 1
    
    print(output_queue[0])

    if len(nums) > 0:
        return (False, "Didn't use all the cards")

    if 24.1 >= output_queue[0] >= 23.9:
        return (True, "Correct!")
    else:
        return (False, "Result not 24")



if __name__ == "__main__":
    print(check_expression([5, 4, 13, 9], "5 * 4 + 13 - 9"))
