def weak_constraint(optimization_statement=None, priority_level=None, clause=None, string=None, weak_constraint_operator=None, terminal_clause=None):
    if clause:
        preds = re.findall(r"\b([A-Za-z_]\w*)\s*\(", clause)
        for p in preds:
            ensure_predicate_defined(p)

    base = ":~ " + clause.strip().lstrip(":~").strip().rstrip(".")
    terminal_vars = []
    assign_vars = []
    terms = []
    parsed_conditions = []

    if terminal_clause:
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

    for t in terms:
        matches = re.findall(r"\(([A-Z][A-Za-z0-9_]*)", t)
        for m in matches:
            if m not in terminal_vars:
                terminal_vars.append(m)

    sign = ""
    if weak_constraint_operator == "-" or (isinstance(weak_constraint_operator, list) and "-" in weak_constraint_operator):
        sign = "-"
    elif optimization_statement == "-" or (isinstance(optimization_statement, list) and "-" in optimization_statement):
        sign = "-"

    prio_map = {"bassa priorità": "1", "media priorità": "2", "alta priorità": "3", "[1]": "1", "[2]": "2", "[3]": "3"}
    if isinstance(priority_level, list) and priority_level:
        priority = prio_map.get(str(priority_level[0]), "1")
    elif isinstance(priority_level, str):
        priority = prio_map.get(priority_level, "1")
    else:
        priority = "1"

    if string:
        weight = string.strip()
    elif "=" in clause:
        m = re.search(r"=\s*([A-Z][A-Za-z0-9_]*)\b", clause)
        weight = m.group(1) if m else "1"
    else:
        weight = "1"

    rules = []
    body_base = base.lstrip(":~").strip()

    var_conditions = {}
    for cond_group in parsed_conditions:
        for var, val in cond_group:
            if var not in var_conditions:
                var_conditions[var] = []
            var_conditions[var].append(val)

    if var_conditions:
        variables = list(var_conditions.keys())
        values_lists = [var_conditions[v] for v in variables]

        for combo in itertools.product(*values_lists):
            assigns = [f'{var} = {val}' for var, val in zip(variables, combo)]
            rule_parts = [body_base]
            if terms:
                rule_parts.extend(terms)
            rule_parts.extend(assigns)

            for var in variables:
                if var not in assign_vars:
                    assign_vars.append(var)

            final_vars = [v for v in terminal_vars if v not in assign_vars]

            vars_part = f", {', '.join(final_vars)}" if final_vars else ""
            rules.append(f":~ {', '.join(rule_parts)}. [{sign}{weight}@{priority}{vars_part}]")
    else:
        rule_parts = [body_base]
        if terms:
            rule_parts.extend(terms)

        vars_part = f", {', '.join(terminal_vars)}" if terminal_vars else ""
        rules.append(f":~ {', '.join(rule_parts)}. [{sign}{weight}@{priority}{vars_part}]")

    result = "\n".join(rules)
    return result

def optimization_statement(*args):
    return ["-"] if args[0] == "quanto più possibile" else ["+"]
def weak_constraint_operator(*args):
    return ["-"] if args[0] == "massimizzato" else ["+"]
def priority_level(*args):
    return [1] if args[0] == "bassa priorità" else [2] if args[0] == "priorità media" else [3]

def weak_constraint_comparison(comparison):
    if not isinstance(comparison, (list, tuple)) or len(comparison) != 3:
        raise ValueError(f"Formato comparison non valido: {comparison}")

    left, operator, right = map(str.strip, map(str, comparison))

    left = left.rstrip('.').strip()
    right = right.rstrip('.').strip()

    result = f":~ {left} {operator} {right}"
    return result
def weak_constraint_simple_definition(simple_definition):
    if not isinstance(simple_definition, str):
        raise ValueError(f"Formato non valido per simple_definition: {simple_definition}")

    cleaned = simple_definition.strip().rstrip(".").strip()

    if ":-" in cleaned:
        head, body = map(str.strip, cleaned.split(":-", 1))
        result = f":~ {head}, {body}"
    else:
        result = f":~ {cleaned}"
    return result
def weak_constraint_whenever_clause(*whenever_clause):
    if len(whenever_clause) == 1 and isinstance(whenever_clause[0], (list, tuple)):
        clauses = whenever_clause[0]
    else:
        clauses = whenever_clause

    formatted = [c.strip().rstrip('.') for c in clauses if isinstance(c, str) and c.strip()]

    if not formatted:
        raise ValueError(f"Nessuna clausola valida trovata in {whenever_clause}")

    result = f":~ {', '.join(formatted)}"
    return result
def weak_constraint_aggregate_clause(aggregate_clause):
    if not isinstance(aggregate_clause, str):
        raise ValueError(f"Formato non valido per aggregate_clause: {aggregate_clause}")

    cleaned = aggregate_clause.strip().rstrip('.')

    if "{" in cleaned:
        agg_type = cleaned.split("{", 1)[0].strip("#").strip()
    else:
        agg_type = "val"

    abbrev = ''.join(ch for ch in agg_type if ch.lower() not in 'aeiou').upper()

    result = f":~ {cleaned} = {abbrev}"
    return result