def validate_data(parameter):
    if not parameter:
        raise ValueError("Значение поля не должно быть пустым.")
    return parameter


def validate_operator(operator: str):
    if operator not in {}.keys():
        raise ValueError(f"operator {operator} is not a valid message service")
    return operator
