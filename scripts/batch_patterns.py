from scripts.plot_figures import varying_num_objects
from vsimsearch.io import read_nodes_from_mot_result_multi_class
from .settings import file_storage_path, raw_file_path, df_funcs, video_name_meta_mapping, index_file_path
import random
import os
import pickle


def find_a_pattern(video_path, obj_num, pattern_length, \
    obj_appear_threshold=0.7, start_fid=None, end_fid=None):
  nodes = read_nodes_from_mot_result_multi_class(video_path)
  min_frame, max_frame = nodes['frame'].min(), nodes['frame'].max()
  if start_fid is not None:
    min_frame = start_fid
  if end_fid is not None:
    max_frame = end_fid

  found_start_point = False
  start_frame = None
  objs = None

  max_tries = (max_frame - pattern_length - min_frame)

  while not found_start_point:
    max_tries -= 1
    if max_tries <= 0:
      return None
    start_frame = random.randint(min_frame, max_frame - pattern_length)
    # get all nodes in the window.
    filtered_nodes = nodes[(nodes['frame'] >= start_frame) & (nodes['frame'] < start_frame + pattern_length)]
    # count # of frames each object appears.
    group_result = filtered_nodes.groupby('id').count()[['frame']]
    group_result = group_result[group_result['frame'] > pattern_length*obj_appear_threshold]
    unique_objs = group_result.index.values
    if len(unique_objs) < obj_num:
      continue
    found_start_point = True
    # select objects.
    sampled = group_result.sample(obj_num)
    objs = sampled.index.values

  # return frame, 
  return [start_frame, start_frame + pattern_length -1], objs

def simplify_pattern(video_path, df_name, frames, ids):
  # group each frame.

  pass

def produce_patterns(video_name, obj_num, pattern_length, pattern_num):
  video_path = '{}/{}.txt'.format(raw_file_path, video_name)
  store_path = '{}/pattern-builder/patterns-{}/{}-{}-{}.txt'.format(file_storage_path,
    video_name, obj_num, pattern_length, pattern_num)
  if not os.path.isdir(os.path.dirname(store_path)):
    os.makedirs(os.path.dirname(store_path))
  with open(store_path, 'w') as wf:
    for i in range(pattern_num):
      frame_pair, ids = find_a_pattern(video_path, obj_num, pattern_length)
      frame_pair = [str(x) for x in frame_pair]
      ids = [str(x) for x in ids]
      wf.write('{};{};\n'.format(','.join(frame_pair), ','.join(ids)))

def produce_patterns2(video_name, params_list, pattern_num):
  max_obj_num = max(params_list, key=lambda x: x[0])[0]
  max_pattern_length = max(params_list, key=lambda x: x[1])[1]
  video_path = '{}/{}.txt'.format(raw_file_path, video_name)

  patterns = list()
  for i in range(pattern_num):
    print('obj_num', max_obj_num, max_pattern_length)
    frame_pair, ids = find_a_pattern(video_path, max_obj_num, max_pattern_length)
    patterns.append((frame_pair, list(ids)))

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

def read_patterns_from_file(file_path):
  with open(file_path, 'r') as rf:
    res = list()
    for idx,line in enumerate(rf.readlines()):
      frame_str, id_str = line.split(';')[:2]
      frame_pair = [int(f) for f in frame_str.split(',')]
      ids = [int(i) for i in id_str.split(',')]
      frame_pair = [str(f) for f in frame_pair]
      ids = [str(i) for i in ids]
      res.append((idx, frame_pair, ids))
    return res

def build_patterns_from_file(video_name, df_name, obj_num, pattern_length, pattern_num):
  file_store_path  = '{}/pattern-builder2/patterns-{}/{}-{}-{}.txt'.format(file_storage_path,
    video_name, obj_num, pattern_length, pattern_num)
  for idx, frame_pair, ids in read_patterns_from_file(file_store_path):
    print('params', video_name, df_name, frame_pair, ids)
    output_path = '{}/pattern-builder2/patterns-{}/{}-{}-{}/{}-{}-{}-{}.pkl'.format(file_storage_path,
      video_name, obj_num, pattern_length, pattern_num, df_name, idx, '_'.join(frame_pair), '_'.join(ids))
    # log_path = '{}/pattern-builder/patterns-{}-{}-{}-{}/{}-{}-{}.out.txt'.format(file_storage_path,
    #   video_name, obj_num, pattern_length, pattern_num, idx, '_'.join(frame_pair), '_'.join(ids))

    # create directory
    if not os.path.isdir(os.path.dirname(output_path)):
      os.makedirs(os.path.dirname(output_path))
    run_build_pattern(video_name, df_name, frame_pair, ids, output_path)
  

def run_build_pattern(video_name, df_name, frame_pair, ids, output_path):
  df, df_p1, df_p2 = df_funcs[df_name]
  file_path = '{}/{}.txt'.format(raw_file_path, video_name)
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

def produce_pattern_groups():

  pattern_num = 5

  produce_patterns2('traffic1', [
    (3, 10), (4, 10), (5, 10), (6, 10),
    (4, 5), (4, 15), (4, 20)
  ], pattern_num)
  produce_patterns2('traffic2', [
    (3, 10), (4, 10), (5, 10), (6, 10),
    (4, 5), (4, 15), (4, 20)
  ], pattern_num)

  # produce_patterns('traffic1', 3, 10, pattern_num)
  # produce_patterns('traffic1', 4, 10, pattern_num)
  # produce_patterns('traffic1', 5, 10, pattern_num)
  # produce_patterns('traffic1', 6, 10, pattern_num)

  # produce_patterns('traffic1', 4, 5, pattern_num)
  # produce_patterns('traffic1', 4, 15, pattern_num)
  # produce_patterns('traffic1', 4, 20, pattern_num)

  # produce_patterns('traffic2', 3, 10, pattern_num)
  # produce_patterns('traffic2', 4, 10, pattern_num)
  # produce_patterns('traffic2', 5, 10, pattern_num)
  # produce_patterns('traffic2', 6, 10, pattern_num)

  # produce_patterns('traffic2', 4, 5, pattern_num)
  # produce_patterns('traffic2', 4, 15, pattern_num)
  # produce_patterns('traffic2', 4, 20, pattern_num)


def get_pattern_configs(video):
  # default_params = [video, 'df5', 4, 10, 5]
  default_params = [video, 'df6', 4, 10, 5]
  
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

  for pos, values in varying_settings:
    current_params = list(default_params)
    for value in values:
      current_params[pos] = value
      configs.append(list(current_params))
  return configs

def build_patterns():
  videos = ['traffic1', 'traffic2']
  for v in videos:
    for config in get_pattern_configs(v):
      build_patterns_from_file(*config)


def run_query(video_name, pattern_path, idx, frame_pair, ids, df, k, method, result_folder_path):
  index_type = 1
  index_path = '{}/{}-{}-{}.pkl'.format(index_file_path, video_name, index_type, df)
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


def query_with_patterns(pattern_config, query_config):
  video_name, df_name, obj_num, pattern_length, pattern_num = pattern_config
  pattern_folder_path = '{}/pattern-builder2/patterns-{}/{}-{}-{}'.format(file_storage_path, 
        video_name, obj_num, pattern_length, pattern_num)
  pattern_txt_file  = '{}/pattern-builder2/patterns-{}/{}-{}-{}.txt'.format(file_storage_path,
    video_name, obj_num, pattern_length, pattern_num)
  query_video, query_k = query_config
  print('query on video', query_video, pattern_config, query_config)
  methods = ['baseline', 'proposed', 'proposed_seq', 'noimd']
  result_folder_path = '{}/batch-results2/patterns-{}/{}-{}-{}-{}'.format(file_storage_path, 
      video_name, obj_num, pattern_length, pattern_num, query_video)
  for idx, frame_pair, ids in read_patterns_from_file(pattern_txt_file):
    pattern_file_path = '{}/{}-{}-{}-{}.pkl'.format(pattern_folder_path,
        df_name, idx, '_'.join(frame_pair), '_'.join(ids))
    print('pattern idx:', idx)

    for method in methods:
      run_query(query_video, pattern_file_path, idx, frame_pair, ids, df_name, query_k, method, result_folder_path)
    

def batch_query():

  # video, df, 
  # default_pattern_params = ['traffic1', 'df5', 4, 10, 5]
  # # video, k
  # default_query_params = ['traffic1', 100]

  # default_pattern_params = ['traffic2', 'df5', 4, 10, 5]
  # default_query_params = ['traffic2', 100]

  # default_pattern_params = ['traffic2', 'df6', 4, 10, 5]
  # default_query_params = ['traffic2', 100]
  default_pattern_params = ['traffic1', 'df6', 4, 10, 5]
  default_query_params = ['traffic1', 100]

  varying_pattern_video = ['traffic1']
  # varying_pattern_video = ['traffic2']
  varying_pattern_objs = [3, 5]
  varying_pattern_length = [5, 15]
  # varying_pattern_df = ['df4', 'df6']
  varying_pattern_df = ['df5', 'df7', 'df8']

  varying_pattern = [
    # (0, varying_pattern_video),
    # (1, varying_pattern_df),
    # (2, varying_pattern_objs),
    # (3, varying_pattern_length)
  ]

  varying_query_video = ['traffic1']
  # varying_query_video = ['traffic2']
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

if __name__ == '__main__':
  # produce_pattern_groups()
  # build_patterns()
  batch_query()