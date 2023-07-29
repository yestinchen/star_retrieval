from scripts.settings import raw_file_path, file_storage_path, video_name_meta_mapping, df_funcs
import os

def build_patterns_for(video_name, df_name, \
  frame_pair, ids):
  ids = [str(i) for i in ids]
  frame_pair = [str(frame_pair[0]), str(frame_pair[1])]
  width, height = video_name_meta_mapping[video_name]
  file_path = '{}/{}.txt'.format(raw_file_path, video_name)
  df, df_p1, df_p2 = df_funcs[df_name]
  store_path = file_storage_path+'/result-pattern'
  output_path = '{}/{}-{}-{}-{}.pkl'.format(store_path, \
    video_name, df_name, '_'.join(ids), '_'.join(frame_pair))
  log_path = '{}/{}-{}-{}-{}.out.txt'.format(store_path, \
    video_name, df_name, '_'.join(ids), '_'.join(frame_pair))
  tokens = ['python', 'vsimsearch/apps/pattern_app.py',
    '--file_path', file_path,
    '--frame_height', height, '--frame_width', width,
    '--output_path', output_path, 
    '--discretize_func', df, 
    '--df_param1', df_p1, '--df_param2', df_p2,
    '--ids', ','.join(ids),
    '--frames', ','.join(frame_pair)
  ]
  command = ' '.join([str(t) for t in tokens]) + ' > ' +  log_path
  print('command', command)
  os.system(command)
  
  pass

if __name__ == '__main__':
  # dfs = ['df1', 'df2', 'df3', 'df4']
  dfs = ['df5']
  # videos = ['traffic1', 'traffic2']
  videos = ['traffic1']
  obj_sets = [
    [14641, 14642, 14660]
  ]
  frames = [
    (39041, 39050)
  ]
  for df in dfs:
    for video in videos:
      for objs in obj_sets:
        for frame in frames:
          print('building : ', video, df, objs, frame)
          build_patterns_for(video, df, frame, objs)