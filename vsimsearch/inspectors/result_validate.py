import pickle
from vsimsearch.graph import extract_pattern_graph
from vsimsearch.io import read_nodes_from_mot_result_multi_class
def display_results(video_path, width, height,
    window_start, window_size, ids):
  
  window_range = [window_start, window_start+window_size -1]
  print('window range', window_range)
  nodes = read_nodes_from_mot_result_multi_class(video_path)
  pattern = extract_pattern_graph(nodes, width, height, 
    ids, window_range)
  edges = pattern.edges
  print('edges\n', edges)

if __name__ == '__main__':
  traffic_1_path = '../storage/results/vsim/raw/traffic2.txt'
  display_results(traffic_1_path, 1280, 720, 39041, 10, [14641, 14642, 14660])