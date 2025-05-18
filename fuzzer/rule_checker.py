FORBIDDEN_IN_A = {
    "a", "form", "div", "section", "article",
    "header", "footer", "h1", "h2", "h3",
    "h4", "h5", "h6", "textarea", "button",
    "label", "meter", "progress"
}

def is_main_already_used(used_tags):
    return used_tags.get("main", False)

def is_valid_child(parent, child, html_rule):
    if parent == "a" and (child in html_rule["TEXTNODE_BLOCK"] or child in FORBIDDEN_IN_A):
        return False
    if parent == "p" and child not in html_rule["TEXTNODE_INLINE"]:
        return False
    return True

def is_tag_allowed(tag, used_tags, apply=False):
    if tag == "main":
        if used_tags.get("main", False):
            return False
        if apply:
            used_tags["main"] = True

    if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        required_prior = {
            "h2": "h1",
            "h3": "h2",
            "h4": "h3",
            "h5": "h4",
            "h6": "h5",
        }
        heading_used = used_tags.setdefault("heading_used", set())

        if tag != "h1":
            required = required_prior[tag]
            if required not in heading_used:
                return False

        if tag in heading_used:
            return False
        if apply:
            heading_used.add(tag)

    return True