from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler
from datetime import datetime, timedelta
import re
import itertools

# Variabili Generali
timeslotDict = {}
temporal_maps = {
    "minuti": "minutes",
    "minuto": "minutes",
    "ore": "hours",
    "ora": "hours",
    "giorni": "days",
    "giorno": "days",
    "steps": "steps",
    "step": "steps"
}
aggregate_symbol = {
    "somma": "#sum",
    "totale": "#sum",
    "più alto": "#max",
    "più basso": "#min",
    "numero": "#count",
}
new_definition = {}

# Elementi Generali
def start(*propositions):
    constants = []
    rules = []

    for prop in propositions:
        if not prop or not isinstance(prop, str):
            continue

        individual_rules = prop.split('\n')

        for single_rule in individual_rules:
            single_rule = single_rule.strip()

            if not single_rule:
                continue

            if single_rule.startswith("#const"):
                constants.append(single_rule)
            else:
                cleaned_prop = clean_rule(single_rule)
                rules.append(cleaned_prop)

    return '\n'.join(constants + rules)
def proposition(fact):
    return fact
def articles(*args):
    return args[0]
def preposition(*args):
    return args[0]
def verb(string, attribute=None, preposition=None):
    verb_name = string.lower()

    if attribute:
        if isinstance(attribute, list) and attribute and isinstance(attribute[0], list):
            attr_list = attribute
        else:
            attr_list = [attribute] if attribute else []

        params = []
        constraints = []

        for attr_block in attr_list:
            if attr_block is None:
                continue

            attr_name = attr_block[0]
            attr_label = attr_block[1] if len(attr_block) > 1 else None
            attr_condition = attr_block[2] if len(attr_block) > 2 else None

            if attr_label:
                if isinstance(attr_label, str) and not attr_label.startswith('"'):
                    if not attr_label.isdigit() and not attr_label.isupper():
                        attr_label = f'"{attr_label}"'
                params.append(attr_label)
            else:
                var_name = normalize_string(verb_name + " " + attr_name).upper()
                params.append(var_name)

            if attr_condition and isinstance(attr_condition, list):
                op = attr_condition[0]
                val = attr_condition[1]

                if isinstance(val, str) and not val.startswith('"') and not val.isdigit() and not val.isupper():
                    val = f'"{val}"'

                used_label = attr_label if attr_label else var_name
                constraints.append(f"{used_label} {op} {val}")

        if preposition:
            verb_name = f"{verb_name}_{preposition}"

        if params:
            result = f"{verb_name}({', '.join(params)})"
        else:
            result = verb_name

        if constraints:
            result += ", " + ", ".join(constraints)

        return result

    if preposition:
        return f"{verb_name}_{preposition.strip()}"

    return verb_name
def auxiliary_verb(*args):
    return args[0]
def attribute_name(articles, string_1, string_2):
    if string_2 is None:
        return [string_1]
    else:
        if len(string_2) == 1 and string_2.isupper():
            raise ValueError(
                f"Errore: '{string_2}' non ha una forma corretta. Gli attributi devono avere nomi in minuscolo."
            )
        elif string_2[0].isupper():
            raise ValueError(
                f"Errore: '{string_2}' non ha una forma corretta. Gli attributi devono avere nomi in minuscolo."
            )
        else:
            return [string_1 + string_2[0].upper() + string_2[1:]]
def assignment_verb(*args):
    return args[0]
def foreach_clause(string):
    return string
def negation(*args):
    return args[0]

# Funzioni Generali
def isTemporalEntityInDictionary(name, value):
    if name not in timeslotDict:
        raise ValueError(f"Concetto temporale non trovato: {name}")

    for entry in timeslotDict[name]:
        if f'"{value}"' in entry:
            index = entry.split("(")[1].split(",")[0]
            return index.strip()

    raise ValueError(f"Valore '{value}' non trovato in {name}")
def extract_head_args_from_entity_string(entity_str):
    if '(' not in entity_str:
        return []

    parts = entity_str.split('), ')

    if len(parts) > 1:
        entity_part = parts[0] + ')'
    else:
        entity_part = parts[0]

    name = entity_part.split('(')[0]

    start_paren = entity_part.find('(')
    end_paren = entity_part.rfind(')')

    if start_paren == -1 or end_paren == -1:
        return []

    content = entity_part[start_paren+1:end_paren]

    if name in CnlWizardCompiler.signatures:
        keys = list(CnlWizardCompiler.signatures[name].keys)
        if not keys:
            return []

        params = []
        depth = 0
        current = ""
        in_quotes = False

        for char in content:
            if char == '"':
                in_quotes = not in_quotes
            elif char == '(' and not in_quotes:
                depth += 1
            elif char == ')' and not in_quotes:
                depth -= 1
            elif char == ',' and depth == 0 and not in_quotes:
                params.append(current.strip())
                current = ""
                continue
            current += char
        if current.strip():
            params.append(current.strip())

        result = []
        for i, key in enumerate(keys):
            if i < len(params) and params[i] != "_":
                result.append(params[i])
        return result if result else [params[0]] if params and params[0] != "_" else []
    else:
        params = []
        depth = 0
        current = ""
        in_quotes = False

        for char in content:
            if char == '"':
                in_quotes = not in_quotes
            elif char == '(' and not in_quotes:
                depth += 1
            elif char == ')' and not in_quotes:
                depth -= 1
            elif char == ',' and depth == 0 and not in_quotes:
                params.append(current.strip())
                current = ""
                continue
            current += char
        if current.strip():
            params.append(current.strip())

        return params
def normalize_string(s: str) -> str:
    no_vowels = "".join(ch for ch in s if ch.lower() not in "aeiou")
    no_spaces = no_vowels.replace(" ", "_")
    return no_spaces.upper()
def extract_head_args_from_entity(ent_block):
    ent, label = ent_block[0][0].lower(), ent_block[0][1]
    attrs = ent_block[1] or []

    if not (isinstance(attrs, list) and attrs and isinstance(attrs[0], (list, tuple))):
        attrs = [attrs] if attrs else []

    keys = list(CnlWizardCompiler.signatures[ent].keys)

    if label is not None:
        if isinstance(label, str) and not (label.isdigit() or label.isupper()):
            return [f'"{label}"']
        else:
            return [str(label)]

    attr_map = {}
    for a in attrs:
        name = a[0]
        lab = a[1] if len(a) > 1 else None
        cond = a[2] if len(a) > 2 else None

        if lab:
            if isinstance(lab, str) and not (lab.isdigit() or lab.isupper()):
                attr_map[name] = f'{lab}'
            else:
                attr_map[name] = str(lab)
        elif cond:
            attr_map[name] = normalize_string(ent + " " + name).upper()

    args = []

    if keys:
        for k in keys:
            if k in attr_map:
                args.append(attr_map[k])

        if not args:
            args = [normalize_string(ent + " " + keys[0]).upper()]
    else:
        all_attrs = list(CnlWizardCompiler.signatures[ent].fields.keys())
        args = [normalize_string(ent + " " + all_attrs[0]).upper()]

    return args
def register_new_definition(pred_name):
    if pred_name not in new_definition:
        new_definition[pred_name] = None
def ensure_predicate_defined(pred_name: str):
    pred_name = pred_name.lower().strip()

    if pred_name in CnlWizardCompiler.signatures:
        return

    if pred_name in new_definition:
        return

    raise ValueError(f"Errore: il predicato '{pred_name}' non è definito. ")
def clean_rule(rule):
    if not rule or not isinstance(rule, str):
        return rule

    rule = rule.strip()

    if not rule or rule.startswith('%'):
        return rule

    if rule.startswith('#const'):
        return rule

    if ':~' in rule:
        parts = rule.split(':~', 1)
        prefix = parts[0]
        rest = parts[1]

        if '. [' in rest:
            body_part, weight_part = rest.split('. [', 1)
            weight_part = '. [' + weight_part
        else:
            body_part = rest.rstrip('.')
            weight_part = '.'

        cleaned_body = _remove_duplicates_from_body(body_part)
        return f":~ {cleaned_body}{weight_part}"

    elif ':-' in rule:
        parts = rule.split(':-', 1)
        head = parts[0].strip()
        body = parts[1].strip().rstrip('.')

        cleaned_body = _remove_duplicates_from_body(body)

        if not head or rule.strip().startswith(':-'):
            return f":- {cleaned_body}."
        else:
            return f"{head} :- {cleaned_body}."

    else:
        if not rule.endswith('.'):
            return rule + '.'
        return rule
def _remove_duplicates_from_body(body):
    if not body:
        return body

    predicates = []
    current = ""
    depth = 0
    brace_depth = 0
    in_quotes = False

    for char in body:
        if char == '"':
            in_quotes = not in_quotes
        elif not in_quotes:
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            elif char == '{':
                brace_depth += 1
            elif char == '}':
                brace_depth -= 1
            elif char == ',' and depth == 0 and brace_depth == 0:
                predicates.append(current.strip())
                current = ""
                continue
        current += char

    if current.strip():
        predicates.append(current.strip())

    seen = set()
    unique_predicates = []

    for pred in predicates:
        pred_normalized = pred.strip()

        if pred_normalized not in seen:
            seen.add(pred_normalized)
            unique_predicates.append(pred_normalized)

    return ', '.join(unique_predicates)
def _save_fact(subject_name, fact):
    if subject_name not in timeslotDict:
        timeslotDict[subject_name] = []
    timeslotDict[subject_name].append(fact)
def extract_subject_head_params(subj_name, subj_params):
    subj_head_params = []

    if subj_name not in CnlWizardCompiler.signatures:
        return subj_head_params

    subj_keys = list(CnlWizardCompiler.signatures[subj_name].keys)
    subj_fields = list(CnlWizardCompiler.signatures[subj_name].fields.keys())
    all_positions = subj_keys + subj_fields

    for i in range(len(all_positions)):
        if i < len(subj_params) and subj_params[i] != "_":
            subj_head_params.append(subj_params[i])

    if not subj_head_params:
        first_key = subj_keys[0]
        subj_head_params = [normalize_string(subj_name + " " + first_key).upper()]

    return subj_head_params
def build_entity_body(entity_name, entity_params):
    if entity_name in CnlWizardCompiler.signatures:
        keys = list(CnlWizardCompiler.signatures[entity_name].keys)
        fields = list(CnlWizardCompiler.signatures[entity_name].fields.keys())
        total_attrs = len(keys) + len(fields)

        body_parts = []
        for i in range(total_attrs):
            if i < len(entity_params):
                body_parts.append(entity_params[i])
            else:
                body_parts.append("_")

        result = f"{entity_name}({', '.join(body_parts)})"
        return result
    else:
        result = f"{entity_name}({', '.join(entity_params)})"
        return result
def verify_obj_attributes_exist(obj_entity_str):
    if '(' not in obj_entity_str:
        return

    obj_name = obj_entity_str.split('(')[0]
    if obj_name in CnlWizardCompiler.signatures:
        return

    name, params, _ = parse_quantified_entity(obj_entity_str)
    params = [p.replace("(", "").replace(")", "").replace(",", "").strip() for p in params]

    for param in params:
        if param == "_" or param.isdigit() or param.isupper():
            continue
        if param.startswith('"') and param.endswith('"'):
            continue
        if param.islower() and param not in CnlWizardCompiler.signatures:
            raise ValueError(
                f"L'attributo o entità '{param}' non è definito nel CNLWizard. "
                f"Se stai definendo '{obj_name}', assicurati che tutti gli attributi esistano."
            )
def parse_quantified_entity(entity_str):
    if '(' not in entity_str:
        return entity_str, [], []

    parts = entity_str.split('), ')
    entity_part = parts[0] + ')'
    constraints = parts[1:] if len(parts) > 1 else []

    name = entity_part.split('(')[0]
    content = entity_part[len(name)+1:-1]

    params = []
    depth = current = 0
    in_quotes = False
    current = ""

    for char in content:
        if char == '"':
            in_quotes = not in_quotes
        elif char == '(' and not in_quotes:
            depth += 1
        elif char == ')' and not in_quotes:
            depth -= 1
        elif char == ',' and depth == 0 and not in_quotes:
            params.append(current.strip())
            current = ""
            continue
        current += char
    if current:
        params.append(current.strip())

    return name, params, constraints
def generate_head_variable(entity_name, param_index):
    return f"_X{param_index}"

