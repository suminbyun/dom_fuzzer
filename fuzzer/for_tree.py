import random

element_counter = 0
text_counter = 1
current_prefix = "el_"

def reset_counters(prefix="el_"):
    global element_counter, text_counter, current_prefix
    element_counter = 1
    text_counter = 1
    current_prefix = prefix

def generate_incremental_text():
    global text_counter
    val = f"{text_counter:06d}"
    text_counter += 1
    return val

def get_element_count(prefix="el_"):
    return element_counter

class Node:
    def __init__(self, tag, children=None, text="", prefix=None):
        global element_counter, current_prefix
        self.tag = tag
        self.children = children or []
        self.text = text
        pfx = prefix or current_prefix
        self.var_name = f"{pfx}{element_counter:06d}"
        element_counter += 1

def build_table_tree(prefix="el_"):
    table = Node("table", prefix=prefix)

    if random.choice([True, False]):
        caption = Node("caption", [generate_incremental_text()], prefix=prefix)
        table.children.append(caption)

    if random.choice([True, False]):
        colgroup = Node("colgroup", prefix=prefix)
        for _ in range(random.randint(1, 3)):
            col = Node("col", prefix=prefix)
            colgroup.children.append(col)
        table.children.append(colgroup)

    # Optional thead
    if random.choice([True, False]):
        thead = Node("thead", prefix=prefix)
        tr = Node("tr", prefix=prefix)
        for _ in range(random.randint(1, 3)):
            th = Node("th", [generate_incremental_text()], prefix=prefix)
            tr.children.append(th)
        thead.children.append(tr)
        table.children.append(thead)

    # Always include tbody
    tbody = Node("tbody", prefix=prefix)
    for _ in range(random.randint(1, 2)):
        tr = Node("tr", prefix=prefix)
        for _ in range(random.randint(1, 3)):
            tag = random.choice(["td", "th"])
            cell = Node(tag, [generate_incremental_text()], prefix=prefix)
            tr.children.append(cell)
        tbody.children.append(tr)
    table.children.append(tbody)

    # Optional tfoot
    if random.choice([True, False]):
        tfoot = Node("tfoot", prefix=prefix)
        tr = Node("tr", prefix=prefix)
        for _ in range(random.randint(1, 3)):
            td = Node("td", [generate_incremental_text()], prefix=prefix)
            tr.children.append(td)
        tfoot.children.append(tr)
        table.children.append(tfoot)

    return table

def build_dl_tree(prefix="el_"):
    dl = Node("dl", prefix=prefix)
    for _ in range(random.randint(2, 4)):
        dl.children.append(Node("dt", [generate_incremental_text()], prefix=prefix))
        dl.children.append(Node("dd", [generate_incremental_text()], prefix=prefix))
    return dl

def build_list_tree(tag="ul", prefix="el_"):
    assert tag in {"ul", "ol"}
    root = Node(tag, prefix=prefix)
    for _ in range(random.randint(2, 5)):
        root.children.append(Node("li", [generate_incremental_text()], prefix=prefix))
    return root

def build_select_tree(prefix="el_"):
    select = Node("select", prefix=prefix)
    if random.choice([True, False]):
        optgroup = Node("optgroup", prefix=prefix)
        for _ in range(random.randint(1, 3)):
            option = Node("option", [generate_incremental_text()], prefix=prefix)
            optgroup.children.append(option)
        select.children.append(optgroup)
    else:
        for _ in range(random.randint(2, 4)):
            option = Node("option", [generate_incremental_text()], prefix=prefix)
            select.children.append(option)
    return select

def build_fieldset_tree(prefix="el_"):
    fieldset = Node("fieldset", prefix=prefix)
    if random.choice([True, False]):
        legend = Node("legend", [generate_incremental_text()], prefix=prefix)
        fieldset.children.append(legend)
    return fieldset

def build_details_tree(prefix="el_"):
    details = Node("details", prefix=prefix)
    summary = Node("summary", [generate_incremental_text()], prefix=prefix)
    details.children.append(summary)
    return details

def build_figure_tree(prefix="el_"):
    figure = Node("figure", prefix=prefix)
    if random.choice([True, False]):
        figcaption = Node("figcaption", [generate_incremental_text()], prefix=prefix)
        figure.children.append(figcaption)
    return figure

STRUCTURED_BUILDERS = {
    "table": build_table_tree,
    "dl": build_dl_tree,
    "ul": lambda prefix: build_list_tree("ul", prefix),
    "ol": lambda prefix: build_list_tree("ol", prefix),
    "select": build_select_tree,
    "fieldset": build_fieldset_tree,
    "details": build_details_tree,
    "figure": build_figure_tree,
}

def build_strongly_structured_tree(tag, prefix="el_"):
    builder = STRUCTURED_BUILDERS.get(tag)
    if builder:
        return builder(prefix=prefix)
    return None
