from scripts.settings import file_storage_path, video_name_meta_mapping, df_funcs
import os
# pass

def build_with_index_for(video_name, rate, index_type, df_name):
  width, height = video_name_meta_mapping[video_name]
  sequence_name = '{}-{}'.format(video, rate)
  file_path = '{}/sample-raw/{}.txt'.format(file_storage_path, sequence_name)
  df, df_p1, df_p2 = df_funcs[df_name]
  output_path = '{}/sample-index/{}-{}-{}.pkl'.format(file_storage_path, \
    sequence_name, index_type, df_name)
  log_path = '{}/sample-index/{}-{}-{}.out.txt'.format(file_storage_path, \
    sequence_name, index_type, df_name)
  tokens = ['python', 'vsimsearch/apps/index_app.py',
    '--file_path', file_path,
    '--frame_height', height, '--frame_width', width,
    '--output_path', output_path, 
    '--index_type', index_type,
    '--discretize_func', df, 
    '--df_param1', df_p1, '--df_param2', df_p2
  ]
  # mkdir if needed
  if not os.path.isdir(os.path.dirname(log_path)):
    os.makedirs(os.path.dirname(log_path))
  command = ' '.join([str(t) for t in tokens]) + ' > ' +  log_path
  os.system(command)

if __name__ == '__main__':
  # dfs = ['df5','df6', 'df7', 'df8']
  videos = ['drtrain', 'drtest', 'bdd100kA', 'bdd100kB']
  sample_rates = [5, 10]
  df = 'df6'
  for video in videos:
    for rate in sample_rates:
      build_with_index_for(video, rate, 1, df)
    # build_with_index_for('bdd100kA', 1, df)
    # build_with_index_for('bdd100kB', 1, df)