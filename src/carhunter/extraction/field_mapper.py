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

def transform_get_param(val: Any, param_key: str) -> str | None:
    if not isinstance(val, list):
        return None
    for p in val:
        if isinstance(p, dict) and p.get('key') == param_key:
            return p.get('displayValue') or p.get('value')
    return None

TRANSFORMS: dict[str, Callable[..., Any]] = {
    'int': transform_int,
    'price': transform_price,
    'get_param': transform_get_param,
}

def apply_transforms(value: Any, transforms_str: str) -> Any:
    if not transforms_str:
        return value
    
    transforms = [t.strip() for t in transforms_str.split('|')]
    for t_expr in transforms:
        if not t_expr: continue
        parts = t_expr.split(':', 1)
        t_name = parts[0]
        t_args = parts[1:]
        
        if t_name in TRANSFORMS:
            value = TRANSFORMS[t_name](value, *t_args)
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

