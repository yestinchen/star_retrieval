from scripts.settings import index_file_path, pattern_file_path, file_storage_path
import os


def run_retrieve(index_type, video_name, pattern_path, idx, frame_pair, ids, df, k, method, result_folder_path):
  index_path = '{}/{}-{}-{}.pkl'.format(index_file_path, video_name, index_type, df)
  print('running retrieve_only_app with settings', video_name, ids, frame_pair, index_type, df, k, method)
  if not os.path.isdir(result_folder_path):
    os.makedirs(result_folder_path)

  tokens = ['python', 'vsimsearch/apps/retrieve_only_app.py', 
    '--index_path', index_path,
    '--pattern_path', pattern_path,
    '--method', method,
    '--k', k,
    '--index_type', index_type
  ]
  output_path = '{}/{}-{}-{}-{}-{}-{}-{}.txt'.format(result_folder_path, video_name, \
    '_'.join(ids), '_'.join(frame_pair), df, k, method, index_type)
  command = ' '.join([str(t) for t in tokens])
  print('exec', command, '>', output_path)
  os.system('{} > {}'.format(command, output_path))

# def retrieve_with_patterns(pattern_config, query_config):
#   pass


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

def retrieve_with_patterns(pattern_config, query_config):
  video_name, df_name, obj_num, pattern_length, pattern_num = pattern_config
  pattern_folder_path = '{}/pattern-builder2/patterns-{}/{}-{}-{}'.format(file_storage_path, 
        video_name, obj_num, pattern_length, pattern_num)
  pattern_txt_file  = '{}/pattern-builder2/patterns-{}/{}-{}-{}.txt'.format(file_storage_path,
    video_name, obj_num, pattern_length, pattern_num)
  query_video, query_k, index_type = query_config
  print('retrieve on video', query_video, pattern_config, query_config)
  # methods = ['baseline', 'proposed', 'proposed_seq']
  methods = ['baseline']
  result_folder_path = '{}/batch-results2-extra/patterns-{}/{}-{}-{}-{}'.format(file_storage_path, 
      video_name, obj_num, pattern_length, pattern_num, query_video)
  for idx, frame_pair, ids in read_patterns_from_file(pattern_txt_file):
    pattern_file_path = '{}/{}-{}-{}-{}.pkl'.format(pattern_folder_path,
        df_name, idx, '_'.join(frame_pair), '_'.join(ids))
    print('pattern idx:', idx)

    for method in methods:
      run_retrieve(index_type, query_video, pattern_file_path, idx, frame_pair, ids, df_name, query_k, method, result_folder_path)
    
if __name__ == '__main__':
  # video = 'drtest'
  video = 'bdd100kB'
  default_pattern_params = [video, 'df6', 4, 10, 20]
  default_query_params = [video, 1, 1]

  varying_index = [3, 4]

  varying_query = [
    (2, varying_index)
  ]

  retrieve_with_patterns(default_pattern_params, default_query_params)

  for pos, varying_values in varying_query:
    query_params = list(default_query_params)
    for value in varying_values:
      query_params[pos] = value
      retrieve_with_patterns(default_pattern_params, query_params)


  # 1. default config

  # for it in index_types:
  #   retrieve_with_patterns(video_name, obj_set, frames, it, df, k, method)