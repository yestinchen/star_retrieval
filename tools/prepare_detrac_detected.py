
DETRAC_DATA_PATH = '/media/ytchen/hdd/dataset/Detrac'

TRAIN_FOLDER = 'Insight-MVT_Annotation_Train'

TEST_FOLDER = 'Insight-MVT_Annotation_Test'

# detected results

DETECTED_RESULT_PATH = "../storage/results/detrac"

DETECTED_TRAIN_FOLDER = "train-mot"

DETECTED_TEST_FOLDER = "test-mot"

DEST_PATH = '../storage/results/vsim-all/raw'

import os
import pandas as pd

def read_txt_file(folder_path, sequence_name):
  file_path = "{}/{}.txt".format(folder_path, sequence_name)
  df = pd.read_csv(file_path, names=[
    'frame', 'id', 'left', 'top', 'width', 'height', 'conf', 'class', 'x', 'y', 'z'
  ], index_col=False)
  return df


def concanate_detected_videos(folder_type):
  assert folder_type in ['test', 'train'], 'please specify test or train'
  if folder_type == 'test':
    raw_name = TEST_FOLDER
    detected_name = DETECTED_TEST_FOLDER
  elif folder_type == 'train':
    raw_name = TRAIN_FOLDER
    detected_name = DETECTED_TRAIN_FOLDER
  frame_num_dict = dict()
  frame_start_id_dict = dict()
  last_frame = 0
  last_id = 0

  raw_folder_path = os.path.join(DETRAC_DATA_PATH, raw_name)
  detected_folder_path = os.path.join(DETECTED_RESULT_PATH, detected_name)
  dataframes_list = list()
  for sequence_name in os.listdir(raw_folder_path):
    print('processing sequence', sequence_name)
    dataframe = read_txt_file(detected_folder_path, sequence_name)
    frame_num = dataframe['frame'].max()
    max_id = dataframe['id'].max()
    # print('frame_num:', frame_num)

    # increase 
    dataframe['frame'] += last_frame
    dataframe['id'] += last_id

    frame_start_id_dict[sequence_name] = last_frame + 1
    frame_num_dict[sequence_name] = frame_num
    last_frame += frame_num
    last_id += max_id + 1
    dataframes_list.append(dataframe)
  
  # save data.
  results = pd.concat(dataframes_list)
  results.to_csv(os.path.join(DEST_PATH, 'dr{}.txt'.format(folder_type)), 
    index=False, header=False)
  # save meta.
  with open(os.path.join(DEST_PATH, 'dr{}-meta.txt'.format(folder_type)), 'w') as wf:
    for key, value in frame_num_dict.items():
      wf.write('{}:{}/{}\n'.format(key, value, frame_start_id_dict[key]))

if __name__ == '__main__':
  # concanate_detected_videos('test')
  concanate_detected_videos('train')