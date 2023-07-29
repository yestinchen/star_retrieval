import pickle
from vsimsearch.visualize import GraphVisualizer
from cv2 import cv2

def visualize_pattern(pattern_pkl, video_path):
  with open(pattern_pkl, 'rb') as pf:
    pattern = pickle.load(pf)
  cap= cv2.VideoCapture(video_path)
  def img_func(fid):
    cap.set(cv2.CAP_PROP_POS_FRAMES, fid)
    ret, frame = cap.read()
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
  gv = GraphVisualizer()
  gv.interactive_visualize(img_func, pattern.nodes, pattern.edges)
  # print(pattern)

if __name__ == '__main__':
  # visualize_pattern('../storage/results/vsim/pattern/traffic2-df3-1_2_3-1_10.pkl', 
  # '/media/ytchen/hdd/dataset/youtube/traffic2.mp4')
  visualize_pattern('../storage/results/vsim/pattern/traffic1-df3-1_2_3-1_10.pkl', 
  '/media/ytchen/hdd/dataset/youtube/traffic1.mp4')