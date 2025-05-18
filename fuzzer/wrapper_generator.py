from fuzzer.property_generator import generate_properties_for_tag
from fuzzer.rule_expander import expand_rule
from fuzzer.rule_checker import is_valid_child
from fuzzer.for_tree import (
    Node,
    generate_incremental_text,
    reset_counters,
    get_element_count,
    element_counter,
    build_strongly_structured_tree
)

FLAT_CHILD_CONTAINERS = {"dl", "ul", "ol", "select", "fieldset", "details", "figure"}
TABLE_LIKE = {"table"}
NO_CLOSING = {"br", "wbr", "hr", "img", "input", "area", "embed"}

ALL_NODES = []
APPENDED_NODES = set()

def render_js_tag(tag_name, children=None, max_props=9, prefix="el_"):
    node = Node(tag_name, children, prefix=prefix)
    js_code, nodes = render_js_dom_tree(node, max_props=max_props, prefix=prefix)
    return js_code, nodes[0]

def render_js_dom_tree(node, max_props=9, prefix="el_"):
    lines = []
    var_name = node.var_name

    lines.append(f"const {var_name} = document.createElement('{node.tag}');")

    props = generate_properties_for_tag(node.tag, max_props=max_props)
    line_acc = []
    for i, (key, val) in enumerate(props.items()):
        val_str = (
            "true" if val is True else
            "false" if val is False else
            str(val) if isinstance(val, (int, float)) else
            f'"{val}"'
        )
        line_acc.append(f"{var_name}.{key} = {val_str};")
        if len(line_acc) == 3:
            lines.append(" ".join(line_acc))
            line_acc = []
    if line_acc:
        lines.append(" ".join(line_acc))

    ALL_NODES.append(node)

    for child in node.children:
        if isinstance(child, Node):
            child_lines, child_nodes = render_js_dom_tree(child, max_props=max_props, prefix=prefix)
            lines.extend(child_lines)
            lines.append(f"{var_name}.appendChild({child.var_name});")
            for n in child_nodes:
                APPENDED_NODES.add(n.var_name)
        elif isinstance(child, str):
            lines.append(f'{var_name}.textContent = "{child}";')

    return lines, [node]

def build_nested_tree_from_list(tags, html_rule, prefix="el_"):
    if not tags:
        return None

    root_tag = tags[0]
    root = Node(root_tag, prefix=prefix)

    if root_tag == "tr":
        root.children = [Node(tag, prefix=prefix) for tag in tags[1:] if is_valid_child(root.tag, tag, html_rule)]
        return root

    if root_tag in {"thead", "tbody", "tfoot"}:
        child_tags = tags[1:]
        if all(t in {"td", "th"} for t in child_tags):
            tr_node = Node("tr", [Node(t, prefix=prefix) for t in child_tags if is_valid_child("tr", t, html_rule)], prefix=prefix)
            root.children.append(tr_node)
            return root

    if len(tags) > 1:
        child = build_nested_tree_from_list(tags[1:], html_rule, prefix=prefix)
        if child and is_valid_child(root.tag, child.tag, html_rule):
            root.children.append(child)

    return root

def build_dom_tree(tags, html_rule, prefix="el_"):
    if not tags:
        return None

    root_tag = tags[0]

    strong_node = build_strongly_structured_tree(root_tag, prefix=prefix)
    if strong_node:
        return strong_node

    def expand_if_group(tag):
        key = f"@{tag.upper()}"
        return expand_rule(key, html_rule) if key in html_rule else [tag]

    root = Node(root_tag, prefix=prefix)

    if root_tag in FLAT_CHILD_CONTAINERS:
        for tag in tags[1:]:
            for sub_tag in expand_if_group(tag):
                if is_valid_child(root.tag, sub_tag, html_rule):
                    root.children.append(Node(sub_tag, prefix=prefix))
        return root

    if root_tag in TABLE_LIKE:
        for tag in tags[1:]:
            sub_tags = expand_if_group(tag)

            if any(t in sub_tags for t in ("tr", "td", "th")) and not any(t in sub_tags for t in ("thead", "tbody", "tfoot")):
                sub_tags = ["tbody"] + sub_tags

            child = build_nested_tree_from_list(sub_tags, html_rule, prefix=prefix)
            if child and is_valid_child(root.tag, child.tag, html_rule):
                root.children.append(child)
        return root

    for tag in tags[1:]:
        sub_tags = expand_if_group(tag)
        if len(sub_tags) == 1:
            if is_valid_child(root.tag, sub_tags[0], html_rule):
                root.children.append(Node(sub_tags[0], prefix=prefix))
        else:
            nested = build_nested_tree_from_list(sub_tags, html_rule, prefix=prefix)
            if nested and is_valid_child(root.tag, nested.tag, html_rule):
                root.children.append(nested)

    return root
