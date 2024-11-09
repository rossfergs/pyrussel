

class Value:
    def __init__(self):
        self.var_type = "Non-Specific Variable"
        self.value = "N/A"


class IntValue(Value):
    def __init__(self, var_value):
        self.var_type = "Int"
        self.value = int(var_value)


class StringValue(Value):
    def __init__(self, var_value):
        self.var_type = "Str"
        self.value = str(var_value)


class FloatValue(Value):
    def __init__(self, var_value):
        self.var_type = "Float"
        self.value = float(var_value)
