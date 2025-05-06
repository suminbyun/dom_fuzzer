import json
import random
import argparse
from fuzzer.wrapper_generator import (
    render_js_dom_tree,
    render_js_tag,
    build_dom_tree,
    reset_counters,
    get_element_count,
    generate_incremental_text,
    ALL_NODES, APPENDED_NODES
)
from fuzzer.rule_expander import expand_rule
from fuzzer.rule_checker import is_tag_allowed, reset_state, used_tags

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("--prefix", type=str, default="el_", help="Prefix for element variable names")
parser.add_argument("--append", action="store_true", help="Append elements to body")
parser.add_argument("--used-headings", type=str, default="", help="Comma-separated list of h1~h6 to exclude")
args = parser.parse_args()

# Initialization
reset_state()
reset_counters(prefix=args.prefix)

used_headings = set(h.strip() for h in args.used_headings.split(",") if h)
for h in used_headings:
    if h in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        used_tags["heading_used"].add(h)

# Load HTML tags and rules
with open("HTML/html_tags.json", "r") as f:
    html_tags = json.load(f)
with open("HTML/html_rule.json", "r") as f:
    html_rule = json.load(f)

body_tags = html_tags["BODY"]
before_main_tags = set(html_rule.get("BEFORE_MAIN", []))
not_only_tags = set(html_rule.get("NOT_ONLY", []))
excluded_tags = before_main_tags.union({"main"}, used_headings, not_only_tags)
valid_tags = [tag for tag in body_tags if tag not in excluded_tags]

# DOM element generation
final_js_code = []
element_nodes = []

while get_element_count(args.prefix) < 100:
    tag = random.choice(valid_tags)
    if not is_tag_allowed(tag, apply=True):
        continue

    rule_key = f"@{tag.upper()}"
    if rule_key in html_rule:
        expanded_tags = expand_rule(rule_key, html_rule)
        dom_tree = build_dom_tree(expanded_tags, html_rule, prefix=args.prefix)
        if dom_tree:
            js_code, nodes = render_js_dom_tree(dom_tree, prefix=args.prefix, max_props=9)
            final_js_code.extend(js_code)
            element_nodes.extend(nodes)
    else:
        text = generate_incremental_text()
        js_code, node = render_js_tag(tag, children=[text], prefix=args.prefix, max_props=9)
        final_js_code.extend(js_code)
        element_nodes.append(node)

# Output generated JS code
print("\n".join(final_js_code))
print("###USED_HEADINGS###:" + ",".join(sorted(used_headings)))

# Output root-level nodes for later append
root_nodes = [n for n in ALL_NODES if n.var_name not in APPENDED_NODES]
print("###APPEND_TARGETS###:" + ",".join(n.var_name for n in root_nodes))

