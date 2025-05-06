import random
import string
import json

url_pool = [
    "https://firstpartytest.site",
    "https://www.firstpartytest.site",
    "https://sub.firstpartytest.site"
]

ID_REGISTRY = {
    "form": [],
    "label": [],
    "thtd": [],
    "datalist": []
}

with open("HTML/metadata_tags.json", "r") as f:
    METADATA = json.load(f)

def generate_tag_id(tag=None):
    tag_id = f"0x{random.randint(0, 0xFFFFFFFF):08x}"
    if tag in ID_REGISTRY:
        ID_REGISTRY[tag].append(tag_id)
    elif tag in {"td", "th"}:
        ID_REGISTRY["thtd"].append(tag_id)
    return tag_id

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_value(value_type, exclude_id=None, tag_name=None, attr_name=None):
    if value_type is None or value_type == "None":
        return None
    if value_type == "URL":
        if (tag_name, attr_name) in {
            ("img", "src"), ("embed", "src"), ("object", "data")
        }:
            filename = random.choice([
                "a.html", "b.html", "c.html"
            ])
            return random.choice(url_pool).rstrip("/") + "/" + filename
        else:
            return random.choice(url_pool)
    if value_type == "string":
        return f"0x{random.randint(0, 0xffffffff):08x}"
    if value_type == "single_string":
        return random.choice(string.ascii_lowercase)
    if value_type == "URL":
        return random.choice(url_pool)
    if value_type == "URLs":
        return " ".join(random.sample(url_pool, 2))
    if value_type == "filename":
        return random.choice([
            "a.txt", "b.txt", "c.txt", "a.html", "b.html", "c.html"
        ])
    if value_type == "positive":
        return str(random.randint(1, 100))
    if value_type == "negative":
        return str(-random.randint(1, 100))
    if value_type == "en":
        return "en"
    if value_type in {"true", "false"}:
        return random.choice(["true", "false"])
    if value_type.startswith("idset_"):
        target = value_type.split("_", 1)[1]
        if target == "thtd":
            id_pool = ID_REGISTRY["thtd"]
        else:
            id_pool = ID_REGISTRY.get(target, [])
        if not id_pool:
            return None
        filtered = [id_ for id_ in id_pool if id_ != exclude_id]
        return random.choice(filtered) if filtered else None

def pick_valid_value(options, exclude_id=None, tag_name=None, attr_name=None):
    valid = [opt for opt in options if opt is not None]
    if not valid:
        return None
    return generate_value(
        random.choice(valid),
        exclude_id=exclude_id,
        tag_name=tag_name,
        attr_name=attr_name
    )

def generate_attributes_for_tag(tag_name, exclude_id=None):
    attributes = {}

    tag_id = generate_tag_id(tag_name)
    attributes["id"] = tag_id

    if tag_name in ID_REGISTRY and tag_id not in ID_REGISTRY[tag_name]:
        ID_REGISTRY[tag_name].append(tag_id)
    if tag_name in {"td", "th"} and tag_id not in ID_REGISTRY["thtd"]:
        ID_REGISTRY["thtd"].append(tag_id)

    common_attrs = METADATA.get("common", {}).get("attributes", {})
    for attr, options in common_attrs.items():
        if random.random() < 0.3:
            if attr.endswith("*"):
                key = f"data-{random_string(5)}"
                attributes[key] = generate_value("string")
            elif options == []:
                attributes[attr] = True
            else:
                val = pick_valid_value(options, exclude_id=tag_id, tag_name=tag_name, attr_name=attr)
                if val is not None:
                    attributes[attr] = val

    tag_attrs = METADATA.get(tag_name, {}).get("attributes", {})
    if isinstance(tag_attrs, list):
        tag_attrs = {attr: ["string"] for attr in tag_attrs}

    for attr, options in tag_attrs.items():
        if random.random() < 0.7:
            if tag_name == "area" and attr == "coords" and isinstance(options, dict):
                shape = random.choice(list(options.keys()))
                attributes["shape"] = shape
                attributes["coords"] = random.choice(options[shape])
            elif options == []:
                attributes[attr] = True
            else:
                val = pick_valid_value(options, exclude_id=tag_id, tag_name=tag_name, attr_name=attr)
                if val is not None:
                    attributes[attr] = val

    return attributes
