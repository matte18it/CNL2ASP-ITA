def implicit_definition_proposition(domain_definition=None):
    return domain_definition

# 1. Definizioni di costanti:
def constant_definition_clause(string_1, string_2=None):
    if string_2 is None:
        CnlWizardCompiler.constants[string_1] = None
    else:
        value = int(string_2) if string_2.isdigit() else f'"{string_2}"'
        CnlWizardCompiler.constants[string_1] = value
        return f'#const {string_1} = {value}.'

# 2. Definizioni di clause composte:
def compounded_clause(*args):
    predicate_name, attribute1, *rest = args[1:]

    attribute_list = []
    attribute2 = None
    for r in rest:
        if isinstance(r, list) and len(r) == 2:
            attribute_list.append(r)
        else:
            attribute2 = r

    if not isinstance(attribute1, list) and attribute_list == []:
        CnlWizardCompiler.signatures[predicate_name.lower()] = (predicate_name.lower(), [], ["id"], '')
        return f'{predicate_name.lower()}({attribute1}..{attribute2}).'
    else:
        main_list = attribute1
        result_lines = []

        for i, val in enumerate(main_list):
            elementi = [val]
            for attr in attribute_list:
                _, attr_vals = attr
                elementi.append(attr_vals[i % len(attr_vals)])

            elementi_str = [(str(e) if str(e).isupper() or str(e).isnumeric() else f'"{e}"') for e in elementi]
            result_lines.append(f"{predicate_name.lower()}({', '.join(elementi_str)}).")

        attr_names = [attr[0] for attr in attribute_list]
        CnlWizardCompiler.signatures[predicate_name.lower()] = (predicate_name.lower(), attr_names, ["id"], "")

        return "\n".join(result_lines)
def compounded_attributes(string, compounded_list):
    return [string, compounded_list]
def compounded_list(string):
    return [string]
def compounded_list_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res

# 3. Definizioni enumerative
def enumerative_definition_clause(clause):
    return clause
def property_assignment(string, articles, value, attribute):
    entity = value.lower().strip()
    key = string.strip().strip('"')

    if entity not in CnlWizardCompiler.signatures:
        raise ValueError(f"Entità non definita: {entity}")

    signature = CnlWizardCompiler.signatures[entity]
    keys = list(signature.keys)
    fields = list(signature.fields.keys())
    positions = keys + fields

    provided = {}
    if attribute:
        attr_blocks = [attribute] if isinstance(attribute[0], str) else attribute
        for attr_name, attr_value, *_ in attr_blocks:
            attr_name = attr_name.strip()
            if attr_name not in fields:
                matches = [f for f in fields if f.startswith(attr_name)]
                if len(matches) == 1:
                    attr_name = matches[0]
                else:
                    raise ValueError(f"Attributo '{attr_name}' non definito per '{entity}'")
            provided[attr_name] = attr_value

    args = [
        (f'"{key}"' if key.isalpha() else key) if pos == keys[0]
        else provided.get(pos, "_")
        for pos in positions
    ]

    return f"{entity}({', '.join(args)})"
def conditional_enumerative(*entity):
    def smart_split(s: str):
        parts, buf, depth = [], "", 0
        for ch in s:
            if ch == "," and depth == 0:
                if buf.strip(): parts.append(buf.strip()); buf = ""
            else:
                buf += ch; depth += (ch == "(") - (ch == ")")
        if buf.strip(): parts.append(buf.strip())
        return parts

    clean_pred = lambda p: p.strip() + (")" * max(0, p.count("(") - p.count(")")))
    functor_and_args = lambda p: (m.group(1), [a.strip() for a in m.group(2).split(",")]) \
        if (m := re.match(r"^\s*([A-Za-z_]\w*)\s*\((.*?)\)\s*$", p)) else (None, [])

    def check_predicate(name: str, args: list[str]):
        if name.lower() not in CnlWizardCompiler.signatures:
            raise ValueError(f"Predicato non definito: {name}")
        sig = CnlWizardCompiler.signatures[name.lower()]
        expected = len(sig.keys) + len(sig.fields)
        if len(args) > expected:
            raise ValueError(f"Troppi argomenti per '{name}': attesi {expected}, trovati {len(args)}")
        for a in args:
            if a not in sig.keys and a not in sig.fields and not re.match(r'^[A-Z_0-9"\'\.]+$', a):
                raise ValueError(f"Attributo '{a}' non valido per '{name}'")

    if len(entity) >= 4 and all(isinstance(entity[i], str) for i in range(3)) \
            and entity[2].endswith("()") and isinstance(entity[3], tuple):

        ent1, subj, verb, terminal = entity[:4]
        subj, verb_name = subj.strip().upper(), verb.split("(")[0].strip()
        head = f"{verb_name}({subj})"
        body_parts = [clean_pred(p) for clause in terminal for p in smart_split(clause) if p.strip()]

        first_pred = re.match(r"([A-Za-z_]\w*)\s*\((.*?)\)", ent1)
        if first_pred:
            name, args = first_pred.group(1), [a.strip() for a in smart_split(first_pred.group(2))]
            check_predicate(name, args)

        if first_pred:
            args[0] = subj
            ent1_new = f"{name}({', '.join(args)})"
            if not any(ent1_new.split("(")[0] in b for b in body_parts):
                body_parts.insert(0, ent1_new)

        uniq_body = []
        for b in map(clean_pred, body_parts):
            if b not in uniq_body: uniq_body.append(b)
        return f"{head} :- {', '.join(uniq_body)}."

    parts = [e for e in entity if e]
    base_entities = [p for p in parts if "(" in p and ")" in p]
    words = [p for p in parts if "(" not in p and ")" not in p]
    terminal_groups = [p for p in parts if isinstance(p, tuple)]

    raw_verb = next((p for p in words if not any(p in b for b in base_entities)), "relazione").strip().lower()

    verb_name_clean = raw_verb.split('_')[0] if '_' in raw_verb else raw_verb

    if verb_name_clean not in CnlWizardCompiler.signatures and verb_name_clean not in new_definition:
        if base_entities:
            subj_name, _, _ = parse_quantified_entity(base_entities[0])
            register_new_definition(verb_name_clean)

    verb = verb_name_clean

    parsed_conditions = []
    for tg in terminal_groups:
        for elem in tg:
            if blocks := re.findall(r"\[\[(.*?)\]\]", elem):
                pairs = [re.findall(r"([A-Za-z_]\w*)\s*=\s*(.+?)(?=\]|,|$)", b) for b in blocks]
                parsed_conditions.append([(v.strip(), val.strip()) for g in pairs for v, val in g])

    if len(base_entities) >= 2:
        args = [(a[0] if a else "_") for _, a in (functor_and_args(be) for be in base_entities)]
        head = f"{verb}({', '.join(args)})"
    else:
        head = verb

    for be in base_entities:
        name, args = functor_and_args(be)
        if name: check_predicate(name, args)

    rules = []
    if parsed_conditions:
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
                rule_body = [*base_entities, *assigns]
                rules.append(f"{head} :- {', '.join(rule_body)}.")
    else:
        rules.append(f"{head} :- {', '.join(base_entities)}.")

    return "\n".join(rules)