def standard_proposition(proposition):
    return proposition

# 1. Quantified Choice Proposition:
def quantified_choice_proposition(*args):
    subject_entity = args[0]
    auxiliary_verb = args[1]

    cardinality = None
    verb = None
    objects_list = []
    foreach_clause = None

    for i in range(2, len(args)):
        arg = args[i]
        if arg is None:
            continue

        if isinstance(arg, list):
            if arg and isinstance(arg[0], str) and (arg[0].startswith('>= ') or arg[0].startswith('<= ')):
                cardinality = arg
            else:
                objects_list = arg

        elif isinstance(arg, str):
            if arg.startswith(('= ', '<= ', '>= ')):
                cardinality = arg
            elif 'per ogni' in arg.lower():
                foreach_clause = arg
            elif verb is not None and arg.split('(')[0] in CnlWizardCompiler.signatures:
                foreach_clause = arg
            elif verb is None:
                verb = arg

    if verb is None:
        verb = auxiliary_verb

    if '(' in verb:
        verb_parts = verb.split('), ')
        verb_entity = verb_parts[0] + ')'
        verb_constraints = verb_parts[1:] if len(verb_parts) > 1 else []
        verb_name = verb_entity.split('(')[0].lower()
    else:
        verb_name = verb.lower()
        verb_entity = None
        verb_constraints = []

    verb_name_clean = verb_name.split('_')[0] if '_' in verb_name else verb_name
    if verb_name_clean in {"uno", "un", "una", "il", "lo", "la", "i", "gli", "le"} and objects_list:
        first_pred = objects_list[0]
        match = re.match(r"^\s*([A-Za-z_]\w*)\s*\(", first_pred)
        if match:
            verb_name_clean = match.group(1).lower()

    subj_name = subject_entity.split('(')[0]
    if subj_name not in CnlWizardCompiler.signatures:
        raise ValueError(f"L'entità '{subj_name}' non è definita nel CNLWizard.")

    if verb_name_clean not in CnlWizardCompiler.signatures:
        register_new_definition(verb_name_clean)

    objects_list = objects_list or []
    for obj in objects_list:
        verify_obj_attributes_exist(obj)

    foreach_name, foreach_params_clean, foreach_params_full = None, [], []
    if foreach_clause:
        foreach_name, foreach_params_full, _ = parse_quantified_entity(foreach_clause)
        if foreach_name not in CnlWizardCompiler.signatures:
            raise ValueError(f"L'entità del foreach '{foreach_name}' non è definita nel CNLWizard.")
        foreach_params_full = [p.replace("(", "").replace(")", "").replace(",", "").strip() for p in foreach_params_full]
        foreach_params_clean = [p for p in foreach_params_full if p != "_"]

    subj_name, subj_params, _ = parse_quantified_entity(subject_entity)
    subj_params = [p.replace("(", "").replace(")", "").replace(",", "").strip() for p in subj_params]
    subj_head_params = extract_subject_head_params(subj_name, subj_params)

    if subj_head_params and (not subj_params or subj_params[0] == "_"):
        subj_params[0] = subj_head_params[0]

    body_parts = [build_entity_body(subj_name, subj_params)]

    if verb_entity:
        body_parts.append(verb_entity)
    body_parts.extend(verb_constraints)

    if foreach_clause and foreach_name in CnlWizardCompiler.signatures:
        keys = list(CnlWizardCompiler.signatures[foreach_name].keys)
        fields = list(CnlWizardCompiler.signatures[foreach_name].fields.keys())
        total = len(keys) + len(fields)
        foreach_body = [foreach_params_full[i] if i < len(foreach_params_full) else "_" for i in range(total)]
        body_parts.append(f"{foreach_name}({', '.join(foreach_body)})")

    body = ", ".join(body_parts)

    if len(objects_list) == 0:
        head_pred = f"{verb_name_clean}({', '.join(subj_head_params + foreach_params_clean)})"

        result = f"{{ {head_pred} }} :- {body}."
        return result.replace("))", ")").replace(", )", ")").replace(" ,", ",").replace("  ", " ")
    if len(objects_list) == 1:
        obj_name, obj_params, _ = parse_quantified_entity(objects_list[0])
        obj_params = [p.replace("(", "").replace(")", "").replace(",", "").strip() for p in obj_params]
        obj_head_params = [p for p in obj_params if p != "_" and p not in subj_head_params]

        verb_head_params = []
        if verb_entity and '(' in verb_entity:
            verb_head_params = extract_head_args_from_entity_string(verb_entity)

        head_pred = f"{verb_name_clean}({', '.join(subj_head_params + verb_head_params + obj_head_params + foreach_params_clean)})"

        if obj_name in CnlWizardCompiler.signatures:
            keys = list(CnlWizardCompiler.signatures[obj_name].keys)
            fields = list(CnlWizardCompiler.signatures[obj_name].fields.keys())
            obj_cond = [obj_params[i] if i < len(obj_params) else "_" for i in range(len(keys) + len(fields))]
            obj_condition = f"{obj_name}({', '.join(obj_cond)})"
        else:
            obj_condition = f"{obj_name}({', '.join(obj_params)})"

        if cardinality:
            if isinstance(cardinality, list):
                card_left, card_right = cardinality[0].split()[1], cardinality[1].split()[1]
            elif cardinality.startswith("= "):
                num = cardinality.split()[1]
                card_left, card_right = num, num
            elif cardinality.startswith("<= "):
                card_left, card_right = "0", cardinality.split()[1]
            elif cardinality.startswith(">= "):
                card_left, card_right = cardinality.split()[1], None
            else:
                card_left, card_right = cardinality, cardinality

            result = f"{card_left} <= {{{head_pred} : {obj_condition}}} "
            result += f"<= {card_right} " if card_right else ""
            result += f":- {body}."
        else:
            result = f"{{{head_pred} : {obj_condition}}} :- {body}."

        return result.replace("))", ")").replace(", )", ")").replace(" ,", ",").replace("  ", " ")

    else:
        head_parts = []
        for obj in objects_list:
            obj_name, obj_params, _ = parse_quantified_entity(obj)
            obj_params = [p.replace("(", "").replace(")", "").replace(",", "").strip() for p in obj_params]
            obj_head_params = [p for p in obj_params if p != "_" and p not in subj_head_params]
            head_parts.append(f"{obj_name}({', '.join(subj_head_params + obj_head_params + foreach_params_clean)})")

        result = f"{' | '.join(head_parts)} :- {body}."
        return result.replace("))", ")").replace(", )", ")").replace(" ,", ",").replace("  ", " ")
def quantified_assignment_proposition(*args):
    subject_entity = args[0]
    auxiliary_verb = args[1]
    objects_list = args[2] if len(args) > 2 else []
    foreach_clause = args[3] if len(args) > 3 else None

    objects_list = objects_list or []

    if objects_list:
        first_obj = objects_list[0]
        pred_name = first_obj.split("(")[0].lower()
    else:
        raise ValueError("quantified_assignment_proposition: manca l'oggetto della regola.")

    subj_name = subject_entity.split('(')[0]
    if subj_name not in CnlWizardCompiler.signatures:
        raise ValueError(f"L'entità '{subj_name}' non è definita nel CNLWizard.")

    if pred_name not in CnlWizardCompiler.signatures and pred_name not in new_definition:
        register_new_definition(pred_name)

    ensure_predicate_defined(pred_name)

    for obj in objects_list:
        verify_obj_attributes_exist(obj)

    foreach_name, foreach_params_clean, foreach_params_full = None, [], []
    if foreach_clause:
        foreach_name, foreach_params_full, _ = parse_quantified_entity(foreach_clause)
        if foreach_name not in CnlWizardCompiler.signatures:
            raise ValueError(f"L'entità del foreach '{foreach_name}' non è definita nel CNLWizard.")
        foreach_params_full = [p.replace("(", "").replace(")", "").replace(",", "").strip() for p in foreach_params_full]
        foreach_params_clean = [p for p in foreach_params_full if p != "_"]

    subj_name, subj_params, subj_constraints = parse_quantified_entity(subject_entity)
    subj_params = [p.replace("(", "").replace(")", "").replace(",", "").strip() for p in subj_params]

    subj_head_params = extract_subject_head_params(subj_name, subj_params)

    body_parts = [build_entity_body(subj_name, subj_params)]
    body_parts.extend(subj_constraints)

    if foreach_clause and foreach_name in CnlWizardCompiler.signatures:
        keys = list(CnlWizardCompiler.signatures[foreach_name].keys)
        fields = list(CnlWizardCompiler.signatures[foreach_name].fields.keys())
        total = len(keys) + len(fields)
        foreach_body = [foreach_params_full[i] if i < len(foreach_params_full) else "_" for i in range(total)]
        body_parts.append(f"{foreach_name}({', '.join(foreach_body)})")

    rules = []
    for obj in objects_list:
        obj_name, obj_params, _ = parse_quantified_entity(obj)
        obj_params = [p.replace("(", "").replace(")", "").replace(",", "").strip() for p in obj_params]
        obj_head_params = [p for p in obj_params if p != "_" and p not in subj_head_params]

        head = f"{obj_name}({', '.join(subj_head_params + obj_head_params + foreach_params_clean)})"
        body = ", ".join(body_parts)

        rules.append(f"{head} :- {body}.".replace("))", ")").replace(", )", ")").replace(" ,", ",").replace("  ", " "))

    return "\n".join(rules)

#  2. Fact Proposition:
def fact_proposition(entity):
    pred = entity.split("(")[0].lower()
    ensure_predicate_defined(pred)
    return f"{entity}."

# 3. Whenever-Then Proposition:
def whenever_then_clause_choice(whenever_clauses, then_subject_choice, auxiliary_verb, verb, cardinality, list_of_entities, such_that_clause):
    body = ", ".join(whenever_clauses).strip().rstrip(",")
    if not body:
        raise ValueError("whenever_then_clause_choice: manca la parte 'whenever' (body vuoto).")

    head_core = ""

    real_verb = verb or ""
    for aux in ("essere", "è", "ha"):
        real_verb = real_verb.replace(aux, "")
    real_verb = real_verb.strip()

    if "(" in real_verb:
        real_verb = real_verb.split("(", 1)[0].strip()

    verb_name_clean = real_verb.lower().split("_")[0] if "_" in real_verb.lower() else real_verb.lower()

    if verb and then_subject_choice and then_subject_choice[0]:
        subject_var = then_subject_choice[0]

        first_clause = whenever_clauses[0]
        match_ent = re.match(r"^not\s+([a-zA-Z_]\w*)|^([a-zA-Z_]\w*)", first_clause.strip())
        if match_ent:
            subject_entity_name = (match_ent.group(1) or match_ent.group(2)).strip()
        else:
            raise ValueError("Impossibile determinare l'entità del soggetto nel whenever.")

        if verb_name_clean and verb_name_clean not in CnlWizardCompiler.signatures:
            register_new_definition(verb_name_clean)

        if list_of_entities and len(list_of_entities) == 1:
            target_pred = list_of_entities[0]

            match = re.match(r"^\s*([a-zA-Z_]\w*)\s*\((.*?)\)\s*$", target_pred)
            if match:
                target_name = match.group(1).strip()
                target_vars = match.group(2).strip()
            else:
                target_name, target_vars = target_pred.strip(), ""

            explicit_vars = [v.strip() for v in target_vars.split(",") if v.strip() and v.strip() != "_"]

            head_args = ", ".join([subject_var] + explicit_vars) if explicit_vars else subject_var

            head_core = f"{verb_name_clean}({head_args}) : {target_name}({target_vars})"

        else:
            head_core = f"{verb_name_clean}({subject_var})"

    elif list_of_entities:
        head_core = " | ".join(list_of_entities) if len(list_of_entities) > 1 else list_of_entities[0]

    else:
        raise ValueError("whenever_then_clause_choice: manca la testa (né verb né list_of_entities presenti).")

    if such_that_clause:
        such_that_str = ", ".join(such_that_clause)
        head_core = f"{head_core}, {such_that_str}" if ":" in head_core else f"{head_core} : {such_that_str}"

    if cardinality:
        card_expr = cardinality.strip()

        eq_match = re.match(r"^=\s*(\S+)", card_expr)
        le_match = re.match(r"^<=\s*(\S+)", card_expr)
        ge_match = re.match(r"^>=\s*(\S+)", card_expr)
        between_match = re.match(r"^[<>]*\s*(?:tra|fra)\s*(\S+)\s*e\s*(\S+)", card_expr)

        if eq_match:
            left = right = eq_match.group(1)
        elif le_match:
            left, right = "0", le_match.group(1)
        elif ge_match:
            left, right = ge_match.group(1), "inf"
        elif between_match:
            left, right = between_match.group(1), between_match.group(2)
        else:
            left, right = "0", "inf"

        rule = f"{left} <= {{ {head_core} }} <= {right} :- {body}."
    else:
        rule = f"{{ {head_core} }} :- {body}."

    return rule
def whenever_then_clause_assignment(whenever_clauses, then_subject_assignment, auxiliary_verb, entity):
    body = ", ".join(whenever_clauses) if whenever_clauses else ""

    def pick_predicate(*candidates):
        for c in candidates:
            if not c:
                continue
            if isinstance(c, list) and c:
                c = c[-1]
            s = str(c).strip()
            if not s or s.lower() in ("avere", "essere", "ha", "è"):
                continue
            if "(" in s and ")" in s and s.index("(") < s.index(")"):
                if s.lower().startswith("avere "):
                    s = s[6:].strip()
                elif s.lower().startswith("essere "):
                    s = s[7:].strip()
                return s
        return None

    head = pick_predicate(entity, auxiliary_verb, then_subject_assignment)
    if not head:
        raise ValueError("Impossibile determinare la testa della regola.")

    match = re.match(r"^\s*([a-zA-Z_]\w*)\s*\((.*?)\)\s*$", head)
    if match:
        head_pred = match.group(1).strip()
        if head_pred not in CnlWizardCompiler.signatures and head_pred not in new_definition:
            first_clause = whenever_clauses[0]
            subj_ent = first_clause.split("(")[0].replace("not", "").strip()
            register_new_definition(head_pred)

        ensure_predicate_defined(head_pred)

        raw_args = match.group(2).strip()
        head_args_list = [a.strip() for a in raw_args.split(",")] if raw_args else []
    else:
        head_pred = head.strip()
        head_args_list = []

    body_vars = set(re.findall(r"\b[A-Z][A-Za-z0-9_]*\b", body))

    subject_var = None
    if then_subject_assignment and isinstance(then_subject_assignment, list) and then_subject_assignment[0]:
        subject_var = then_subject_assignment[0].strip()

    if subject_var:
        if head_args_list:
            head_args_list[0] = subject_var
        else:
            head_args_list = [subject_var]

    body_predicates = []
    for match in re.finditer(r"([a-zA-Z_]\w*)\s*\(([^)]*)\)", body):
        name = match.group(1).strip()
        args = [a.strip() for a in match.group(2).split(",")] if match.group(2).strip() else []
        body_predicates.append((name, args))

    signatures = CnlWizardCompiler.signatures

    new_body_parts = []
    replaced = False
    for body_name, body_args in body_predicates:
        if not subject_var or body_name not in signatures:
            new_body_parts.append(f"{body_name}({', '.join(body_args)})")
            continue

        body_sig = signatures[body_name]
        keys_list = list(body_sig.keys.keys()) if isinstance(body_sig.keys, dict) else list(body_sig.keys)
        fields_list = list(body_sig.fields.keys()) if isinstance(body_sig.fields, dict) else list(body_sig.fields)

        if head_pred not in fields_list:
            new_body_parts.append(f"{body_name}({', '.join(body_args)})")
            continue

        abs_index = len(keys_list) + fields_list.index(head_pred)

        total_len = max(len(body_args), abs_index + 1)
        new_args = ["_"] * total_len
        new_args[abs_index] = subject_var

        new_body_parts.append(f"{body_name}({', '.join(new_args)})")
        replaced = True

    new_body = ", ".join(new_body_parts) if new_body_parts else body
    if subject_var and not replaced and body_predicates:
        raise ValueError(f"Nel body non esiste un campo '{head_pred}' in nessun predicato: {body}")

    head_args = ", ".join(head_args_list)

    rule = f"{head_pred}({head_args}) :- {new_body}." if head_args else f"{head_pred} :- {new_body}."
    return rule

def then_subject_choice(string):
    return [string] if string else [None]
def then_subject_assignment(string):
    return [string] if string else [None]
def whenever_clauses(*whenever_clause):
    return list(whenever_clause)
def whenever_clause(existence_condition):
    return existence_condition
def such_that_clause(*existence_condition):
    return list(existence_condition)
def existence_condition(negation=None, entity=None):
    if negation:
        return f"not {entity}"
    return entity