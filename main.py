import re
from collections import deque

while True:
    equation = input()
    numbers = deque(re.findall(r"(?<![\w])(-?[\d]+)(?![+\w-])", equation))  # Numbers must match regex
    operators = deque(re.findall(r"(?<=\s)+[()+*/-]+(?=\s)+", equation))  # Operators must match regex
    if equation == "/exit":
        print("Bye!")
        break
    elif equation == "/help":
        print("The program calculates the sum/difference of numbers")
    elif re.match(r"/[\w]+", equation) is not None:
        print("Unknown command")
    else:
        if len(numbers) > 0 and re.match("[A-Za-z]+", equation) is None:  # The math equation must be #s
            try:
                for operator in operators:
                    if re.match(r"^[+]+$", operator) is not None:
                        numbers.appendleft(int(numbers.popleft()) + int(numbers.popleft()))
                    elif re.match(r"^[-]+$", operator) is not None:
                        if len(operator) % 2 == 0:
                            numbers.appendleft(int(numbers.popleft()) + int(numbers.popleft()))
                        else:
                            numbers.appendleft(int(numbers.popleft()) - int(numbers.popleft()))
                # The expression is valid if we did some operations on the equation (it reduced it to one number)
                print(*numbers) if len(numbers) == 1 else print("Invalid expression")
            except IndexError:
                print("Invalid expression")
        else:
            print("Invalid expression") if equation != "" else ""
