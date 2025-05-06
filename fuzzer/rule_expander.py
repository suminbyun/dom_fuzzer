import random

def expand_rule(rule_key, html_rule):
    sequence = random.choice(html_rule[rule_key])
    expanded = []
    for part in sequence.split(","):
        part = part.strip()
        if part.startswith("@"):
            expanded.extend(expand_rule(part, html_rule))
        else:
            expanded.append(part)
    return expanded
