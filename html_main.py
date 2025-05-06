import json
import random
import argparse
from fuzzer.html_renderer import render_tag, render_dom_tree, build_dom_tree
from fuzzer.rule_expander import expand_rule
from fuzzer.rule_checker import is_tag_allowed, reset_state, used_tags

def generate_random_string():
    return f"0x{random.randint(0, 0xffffffff):08x}"

parser = argparse.ArgumentParser()
parser.add_argument("--used-headings", type=str, default="", help="Comma-separated list of used h1~h6")
args = parser.parse_args()

reset_state()
for h in args.used_headings.split(","):
    h = h.strip()
    if h in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        used_tags["heading_used"].add(h)

with open("HTML/html_tags.json", "r") as f:
    html_tags = json.load(f)
with open("HTML/html_rule.json", "r") as f:
    html_rule = json.load(f)

before_main_tags = set(html_rule.get("BEFORE_MAIN", []))
no_closing_tags = set(html_rule.get("NO_CLOSING", []))
not_only = set(html_rule.get("NOT_ONLY", []))
excluded_tags = before_main_tags.union({"main"}, used_tags["heading_used"])

body_tags = {tag: val for tag, val in html_tags["BODY"].items() if tag not in excluded_tags}
valid_tags = list(body_tags.keys())

final_html = []
while len(final_html) < 100:
    tag = random.choice(valid_tags)
    if not is_tag_allowed(tag, apply=False):
        continue
    is_tag_allowed(tag, apply=True)

    rule_key = f"@{tag.upper()}"
    if rule_key in html_rule:
        expanded_tags = expand_rule(rule_key, html_rule)
        dom_tree = build_dom_tree(expanded_tags, html_rule, no_closing_tags)
        if dom_tree is None:
            continue
        html = render_dom_tree(dom_tree)
    else:
        text = generate_random_string()
        html = render_tag(tag, children=[text], no_closing=(tag in no_closing_tags))

    final_html.append(html)

print("\n".join(final_html))
print("###USED_HEADINGS###:" + ",".join(sorted(used_tags["heading_used"])))
