from parser import parse
from interpreter import interpret

def main():
    while True:
        user_input = input(" -> ")
        if user_input == "!quit!":
            exit(1)
        tree = parse(user_input)
        interpret(tree)


main()
