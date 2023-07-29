from vsimsearch.io import read_nodes_from_mot_result
from vsimsearch.graph import compute_edges_from_nodes, extract_pattern_graph
import networkx as nx
from matplotlib import pyplot as plt
import pandas as pd
from vsimsearch.visualize import GraphVisualizer
from cv2 import cv2

def visualize_network():
  G = nx.DiGraph()
  G.add_node('1', pos=[2, 5])
  G.add_node('2', pos=[50,40])
  G.add_edge('1', '2', theta=0.1, d=10)
  G.add_edge('2', '1', theta=-0.1, d=10)
  pos = nx.get_node_attributes(G, 'pos')
  edge_labels = nx.get_edge_attributes(G, 'theta')
  nx.draw_networkx(G, pos, with_labels=True, arrows=True)
  # nx.draw_networkx_edge_labels(G, pos, edge_labels)
  plt.show()

def visualize_on_frame(result_path, height, width, img_folder, frame_id):
  nodes = read_nodes_from_mot_result(result_path, 1)
  edges = compute_edges_from_nodes(nodes, width, height)
  nodes = nodes[nodes['frame'] == frame_id]
  edges = edges[edges['frame'] == frame_id]
  img_path = '{}/{:06d}.jpg'.format(img_folder, frame_id)
  gv = GraphVisualizer()
  gv.visualize_one_on_frame(img_path, nodes, edges)

def visualize_on_frame_range(result_path, height, width, img_folder, frange):
  nodes = read_nodes_from_mot_result(result_path, 1)
  edges = compute_edges_from_nodes(nodes, width, height)
  img_func = lambda fid: '{}/{:06d}.jpg'.format(img_folder, fid)
  gv = GraphVisualizer()
  gv.interactive_visualize(img_func, nodes, edges, frange)


def visualize_extracted_graph(result_path, height, width, img_folder_or_video_path, ids, frange):
  nodes = read_nodes_from_mot_result(result_path, 1)
  print('read done')
  pattern = extract_pattern_graph(nodes, width, height, ids, frange)
  print('pattern graph done')
  if '.mp4' in img_folder_or_video_path:
    # open video
    cap= cv2.VideoCapture(img_folder_or_video_path)
    def img_func(fid):
      cap.set(cv2.CAP_PROP_POS_FRAMES, fid)
      ret, frame = cap.read()
      return frame
  else:
    img_func = lambda fid: '{}/{:06d}.jpg'.format(img_folder_or_video_path, fid)
  gv = GraphVisualizer()
  gv.interactive_visualize(img_func, pattern.nodes, pattern.edges, frange)

if __name__ == '__main__':
  # visualize_on_frame_range('./data/faster_rcnn-tracktor-person.txt', 1080, 1920,\
  #    '../storage/dataset/MOT17/train/MOT17-04-DPM/img1', (1, 10))
  # visualize_extracted_graph('./data/faster_rcnn-tracktor-person.txt', 1080, 1920,\
  #    '../storage/dataset/MOT17/train/MOT17-04-DPM/img1', set([1,2,3]), (1, 10))

  # visualize_extracted_graph('../storage/results/vsim/raw/traffic1.txt', 720, 1080, \
  #   '/media/ytchen/hdd/dataset/youtube/traffic1.mp4', set([1,2,3]), (1, 10))
  visualize_extracted_graph('../storage/results/vsim/raw/traffic2.txt', 720, 1080, \
    '/media/ytchen/hdd/dataset/youtube/traffic2.mp4', set([1,2,3]), (1, 10))