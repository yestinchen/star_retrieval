from bitarray import bitarray

def compute_if_absent(some_dict, key, default_value_func):
  key_value = some_dict.get(key)
  if key_value is None:
    key_value = default_value_func()
    some_dict[key] = key_value
  return key_value

def get_from_multi_level_dict(some_dict, keys):
  current_dict = some_dict
  for key in keys:
    current_dict = current_dict.get(key)
    if current_dict is None:
      return None
  return current_dict

def init_bitset(length):
  bitset = bitarray(length)
  bitset.setall(0)
  return bitset


def print_multi_level_dict(some_dict, padding=0):
  for key, value in some_dict.items():
    print(' '*padding + str(key))
    if type(value) == dict:
      print_multi_level_dict(value, padding + 2)
    else:
      print(' '*(padding+2) + str(value))