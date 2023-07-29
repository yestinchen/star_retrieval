
def read_ini_as_dict(file_path):
  result = dict()
  with open(file_path,'r') as f:
    for line in f.readlines():
      k, v = line.split('=')
      result[k.strip()] = v.strip()
  return result

def read_query_conf(file_path):
  d = read_ini_as_dict(file_path)
  # convert values
  d['height'] = int(d['height'])
  d['width'] = int(d['width'])
  d['class_type'] = int(d['class_type'])
  d['theta_n'] = int(d['theta_n'])
  d['d_n'] = int(d['d_n'])
  d['ids'] = [int(i) for i in d['ids'].split(',')]
  d['frame_range'] = [int(i) for i in d['frame_range'].split(',')]
  return d
