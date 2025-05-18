import random
import json
from fuzzer.for_wrapper import FORCE_BOOLEAN_PROPERTIES, PROPERTY_NAME_MAP, WRAPPER_ONLY_PROPERTIES

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
    tag_id = f"0x{random.randint(0, 0xFFFFFFFFFFFFFFFF):016x}"
    if tag in ID_REGISTRY:
        ID_REGISTRY[tag].append(tag_id)
    elif tag in {"td", "th"}:
        ID_REGISTRY["thtd"].append(tag_id)
    return tag_id

def generate_value(value_type, exclude_id=None, tag_name=None, attr_name=None):
    if value_type is None or value_type == "None":
        return None

    if isinstance(value_type, (bool, int, float)):
        return value_type

    if not isinstance(value_type, str):
        return None

    if value_type == "URL":
        return random.choice(url_pool)

    if value_type == "URLs":
        return " ".join(random.sample(url_pool, min(len(url_pool), 2)))

    if value_type == "string":
        return f"0x{random.randint(0, 0xFFFFFFFFFFFFFFFF):016x}"

    if value_type == "single_string":
        return random.choice("abcdefghijklmnopqrstuvwxyz")

    if value_type == "filename":
        return random.choice(["a.txt", "b.txt", "c.txt", "a.html", "b.html", "c.html"])

    if value_type == "positive":
        return random.randint(1, 100)

    if value_type == "negative":
        return -random.randint(1, 100)

    if value_type == "en":
        return "en"

    if value_type in {"true", "false"}:
        return value_type == "true"

    if value_type.startswith("idset_"):
        target = value_type.split("_", 1)[1]
        pool = ID_REGISTRY.get(target, []) if target != "thtd" else ID_REGISTRY["thtd"]
        filtered = [i for i in pool if i != exclude_id]
        return random.choice(filtered) if filtered else None

    return value_type

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

def generate_properties_for_tag(tag_name, exclude_id=None, max_props=9):
    properties = {}
    used_keys = set()

    tag_id = generate_tag_id(tag_name)
    properties["id"] = tag_id
    used_keys.add("id")

    if tag_name == "input":
        input_types = list(METADATA.get("input", {}).get("type", {}).keys())
        input_type = random.choice(input_types)
        properties["type"] = input_type
        used_keys.add("type")

        js_input_props = METADATA.get("input", {}).get("properties", {})
        for prop, options in js_input_props.items():
            if prop in used_keys:
                continue
            value = pick_valid_value(options, exclude_id=tag_id, tag_name=tag_name, attr_name=prop)
            if value is not None:
                properties[prop] = value
                used_keys.add(prop)
            if len(properties) >= max_props:
                break

    prop_candidates = []

    common_props = METADATA.get("common", {}).get("properties", {})
    for prop, options in common_props.items():
        prop = PROPERTY_NAME_MAP.get(prop, prop)
        if prop not in used_keys:
            prop_candidates.append((prop, options))

    tag_props = METADATA.get(tag_name, {}).get("properties", {})
    for prop, options in tag_props.items():
        prop = PROPERTY_NAME_MAP.get(prop, prop)
        if prop not in used_keys:
            prop_candidates.append((prop, options))

    for prop, generator in WRAPPER_ONLY_PROPERTIES.items():
        if prop not in used_keys:
            properties[prop] = generator()
            used_keys.add(prop)
            if len(properties) >= max_props:
                return properties

    random.shuffle(prop_candidates)

    for prop, options in prop_candidates:
        if prop in used_keys:
            continue

        value = (
            random.choice([True, False])
            if prop in FORCE_BOOLEAN_PROPERTIES
            else pick_valid_value(options, exclude_id=tag_id, tag_name=tag_name, attr_name=prop)
        )

        if value is not None:
            properties[prop] = value
            used_keys.add(prop)

        if len(properties) >= max_props:
            break

    return properties