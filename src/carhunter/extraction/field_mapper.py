import re
from typing import Any, Callable

def transform_int(val: Any) -> int:
    if isinstance(val, int):
        return val
    if not val:
        return 0
    clean = re.sub(r'[^\d]', '', str(val))
    return int(clean) if clean else 0

def transform_price(val: Any) -> int:
    # "123 456 PLN" -> 123456
    return transform_int(val)

TRANSFORMS: dict[str, Callable[[Any], Any]] = {
    'int': transform_int,
    'price': transform_price,
}

def apply_transforms(value: Any, transforms_str: str) -> Any:
    if not transforms_str:
        return value
    
    transforms = [t.strip() for t in transforms_str.split('|')]
    for t_name in transforms:
        if not t_name: continue
        if t_name in TRANSFORMS:
            value = TRANSFORMS[t_name](value)
    return value

def extract_json_path(data: dict | list, path: str) -> Any:
    parts = path.split('.')
    current = data
    for part in parts:
        if part == '*':
            # If we hit a wildcard and current is a dict, return its values
            if isinstance(current, dict):
                return list(current.values())
            elif isinstance(current, list):
                return current
            return []
        
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list):
            # Try to get from first item or map over items?
            # For simplicity, if we need specific index we should support [0], but let's keep it simple
            if not current: return None
            current = current[0].get(part) if isinstance(current[0], dict) else None
        else:
            return None
        
        if current is None:
            return None
    return current

