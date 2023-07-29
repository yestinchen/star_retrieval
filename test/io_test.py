from vsimsearch.preprocessing import discretize_function_1
from vsimsearch.graph import compute_edges_from_nodes
from vsimsearch.indexing import ProposedIndex
from vsimsearch.io import read_nodes_from_mot_result
from vsimsearch.visualize import GraphVisualizer
import time
import pickle


def test_index_write():
  # read data.
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

  time_start = time.process_time()
  edges = compute_edges_from_nodes(nodes, height, width)
  discretize_function_1(edges, 1, 1)
  pi = ProposedIndex()
  index = pi.build_index(nodes, edges)
  time_end = time.process_time()
  print('index build complete, time used', time_end - time_start)

  time_start = time.process_time()
  with open('../storage/results/vsim/test_index.pkl', 'wb') as wf:
    pickle.dump(index, wf)
  time_end = time.process_time()
  print('index write complete, time used', time_end - time_start)

def test_index_read():
  with open('../storage/results/vsim/test_index.pkl', 'rb') as rf:
    time_start = time.process_time()
    index = pickle.load(rf)
    time_end = time.process_time()
    print('load time', time_end - time_start)
    print(type(index))
    print(len(index))
    # print(index)

if __name__ == '__main__':
  # test_index_write()
  test_index_read()
  pass