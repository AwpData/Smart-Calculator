import re
from collections import deque

while True:
    equation = input()
    numbers = deque(re.findall(r"(-?[\d]+)+", equation))
    operators = deque(re.findall(r"[()+*/-]+(?=\s)+?", equation))
    if equation == "/exit":
        print("Bye!")
        break
    elif equation == "/help":
        print("The program calculates the sum/difference of numbers")
    elif re.match(r"/[\w]+", equation) is not None:
        print("Unknown command")
    else:
        if equation != "":
            for operator in operators:
                if re.match(r"[+]+", operator) is not None:
                    numbers.appendleft(int(numbers.popleft()) + int(numbers.popleft()))
                elif re.match(r"[-]+", operator) is not None:
                    if len(operator) % 2 == 0:
                        numbers.appendleft(int(numbers.popleft()) + int(numbers.popleft()))
                    else:
                        numbers.appendleft(int(numbers.popleft()) - int(numbers.popleft()))
            print(*numbers) if len(operators) != 0 or len(numbers) > 0 else print("Invalid expression")
