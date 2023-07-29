from vsimsearch.visualize import GraphVisualizer
from matplotlib import pyplot as plt
import cv2
import pickle
from scripts.batch_patterns import read_patterns_from_file
import os

# base_path = '../storage/results/vsim-detrac/'
# frame_sample_rate = 1
# base_path = '../storage/results/vsim-detrac-10/'
# frame_sample_rate = 10
base_path = '../storage/results/vsim-detrac-5/'
frame_sample_rate = 5

img_folder_dict = dict(
  drtrain='/media/ytchen/hdd/dataset/Detrac/Insight-MVT_Annotation_Train/',
  drtest='/media/ytchen/hdd/dataset/Detrac/Insight-MVT_Annotation_Test/',
)

def wait_with_check_closing(win_name):
  """ 
      https://stackoverflow.com/questions/35003476/"
      "opencv-python-how-to-detect-if-a-window-is-closed/37881722
  """
  while True:
    keyCode = cv2.waitKey(50)
    if keyCode != -1:
      break
    win_prop = cv2.getWindowProperty(win_name, cv2.WND_PROP_VISIBLE)
    if win_prop <= 0:
      break

def batch_process(pattern_video, obj_num, pattern_length, pattern_num, df):
  pattern_list_path = '{}/pattern-builder2/patterns-{}/{}-{}-{}.txt'\
    .format(base_path, pattern_video, obj_num, pattern_length, pattern_num)
  output_folder = '{}/visualize_patterns/patterns-{}/{}-{}-{}-{}/'\
    .format(base_path, pattern_video, obj_num, pattern_length, pattern_num, df)
  sequence_folder = img_folder_dict[pattern_video]

  pattern_list = read_patterns_from_file(pattern_list_path)
  sequence_list = read_video_meta_info(pattern_video)

  for idx, frame_pair, ids in pattern_list:
    pattern_path = '{}/pattern-builder2/patterns-{}/{}-{}-{}/{}-{}-{}-{}.pkl'\
      .format(base_path, pattern_video, obj_num, pattern_length, pattern_num, \
        df, idx, '_'.join(frame_pair), '_'.join(ids))
    save_visualize_patterns(
      os.path.join(output_folder, '{}-{}-{}'.format(idx, '_'.join(frame_pair), '_'.join(ids))),
      sequence_folder,
      pattern_path, frame_pair, sequence_list
    )
    # import sys
    # sys.exit(0)

def save_visualize_patterns(output_path, sequence_folder, pattern_path, frame_pair, sequence_list):
  if not os.path.isdir(output_path):
    os.makedirs(output_path)
  with open(pattern_path, 'rb') as rf:
    pattern = pickle.load(rf)
  assert pattern is not None, 'Oops'
  # retrieve. image.
  nodes, edges = pattern.nodes, pattern.edges

  for frame_id in range(1, pattern.length + 1):
    sequence_name, seq_frame = find_sequence_for(sequence_list, frame_id + int(frame_pair[0]) - 1)
    frame_path = '{}/{}/img{:05d}.jpg'.format(sequence_folder, sequence_name, seq_frame * frame_sample_rate)

    # visualize each one.
    sub_nodes = nodes[nodes['frame'] == frame_id]
    sub_edges = edges[edges['frame'] == frame_id]
    img = draw_frame(frame_path, sub_nodes, sub_edges)
    # save img.
    cv2.imwrite('{}/{}.jpg'.format(output_path, frame_id), img)

def draw_frame(frame_path, nodes, edges, show=False):
  img = cv2.imread(frame_path)
  # print(nodes)
  # print(edges)
  # draw vertex
  for idx, node in nodes.iterrows():
    vertex_center = (int(node['center_x']), int(node['center_y']))
    cv2.circle(img, vertex_center, \
      50, (255, 255, 255), thickness=2 )
    cv2.putText(img, '{:.0f}/{:.0f}'.format(node['id'], node['class']), 
      (vertex_center[0]-30, vertex_center[1]), cv2.FONT_HERSHEY_SIMPLEX, \
      .5, (255, 255, 255))
  # draw edges
  for idx, edge in edges.iterrows():
    sid, eid, theta, d = edge['sid'], edge['eid'], edge['theta'], edge['d_ratio']
    from_node = nodes[nodes['id'] == sid].iloc[0]
    to_node = nodes[nodes['id'] == eid].iloc[0]
    start_center = (int(from_node['center_x']), int(from_node['center_y']))
    end_center = (int(to_node['center_x']), int(to_node['center_y']))
    cv2.line(img, start_center, end_center, (255, 255, 255), thickness=2)
    text_place = ((start_center[0] + end_center[0])//2 , (start_center[1] + end_center[1])//2)
    cv2.putText(img, '{:.0f}/{:.0f}'.format(theta, d), text_place, cv2.FONT_HERSHEY_COMPLEX, 
      .5, (255, 255, 255))
  if show:
    cv2.imshow('preview',img)
    wait_with_check_closing('preview')
    cv2.destroyAllWindows()
  return img

def read_video_meta_info(pattern_video):
  meta_path = '{}/raw/{}-meta.txt'.format(base_path, pattern_video)
  sequences_list = list() # store tuples of (sequence_name, start_frame, length)
  with open(meta_path, 'r') as rf:
    for line in rf.readlines():
      name, arr = line.split(':')
      length, start_frame = arr.split('/')
      sequences_list.append((name, int(start_frame), int(length)))
  return sequences_list

def find_sequence_for(sequence_list, frame_idx):
  for sequence_tuple in sequence_list:
    name, sframe, length = sequence_tuple
    if frame_idx >= sframe and frame_idx < sframe + length:
      # this frame 
      # return sequence name, frame_offset relative to the start of the sequence
      return name, frame_idx - sframe + 1
  return None

if __name__ == '__main__':
  # save_visualize_patterns(
  #   None,
  #   (304, 318),
  #   [278, 333, 362, 270]
  # )
  # batch_process('drtest', 4, 10, 40, 'df8')
  # batch_process('drtest', 4, 10, 40, 'df6')
  # batch_process('drtrain', 4, 10, 60, 'df8')
  batch_process('drtrain', 4, 10, 60, 'df6')

  # name, fid = find_sequence_for( read_video_meta_info(), 10000 )
  # print("name", name, 'fid', fid)