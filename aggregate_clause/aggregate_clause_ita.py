def aggregate_clause(clause):
    return clause
def simple_aggregate(aggregate_operator, preposition, entity):
    op = (aggregate_operator or "").lower().strip()
    op_symbol = next((v for k, v in aggregate_symbol.items() if re.search(k, op)), None)
    if not op_symbol:
        raise ValueError(f"Operatore di aggregazione non riconosciuto: {op}")

    entity_str = str(entity).strip()
    pred = entity_str.split("(", 1)[0]
    if pred not in CnlWizardCompiler.signatures:
        raise ValueError(f"Entità non riconosciuta: {pred}")

    sig = CnlWizardCompiler.signatures[pred]
    keys = getattr(sig, "keys", [])
    fields = getattr(sig, "fields", [])
    arity = len(keys or []) + len(fields or [])

    rm_vowels = lambda s: ''.join(ch for ch in s.upper() if ch not in "AEIOU")

    given_args = []
    if "(" in entity_str and ")" in entity_str:
        args_str = entity_str[entity_str.find("(") + 1:entity_str.rfind(")")]
        given_args = [a.strip() for a in args_str.split(",") if a.strip()]

    key = given_args[0] if given_args else (keys[0] if keys else "_")
    key_var = key if given_args else f"{rm_vowels(pred)}_{rm_vowels(key)}"

    if arity <= 0:
        pred_term = pred
    elif arity == 1:
        pred_term = f"{pred}({key_var})"
    else:
        args = given_args + ["_"] * (arity - len(given_args))
        args[0] = key_var
        pred_term = f"{pred}({', '.join(args[:arity])})"

    return f"{op_symbol}{{{pred_term}: {pred_term}}}"
def qualified_aggregate(aggregate_operator, preposition_1, string, preposition_2, entity):
    op = (aggregate_operator or "").lower().strip()
    op_symbol = next((v for k, v in aggregate_symbol.items() if re.search(k, op)), None)
    if not op_symbol:
        raise ValueError(f"Operatore di aggregazione non riconosciuto: {op}")

    entity_str = str(entity).strip()
    pred = entity_str.split("(", 1)[0]
    if pred not in CnlWizardCompiler.signatures:
        raise ValueError(f"Entità non riconosciuta: {pred}")

    sig = CnlWizardCompiler.signatures[pred]
    keys = list(sig.keys)
    fields = list(sig.fields.keys())
    all_attrs = keys + fields

    target_field = string.strip().lower()
    if target_field not in all_attrs:
        raise ValueError(f"L'attributo '{target_field}' non esiste in {pred}")

    var = normalize_string(target_field)

    if "(" in entity_str and ")" in entity_str:
        args_str = entity_str[entity_str.find("(") + 1:entity_str.rfind(")")]
        given_args = [a.strip() for a in args_str.split(",") if a.strip()]
    else:
        given_args = []

    pred_args = []
    for i, attr in enumerate(all_attrs):
        if i < len(given_args) and given_args[i] != "_":
            val = given_args[i]
        else:
            val = "_"

        if attr == target_field:
            val = var

        pred_args.append(val)

    pred_term = f"{pred}({', '.join(pred_args)})"
    return f"{op_symbol}{{{var}: {pred_term}}}"
def relative_aggregate(aggregate_operator, preposition, string, entity, auxiliary_verb, list_of_entities):
    op = (aggregate_operator or "").lower().strip()
    op_symbol = next((v for k, v in aggregate_symbol.items() if re.search(k, op)), None)
    if not op_symbol:
        raise ValueError(f"Operatore di aggregazione non riconosciuto: {op}")

    def ent_name(s: str) -> str:
        s = str(s).strip()
        return s.split("(", 1)[0]

    def ent_args(s: str):
        s = str(s)
        if "(" not in s:
            return []
        inside = s[s.find("(")+1:s.rfind(")")]
        return [a.strip() for a in inside.split(",")] if inside.strip() else []

    target_field = (string or "").strip().lower()
    rel_str = str(entity).strip()
    rel_pred = ent_name(rel_str)
    rel_sig = CnlWizardCompiler.signatures[rel_pred]
    if not rel_sig:
        raise ValueError(f"Relazione non riconosciuta: {rel_pred}")

    rel_attrs = list(rel_sig.keys) + list(rel_sig.fields.keys())
    rel_args_in = ent_args(rel_str)

    if not list_of_entities or not list_of_entities[0]:
        raise ValueError("Relazione/entità di contesto mancante nella clausola relativa.")
    ctx_str = str(list_of_entities[0]).strip()
    ctx_pred = ent_name(ctx_str)
    ctx_sig = CnlWizardCompiler.signatures[ctx_pred]
    if not ctx_sig:
        raise ValueError(f"Entità di contesto non riconosciuta: {ctx_pred}")
    ctx_attrs = list(ctx_sig.keys) + list(ctx_sig.fields.keys())
    ctx_args_in = ent_args(ctx_str)

    if target_field not in rel_attrs:
        raise ValueError(f"L'attributo '{target_field}' non esiste in {rel_pred}")

    def find_ref(name, attrs):
        return next((a for a in attrs if a == name or a.startswith(name) or re.search(name[:4], a)), None)

    rel_ref_to_ctx = find_ref(ctx_pred, rel_attrs)
    if not rel_ref_to_ctx:
        raise ValueError(f"La relazione '{rel_pred}' non ha riferimento a '{ctx_pred}'")

    var_target = normalize_string(target_field)
    if ctx_args_in and ctx_args_in[0] and ctx_args_in[0] != "_":
        var_ctx_key = ctx_args_in[0]
    else:
        ctx_key_name = (list(ctx_sig.keys) or ["ID"])[0]
        var_ctx_key = normalize_string(f"{ctx_pred} {ctx_key_name}")

    rel_final = []
    for i, a in enumerate(rel_attrs):
        if a == target_field:
            rel_final.append(var_target)
        elif a == rel_ref_to_ctx:
            rel_final.append(var_ctx_key)
        else:
            rel_final.append(rel_args_in[i] if i < len(rel_args_in) and rel_args_in[i] else "_")
    rel_term = f"{rel_pred}({', '.join(rel_final)})"

    ctx_arity = len(ctx_attrs)
    if ctx_arity <= 0:
        ctx_term = ctx_pred
    else:
        ctx_out = []
        for i in range(ctx_arity):
            if i == 0:
                ctx_out.append(var_ctx_key)
            else:
                ctx_out.append(ctx_args_in[i] if i < len(ctx_args_in) and ctx_args_in[i] else "_")
        ctx_term = f"{ctx_pred}({', '.join(ctx_out)})"

    return f"{op_symbol}{{{var_target}: {rel_term}, {ctx_term}}}"
def locative_aggregate(aggregate_operator, preposition, string, entity_1, auxiliary_verb, entity, list_of_entities):
    op = (aggregate_operator or "").lower().strip()
    op_symbol = next((v for k, v in aggregate_symbol.items() if re.search(k, op)), None)
    if not op_symbol:
        raise ValueError(f"Operatore di aggregazione non riconosciuto: {op}")

    rm_vowels = lambda s: ''.join(ch for ch in s.upper() if ch not in "AEIOU")
    ent_name  = lambda s: str(s).strip().split("(", 1)[0]
    ent_args  = lambda s: [a.strip() for a in str(s)[str(s).find("(")+1:str(s).rfind(")")].split(",")] if "(" in str(s) else []

    def get_sig(name):
        name = name.strip().lower()

        if name in CnlWizardCompiler.signatures:
            return CnlWizardCompiler.signatures[name]

        if name in new_definition:
            class FakeSig:
                keys = []
                fields = {}
            return FakeSig()

        raise ValueError(f"Entità o relazione non riconosciuta: {name}")

    def key_var(name, args, sig):
        keys = list(sig.keys)
        if not keys: return "_"
        return args[0] if args and args[0] and args[0] != "_" else f"{rm_vowels(name)}_{rm_vowels(keys[0])}"

    def find_ref(entity, attrs):
        for cond in (lambda a: a == entity,
                     lambda a: a.startswith(entity),
                     lambda a: re.search(entity[:4], a)):
            found = next((a for a in attrs if cond(a)), None)
            if found: return found
        return None

    main_str, rel_str = str(entity_1).strip(), str(entity).strip()
    rel_sig = get_sig(ent_name(rel_str))
    rel_attrs = list(rel_sig.keys) + list(rel_sig.fields.keys())

    if len(rel_attrs) <= 1:
        main = ent_name(main_str)
        main_sig = get_sig(main)
        var = key_var(main, ent_args(main_str), main_sig)

        rel_pred = ent_name(rel_str)
        rel_call = f"{rel_pred}({var})"

        return f"{op_symbol}{{{var}: {rel_call}}}"

    sec_str = (list_of_entities or [None])[0]
    if sec_str is None:
        raise ValueError("Aggregato relazionale richiesto ma manca la seconda entità nella frase.")

    main, rel, sec = map(ent_name, (main_str, rel_str, sec_str))
    main_sig, rel_sig, sec_sig = map(get_sig, (main, rel, sec))
    main_keys, sec_keys = list(main_sig.keys), list(sec_sig.keys)
    main_fields, sec_fields = list(main_sig.fields.keys()), list(sec_sig.fields.keys())
    rel_attrs = list(rel_sig.keys) + list(rel_sig.fields.keys())

    main_args, rel_args, sec_args = map(ent_args, (main_str, rel_str, sec_str))

    target_field = string.strip().lower()
    if target_field not in rel_attrs:
        raise ValueError(f"L'attributo '{target_field}' non esiste in {rel}")
    var_target = normalize_string(target_field)

    rel_main_ref, rel_sec_ref = map(lambda e: find_ref(e, rel_attrs), (main, sec))
    if not rel_main_ref or not rel_sec_ref:
        raise ValueError(f"'{rel}' non collega correttamente '{main}' e '{sec}'")

    var_main_ref = key_var(main, main_args, main_sig)
    var_sec_ref  = key_var(sec, sec_args, sec_sig)

    rel_final = [
        var_target if a == target_field else
        var_main_ref if a == rel_main_ref else
        var_sec_ref if a == rel_sec_ref else
        (rel_args[i] if i < len(rel_args) and rel_args[i] else "_")
        for i, a in enumerate(rel_attrs)
    ]
    rel_term = f"{rel}({', '.join(rel_final)})"

    def build_entity(name, args, keys, fields, key_ref):
        all_attrs = keys + fields
        out = [(args[i] if i < len(args) and args[i] and args[i] != "_" else
                (key_ref if i == 0 and keys else "_"))
               for i, _ in enumerate(all_attrs)]
        return f"{name}({', '.join(out)})"

    main_term = build_entity(main, main_args, main_keys, main_fields, var_main_ref)
    sec_term  = build_entity(sec,  sec_args,  sec_keys,  sec_fields,  var_sec_ref)

    return f"{main_term}, {op_symbol}{{{var_target}: {rel_term}, {sec_term}}}"
def aggregate_operator(*args):
    return args[0]