import re
import sqlite3
from collections import deque

# TO DO:
# 1. Implement database for vars
# 2. /clear (for vars), /variables (list variables)
# 3. Up arrow = previous equation?

conn = sqlite3.connect("Calculator.db")
curr = conn.cursor()

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

    else:  # This is the parser to convert the infix to postfix notation
        if re.search(r"[\d]+[+/*-]-[\d]+", equation):  # Checks to make sure user did not put 5--5, 5+-5, etc.
            print("Invalid expression")
        elif re.match(r"^[+-]+[\d]+$", equation):  # Checks if user did +#..., it will just print the number positive
            print(re.findall(r"[-]?[\d]+", equation)[0])
        elif re.search(r"(?<![\w])[-]?[\d]", equation) is not None or re.search("[A-Za-z]+", equation) is not None:
            vars = re.split("([()+*/-]+)", equation)
            vars = [var.strip() for var in vars if var != " "]
            operators = deque()  # This will store all of our operators for easy access (stack)
            computation = deque()  # This will store the postfix expression
            priorities = {"(": 0, "/": 2, "*": 2, "+": 1, "-": 1}
            for var in vars:
                # If the number is a variable, add its value
                if var.isalpha() and var in variables:  # Variable that is VALID
                    computation.append(variables[var])
                elif var.isnumeric() or re.match(r"[+-][\d]+$", var) is not None:  # All digits
                    computation.append(var)
                elif var == "(":  # Left parenthesis
                    operators.append("(")
                elif var == ")":  # Right parenthesis (pop until we find left p)
                    operator = operators.pop()
                    try:
                        while operator != "(":  # Keep adding to computation until we reach the left parenthese
                            computation.append(operator)
                            operator = operators.pop()
                    except IndexError:
                        print("Invalid expression")
                        break

                elif var.isalpha() and var not in variables:  # Invalid variable (STOP)
                    print("Unknown variable")
                    break

                elif re.match("[+-]+$", var) is not None or re.search("[*/]{2,}", var) is None:  # Signage
                    if len(var) % 2 == 0 and var.find("-") != -1:  # Two negatives = a positive
                        var = "+"
                    try:
                        adj_operator = var[0]  # Get rid of all the duplicates
                    except IndexError:
                        print("Invalid expression")
                        break
                    if len(operators) > 0:
                        operator = operators.pop()
                        while priorities[adj_operator] <= priorities[operator]:  # Keep popping if < due to PEMDAS
                            computation.append(operator)  # Append greater one to numbers first
                            if len(operators) > 0:
                                operator = operators.pop()
                            else:  # However, stop popping if the operator stack is empty
                                break
                        if priorities[adj_operator] > priorities[operator]:  # However, re-push the operator if >
                            operators.append(operator)
                    operators.append(adj_operator)  # All-in-all, push the new operator for further evaluation later

                elif any(x.isalpha() for x in var) and any(x.isnumeric() for x in var):  # Makes sure var is valid
                    print("Invalid identifier")
                    break
            else:
                while len(operators) > 0:  # There are no more symbols, push the rest of the operators
                    computation.append(operators.pop())

                try:
                    num_stack = deque()  # Num_stack will only have #'s that lead to the result
                    print(computation)
                    while len(computation) > 0:
                        print(num_stack)
                        sign = computation.popleft()
                        if re.match(r"^[+/*-]$", sign) is not None:
                            num2 = int(num_stack.pop())
                            num1 = int(num_stack.pop())
                            if sign == "+":
                                num_stack.append(num1 + num2)
                            elif sign == "-":
                                num_stack.append(num1 - num2)
                            elif sign == "*":
                                num_stack.append(num1 * num2)
                            elif sign == "/":
                                num_stack.append(num1 // num2)
                        else:  # The sign turned out to be a #
                            num_stack.append(sign)
                        # The expression is valid if it reduced it to one number
                    print(num_stack.pop()) if len(num_stack) == 1 else print("Invalid expression")
                except IndexError and ValueError:
                    print("Invalid expression")
        else:  # It is something the program cannot comprehend or empty input
            print("Invalid expression") if equation != "" else ""
