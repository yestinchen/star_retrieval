from scripts.settings import raw_file_path, index_file_path, video_name_meta_mapping, df_funcs
import os
# pass

def build_with_index_for(video_name, index_type, df_name, percent=None):
  width, height = video_name_meta_mapping[video_name]
  file_path = '{}/{}.txt'.format(raw_file_path, video_name)
  df, df_p1, df_p2 = df_funcs[df_name]
  if percent is None:
    output_path = '{}/{}-{}-{}.pkl'.format(index_file_path, \
      video_name, index_type, df_name)
    log_path = '{}/{}-{}-{}.out.txt'.format(index_file_path, \
      video_name, index_type, df_name)
  else:
    output_path = '{}/percent/{}-{}-{}-{}.pkl'.format(index_file_path, \
      video_name, index_type, df_name, percent)
    log_path = '{}/percent/{}-{}-{}-{}.out.txt'.format(index_file_path, \
      video_name, index_type, df_name, percent)
  tokens = ['python', 'vsimsearch/apps/index_app.py',
    '--file_path', file_path,
    '--frame_height', height, '--frame_width', width,
    '--output_path', output_path, 
    '--index_type', index_type,
    '--discretize_func', df, 
    '--df_param1', df_p1, '--df_param2', df_p2
  ]
  if percent is not None:
    tokens.extend(['--percent', str(percent)])
  # mkdir if needed
  if not os.path.isdir(os.path.dirname(log_path)):
    os.makedirs(os.path.dirname(log_path))
  command = ' '.join([str(t) for t in tokens]) + ' > ' +  log_path
  os.system(command)

if __name__ == '__main__':
  # build_with_index_for('test', 1, 'df1')
  # build_with_index_for('traffic1', 1, 'df1')
  # build_with_index_for('traffic2', 1, 'df1')
  # build_with_index_for('traffic1', 2, 'df1')
  # build_with_index_for('traffic2', 2, 'df1')
  # dfs = ['df1', 'df2', 'df3', 'df4']
  # dfs = ['df5']
  # dfs = ['df6']
  # dfs = ['df7', 'df8']
  # for df in dfs:
  #   build_with_index_for('traffic1', 1, df)
  #   # build_with_index_for('traffic1', 2, df)
  #   build_with_index_for('traffic2', 1, df)
  #   # build_with_index_for('traffic2', 2, df)
  #   pass

  # dfs = ['df5','df6', 'df7', 'df8']
  # for df in dfs:
  #   build_with_index_for('drtrain', 1, df)
  #   build_with_index_for('drtest', 1, df)
  #   # build_with_index_for('bdd100kA', 1, df)
  #   # build_with_index_for('bdd100kB', 1, df)

  videos = ['drtrain', 'drtest', 'bdd100kA', 'bdd100kB']
  # percents = [0.25, 0.5, 0.75, 1]
  # # videos = videos[:1]
  # # percents = percents[:1]

  # for v in videos:
  #   for p in percents:
  #     build_with_index_for(v, 1, 'df6', p)

  for v in videos:
    for i in [3, 4]:
      build_with_index_for(v, i, 'df6')