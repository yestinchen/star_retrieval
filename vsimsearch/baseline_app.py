from vsimsearch.baseline import BaselineWithProposedIndex
from vsimsearch.indexing import BaselineIndex, ProposedIndex, ProposedIndexPerFrame
from vsimsearch.io import read_nodes_from_mot_result
from vsimsearch.preprocessing import discretize_attributes, discretize_function_4
from vsimsearch.graph import compute_edges_from_nodes, extract_pattern_graph
import time
import math

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


def test_basline():
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
  # nodes = nodes[nodes['frame'] <= 20]
  print('total frames', nodes['frame'].max())

  # nodes_with_missing_frames = nodes[~nodes['frame'].isin([3,5])]
  time_start = time.process_time()
  edges = compute_edges_from_nodes(nodes, height, width)
  discretize_theta_d(edges, theta_n, d_n)
  baseline = BaselineWithProposedIndex()
  # index = ProposedIndexPerFrame().build_index(nodes, edges)
  index = ProposedIndex().build_index(nodes, edges)
  time_end = time.process_time()
  print('index build complete, time used', time_end - time_start)

  # read pattern.
  temporal_pattern = extract_pattern_graph(nodes, width, height, [1,2,3], [1,10])
  discretize_theta_d(temporal_pattern.edges, theta_n, d_n)

  # baseline_eval = BaselineWithNodeIndexEval()
  
  time_start = time.process_time()
  result = baseline.query(index, temporal_pattern, 1)
  # result = baseline.query_with_index_per_frame(index, temporal_pattern, 1)
  time_end = time.process_time()

  print('result', result)
  print('query time', time_end - time_start)


if __name__ == '__main__':
  # index per frame.
  test_basline()