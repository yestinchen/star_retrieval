import pandas as pd
import random
import os
import shutil

def generate_multilabels(origin_path, new_path, color_num):
  df = pd.read_csv(origin_path, names=[
    'frame', 'id', 'left', 'top', 'width', 'height', 'conf', 'class', 'x', 'y', 'z'
  ], index_col=False)
  # get unique objects.
  unique_ids = df['id'].unique().tolist()
  # assign new labels to unique_ids
  id_color_mappings = dict()
  for _id in unique_ids:
    color = random.randint(1, color_num)
    id_color_mappings[_id] = color
    df.loc[df['id'] == _id, 'color'] = color
  # concat
  # df['new_class'] = df.apply(lambda x: str(x['color'])+'-'+str(x['class']), axis=1)
  # compsite class.
  df['new_class'] = df.apply(lambda x: int(x['color'])*1000+int(x['class']), axis=1)
  # df = df.drop(['color', 'class'], axis=1)
  # df = df.rename(dict(new_class='class'), axis=1)
  df['class'] = df['new_class']
  df.drop(['color', 'new_class'], axis=1, inplace=True)
  if not os.path.isdir(os.path.dirname(new_path)):
    os.makedirs(os.path.dirname(new_path))
  # save back.
  df.to_csv(new_path, index=False, header=False)
  # also save color mapping.
  with open('{}.color'.format(new_path), 'w') as wf:
    for _id, _color in id_color_mappings.items():
      wf.write('{}:{}\n'.format(_id, _color))

if __name__ == '__main__':
  sequences = ['drtest', 'drtrain', 'bdd100kA', 'bdd100kB']
  color_nums = [10, 20, 30]
  # sequences = sequences[:1]
  for seq in sequences:
    # for color_num in color_nums: 
      generate_multilabels(
        '../storage/results/vsim-all/raw/{}.txt'.format(seq),
        '../storage/results/vsim-all/multi-raw/{}.txt'.format(seq),
        # '../storage/results/vsim-all/multi-raw/{}-{}.txt'.format(seq, color_num),
        3
      )
      shutil.copy(
        '../storage/results/vsim-all/raw/{}-meta.txt'.format(seq),
        '../storage/results/vsim-all/multi-raw/{}-meta.txt'.format(seq)
        # '../storage/results/vsim-all/multi-raw/{}-{}-meta.txt'.format(seq, color_num)
      )