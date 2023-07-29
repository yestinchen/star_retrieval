from scripts.settings import raw_file_path, file_storage_path
from scripts.batch_patterns import find_a_pattern, build_patterns_from_file,query_with_patterns
import os, random

def produce_patterns(video_name, params_list, pick_intervals):
  max_obj_num = max(params_list, key=lambda x: x[0])[0]
  max_pattern_length = max(params_list, key=lambda x: x[1])[1]
  video_path = '{}/{}.txt'.format(raw_file_path, video_name)

  patterns = list()
  for i, interval in enumerate(pick_intervals):
    start_fid, end_fid = interval
    print('obj_num', max_obj_num, max_pattern_length)
    print('interval', start_fid, end_fid)
    rt_value = find_a_pattern(video_path, max_obj_num, max_pattern_length, \
      start_fid=start_fid, end_fid=end_fid)
    if rt_value is None:
      continue
    frame_pair, ids = rt_value
    patterns.append((frame_pair, list(ids)))

  pattern_num = len(pick_intervals)
  for params in params_list:
    obj_num, pattern_length = params
    store_path = '{}/pattern-builder2/patterns-{}/{}-{}-{}.txt'.format(file_storage_path,
      video_name, obj_num, pattern_length, pattern_num)
    if not os.path.isdir(os.path.dirname(store_path)):
      os.makedirs(os.path.dirname(store_path))
    with open(store_path, 'w') as wf:
      for pattern in patterns:
        frame_pair, ids = pattern
        frame_pair = [frame_pair[0], frame_pair[0] + pattern_length-1]
        ids = random.sample(ids, obj_num)
        frame_pair = [str(x) for x in frame_pair]
        ids = [str(x) for x in ids]
        wf.write('{};{};\n'.format(','.join(frame_pair), ','.join(ids)))
        # print('{};{};\n'.format(','.join(frame_pair), ','.join(ids)))
    print('\n')

def parse_meta_file(file_path):
  res = list()
  with open(file_path, 'r') as rf:
    for line in rf.readlines():
      name, pair_str = line.split(':')
      length, start_fid = list(map(int, pair_str.split('/')))
      res.append((name, length, start_fid))
    return res


# def produce_pattern_group(video_name, params):
#   # read meta data.
#   meta_data_file = '{}/{}-meta.txt'.format(raw_file_path, video_name)
#   # collect 
#   intervals = [(z,z+y-1) for x,y,z in  parse_meta_file(meta_data_file)]
#   produce_patterns(video_name, params, intervals)

def produce_pattern_group(video_name, params, pattern_num):
  # read meta data.
  meta_data_file = '{}/{}-meta.txt'.format(raw_file_path, video_name)
  # collect 
  intervals = [(z,z+y-1) for x,y,z in  parse_meta_file(meta_data_file)]
  interval_samples =  random.sample(intervals, pattern_num)
  # print('intervals', len(set(interval_samples)))
  produce_patterns(video_name, params, interval_samples)

def produce_pattern_groups():
  produce_pattern_group('drtest', [
    (3, 10), (4, 10), 
    (5, 10), 
    (6, 10),
    (4, 5), (4, 15), (4, 20)
  ], 20)
  produce_pattern_group('drtrain', [
    (3, 10), (4, 10), 
    (5, 10), 
    (6, 10),
    (4, 5), (4, 15), (4, 20)
  ], 20)
  
def get_pattern_configs(video):
  # default_params = [video, 'df5', 4, 10, 5]
  pattern_num = 20
  # if video == 'drtest':
  #   pattern_num = 40
  # elif video == 'drtrain':
  #   pattern_num = 60
  default_params = [video, 'df6', 4, 10, pattern_num]
  
  varying_pattern_objs = [3, 5]
  varying_pattern_length = [5, 15]
  # varying_pattern_df = ['df4', 'df6']
  varying_pattern_df = ['df5', 'df7', 'df8']

  varying_settings = [
    (1, varying_pattern_df),
    (2, varying_pattern_objs),
    (3, varying_pattern_length),
  ]

  configs = list()
  configs.append(list(default_params))

  # for pos, values in varying_settings:
  #   current_params = list(default_params)
  #   for value in values:
  #     current_params[pos] = value
  #     configs.append(list(current_params))
  return configs

def build_patterns():
  videos = ['drtest', 'drtrain']
  for v in videos:
    for config in get_pattern_configs(v):
      build_patterns_from_file(*config)


def batch_query():

  default_pattern_params = ['drtest', 'df6', 4, 10, 20]
  default_query_params = ['drtest', 100]
  # default_pattern_params = ['drtrain', 'df6', 4, 10, 20]
  # default_query_params = ['drtrain', 100]

  # varying_pattern_video = ['drtest']
  # varying_pattern_video = ['drtrain']
  varying_pattern_objs = [3, 5]
  varying_pattern_length = [5, 15]
  # varying_pattern_df = ['df4', 'df6']
  varying_pattern_df = ['df5', 'df7', 'df8']

  varying_pattern = [
    # (0, varying_pattern_video),
    (1, varying_pattern_df),
    (2, varying_pattern_objs),
    (3, varying_pattern_length)
  ]

  # varying_query_video = ['drtest']
  # varying_query_video = ['drtrain']
  varying_query_ks = [
    # 1000, 2000, 
    5000, 10000
  ]

  varying_query = [
    # (0, varying_query_video),
    (1, varying_query_ks)
  ]

  # 1. use default config
  query_with_patterns(default_pattern_params, default_query_params)

  # 2. fix query, varying pattern
  for pos, varying_values in varying_pattern:
    pattern_params = list(default_pattern_params)
    for value in varying_values:
      pattern_params[pos] = value
      query_with_patterns(pattern_params, default_query_params)
  
  # 3. fix pattern, varying query
  for pos, varying_values in varying_query:
    query_prams = list(default_query_params)
    for value in varying_values:
      query_prams[pos] = value
      query_with_patterns(default_pattern_params, query_prams)

if __name__ =='__main__':
  # produce_pattern_groups()
  # build_patterns()
  batch_query()