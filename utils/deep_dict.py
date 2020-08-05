import copy
import logging

log = logging.getLogger(__name__)

def nested_get(data_dict, keys):
    data_copy = copy.copy(data_dict)
    for k in keys:
        if k not in data_copy:
            log.warning(f'key {k} not in dictionary, setting to default value of None.')

        data_copy = data_copy.get(k)
    return data_copy

#def nested_set(data_dict, keys, value):
#    data_dict = dict(data_dict)
#    for key in keys[:-1]:
#        data_dict = data_dict.setdefault(key, {})
#    data_dict[keys[-1]] = value