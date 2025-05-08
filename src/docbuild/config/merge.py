

def deep_merge(dict1, *dicts):
    """
    Iteratively merge dict2, dict3, ..., into dict1 deeply,
    with later dict values overwriting earlier ones.
    Requires at least one dictionary argument.
    Returns a new merged dictionary without modifying inputs.
    """

    # Start with a shallow copy of the first dictionary
    merged = dict1.copy()

    for d in dicts:
        stack = [(merged, d)]

        while stack:
            d1, d2 = stack.pop()
            for key, value in d2.items():
                if key in merged and \
                   isinstance(d1[key], dict) and \
                   isinstance(value, dict):
                    stack.append((d1[key], value))
                else:
                    d1[key] = value

    return merged