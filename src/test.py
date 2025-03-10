from dataclasses import dataclass


class MyClass:
    pass


@dataclass
class FirstSub(MyClass):
    a: str = None,
    b: int = None


@dataclass
class SecondSub(MyClass):
    a: str = None,
    b: int = None


c = FirstSub("name", 1)

match c:
    case FirstSub(name, _):
        print(f"{name=}")
    case _:
        print("UNMAtCHED")
