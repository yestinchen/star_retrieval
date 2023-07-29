
import json
import os
import pandas as pd
from pandas.core.frame import DataFrame

base_path = '/media/ytchen/hdd/dataset/autodrive/bdd100k_labels20_box_track/bdd100k/labels-20/box-track/'

annotation_path= base_path+'train/'
txt_path = base_path + 'train-txt/'
concat_txt_path = base_path + 'concat-txt/'

# convert categories to coco object code.
class_dict = dict([
  ('pedestrian', 1),
  ('bicycle', 2),
  ('car', 3),
  ('motorcycle', 4),
  ('bus', 6),
  ('train', 7),
  ('truck', 8),
  ('other vehicle', 81),
  ('rider', 82),
  ('other person', 83),
  ('trailer', 84),
])

def read_json(file_path):
  obj_list = []
  # of tuple (frame, id, left, top, width, height, conf, class, x, y, z)
  with open(file_path, 'r') as rf:
    video_json = json.load(rf)
    for fid, frame_json in enumerate(video_json, 1):
      for obj_json in frame_json['labels']:
        obj_id = obj_json['id']
        box2d = obj_json['box2d']
        obj_class = obj_json['category']
        obj_list.append(
          (fid, int(obj_id), 
            box2d['x1'], box2d['y1'], box2d['x2'] -box2d['x1'], box2d['y2']-box2d['y1'],
            1, class_dict[obj_class], 0, 0, 0
          )
        )
  df = pd.DataFrame(obj_list, columns=[
    'frame', 'id', 'left', 'top', 'width', 'height', 'conf', 'class', 'x', 'y', 'z'
    ])
  return df

def write_txt_file(target_path, df:DataFrame):
  if not os.path.isdir(os.path.dirname(target_path)):
    os.makedirs(os.path.dirname(target_path))
  df.to_csv(target_path, header=False, index=False)

def read_txt_file(file_path):
  df = pd.read_csv(file_path, names=[
    'frame', 'id', 'left', 'top', 'width', 'height', 'conf', 'class', 'x', 'y', 'z'
  ], index_col=False)
  return df

def get_sorted_files(folder):
  files = [x for x in  os.listdir(folder)]
  return sorted(files)

def convert_json_files(source_path, target_path):
  write_txt_file(target_path, read_json(source_path))

def concanate_files(folder_path, files, output_name):
  frame_num_dict = dict()
  frame_start_id_dict = dict()
  last_frame = 0
  dataframes_list = list()
  for file_name in files:
    print('processing sequence', file_name)
    dataframe = read_txt_file(os.path.join(folder_path, file_name))
    frame_num = dataframe['frame'].max()

    # increase
    dataframe['frame'] += last_frame
    frame_start_id_dict[file_name] = last_frame + 1
    frame_num_dict[file_name] = frame_num
    last_frame += frame_num
    dataframes_list.append(dataframe)
  
  if not os.path.isdir(concat_txt_path):
    os.makedirs(concat_txt_path)

  # save data.
  results = pd.concat(dataframes_list)
  results.to_csv(os.path.join(concat_txt_path, '{}.txt'.format(output_name)), 
    index=False, header=False)
  # save meta.
  with open(os.path.join(concat_txt_path, '{}-meta.txt'.format(output_name)), 'w') as wf:
    for key, value in frame_num_dict.items():
      wf.write('{}:{}/{}\n'.format(key, value, frame_start_id_dict[key]))


# main entries.

def main_obtain_txt_files():
  all_files = get_sorted_files(annotation_path)
  for idx, file in enumerate(all_files):
    print('processing: ', file, 'progress:', idx, '/', len(all_files))
    source = os.path.join(annotation_path, file)
    target = os.path.join(txt_path, file.replace('.json', '.txt'))
    convert_json_files(source, target)

def main_obtain_merged_files():
  all_files = get_sorted_files(txt_path)
  split_point = len(all_files) // 2
  partA = all_files[:split_point]
  partB = all_files[split_point:]

  concanate_files(txt_path, partA, 'bdd100kA')
  concanate_files(txt_path, partB, 'bdd100kB')

if __name__ ==  '__main__':
  # df = read_json(os.path.join(annotation_path, get_sorted_files(annotation_path)[0]))
  # print(df['class'].unique())

  # main_obtain_txt_files()
  main_obtain_merged_files()