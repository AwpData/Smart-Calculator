import re
from collections import deque

variables = dict()
while True:
    equation = input()
    operators = deque(re.findall(r"(?<=\s)+[()+*/-]+(?=\s)+", equation))  # Operators must match regex
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
            if variable_parts[1].isalpha():
                if variable_parts[1] in variables:
                    variables[variable_parts[0]] = variables[variable_parts[1]]
                else:
                    print("Unknown variable")
            else:
                variables[variable_parts[0]] = variable_parts[1]
    else:
        if re.search("[A-Za-z]+", equation) is not None and len(operators) == 0:
            if re.search(r"[\d]+", equation) is not None:  # Check for valid left side
                print("Invalid identifier")
            else:
                print(variables[equation]) if equation in variables else print("Unknown variable")

        elif re.search(r"(?<![\w])[-]?[\d]", equation) is not None or len(operators) > 0:
            vars = re.split(r"\s+[+*/-]+\s+", equation)
            numbers = deque()
            for var in vars:
                if var.isalpha():
                    numbers.append(variables[var])
                else:
                    numbers.append(int(var))
            try:
                for operator in operators:
                    if re.match(r"^[+]+$", operator) is not None:
                        numbers.appendleft(int(numbers.popleft()) + int(numbers.popleft()))
                    elif re.match(r"^[-]+$", operator) is not None:
                        if len(operator) % 2 == 0:
                            numbers.appendleft(int(numbers.popleft()) + int(numbers.popleft()))
                        else:
                            numbers.appendleft(int(numbers.popleft()) - int(numbers.popleft()))
                # The expression is valid if it reduced it to one number
                print(*numbers) if len(numbers) == 1 else print("Invalid expression")
            except IndexError:

                print("Invalid expression")

        else:
            print("Invalid expression") if equation != "" else ""
