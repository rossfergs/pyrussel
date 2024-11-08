

class Variable:
    def __init__(self):
        variable_type = "Non-Specific Variable"
        variable_value = "N/A"


class IntVariable(Variable):
    def __init__(self, var_value):
        self.var_type = "Int"
        self.value = int(var_value)


class StringVariable(Variable):
    def __init__(self, var_value):
        self.var_type = "Str"
        self.value = var_value


class FloatVariable(Variable):
    def __init__(self, var_value):
        self.var_type = "Float"
        self.value = float(var_value)
