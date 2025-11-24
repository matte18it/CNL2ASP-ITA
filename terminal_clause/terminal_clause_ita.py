def terminal_clause(*clause):
    return clause
def where_clause(*values):
    needs_quotes = lambda v: isinstance(v, str) and v.strip('"').strip("'").isalpha() and v.strip('"').strip("'").islower()
    with_quotes = {"è uno di", "è uno dei", "fa parte di", "rientra tra", "è uno tra", "è rispettivamente"}
    without_quotes = {
        "è rispettivamente uno dei", "è rispettivamente uno tra",
        "fa rispettivamente parte di uno dei", "fa rispettivamente parte di uno tra",
        "corrisponde rispettivamente a uno dei", "corrisponde rispettivamente a uno tra"
    }

    def build_list(field, where_type, vals):
        if not isinstance(vals, (list, tuple)):
            vals = [vals]
        if where_type in with_quotes:
            items = [f'[{field} = {v}]' if str(v).isdigit() else f'[{field} = "{v}"]'for v in vals]
        elif where_type in without_quotes:
            for v in vals:
                if v not in CnlWizardCompiler.constants and not v.isdigit():
                    raise ValueError(f"Errore: costante '{v}' non presente in CnlWizard")
            items = [f"[{field} = {v}]" for v in vals]
        else:
            raise ValueError(f"Tipo where_type non riconosciuto: {where_type}")
        return items

    if len(values) == 3 and all(isinstance(v, str) for v in values) and values[1].strip().startswith("è"):
        field, op, val = values
        result = build_list(field, op, [val])
        return "[" + ", ".join(result) + "]"

    if len(values) == 2 and isinstance(values[0], str) and isinstance(values[1], list) and len(values[1]) == 2:
        low, high = values[1]
        return f"{low} <= {values[0]} <= {high}"

    if len(values) == 3 and all(isinstance(values[i], str if i < 2 else list) for i in range(3)):
        result = build_list(values[0], values[1], values[2])
        return "[" + ", ".join(result) + "]"

    blocks = []
    for v in values:
        if isinstance(v, str):
            blocks.append(v)
        elif isinstance(v, (list, tuple)):
            if len(v) == 3:
                field, op, val = v
                if op.strip().startswith("è"):
                    val_list = val if isinstance(val, (list, tuple)) else [val]
                    result = build_list(field, op, val_list)
                    blocks.append("[" + ", ".join(result) + "]")
                else:
                    val_str = f'"{val}"' if needs_quotes(val) else val
                    blocks.append(f"{field} {op} {val_str}")
        else:
            raise ValueError(f"Formato non riconosciuto per where_clause: {v}")

    return ", ".join(blocks)
def when_clause(simple_clause_list):
    if not isinstance(simple_clause_list, list) or not simple_clause_list:
        raise ValueError(f"Formato non valido per when_clause: {simple_clause_list}")

    entity = simple_clause_list[0]

    has_negation = len(simple_clause_list) > 1 and simple_clause_list[1] == 'non'

    if has_negation:
        negation = 'non'
        verb = simple_clause_list[2] if len(simple_clause_list) > 2 else None
        targets = simple_clause_list[3] if len(simple_clause_list) > 3 else []
    else:
        negation = None
        verb = simple_clause_list[2] if len(simple_clause_list) > 2 else None
        targets = simple_clause_list[3] if len(simple_clause_list) > 3 else []

    skip_check, articles = {"serve", "lavora_in", "ha"}, {"un", "una", "uno", "il", "lo", "la"}

    def extract(pred):
        if "(" not in pred: return pred.strip(), []
        name = pred.split("(")[0].strip()
        return name, [p.strip() for p in pred[pred.find("(")+1:pred.rfind(")")].split(",")]

    def is_known(pred):
        n, _ = extract(pred)
        return n.lower() in skip_check or n in CnlWizardCompiler.signatures

    first_var = lambda params: next((p for p in params if p and p != "_" and p.isupper()), None)

    ent_name, ent_params = extract(entity)
    if not is_known(entity):
        raise ValueError(f"Entità non riconosciuta in CnlWizard: {ent_name}")

    targets = [targets] if isinstance(targets, str) else (targets if isinstance(targets, list) else [])
    is_attr_mode = verb and verb.lower() in articles

    if not is_attr_mode:
        main_var = first_var(ent_params)
        target_vars = []
        for t in targets:
            if not isinstance(t, str): raise ValueError(f"Target non valido: {t}")
            name, params = extract(t)
            if not is_known(t): raise ValueError(f"Predicato non riconosciuto in CnlWizard: {name}")
            if v := first_var(params): target_vars.append(v)

        result = []
        if verb and main_var and target_vars:
            verb_pred = f"{verb.strip()}({', '.join([main_var]+target_vars)})"
            if negation:
                verb_pred = f"not {verb_pred}"
            result.append(verb_pred)
        result.extend([entity] + targets)
        return ", ".join(result)

    sig = CnlWizardCompiler.signatures[ent_name]
    if not sig:
        raise ValueError(f"Nessuna signature definita per l'entità '{ent_name}'.")
    positions = list(getattr(sig, "keys", [])) + list(getattr(sig, "fields", {}).keys())
    ent_params += ["_"] * (len(positions) - len(ent_params))

    for t in targets:
        if not isinstance(t, str): raise ValueError(f"Target non valido: {t}")
        t_name, t_params = extract(t)
        if not is_known(t): raise ValueError(f"Predicato non riconosciuto in CnlWizard: {t_name}")
        try:
            idx = next(i for i, f in enumerate(positions) if f.lower() == t_name.lower())
            if var := first_var(t_params): ent_params[idx] = var
        except StopIteration:
            raise ValueError(f"L'entità '{ent_name}' non possiede il campo '{t_name}'.")

    return ", ".join([f"{ent_name}({', '.join(ent_params)})"] + targets)
def simple_clause_list(entity, negation, auxiliary_verb, verb, list_of_entities):
    return [entity, negation, verb, list_of_entities]
def variable(string):
    return string
def string_list(string):
    return string
def string_list_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res
def where_type(*args):
    return args[0]