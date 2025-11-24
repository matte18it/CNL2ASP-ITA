def explicit_definition_proposition(domain_definition=None):
    return domain_definition

# 1. Definizioni di dominio
def domain_definition(*clause):
    if clause[2] is None and clause[3] is None:
        CnlWizardCompiler.signatures[clause[1].lower()] = (clause[1].lower(), [], [], '')
    elif clause[2] is None:
        CnlWizardCompiler.signatures[clause[1].lower()] = (clause[1].lower(), [item[0] for item in clause[3:]], [], '')
    elif clause[3] is None:
        CnlWizardCompiler.signatures[clause[1].lower()] = (clause[1].lower(), [], clause[2], '')
    else:
        CnlWizardCompiler.signatures[clause[1].lower()] = (clause[1].lower(), [item[0] for item in clause[3:]], clause[2], '')
def subject_name(string):
    return string
def key_name(articles, string_1, string_2=None):
    if string_1[0].isupper():
        raise ValueError(
            f"Errore: '{string_1}' non ha una forma corretta. Le chiavi devono avere nomi in minuscolo."
        )

    if string_2 is None:
        return [string_1]
    else:
        if string_2[0].isupper():
            raise ValueError(
                f"Errore: '{string_2}' non ha una forma corretta. "
                f"Le chiavi devono avere nomi in minuscolo."
            )
        return [string_1 + string_2[0].upper() + string_2[1:]]
def key_name_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res

# 2. Definizioni di concetti temporali
def temporal_concept_definition(articles, subject_name, temporal_type_1, temporal_range_1, temporal_range_2, number=None, temporal_type_2=None):
    if temporal_type_2 is not None and temporal_maps.__getitem__(temporal_type_1[0]) != temporal_maps.__getitem__(temporal_type_2[0]):
        raise ValueError(f"I tipi temporali devono essere uguali: {temporal_type_1[0]} e {temporal_type_2[0]}.")

    if subject_name in timeslotDict:
        raise ValueError(f"Il concetto temporale '{subject_name.lower()}' è già definito.")

    temporal_type_1 = temporal_type_1[0]
    temporal_range_1 = temporal_range_1[0]
    temporal_range_2 = temporal_range_2[0]
    if temporal_type_2 is not None:
        temporal_type_2 = temporal_type_2[0]

    if number is not None:
        number = int(number)

    results = []
    index = 1

    if temporal_type_1 == "steps":
        start = int(temporal_range_1)
        end = int(temporal_range_2)
        step = number if number is not None else 1

        current = start
        while current <= end:
            fact = f'{subject_name.lower()}({index}, {current}).'
            results.append(fact)
            _save_fact(subject_name.lower(), fact)
            current += step
            index += 1

    elif temporal_type_1 in ["minuti", "ore"]:
        start_time = datetime.strptime(temporal_range_1, "%H:%M")
        end_time = datetime.strptime(temporal_range_2, "%H:%M")

        if number is None:
            step = timedelta(minutes=1) if temporal_type_1 == "minuti" else timedelta(hours=1)
        else:
            if temporal_type_2 == "minuti":
                step = timedelta(minutes=number)
            elif temporal_type_2 == "ore":
                step = timedelta(hours=number)
            else:
                raise ValueError(f"Unsupported temporal type for step: {temporal_type_2}")

        current = start_time
        while current <= end_time:
            formatted_time = current.strftime("%H:%M")
            fact = f'{subject_name.lower()}({index}, "{formatted_time}").'
            results.append(fact)
            _save_fact(subject_name.lower(), fact)
            current += step
            index += 1

    elif temporal_type_1 == "giorni":
        start_date = datetime.strptime(temporal_range_1, "%d/%m/%Y")
        end_date = datetime.strptime(temporal_range_2, "%d/%m/%Y")

        if number is None:
            step = timedelta(days=1)
        else:
            if temporal_type_2 in ["giorno", "giorni"]:
                step = timedelta(days=number)
            else:
                raise ValueError(f"Unsupported temporal type for step: {temporal_type_2}")

        current = start_date
        while current <= end_date:
            formatted_date = current.strftime("%d/%m/%Y")
            fact = f'{subject_name.lower()}({index}, "{formatted_date}").'
            results.append(fact)
            _save_fact(subject_name.lower(), fact)
            current += step
            index += 1

    if results:
        results.pop()

    CnlWizardCompiler.signatures[subject_name.lower()] = (subject_name.lower(), ['valore'], ['id'], '')

    return "\n".join(results)
def temporal_type(*args):
    return [args[0]]
def temporal_range(number_1, number_2=None, number_3=None):
    if number_2 is None and number_3 is None:
        return [number_1]
    elif number_2 is not None and number_3 is None:
        return [f"{number_1}:{number_2}"]
    elif number_2 is not None and number_3 is not None:
        return [f"{number_1}/{number_2}/{number_3}"]