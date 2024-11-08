

class Error:
    def __init__(self, message):
        self.show_error_message(message)
        exit(0)

    def show_error_message(self, message):
        print(f"Error: {message}")


class ParseError(Error):
    def __init__(self, message):
        super().__init__(message)

    def show_error_message(self, message):
        print(f"Error in parsing: {message}")


class LexerError(Error):
    def __init__(self, message):
        super().__init__(message)

    def show_error_message(self, message):
        print(f"Error in lexing: {message}")


class InterpreterError(Error):
    def __init__(self, message):
        super().__init__(message)

    def show_error_message(self, message):
        print(f"Error in interpreting: {message}")
