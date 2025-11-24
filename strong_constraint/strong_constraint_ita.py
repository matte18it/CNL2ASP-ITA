def strong_constraint(clause):
    preds = re.findall(r"\b([A-Za-z_]\w*)\s*\(", clause)
    for p in preds:
        ensure_predicate_defined(p)
    return clause
def simple_definition_sequence(*simple_definition):
    return list(simple_definition)
def when_then_clause(simple_definition_1, simple_definition_2):
    return [simple_definition_1, simple_definition_2]

# 1. Positive Constraints
def positive_constraint(positive_constraint_body, terminal_clause=None):
    if not isinstance(positive_constraint_body, str):
        raise ValueError(f"Formato non valido per positive_constraint_body: {positive_constraint_body}")

    base = positive_constraint_body.strip().rstrip(".")

    if not terminal_clause:
        return base + "."

    terms = []
    parsed_conditions = []

    for t in terminal_clause:
        if not t:
            continue
        if isinstance(t, (list, tuple)):
            for elem in t:
                elem_str = str(elem)
                if blocks := re.findall(r"\[\[(.*?)\]\]", elem_str):
                    pairs = [re.findall(r"([A-Za-z_]\w*)\s*=\s*(.+?)(?=\]|,|$)", b) for b in blocks]
                    parsed_conditions.append([(v.strip(), val.strip()) for g in pairs for v, val in g])
                else:
                    terms.append(elem_str)
        else:
            t_str = str(t)
            if blocks := re.findall(r"\[\[(.*?)\]\]", t_str):
                pairs = [re.findall(r"([A-Za-z_]\w*)\s*=\s*(.+?)(?=\]|,|$)", b) for b in blocks]
                parsed_conditions.append([(v.strip(), val.strip()) for g in pairs for v, val in g])
            else:
                terms.append(t_str)

    if not parsed_conditions:
        if terms:
            return base + ", " + ", ".join(terms) + "."
        return base + "."

    rules = []

    var_conditions = {}
    for cond_group in parsed_conditions:
        for var, val in cond_group:
            if var not in var_conditions:
                var_conditions[var] = []
            var_conditions[var].append(val)

    if var_conditions:
        variables = list(var_conditions.keys())
        values_lists = [var_conditions[v] for v in variables]

        for value_combo in itertools.product(*values_lists):
            assigns = [f"{var} = {val}" for var, val in zip(variables, value_combo)]
            rule_parts = [base]
            if terms:
                rule_parts.extend(terms)
            rule_parts.extend(assigns)
            rules.append(", ".join(rule_parts) + ".")

    return "\n".join(rules)
def positive_constraint_body(clause):
    return clause
def positive_constraint_comparison(comparison):
    if not isinstance(comparison, (list, tuple)) or len(comparison) != 3:
        raise ValueError(f"Formato non riconosciuto per positive_constraint_comparison: {comparison}")

    left, op, right = comparison

    negated_ops = {
        "=": "!=",
        "!=": "=",
        "<": ">=",
        ">": "<=",
        "<=": ">",
        ">=": "<",
    }

    negated_op = negated_ops.get(op, f"NOT({op})")
    return f":- {left.strip()} {negated_op} {right.strip()}"
def positive_constraint_quantified_assignment_proposition(quantified_assignment_proposition):
    if not isinstance(quantified_assignment_proposition, str):
        raise ValueError(f"Formato non valido: {quantified_assignment_proposition}")

    if ":-" in quantified_assignment_proposition:
        head, body = map(str.strip, quantified_assignment_proposition.split(":-", 1))
        return f":- not {head}, {body}"
    else:
        return f":- not {quantified_assignment_proposition.strip()}"
def positive_constraint_quantified_choice_proposition(quantified_choice_proposition):
    if not isinstance(quantified_choice_proposition, str):
        raise ValueError(f"Formato non valido: {quantified_choice_proposition}")

    if ":-" in quantified_choice_proposition:
        head, body = map(str.strip, quantified_choice_proposition.split(":-", 1))
    else:
        head, body = quantified_choice_proposition.strip(), ""

    head = head.rstrip(".").strip()
    body = body.rstrip(".").strip()

    m = re.search(r"(\d+)\s*<=\s*\{(.+?)\}\s*<=\s*(\d+)", head)
    if m:
        lower, content, upper = m.groups()
        lower, upper = lower.strip(), upper.strip()
        left = f":- {{{content.strip()}}} < {lower}"
        right = f":- {{{content.strip()}}} > {upper}"
        if body:
            left += f", {body}"
            right += f", {body}"
        return left + ".\n" + right + "."

    invert = {"=": "!=", "!=": "=", "<": ">=", "<=": ">", ">": "<=", ">=": "<"}
    inverted_head = re.sub(r"(<=|>=|!=|=|<|>)", lambda m: invert[m.group(0)], head)

    if body:
        return f":- {inverted_head}, {body}"
    else:
        return f":- {inverted_head}"
def positive_constraint_when_then_clause(when_then_clause):
    if not isinstance(when_then_clause, (list, tuple)) or len(when_then_clause) != 2:
        raise ValueError(f"Formato non valido per when_then_clause: {when_then_clause}")

    when_part, then_parts = when_then_clause

    when_part = when_part.strip().rstrip(".")
    when_head, when_body = map(str.strip, when_part.split(":-", 1)) if ":-" in when_part else (when_part, "")

    if isinstance(then_parts, str):
        then_parts = [then_parts]

    negated_then_heads = []
    then_bodies = []

    for clause in then_parts:
        clause = clause.strip().rstrip(".")

        head, body = map(str.strip, clause.split(":-", 1)) if ":-" in clause else (clause, "")

        if head.startswith("not "):
            head = head.replace("not ", "", 1).strip()
        else:
            head = f"not {head}"

        negated_then_heads.append(head)
        if body:
            then_bodies.append(body)

    parts = [when_head] + negated_then_heads + ([when_body] if when_body else []) + then_bodies
    full_body = ", ".join(parts)

    return f":- {full_body}"
def positive_constraint_simple_definition_sequence(simple_definition_sequence):
    if not isinstance(simple_definition_sequence, (list, tuple)) or len(simple_definition_sequence) == 0:
        raise ValueError(f"Formato non valido per simple_definition_sequence: {simple_definition_sequence}")

    parts = []

    for clause in simple_definition_sequence:
        clause = clause.strip().rstrip(".")
        head, body = map(str.strip, clause.split(":-", 1)) if ":-" in clause else (clause, "")

        if head.startswith("not "):
            head = head.replace("not ", "", 1).strip()
        else:
            head = f"not {head.strip()}"

        if body:
            parts.append(f"{head}, {body}")
        else:
            parts.append(head)

    full_body = ", ".join(parts)
    return f":- {full_body}"
def positive_constraint_fact_proposition(fact_proposition):
    if not isinstance(fact_proposition, str):
        raise ValueError(f"Formato non valido per fact_proposition: {fact_proposition}")

    fact = fact_proposition.strip().rstrip(".")
    return f":- not {fact}"
def positive_constraint_whenever_then_clause_choice(whenever_then_clause_choice):
    if not isinstance(whenever_then_clause_choice, str):
        raise ValueError(f"Formato non valido per whenever_then_clause_choice: {whenever_then_clause_choice}")

    rule = whenever_then_clause_choice.strip().rstrip(".")
    if ":-" in rule:
        head, body = map(str.strip, rule.split(":-", 1))
    else:
        head, body = rule, ""

    match = re.search(r"(\d+)\s*<=\s*\{(.+?)\}\s*<=\s*(\d+)", head)
    if match:
        lower, content, upper = match.groups()
        content = content.strip()
        lower, upper = lower.strip(), upper.strip()

        left = f":- {{{content}}} < {lower}"
        right = f":- {{{content}}} > {upper}"
        if body:
            left += f", {body}"
            right += f", {body}"
        return left + ".\n" + right + "."

    if "{" in head and "}" in head:
        if body:
            return f":- not {head}, {body}."
        else:
            return f":- not {head}."

    if body:
        return f":- not {head}, {body}."
    else:
        return f":- not {head}."
def positive_constraint_whenever_then_clause_assignment(whenever_then_clause_assignment):
    if not isinstance(whenever_then_clause_assignment, str):
        raise ValueError(f"Formato non valido per whenever_then_clause_assignment: {whenever_then_clause_assignment}")

    rule = whenever_then_clause_assignment.strip().rstrip(".")
    if ":-" in rule:
        head, body = map(str.strip, rule.split(":-", 1))
        return f":- not {head}, {body}."
    else:
        return f":- not {rule}."

# 2. Negative Constraints
def negative_constraint(negative_constraint_body, terminal_clause=None):
    if not isinstance(negative_constraint_body, str):
        raise ValueError(f"Formato non valido per negative_constraint_body: {negative_constraint_body}")

    base = ":- " + negative_constraint_body.strip().lstrip(":-").strip().rstrip(".")

    if not terminal_clause:
        return base + "."

    terms = []
    parsed_conditions = []

    for t in terminal_clause:
        if not t:
            continue
        if isinstance(t, (list, tuple)):
            for elem in t:
                elem_str = str(elem)
                if blocks := re.findall(r"\[\[(.*?)\]\]", elem_str):
                    pairs = [re.findall(r"([A-Za-z_]\w*)\s*=\s*(.+?)(?=\]|,|$)", b) for b in blocks]
                    parsed_conditions.append([(v.strip(), val.strip()) for g in pairs for v, val in g])
                else:
                    terms.append(elem_str)
        else:
            t_str = str(t)
            if blocks := re.findall(r"\[\[(.*?)\]\]", t_str):
                pairs = [re.findall(r"([A-Za-z_]\w*)\s*=\s*(.+?)(?=\]|,|$)", b) for b in blocks]
                parsed_conditions.append([(v.strip(), val.strip()) for g in pairs for v, val in g])
            else:
                terms.append(t_str)

    if not parsed_conditions:
        if terms:
            return base + ", " + ", ".join(terms) + "."
        return base + "."

    rules = []
    body_base = base.lstrip(":-").strip()

    var_conditions = {}
    for cond_group in parsed_conditions:
        for var, val in cond_group:
            if var not in var_conditions:
                var_conditions[var] = []
            var_conditions[var].append(val)

    if var_conditions:
        variables = list(var_conditions.keys())
        values_lists = [var_conditions[v] for v in variables]

        for value_combo in itertools.product(*values_lists):
            assigns = [f"{var} = {val}" for var, val in zip(variables, value_combo)]
            rule_parts = [body_base]
            if terms:
                rule_parts.extend(terms)
            rule_parts.extend(assigns)
            rules.append(":- " + ", ".join(rule_parts) + ".")

    return "\n".join(rules)
def negative_constraint_body(clause):
    return clause
def negative_constraint_comparison(comparison):
    if not isinstance(comparison, (list, tuple)) or len(comparison) != 3:
        raise ValueError(f"Formato non riconosciuto per negative_constraint_comparison: {comparison}")

    left, op, right = comparison
    return f":- {left.strip()} {op.strip()} {right.strip()}"
def negative_constraint_quantified_choice_proposition(quantified_choice_proposition):
    if not isinstance(quantified_choice_proposition, str):
        raise ValueError(f"Formato non valido per quantified_choice_proposition: {quantified_choice_proposition}")

    if ":-" in quantified_choice_proposition:
        head, body = map(str.strip, quantified_choice_proposition.split(":-", 1))
        asp_rule = f":- {head}, {body}"
    else:
        asp_rule = f":- {quantified_choice_proposition.strip()}"

    return asp_rule
def negative_constraint_quantified_assignment_proposition(quantified_assignment_proposition):
    if not isinstance(quantified_assignment_proposition, str):
        raise ValueError(f"Formato non valido per quantified_assignment_proposition: {quantified_assignment_proposition}")

    if ":-" in quantified_assignment_proposition:
        head, body = map(str.strip, quantified_assignment_proposition.split(":-", 1))
        asp_rule = f":- {head}, {body}"
    else:
        asp_rule = f":- {quantified_assignment_proposition.strip()}"

    return asp_rule
def negative_constraint_when_then_clause(when_then_clause):
    if not isinstance(when_then_clause, (list, tuple)) or len(when_then_clause) != 2:
        raise ValueError(f"Formato non valido per when_then_clause: {when_then_clause}")

    when_part, then_parts = when_then_clause

    when_part = when_part.strip().rstrip(".")
    when_head, when_body = map(str.strip, when_part.split(":-", 1)) if ":-" in when_part else (when_part, "")

    if isinstance(then_parts, str):
        then_parts = [then_parts]

    then_heads = []
    then_bodies = []

    for clause in then_parts:
        clause = clause.strip().rstrip(".")

        head, body = map(str.strip, clause.split(":-", 1)) if ":-" in clause else (clause, "")

        then_heads.append(head)
        if body:
            then_bodies.append(body)

    parts = [when_head] + then_heads + ([when_body] if when_body else []) + then_bodies
    full_body = ", ".join(parts)

    return f":- {full_body}"
def negative_constraint_simple_definition_sequence(simple_definition_sequence):
    if not isinstance(simple_definition_sequence, (list, tuple)) or len(simple_definition_sequence) == 0:
        raise ValueError(f"Formato non valido per simple_definition_sequence: {simple_definition_sequence}")

    parts = []

    for clause in simple_definition_sequence:
        clause = clause.strip().rstrip(".")
        head, body = map(str.strip, clause.split(":-", 1)) if ":-" in clause else (clause, "")

        if body:
            parts.append(f"{head}, {body}")
        else:
            parts.append(head)

    full_body = ", ".join(parts)
    return f":- {full_body}"
def negative_constraint_fact_proposition(fact_proposition):
    if not isinstance(fact_proposition, str):
        raise ValueError(f"Formato non valido per fact_proposition: {fact_proposition}")

    fact = fact_proposition.strip().rstrip(".")
    return f":- {fact}"
def negative_constraint_whenever_then_clause_choice(whenever_then_clause_choice):
    if not isinstance(whenever_then_clause_choice, str):
        raise ValueError(f"Formato non valido per whenever_then_clause_choice: {whenever_then_clause_choice}")

    rule = whenever_then_clause_choice.strip().rstrip(".")
    if ":-" in rule:
        head, body = map(str.strip, rule.split(":-", 1))
        return f":- {head}, {body}."
    else:
        return f":- {rule}."
def negative_constraint_whenever_then_clause_assignment(whenever_then_clause_assignment):
    if not isinstance(whenever_then_clause_assignment, str):
        raise ValueError(f"Formato non valido per whenever_then_clause_assignment: {whenever_then_clause_assignment}")

    rule = whenever_then_clause_assignment.strip().rstrip(".")
    if ":-" in rule:
        head, body = map(str.strip, rule.split(":-", 1))
        return f":- {head}, {body}."
    else:
        return f":- {rule}."