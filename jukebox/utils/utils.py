from functools import reduce

def dict_recursive_get(data:dict, keys:list) -> dict:
    return reduce(lambda d, k: d.get(k, {}), keys, data)