import random
from fuzzer.attribute_generator import generate_attributes_for_tag
from fuzzer.rule_expander import expand_rule
from fuzzer.rule_checker import is_valid_child

FLAT_CHILD_CONTAINERS = {"dl", "ul", "ol", "select", "fieldset", "details", "figure"}
VOID_ELEMENTS = {"br", "wbr", "hr", "img", "input", "area", "embed"}

class Node:
    def __init__(self, tag, children=None, no_closing=False, text=""):
        self.tag = tag
        self.children = children or []
        self.no_closing = no_closing
        self.text = text

def render_dom_tree(node):
    attrs = generate_attributes_for_tag(node.tag)
    attr_str = render_attributes(attrs)

    if node.no_closing or node.tag in VOID_ELEMENTS:
        return f"<{node.tag} {attr_str}>"

    inner = "".join([
        render_dom_tree(child) if isinstance(child, Node) else str(child)
        for child in node.children
    ])

    return f"<{node.tag} {attr_str}>{inner}</{node.tag}>"

def render_tag(tag_name, children=None, no_closing=False):
    node = Node(tag_name, children or [f"0x{random.getrandbits(32):08x}"], no_closing)
    return render_dom_tree(node)

def render_attributes(attrs):
    return " ".join(
        key if value is True else f'{key}="{value}"'
        for key, value in attrs.items()
        if value is not None
    )

def build_nested_tree_from_list(tags, html_rule, no_closing_tags):
    if not tags:
        return None

    root_tag = tags[0]
    root = Node(root_tag, no_closing=root_tag in no_closing_tags)

    if root_tag == "tr":
        for tag in tags[1:]:
            if is_valid_child("tr", tag, html_rule):
                root.children.append(Node(tag, no_closing=tag in no_closing_tags))
        return root

    if root_tag in {"thead", "tbody", "tfoot"}:
        child_tags = tags[1:]
        if all(t in {"td", "th"} for t in child_tags):
            tr_node = Node("tr", [
                Node(t, no_closing=t in no_closing_tags)
                for t in child_tags
                if is_valid_child("tr", t, html_rule)
            ])
            if is_valid_child(root_tag, "tr", html_rule):
                root.children.append(tr_node)
            return root

    if len(tags) > 1:
        child = build_nested_tree_from_list(tags[1:], html_rule, no_closing_tags)
        if child and is_valid_child(root.tag, child.tag, html_rule):
            root.children.append(child)

    return root

def is_dt_dd_safe_to_add(parent_tag, child_tag, last_child_tag, last_child_node):
    if parent_tag != "dl":
        return True
    if child_tag not in {"dt", "dd"}:
        return True
    # 1단계: 같은 태그 연속 방지
    if last_child_tag == child_tag:
        return False
    # 2단계: 중첩된 경우 방지
    if isinstance(last_child_node, Node) and last_child_node.tag in {"dt", "dd"}:
        if any(isinstance(c, Node) and c.tag in {"dt", "dd"} for c in last_child_node.children):
            return False
    return True

def build_dom_tree(tags, html_rule, no_closing_tags):
    if not tags:
        return None

    def expand_if_group(tag):
        key = f"@{tag.upper()}"
        return expand_rule(key, html_rule) if key in html_rule else [tag]

    root_tag = tags[0]
    root = Node(root_tag, no_closing=root_tag in no_closing_tags)

    if root_tag in FLAT_CHILD_CONTAINERS:
        last_child_tag = None
        for tag in tags[1:]:
            sub_tags = expand_if_group(tag)
            for sub_tag in sub_tags:
                if not is_valid_child(root.tag, sub_tag, html_rule):
                    continue
                if root.tag == "dl" and not is_dt_dd_safe_to_add(root.tag, sub_tag, last_child_tag, root.children[-1] if root.children else None):
                    continue
                root.children.append(Node(sub_tag, no_closing=sub_tag in no_closing_tags))
                last_child_tag = sub_tag
        return root

    if root_tag == "table":
        for tag in tags[1:]:
            sub_tags = expand_if_group(tag)
            if any(t in sub_tags for t in ("tr", "td", "th")) and not any(t in sub_tags for t in ("thead", "tbody", "tfoot")):
                sub_tags = ["tbody"] + sub_tags

            child = build_nested_tree_from_list(sub_tags, html_rule, no_closing_tags)
            if child and is_valid_child(root.tag, child.tag, html_rule):
                root.children.append(child)
        return root

    for tag in tags[1:]:
        sub_tags = expand_if_group(tag)

        if len(sub_tags) == 1:
            sub_tag = sub_tags[0]
            if not is_valid_child(root.tag, sub_tag, html_rule):
                continue
            if root.tag == "dl" and not is_dt_dd_safe_to_add(root.tag, sub_tag, root.children[-1].tag if root.children else None):
                continue
            root.children.append(Node(sub_tag, no_closing=sub_tag in no_closing_tags))
        else:
            nested = build_nested_tree_from_list(sub_tags, html_rule, no_closing_tags)
            if nested and is_valid_child(root.tag, nested.tag, html_rule):
                root.children.append(nested)

    return root
