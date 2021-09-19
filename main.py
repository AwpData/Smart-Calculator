import re
from collections import deque

# TO DO:
# 1. Try to adjust program so that input doesn't have to have spaces (.replace?)
# 2. Clean up program, especially the part where I assign num1 and num2


variables = dict()
while True:
    equation = input()
    if equation == "/exit":
        print("Bye!")
        break
    elif equation == "/help":
        print("The program calculates the sum/difference of numbers")
    elif re.match(r"/[\w]+", equation) is not None:
        print("Unknown command")
    elif re.search(".*=.*", equation) is not None:  # IF the equation has and equals, assume it is a variable
        variable_parts = equation.split("=")  # Split the variable into three parts [left, =, right] for checking
        variable_parts = [x.strip() for x in variable_parts]
        if re.search(r"[\d]+", variable_parts[0]) is not None:  # Check for valid left side
            print("Invalid identifier")
        # Check if right side has invalid variable or if variable is not 3 length
        elif len(variable_parts) != 2 or any(x.isalpha() for x in variable_parts[1]) and any(x.isnumeric() for x in
                                                                                             variable_parts[1]):
            print("Invalid assignment")
        else:
            if variable_parts[1].isalpha():  # If the variable on the right is made of letters (another variable)
                if variable_parts[1] in variables:  # Assign the variable with the value of the right variable
                    variables[variable_parts[0]] = variables[variable_parts[1]]
                else:
                    print("Unknown variable")
            else:  # The right side is all numbers, so assign it this value
                variables[variable_parts[0]] = variable_parts[1]




    else:
        # There are digits instead or the user wants to do math with variables
        if re.search(r"(?<![\w])[-]?[\d]", equation) is not None or re.search("[A-Za-z]+", equation) is not None:
            vars = equation.split()  # Split all numbers (or variables) by spaces first
            operators = deque()  # This will store all of our operators for easy access (stack)
            numbers = deque()  # This will store all of our numbers for easy access (queue)
            priorities = {"(": 0, "/": 2, "*": 2, "+": 1, "-": 1}
            for var in vars:
                # If the number is a variable, add its value
                if var.isalpha() and var in variables:  # Variable that is VALID
                    numbers.append(variables[var])
                elif var.isnumeric() or re.match(r"[+-][\d]+$", var) is not None:  # All digits
                    numbers.append(var)
                elif re.search(r"[(]+[\d]+", var) is not None:  # Left parenthesis
                    numbers.append("".join(re.findall("[\d]+", var)))
                    for _ in range(len(var) - 1):
                        operators.append("(")
                elif re.search(r"[\d]+[)]+", var) is not None:  # Right parenthesis (pop until we find left p)
                    numbers.append("".join(re.findall("[\d]+", var)))
                    operator = operators.pop()
                    while operator != "(":
                        numbers.append(operator)
                        operator = operators.pop()
                elif var.isalpha() and var not in variables:  # Invalid variable (STOP)
                    print("Unknown variable")
                    break
                elif re.match("[*/+-]+$", var) is not None:  # Signage
                    if len(var) % 2 == 0 and var.find("-") != -1:  # Two negatives = a positive
                        var = "+"
                    adj_operator = var[0]  # Get rid of all the duplicates
                    if len(operators) > 0:
                        operator = operators.pop()
                        if priorities[adj_operator] < priorities[operator]:  # If the variable is less priority than op
                            numbers.append(operator)  # Append greater one to numbers first
                        else:
                            operators.append(operator)
                    operators.append(adj_operator)
                elif any(x.isalpha() for x in var) and any(x.isnumeric() for x in var):  # Makes sure var is valid
                    print("Invalid identifier")
                    break
            while len(operators) > 0:
                numbers.append(operators.pop())
            else:
                try:  # if there was only a digit(s) (no operators), it will skip the loop and print the digit(s)
                    num_stack = deque()
                    while len(numbers) > 0:
                        sign = numbers.popleft()
                        if re.match(r"^[+]+$", sign) is not None:  # Check for addition sign(s)
                            num2 = int(num_stack.pop())
                            num1 = int(num_stack.pop())
                            num_stack.append(num1 + num2)
                        elif re.match(r"^[-]+$", sign) is not None:  # Check for subtraction sign(s)
                            num2 = int(num_stack.pop())
                            num1 = int(num_stack.pop())
                            if len(sign) % 2 == 0:  # Two negatives = a positive
                                num_stack.append(num1 + num2)
                            else:
                                num_stack.append(num1 - num2)
                        elif re.match(r"^[*]+$", sign) is not None:
                            num2 = int(num_stack.pop())
                            num1 = int(num_stack.pop())
                            num_stack.append(num1 * num2)
                        elif re.match(r"^[/]+$", sign) is not None:
                            num2 = int(num_stack.pop())
                            num1 = int(num_stack.pop())
                            num_stack.append(num1 // num2)
                        else:
                            num_stack.append(sign)
                        # The expression is valid if it reduced it to one number
                    print(num_stack.pop()) if len(num_stack) == 1 else print("Invalid expression")
                except IndexError and ValueError:
                    print("Invalid expression")
        else:  # It is something I cannot comprehend
            print("Invalid expression") if equation != "" else ""
