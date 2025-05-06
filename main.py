import subprocess
import re

def multi_replace(template: str, replacements: dict) -> str:
    for key, value in replacements.items():
        template = template.replace(f"{{{{{key}}}}}", value)
    return template

def format_elements_list(vars, per_line=5):
    if not vars:
        return ""
    lines = []
    for i in range(0, len(vars), per_line):
        chunk = ", ".join(vars[i:i + per_line])
        lines.append(f"    {chunk}")
    return "const elements = [\n" + ",\n".join(lines) + "\n];\nelements.forEach(e => document.body.appendChild(e));"

with open("template.html", "r", encoding="utf-8") as f:
    template = f.read()

used_headings = set()
html_outputs = {}

for i in range(1, 5):
    args = ["python", "html_main.py", "--used-headings", ",".join(sorted(used_headings))]
    html_raw = subprocess.check_output(args, text=True)

    match = re.search(r"###USED_HEADINGS###:(.*)", html_raw)
    html_content = re.sub(r"###USED_HEADINGS###:.*", "", html_raw).strip()
    html_outputs[f"HTML_{i}"] = html_content

    if match:
        used = match.group(1).strip()
        used_headings.update(h.strip() for h in used.split(",") if h)

js_outputs = {}
all_append_targets = []

used_heading_arg = ",".join(sorted(used_headings))
for i in range(1, 3):
    args = [
        "python", "wrapper_main.py",
        "--prefix", f"el{i}_",
        "--used-headings", used_heading_arg
    ]
    if i == 2:
        args.append("--append")

    js_raw = subprocess.check_output(args, text=True)

    match_heading = re.search(r"###USED_HEADINGS###:(.*)", js_raw)
    if match_heading:
        used = match_heading.group(1).strip()
        used_headings.update(h.strip() for h in used.split(",") if h)

    match_append = re.search(r"###APPEND_TARGETS###:(.*)", js_raw)
    if match_append:
        targets = match_append.group(1).strip().split(",")
        all_append_targets.extend(targets)

    js_code = re.sub(r"###(USED_HEADINGS|APPEND_TARGETS)###:.*", "", js_raw).strip()
    js_outputs[f"JS_{i}"] = js_code

append_block = format_elements_list(all_append_targets)

replacements = {**html_outputs, **js_outputs, "APPEND_ALL": append_block}
filled = multi_replace(template, replacements)

with open("output.html", "w", encoding="utf-8") as f:
    f.write(filled)

print("output.html")
