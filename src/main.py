import argparse

from parser import parse
from interpreter import interpret
from error import Error


def show_version():
    print(
        """  LAMBDRADOR
    \\ _ /_
    /\\-/\\
    V 0.1"""
    )
    exit(0)


def main():
    ap = argparse.ArgumentParser("Russel Interpreter \n rsli")
    ap.add_argument("filename", nargs="?", type=str, help="File to interpret (.rsl file)")

    args = ap.parse_args()

    if args.filename:
        try:
            with open(args.filename, 'r') as input_file:
                file_content = input_file.read().replace('\n', ' ')
                interpret(file_content)
                exit(1)
        except FileNotFoundError:
            Error(f"Error: File '{args.filename}' not found.")
    else:
        while True:
            user_input = input(" -> ")
            if user_input == "!quit!":
                exit(1)
            interpret(user_input)


main()
