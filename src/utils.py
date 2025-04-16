from sqlalchemy import inspect
from datetime import datetime


def model_to_dict(obj, exclude=None):
    exclude = set(exclude or [])
    result = {}

    for c in inspect(obj).mapper.column_attrs:
        if c.key in exclude:
            continue

        value = getattr(obj, c.key)

        if isinstance(value, datetime):
            result[c.key] = value.isoformat()
        else:
            result[c.key] = value

    return result
