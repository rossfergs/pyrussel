from parser import parse
from pratt_parser import pp


def main():
    while True:
        user_input = input(" -> ")
        if user_input == "!quit!":
            exit(1)
        parse(user_input)


main()
