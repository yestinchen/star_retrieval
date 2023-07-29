from scripts.settings import file_storage_path, df_funcs, video_name_meta_mapping
from scripts.batch_patterns import find_a_pattern, read_patterns_from_file
import os, random

def produce_patterns(video_name, params_list, pick_intervals):
  max_obj_num = max(params_list, key=lambda x: x[0])[0]
  max_pattern_length = max(params_list, key=lambda x: x[1])[1]
  video_path = '{}/sample-raw/{}.txt'.format(file_storage_path, video_name)

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
    store_path = '{}/sample-pattern-builder2/patterns-{}/{}-{}-{}.txt'.format(file_storage_path,
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
  meta_data_file = '{}/sample-raw/{}-meta.txt'.format(file_storage_path, video_name)
  # collect 
  intervals = [(z,z+y-1) for x,y,z in  parse_meta_file(meta_data_file)]
  interval_samples =  random.sample(intervals, pattern_num)
  # print('intervals', len(set(interval_samples)))
  produce_patterns(video_name, params, interval_samples)

def produce_pattern_groups():
  # produce_pattern_group('drtest-5', [
  #   (3, 10), (4, 10), 
  #   (5, 10), 
  #   (6, 10),
  #   (4, 5), (4, 15), (4, 20)
  # ], 20)
  # produce_pattern_group('drtrain-5', [
  #   (3, 10), (4, 10), 
  #   (5, 10), 
  #   (6, 10),
  #   (4, 5), (4, 15), (4, 20)
  # ], 20)
  produce_pattern_group('drtest-5', [(4, 10)], 20)
  produce_pattern_group('drtest-10', [(4, 10)], 20)

  produce_pattern_group('drtrain-5', [(4, 10)], 20)
  produce_pattern_group('drtrain-10', [(4, 10)], 20)

  produce_pattern_group('bdd100kA-5', [(4, 10)], 20)
  produce_pattern_group('bdd100kA-10', [(4, 10)], 20)

  produce_pattern_group('bdd100kB-5', [(4, 10)], 20)
  produce_pattern_group('bdd100kB-10', [(4, 10)], 20)

def get_pattern_configs(video, rate):
  # default_params = [video, 'df5', 4, 10, 5]
  pattern_num = 20
  # if video == 'drtest':
  #   pattern_num = 40
  # elif video == 'drtrain':
  #   pattern_num = 60
  default_params = [video,rate, 'df6', 4, 10, pattern_num]
  

  configs = list()
  configs.append(list(default_params))

  return configs

def build_patterns():
  videos = ['drtest', 'drtrain', 'bdd100kA', 'bdd100kB']
  sample_rates = [5, 10]
  for v in videos:
    for sample_rate in sample_rates:
      for config in get_pattern_configs(v, sample_rate):
        build_patterns_from_file(*config)

def build_patterns_from_file(video_name, sample_rate, df_name, obj_num, pattern_length, pattern_num):
  
  seq_name = '{}-{}'.format(video_name, sample_rate)
  file_store_path  = '{}/sample-pattern-builder2/patterns-{}/{}-{}-{}.txt'.format(file_storage_path,
    seq_name, obj_num, pattern_length, pattern_num)
  for idx, frame_pair, ids in read_patterns_from_file(file_store_path):
    print('params', video_name, df_name, frame_pair, ids)
    output_path = '{}/sample-pattern-builder2/patterns-{}/{}-{}-{}/{}-{}-{}-{}.pkl'.format(file_storage_path,
      seq_name, obj_num, pattern_length, pattern_num, df_name, idx, '_'.join(frame_pair), '_'.join(ids))
    # log_path = '{}/pattern-builder/patterns-{}-{}-{}-{}/{}-{}-{}.out.txt'.format(file_storage_path,
    #   video_name, obj_num, pattern_length, pattern_num, idx, '_'.join(frame_pair), '_'.join(ids))

    # create directory
    if not os.path.isdir(os.path.dirname(output_path)):
      os.makedirs(os.path.dirname(output_path))
    run_build_pattern(video_name, sample_rate, df_name, frame_pair, ids, output_path)
  
def run_build_pattern(video_name, sample_rate, df_name, frame_pair, ids, output_path):
  df, df_p1, df_p2 = df_funcs[df_name]
  seq_name = '{}-{}'.format(video_name, sample_rate)
  file_path = '{}/sample-raw/{}.txt'.format(file_storage_path, seq_name)
  width, height = video_name_meta_mapping[video_name]
  tokens = ['python', 'vsimsearch/apps/pattern_app.py',
    '--file_path', file_path,
    '--frame_height', height, '--frame_width', width,
    '--output_path', output_path, 
    '--discretize_func', df, 
    '--df_param1', df_p1, '--df_param2', df_p2,
    '--ids', ','.join(ids),
    '--frames', ','.join(frame_pair)
  ]
  command = ' '.join([str(t) for t in tokens])
  print('command', command)
  os.system(command)
  pass

def query_with_patterns(pattern_config, query_config):
  video_name, df_name, obj_num, pattern_length, pattern_num = pattern_config
  pattern_folder_path = '{}/sample-pattern-builder2/patterns-{}/{}-{}-{}'.format(file_storage_path, 
        video_name, obj_num, pattern_length, pattern_num)
  pattern_txt_file  = '{}/sample-pattern-builder2/patterns-{}/{}-{}-{}.txt'.format(file_storage_path,
    video_name, obj_num, pattern_length, pattern_num)
  query_video, query_k = query_config
  print('query on video', query_video, pattern_config, query_config)
  methods = ['baseline', 'proposed', 'proposed_seq']
  result_folder_path = '{}/sample-batch-results2/patterns-{}/{}-{}-{}-{}'.format(file_storage_path, 
      video_name, obj_num, pattern_length, pattern_num, query_video)
  for idx, frame_pair, ids in read_patterns_from_file(pattern_txt_file):
    pattern_file_path = '{}/{}-{}-{}-{}.pkl'.format(pattern_folder_path,
        df_name, idx, '_'.join(frame_pair), '_'.join(ids))
    print('pattern idx:', idx)

    for method in methods:
      run_query(query_video, pattern_file_path, idx, frame_pair, ids, df_name, query_k, method, result_folder_path)
    
def run_query(video_name, pattern_path, idx, frame_pair, ids, df, k, method, result_folder_path):
  index_type = 1
  index_path = '{}/sample-index/{}-{}-{}.pkl'.format(file_storage_path, video_name, index_type, df)
  print('running query with settings', video_name, ids, frame_pair, index_type, df, k, method)
  if not os.path.isdir(result_folder_path):
    os.makedirs(result_folder_path)

  tokens = ['python', 'vsimsearch/apps/query_app.py', 
    '--index_path', index_path,
    '--pattern_path', pattern_path,
    '--method', method,
    '--k', k,
    '--index_type', index_type
  ]
  output_path = '{}/{}-{}-{}-{}-{}-{}.txt'.format(result_folder_path, video_name, \
    '_'.join(ids), '_'.join(frame_pair), df, k, method)
  command = ' '.join([str(t) for t in tokens])
  print('exec', command, '>', output_path)
  os.system('{} > {}'.format(command, output_path))

def batch_query():

  # default_pattern_params = ['drtest', 'df6', 4, 10, 20]
  # default_query_params = ['drtest', 100]

  videos = ['drtrain', 'drtest', 'bdd100kA', 'bdd100kB']
  sample_rates = [5, 10]

  for video in videos:
    for rate in sample_rates:
      seq_name = '{}-{}'.format(video, rate)
      default_pattern_params = [seq_name, 'df6', 4, 10, 20]
      default_query_params = [seq_name, 100]
      query_with_patterns(default_pattern_params, default_query_params)

  # # varying_pattern_video = ['drtest']
  # # varying_pattern_video = ['drtrain']
  # varying_pattern_objs = [3, 5]
  # varying_pattern_length = [5, 15]
  # # varying_pattern_df = ['df4', 'df6']
  # varying_pattern_df = ['df5', 'df7', 'df8']

  # varying_pattern = [
  #   # (0, varying_pattern_video),
  #   (1, varying_pattern_df),
  #   (2, varying_pattern_objs),
  #   (3, varying_pattern_length)
  # ]

  # # varying_query_video = ['drtest']
  # # varying_query_video = ['drtrain']
  # varying_query_ks = [
  #   # 1000, 2000, 
  #   5000, 10000
  # ]

  # varying_query = [
  #   # (0, varying_query_video),
  #   (1, varying_query_ks)
  # ]

  # # 1. use default config
  # query_with_patterns(default_pattern_params, default_query_params)

  # # 2. fix query, varying pattern
  # for pos, varying_values in varying_pattern:
  #   pattern_params = list(default_pattern_params)
  #   for value in varying_values:
  #     pattern_params[pos] = value
  #     query_with_patterns(pattern_params, default_query_params)
  
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