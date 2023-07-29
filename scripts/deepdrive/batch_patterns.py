from scripts.settings import raw_file_path, file_storage_path
from scripts.batch_patterns import find_a_pattern, build_patterns_from_file,query_with_patterns
from scripts.detrac.batch_patterns import produce_patterns
import os, random

def parse_meta_file(file_path):
  res = list()
  with open(file_path, 'r') as rf:
    for line in rf.readlines():
      name, pair_str = line.split(':')
      length, start_fid = list(map(int, pair_str.split('/')))
      res.append((name, length, start_fid))
    return res

def produce_pattern_group(video_name, params, pattern_num):
  # read meta data.
  meta_data_file = '{}/{}-meta.txt'.format(raw_file_path, video_name)
  # collect 
  intervals = [(z,z+y-1) for x,y,z in  parse_meta_file(meta_data_file)]
  interval_samples =  random.sample(intervals, pattern_num)
  # print('intervals', len(set(interval_samples)))
  produce_patterns(video_name, params, interval_samples)

def produce_pattern_groups():
  produce_pattern_group('bdd100kA', [
    (3, 10), (4, 10), 
    (5, 10), 
    (6, 10),
    (4, 5), (4, 15), (4, 20)
  ], 20)
  # produce_pattern_group('bdd100kB', [
  #   (3, 10), (4, 10), 
  #   (5, 10), 
  #   (6, 10),
  #   (4, 5), (4, 15), (4, 20)
  # ], 20)
  
def get_pattern_configs(video):
  # default_params = [video, 'df5', 4, 10, 5]
  pattern_num = 20
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
  videos = [
    'bdd100kA', 
    'bdd100kB'
    ]
  for v in videos:
    for config in get_pattern_configs(v):
      build_patterns_from_file(*config)


def batch_query():

  # default_pattern_params = ['bdd100kA', 'df6', 4, 10, 20]
  # default_query_params = ['bdd100kA', 100]
  default_pattern_params = ['bdd100kB', 'df6', 4, 10, 20]
  default_query_params = ['bdd100kB', 100]
  # default_pattern_params = ['drtrain', 'df6', 4, 10, 60]
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
  # query_with_patterns(default_pattern_params, default_query_params)

  # # 2. fix query, varying pattern
  for pos, varying_values in varying_pattern:
    pattern_params = list(default_pattern_params)
    for value in varying_values:
      pattern_params[pos] = value
      query_with_patterns(pattern_params, default_query_params)
  
  # # 3. fix pattern, varying query
  # for pos, varying_values in varying_query:
  #   query_prams = list(default_query_params)
  #   for value in varying_values:
  #     query_prams[pos] = value
  #     query_with_patterns(default_pattern_params, query_prams)

if __name__ =='__main__':
  # produce_pattern_groups()
  # build_patterns()
  batch_query()