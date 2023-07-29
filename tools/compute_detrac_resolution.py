import cv2
import os
from collections import defaultdict

def read_resolution(parent_folder, sequence_name):
  check_file = '{}/{}/img00001.jpg'.format(parent_folder, sequence_name)
  im = cv2.imread(check_file)
  height, width, color = im.shape
  return (height, width)

def compute_unique_resolution(check_folder):
  resolution_dict = defaultdict(set)
  for sequence_name in os.listdir(check_folder):
    resolution = read_resolution(check_folder, sequence_name)
    resolution_dict[resolution].add(sequence_name)
  for key, value in resolution_dict.items():
    print(key, value)

if __name__ == '__main__':
  compute_unique_resolution(
    # '/media/ytchen/hdd/dataset/Detrac/Insight-MVT_Annotation_Test'

    '/media/ytchen/hdd/dataset/Detrac/Insight-MVT_Annotation_Train'
  )