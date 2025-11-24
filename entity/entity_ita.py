def entity(articles, entity_name, attribute):
    ent_name = entity_name[0].lower()
    label = entity_name[1]

    if attribute is None:
        attr_list = []
    elif isinstance(attribute, list) and attribute and isinstance(attribute[0], list):
        attr_list = attribute
    else:
        attr_list = [attribute]

    if ent_name in CnlWizardCompiler.signatures:
        entity_keys = list(CnlWizardCompiler.signatures[ent_name].keys)
        entity_fields = list(CnlWizardCompiler.signatures[ent_name].fields.keys())
        entity_positions = entity_keys + entity_fields
        total_len = len(entity_positions)

        attr_map = {}
        constraints = []

        for attr_block in attr_list:
            if attr_block is None:
                continue

            attr_name = attr_block[0]
            attr_label = attr_block[1] if len(attr_block) > 1 else None
            attr_condition = attr_block[2] if len(attr_block) > 2 else None

            if attr_condition and isinstance(attr_condition, list) and len(attr_condition) == 3:
                attr_label = attr_condition[0]
                attr_condition = attr_condition[1:]

            if attr_name not in entity_positions:
                entity_positions.append(attr_name)

            used_label = attr_label or normalize_string(ent_name + " " + attr_name).upper()
            attr_map[attr_name] = used_label

            if attr_condition:
                if isinstance(attr_condition, list) and len(attr_condition) == 2:
                    op, val = attr_condition
                    if isinstance(val, str) and not val.startswith('"') and not val.isdigit() and not val.isupper():
                        val = f'"{val}"'
                    if op in ["=", "!=", ">", "<", ">=", "<="]:
                        constraints.append(f"{used_label} {op} {val}")
                    elif all(str(x).isdigit() for x in attr_condition):
                        constraints.append(f"{attr_condition[0]} <= {used_label} <= {attr_condition[1]}")
                elif isinstance(attr_condition, str):
                    constraints.append(f"{used_label} {attr_condition}")

        head_parts = []
        has_key_specified = any(k in attr_map for k in entity_keys)

        for i, attr_name in enumerate(entity_positions):
            if attr_name in attr_map:
                head_parts.append(attr_map[attr_name])
            else:
                head_parts.append("_")

        if entity_keys and not has_key_specified:
            if label is not None:
                if isinstance(label, str) and not (label.isdigit() or label.isupper()):
                    head_parts[0] = f'"{label}"'
                else:
                    head_parts[0] = str(label)
            else:
                first_key = entity_keys[0]
                key_label = normalize_string(ent_name + " " + first_key).upper()
                head_parts[0] = key_label

        entity_str = f"{ent_name}({', '.join(head_parts)})"

        if constraints:
            return entity_str + ", " + ", ".join(constraints)
        else:
            return entity_str

    else:
        params = []
        constraints = []

        if label is not None:
            params.append(str(label))

        for attr_block in attr_list:
            if attr_block is None:
                continue

            attr_name = attr_block[0]
            attr_label = attr_block[1] if len(attr_block) > 1 else None
            attr_condition = attr_block[2] if len(attr_block) > 2 else None

            if attr_label:
                clean_label = attr_label.strip('"')
                if not clean_label.isdigit() and not clean_label.isupper():
                    params.append(f'"{clean_label}"')
                else:
                    params.append(clean_label)

            if attr_condition and isinstance(attr_condition, list) and len(attr_condition) == 2:
                op, val = attr_condition
                if isinstance(val, str) and not val.startswith('"') and not val.isdigit() and not val.isupper():
                    val = f'"{val}"'
                constraints.append(f"{attr_label} {op} {val}")

        entity_str = f"{ent_name}({', '.join(params)})"
        if constraints:
            return entity_str + ", " + ", ".join(constraints)
        else:
            return entity_str
def entity_name(string_1, string_2=None):
    return [string_1, string_2]
def attribute(name, equal_to=None, value_attribute=None, attribute_comparison=None):
    if attribute_comparison and isinstance(attribute_comparison, list) and len(attribute_comparison) == 3:
        value_attribute = attribute_comparison[0]
        attribute_comparison = attribute_comparison[1:]

    if equal_to and value_attribute is not None and not value_attribute.isdigit():
        value_attribute = f'"{value_attribute}"'

    return [name, value_attribute, attribute_comparison]
def attribute_concat(*args):
    result = []
    for arg in args:
        if isinstance(arg, list) and len(arg) > 0:
            if isinstance(arg[0], list):
                result.extend(arg)
            else:
                result.append(arg)
        else:
            result.append(arg)
    return result
def value_attribute(value):
    return value
def math_expression(string, math_symbol, number):
    return f"{string}{math_symbol}{number}"
def math_symbol(*args):
    return args[0]
def attribute_comparison(comparison, predicate=None, value=None):
    if value is None:
        return comparison

    if isinstance(value, str) and value.isdigit():
        return [comparison, value]

    if isinstance(value, str) and value in CnlWizardCompiler.constants:
        return [comparison, value]

    if isinstance(value, str) and value.isupper():
        return [comparison, value]

    if isinstance(value, str):
        return [comparison, f'"{value}"']

    if isinstance(value, (int, float)):
        return [comparison, str(value)]

    return [comparison, value]
def equal_to(*args):
    return args[0]
def list_of_entities(*entity):
    return list(entity)