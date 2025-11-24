def simple_definition(*args):
    subject = args[0]
    negation = args[1] if args[1] == 'non' else None
    auxiliary = args[2]
    verb = args[3]
    objects = args[4] if len(args) > 4 and args[4] is not None else []

    subj_name = subject.split('(')[0]
    if subj_name not in CnlWizardCompiler.signatures:
        raise ValueError(f"L'entità '{subj_name}' non è definita nel CNLWizard.")

    if '(' in verb:
        verb_parts = verb.split('), ')
        verb_entity = verb_parts[0] + ')'
        verb_constraints = verb_parts[1:] if len(verb_parts) > 1 else []
        verb_name = verb_entity.split('(')[0].lower()
    else:
        verb_name = verb.lower()
        verb_entity = verb
        verb_constraints = []

    verb_name_clean = verb_name.split('_')[0] if '_' in verb_name else verb_name

    for obj in objects:
        obj_name = obj.split('(')[0]
        if obj_name not in CnlWizardCompiler.signatures:
            raise ValueError(f"L'entità '{obj_name}' non è definita nel CNLWizard.")

    subject_args = extract_head_args_from_entity_string(subject)
    object_args = []
    for obj in objects:
        object_args.extend(extract_head_args_from_entity_string(obj))

    head_args = subject_args + object_args

    if verb_name_clean not in CnlWizardCompiler.signatures:
        register_new_definition(verb_name_clean)

    if negation:
        head = f"not {verb_name_clean}({', '.join(head_args)})"
    else:
        head = f"{verb_name_clean}({', '.join(head_args)})"

    body_parts = [subject]

    if '(' in verb_entity and verb_entity != verb:
        body_parts.append(verb_entity)

    body_parts.extend(verb_constraints)
    body_parts.extend(objects)

    body = ", ".join(body_parts)

    return f"{head} :- {body}."