from scripts.settings import raw_file_path, inspectors_file_path, video_name_meta_mapping, df_funcs
import os
# pass

def build_with_index_for(video_name, index_type, df_name):
  width, height = video_name_meta_mapping[video_name]
  file_path = '{}/{}.txt'.format(raw_file_path, video_name)
  df, df_p1, df_p2 = df_funcs[df_name]
  store_path = os.path.join(inspectors_file_path, 'edges')
  output_path = '{}/{}-{}-{}.pkl'.format(store_path, \
    video_name, index_type, df_name)
  log_path = '{}/{}-{}-{}.out.txt'.format(store_path, \
    video_name, index_type, df_name)
  tokens = ['python', 'vsimsearch/apps/index_app.py',
    '--file_path', file_path,
    '--frame_height', height, '--frame_width', width,
    '--output_path', output_path, 
    '--discretize_func', df, 
    '--df_param1', df_p1, '--df_param2', df_p2
  ]
  command = ' '.join([str(t) for t in tokens]) + ' > ' +  log_path
  os.system(command)

if __name__ == '__main__':
  # build_with_index_for('test', 1, 'df1')
  # build_with_index_for('traffic1', 1, 'df1')
  # build_with_index_for('traffic2', 1, 'df1')
  # build_with_index_for('traffic1', 2, 'df1')
  # build_with_index_for('traffic2', 2, 'df1')
  for df in ['df2', 'df3', 'df4']:
    build_with_index_for('traffic1', 1, df)
    build_with_index_for('traffic1', 2, df)
    build_with_index_for('traffic2', 1, df)
    build_with_index_for('traffic2', 2, df)
  pass