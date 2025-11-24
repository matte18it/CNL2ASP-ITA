def operation(value):
    return value
def math_operator(*args):
    items_dict = {'somma': '+', 'differenza': '-', 'moltiplicazione': '*', 'divisione': '/'}
    item = ' '.join(args)
    return items_dict[item]
def math(*args):
    if len(args) != 3:
        raise ValueError("Servono esattamente un operatore e due operandi")

    operator, left, right = args
    if left.isdigit() and right.isdigit():
        try:
            return str(eval(f"{left}{operator}{right}"))
        except Exception as e:
            raise ValueError(f"Espressione non valida: {left}{operator}{right}") from e
    else:
        constant = left if isinstance(left, str) else right
        if CnlWizardCompiler.constants.get(constant) is None:
            raise ValueError(f"Costante non definita o non inizializzata: {constant}")

        if isinstance(left, str) and left in CnlWizardCompiler.constants:
            left = CnlWizardCompiler.constants[left]
        if isinstance(right, str) and right in CnlWizardCompiler.constants:
            right = CnlWizardCompiler.constants[right]

        try:
            return str(eval(f"{left}{operator}{right}"))
        except Exception as e:
            raise ValueError(f"Espressione non valida: {left}{operator}{right}") from e
def math_operand(value):
    return value
def comparison_operator(*args):
    items_dict = {'lo stesso': '=', 'uguale': '=', 'diverso': '!=', 'più': '>', 'maggiore': '>', 'minore': '<', 'maggiore o uguale': '>=', 'minore o uguale': '<=', 'almeno': '>=', 'al massimo': '<=', 'non dopo': '<=', 'prima': '<', 'dopo': '>'}
    item = ' '.join(args)
    return items_dict[item]
def comparison(*args):
    return [args[0], args[1], args[3]]
def comparison_value(value):
    return value
def between_operator(string_1, string_2):
    return [string_1, string_2]