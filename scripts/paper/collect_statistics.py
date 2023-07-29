from scripts.settings import file_storage_path, raw_file_path

import pandas as pd

def collect_statistics_for_video(video_name):
  print('collecting data from :', video_name)
  # read file
  video_path = '{}/{}.txt'.format(raw_file_path, video_name)
  df = pd.read_csv(video_path, names=[
    'frame', 'id', 'left', 'top', 'width', 'height', 'conf', 'class', 'x', 'y', 'z'
  ], index_col=False)
  # objects' position can not exceed image boundary
  # add column
  df.drop(columns=['conf', 'x', 'y', 'z'])

  # 1. avg objects per frame.
  groupby_frames = df.groupby('frame')['id'].count().reset_index(name='count')

  avg_obj_per_frame = groupby_frames['count'].sum()/groupby_frames['frame'].max()
  print("avg obj/f:", avg_obj_per_frame)

  # 2. total # of objects.
  total_obj_num = df['id'].nunique()
  print('unique objects: ', total_obj_num)

  # 3. total # of frames.
  total_frames_num = groupby_frames['frame'].max()
  print('total frames:', total_frames_num)
  
  # 4. avg duration of each id.
  groupby_ids = df.groupby('id').aggregate(min=('frame', 'min'), max=('frame', max))
  groupby_ids['gap'] = groupby_ids['max'] - groupby_ids['min']
  average_duration = groupby_ids['gap'].mean()
  print('avg duration:', groupby_ids['gap'].mean())

  return dict([
    ('# frames', total_frames_num),
    ('# avg obj/f', avg_obj_per_frame),
    ('# objects', total_obj_num),
    ('avg duration', average_duration),
  ])

def print_latex_table(videos, video_results):
  # print head
  lines = []

  head_line = ['video', *videos]

  lines.append(head_line)
  for key in video_results[0].keys():
    new_line = [key.replace('#', '\#')]
    for res in video_results:
      # round.
      value = res[key]
      if key == '# frames' or key == '# objects':
        value = '{:.2f}k'.format(value/1000)
      else:
        value = '{:.2f}'.format(value)
      new_line.append(value)
    lines.append(new_line)
  
  # print.
  for line in lines:
    print('\t&\t'.join(line), '\\\\ \hline')


if __name__ == '__main__':
  videos = ['drtest', 'drtrain', 'bdd100kA', 'bdd100kB', ]
  video_results = []
  for video in videos:
    res = collect_statistics_for_video(video)
    video_results.append(res)
  print('')
  print_latex_table(videos, video_results)