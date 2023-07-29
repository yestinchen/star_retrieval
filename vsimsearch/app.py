import pandas as pd
from vsimsearch.proposed_new_we import ProposedEval
from vsimsearch.indexing import ProposedIndex, ProposedIndexPerFrame
from vsimsearch.io import read_nodes_from_mot_result
from vsimsearch.preprocessing import discretize_attributes, discretize_function_4
from vsimsearch.graph import compute_edges_from_nodes, extract_pattern_graph
from vsimsearch.config import read_query_conf
import time
import math

def build_index(file_path, height, width, class_type, theta_n, d_n):
  nodes = read_nodes_from_mot_result(file_path, class_type)
  edges = compute_edges_from_nodes(nodes, height, width)
  discretize_theta_d(edges, theta_n, d_n)
  ib = ProposedIndex()
  index = ib.build_index(nodes, edges)
  # print(index)
  return index

def read_pattern_graph(file_path, height, width, class_type, theta_n, d_n, ids, frame_range):
  nodes = read_nodes_from_mot_result(file_path, class_type)
  temporal_pattern = extract_pattern_graph(nodes, width, height, ids, frame_range)
  discretize_theta_d(temporal_pattern.edges, theta_n, d_n)
  pe = ProposedEval()
  generalized_edges = pe._extract_edge(temporal_pattern)
  print(generalized_edges)
  pattern_signature_dict = pe._compute_signatures_for_edges(generalized_edges)
  # print(pattern_signature_dict)
  unique_pattern_signatures = pe._collect_unique_signatures(pattern_signature_dict)
  print(unique_pattern_signatures)
  ordered_patterns, global_order_frames = pe._extract_pattern_conditions(temporal_pattern)
  print('ordered patterns:', ordered_patterns)
  print('global frames', global_order_frames)
  unique_patterns = set([tuple(k) for k in ordered_patterns])
  print('unique patterns', unique_patterns)

  generalized_edges_with_pos_dict = pe._associate_pattern_edge_with_pos(generalized_edges, ordered_patterns)
  print('edges with pos', generalized_edges_with_pos_dict)
  pass

def discretize_theta_d(edges, theta_n, d_n):
  # discretize_attributes(edges, [
  #   ('theta', lambda x: round(x, theta_n)),
  #   ('d_ratio', lambda x: round(x, d_n))
  # ])
  # discretize_attributes(edges, [
  #   ('theta', lambda x: x // (math.pi / 2)),
  #   ('d_ratio', lambda _: 0)
  # ])
  # discretize_function_4(edges, 12)
  discretize_function_4(edges, 4, 5)

def test_query():
  # build index
  file_path = './data/faster_rcnn-tracktor-person.txt'
  height = 1080
  width = 1920
  class_type = 1
  # theta_n, d_n = 2, 3
  theta_n, d_n = 1, 1
  time_start = time.process_time()
  nodes = read_nodes_from_mot_result(file_path, class_type)
  time_end = time.process_time()
  print('read complete, time', time_end - time_start)
  # only consider the first 100 frames.
  nodes = nodes[nodes['frame'] <= 20]

  print('building index, total frames', nodes['frame'].max())
  time_start = time.process_time()
  edges = compute_edges_from_nodes(nodes, height, width)
  discretize_theta_d(edges, theta_n, d_n)
  ib = ProposedIndex()
  # ib = ProposedIndexPerFrame()
  # nodes_with_missing_frames = nodes[~nodes['frame'].isin([3,5])]
  index = ib.build_index(nodes, edges)
  time_end = time.process_time()
  print('index build complete, time used', time_end - time_start)
  temporal_pattern = extract_pattern_graph(nodes, width, height, [1,2,3], [1,10])
  discretize_theta_d(temporal_pattern.edges, theta_n, d_n)
  pe = ProposedEval()
  
  time_start = time.process_time()
  result = pe.query(index, temporal_pattern, 1, sequential=True)
  # result = pe.query_with_index_per_frame(index, temporal_pattern, 1, sequential=False)
  time_end = time.process_time()
  print('result', result)
  print('query time', time_end - time_start)
  pass

if __name__ == '__main__':
  # evaluate_mot_method('./data/faster_rcnn-tracktor-person.txt', 
  #   1080, 1920, 1, 2, 3)
  # config_dict = read_query_conf('./config/query_test.ini')
  # print(config_dict)
  # read_pattern_graph(**config_dict)
  test_query()
  pass
