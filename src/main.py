from parser import parse


def main():
    while True:
        user_input = input(" -> ")
        parse(user_input)


main()
