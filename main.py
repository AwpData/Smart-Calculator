import math
import re
import sqlite3
from collections import deque

conn = sqlite3.connect("Calculator.db")
curr = conn.cursor()

with conn:
    curr.execute("""CREATE TABLE IF NOT EXISTS variables (
                    name VARCHAR(50) NOT NULL,
                    value VARCHAR(50) NOT NULL);""")

    variables = dict()
    data_vars = curr.execute("SELECT * FROM variables").fetchall()
    for data_var in data_vars:
        variables[data_var[0]] = data_var[1]

while True:
    equation = input()
    if equation == "/exit":  # Quit the program
        print("Terminated program")
        break
    elif equation == "/help":  # Get a list of all the commands
        print("""\t***SMART Calculator with PEMDAS and Variables***
        
        COMMANDS:
        /variables <- List all current variables
        /clear <- Clears all variables from variable list
        /delete <name> <- Deletes the given variable from the list
        /exit <- Quit the program (and save variables created)
        /help <- Opens this screen
        
        VARIABLE USAGE:
        <any letter(s)> = # <- Create a variable
        <any letter(s)> = <any letters(s) <- Sets left variable value to right variable value
        <any letter(s)> <- Prints the variable value
         """)

    elif equation == "/variables":  # List all of the variables
        for variable, value in variables.items():
            print("{} = {}".format(variable, value))
    elif equation == "/clear":  # Clear all the variables
        with conn:
            curr.execute("DELETE FROM variables")
        variables = dict()
    elif re.match(r"/delete [\w]+", equation):  # Delete a variable
        var = equation.split()
        if var[1] in variables:
            with conn:
                curr.execute("DELETE FROM variables WHERE name = ?", (var[1],))
            del variables[var[1]]
        else:
            print("Could not find variable {}".format(var[1]))

    elif re.match(r"/[\w]+", equation) is not None:  # Command it doesn't know
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
                    with conn:
                        curr.execute("UPDATE variables SET value = ? WHERE name = ?",
                                     (variables[variable_parts[1]], variable_parts[0]))
                else:
                    print("Unknown variable {}".format(variable_parts[1]))
            else:  # The right side is all numbers, so assign it this value
                with conn:
                    if variable_parts[0] not in variables.keys():
                        curr.execute("INSERT INTO variables VALUES (?, ?)", (variable_parts[0], variable_parts[1]))
                    else:
                        curr.execute("UPDATE variables SET value = ? WHERE name = ?",
                                     (variable_parts[1], variable_parts[0]))
                variables[variable_parts[0]] = variable_parts[1]

    else:  # This is the parser to convert the infix to postfix notation
        if re.match("[A-Za-z]+$", equation):
            if equation in variables:
                print(variables[equation])
            else:
                print("Unknown variable {}".format(equation))
            continue
        if re.search(r"[\d]+[+^/*-]-[\d]+", equation):  # Checks to make sure user did not put 5--5, 5+-5, etc.
            print("Invalid expression")
        elif re.match(r"^[+-]+[\d]+$", equation):  # Checks if user did +#..., it will just print the number positive
            print(re.findall(r"[-]?[\d]+", equation)[0])
        elif re.search(r"(?<![\w])[-]?[\d]", equation) is not None or re.search("[A-Za-z]+", equation) is not None:
            if re.search("[*^/]{2,}", equation) is not None:
                print("Invalid expression")
                continue
            vars = re.split(r"((?<![\d])[()+^*/-]+(?![\d]+))", equation)
            vars = [var.strip() for var in vars]
            operators = deque()  # This will store all of our operators for easy access (stack)
            computation = deque()  # This will store the postfix expression
            priorities = {"(": 0, "^": 3, "/": 2, "*": 2, "+": 1, "-": 1}
            for var in vars:
                # If the number is a variable, add its value
                if var.isalpha() and var in variables:  # Add variable value if it is valid
                    computation.append(variables[var])
                elif re.match(r"[-]*[\d]+$", var) is not None:  # Add digits
                    computation.append(var)
                elif re.search(r"[(]+[\d]+", var) is not None:  # Left parenthesis
                    computation.append("".join(re.findall(r"[\d]+", var)))
                    for _ in range(len(var) - 1):
                        operators.append("(")
                elif re.search(r"[\d]+[)]+", var) is not None:  # Right parenthesis (pop until we find left p)
                    computation.append("".join(re.findall(r"[\d]+", var)))
                    operator = operators.pop()
                    try:
                        while operator != "(":  # Keep adding to computation until we reach the left parenthese
                            computation.append(operator)
                            operator = operators.pop()
                    except IndexError:  # This will go off if the person forgot to close the parenthesis (either one)
                        print("Invalid expression")
                        break

                elif var.isalpha() and var not in variables:  # Invalid variable (STOP)
                    print("Unknown variable {}".format(var))
                    break

                elif re.match("[+^*/-]+", var) is not None:  # Signage
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
                    print("Invalid identifier {}".format(var))
                    break
            else:
                while len(operators) > 0:  # There are no more symbols, push the rest of the operators
                    computation.append(operators.pop())
                try:
                    num_stack = deque()  # Num_stack will only have #'s that lead to the result
                    while len(computation) > 0:
                        sign = computation.popleft()
                        if re.match(r"^[+^/*-]$", sign) is not None:  # Found a sign, so do operation
                            num2 = int(num_stack.pop())  # Get the next two numbers in our postfix expression
                            num1 = int(num_stack.pop())
                            if sign == "+":
                                num_stack.append(num1 + num2)
                            elif sign == "-":
                                num_stack.append(num1 - num2)
                            elif sign == "*":
                                num_stack.append(num1 * num2)
                            elif sign == "/":
                                num_stack.append(num1 // num2)
                            elif sign == "^":
                                num_stack.append(int(math.pow(num1, num2)) if num2 > 0 else math.pow(num1, num2))
                        else:  # The sign turned out to be a #
                            num_stack.append(sign)
                        # The expression is valid if it reduced it to one number
                    print(num_stack.pop()) if len(num_stack) == 1 else print("Invalid expression")
                except IndexError and ValueError:
                    print("Invalid expression")
        else:  # It is something the program cannot comprehend or empty input
            print("Invalid expression") if equation != "" else ""
