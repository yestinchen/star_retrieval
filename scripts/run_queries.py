from scripts.settings import index_file_path, pattern_file_path, result_file_path
import os

def run_queries(video_name, obj_set, frames, index_type, df, k, method):
  print('running query with settings', video_name, obj_set, frames, index_type, df, k, method)
  obj_set = [str(i) for i in obj_set]
  frame_pair = [str(frames[0]), str(frames[1])]
  index_path = '{}/{}-{}-{}.pkl'.format(index_file_path, video_name, index_type, df)
  pattern_path = '{}/{}-{}-{}-{}.pkl'.format(pattern_file_path, video_name, df, \
    '_'.join(obj_set), '_'.join(frame_pair))
  tokens = ['python', 'vsimsearch/apps/query_app.py', 
    '--index_path', index_path,
    '--pattern_path', pattern_path,
    '--method', method,
    '--k', k,
    '--index_type', index_type
  ]
  store_path = result_file_path
  output_path = '{}/{}-{}-{}-{}-{}-{}.txt'.format(result_file_path, video_name, \
    '_'.join(obj_set), '_'.join(frame_pair), df, k, method)
  command = ' '.join([str(t) for t in tokens])
  os.system('{} > {}'.format(command, output_path))

if __name__ == '__main__':
  videos = ['traffic1', 'traffic2']
  methods = ['baseline', 'proposed', 'proposed_seq']
  # methods = ['proposed', 'proposed_seq']
  # index_types = [1, 2]
  index_types = [1]
  ks = [1, 10, 100]
  # dfs = ['df1', 'df2', 'df3', 'df4']
  dfs = ['df5']
  pattern_settings = [
    dict(obj_set=[1,2,3], frames=[1,10]),
  ]
  
  for video in videos:
    for index in index_types:
      for k in ks:
        for df in dfs:
          for pattern_setting in pattern_settings:
            for method in methods:
              run_queries(video, pattern_setting['obj_set'], pattern_setting['frames'], \
                index, df, k, method)