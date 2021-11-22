def opt(data: dict, keys: str, default=None):
    keys = keys.split('.')
    val = None

    for key in keys:
        val = data.get(key, None)

        if val is None:
            return default

        data = val

    return val
