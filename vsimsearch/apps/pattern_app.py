import argparse
import pickle
from vsimsearch.apps.common import discretize_func_from_args
from vsimsearch.graph import extract_pattern_graph
from vsimsearch.io import read_nodes_from_mot_result, read_nodes_from_mot_result_multi_class
from vsimsearch.apps.index_app import prepare_parser

if __name__ == '__main__':
  parser = argparse.ArgumentParser('build and persist a pattern from a detected file')
  prepare_parser(parser)
  # ids: 1,2,3
  parser.add_argument('--ids')
  # consecutive frames: e.g, 2,20
  parser.add_argument('--frames')

  args = parser.parse_args()
  # parse frames
  [start_frame, end_frame] =list(map(int, args.frames.split(',')))

  assert end_frame > start_frame, 'end frame should > start frame'

  id_list = list(map(int, args.ids.split(',')))

  nodes = None
  if args.single_type:
    nodes = read_nodes_from_mot_result(args.file_path)
  else:
    nodes = read_nodes_from_mot_result_multi_class(args.file_path)


  pattern = extract_pattern_graph(nodes, args.frame_width,\
     args.frame_height, id_list, [start_frame, end_frame])

  discretize_func_from_args(args)(pattern.edges)

  # save pattern.
  with open(args.output_path, 'wb') as wf:
    pickle.dump(pattern, wf)