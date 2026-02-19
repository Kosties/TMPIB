def parse_planet(text):
    parts = []
    current = ""
    in_quotes = False

    for char in text:
        if char == '"':
            in_quotes = not in_quotes
            current += char
        elif char == " " and not in_quotes:
            if current:
                parts.append(current)
                current = ""
        else:
            current += char
    if current:
        parts.append(current)

    obj_type = None
    name = None
    discovery_date = None
    radius = None

    for value in parts:
        if not value.startswith('"') and not value.endswith('"') and value.isalpha():
            obj_type = value
        elif value.startswith('"') and value.endswith('"'):
            name = value.strip('"')
        elif "." in value and len(value.split(".")) == 3:
            discovery_date = value 
        elif "." in value:
            radius = float(value)

    return {
        "type": obj_type,
        "name": name,
        "discovery_date": discovery_date,
        "radius": radius
    }

input_string = '3389.5 planeta "earth" 1877.08.12'
result = parse_planet(input_string)
print(result)
