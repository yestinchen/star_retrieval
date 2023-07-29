# for index building
import argparse
from typing import NamedTuple
from vsimsearch.graph import compute_edges_from_nodes
from vsimsearch.io import read_nodes_from_mot_result, read_nodes_from_mot_result_multi_class
from vsimsearch.apps.common import add_args_for_discretize_func, discretize_func_from_args
import pickle
import time

def prepare_parser(parser: argparse.ArgumentParser):
  parser.add_argument('--file_path')
  parser.add_argument('--frame_height', type=int)
  parser.add_argument('--frame_width', type=int)
  parser.add_argument('--output_path')
  add_args_for_discretize_func(parser)
  parser.add_argument('--single_type', type=bool, default=False)

if __name__ == '__main__':
  parser = argparse.ArgumentParser('build and persist index from a detected file')
  prepare_parser(parser)
  args = parser.parse_args()

  # start working
  nodes = None
  if args.single_type:
    nodes = read_nodes_from_mot_result(args.file_path)
  else:
    nodes = read_nodes_from_mot_result_multi_class(args.file_path)
  
  edges = compute_edges_from_nodes(nodes, args.frame_height, args.frame_width)
  # apply func
  discretize_func_from_args(args)(edges)

  index = object()
  index.nodes = nodes
  index.edges = edges

  with open(args.output_path, 'wb') as wf:
    pickle.dump(index, wf)
