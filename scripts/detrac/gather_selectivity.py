from scripts.batch_patterns import read_patterns_from_file
from scripts.settings import file_storage_path, index_file_path
import pickle
from collections import defaultdict

from vsimsearch.utils import get_from_multi_level_dict

def get_unique_patterns(pattern_file_path):
  with open(pattern_file_path, 'rb') as rf:
    pattern = pickle.load(rf)
    nodes, edges = pattern.nodes, pattern.edges
    # collect node types.
    oid_type_dict = dict()
    gpresult = nodes.groupby('id')
    # print(nodes)
    for oid, group in gpresult:
      unique_class_labels = group['class'].unique()
      # assert len(unique_class_labels) == 1, 'expecting one class label'+str(unique_class_labels)
      unique_class_labels = sorted(unique_class_labels)
      if len(unique_class_labels) > 1:
        print('warning: multiple class labels extracted, taking the first one', unique_class_labels)
      oid_type_dict[oid] = unique_class_labels[0]
    # print(pattern.edges)
    edge_count_dict = defaultdict(list)
    for index, row in edges.iterrows():
      stype, etype = oid_type_dict[row['sid']], oid_type_dict[row['eid']]
      key = (stype, etype, row['theta'], row['d_ratio'])
      edge_count_dict[key].append(row['frame'])
    return edge_count_dict

def retrieve_candidates(query_config, unique_edge_dict):
  # 1. load index file.
  # 2. retrieve each 
  pass

def compute_unique_pattern_per_frame(edge_count_dict):
  frame_unique_edge_dict = defaultdict(set)
  for unique_edge, frame_list in edge_count_dict.items():
    for frame in frame_list:
      frame_unique_edge_dict[frame].add(unique_edge)
  return frame_unique_edge_dict

def read_pattern(pattern_config, query_config):
  video_name, df_name, obj_num, pattern_length, pattern_num = pattern_config
  pattern_folder_path = '{}/pattern-builder2/patterns-{}/{}-{}-{}'.format(file_storage_path, 
        video_name, obj_num, pattern_length, pattern_num)
  pattern_txt_file  = '{}/pattern-builder2/patterns-{}/{}-{}-{}.txt'.format(file_storage_path,
    video_name, obj_num, pattern_length, pattern_num)
  frame_pair_dict = dict()
  for idx, frame_pair, ids in read_patterns_from_file(pattern_txt_file):
    pattern_file_path = '{}/{}-{}-{}-{}.pkl'.format(pattern_folder_path,
        df_name, idx, '_'.join(frame_pair), '_'.join(ids))
    # print('pattern idx:', idx, frame_pair, ids)
    edge_count_dict = get_unique_patterns(pattern_file_path)
    # print(edge_count_dict)
    # print('len', len(edge_count_dict))
    frame_pair_str = '_'.join(frame_pair)
    frame_pair_dict[frame_pair_str] = edge_count_dict
  return frame_pair_dict

def read_index(video_name, df):
  index_path = '{}/{}-{}-{}.pkl'.format(index_file_path, video_name, 1, df)
  # num of candidates
  with open(index_path, 'rb') as rf:
    return pickle.load(rf)

def compute_num_candidates(index, edge_count_dict):
  # select raw frames.
  total_count = 0
  frame_set = set()
  for key, pattern_frames in edge_count_dict.items():
    stype, etype, theta, d = key
    edge_frames_dict = get_from_multi_level_dict(index, [stype, etype, (theta, d)])
    # count candidates
    for edge, frames in edge_frames_dict.items():
      total_count += len(frames) * len(pattern_frames)
      frame_set = frame_set.union(frames)

  print('count', total_count)
  print('what', len(frame_set))
  return total_count / len(frame_set) if len(frame_set)  > 0 else 0

if __name__ == '__main__':
  pattern_config = ['drtrain', 'df6', 4, 10, 60]
  query_config = ['drtrain', 100]
  frame_pair_dict = read_pattern(pattern_config, query_config)
  for key, value in frame_pair_dict.items():
    print('frames', key, 'len', len(value))