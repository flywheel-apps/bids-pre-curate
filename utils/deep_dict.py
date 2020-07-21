import copy

def nested_get(data_dict, keys):
    data_copy = copy.copy(data_dict)
    for k in keys:
        data_copy = data_copy[k]
    return data_copy

#def nested_set(data_dict, keys, value):
#    data_dict = dict(data_dict)
#    for key in keys[:-1]:
#        data_dict = data_dict.setdefault(key, {})
#    data_dict[keys[-1]] = value