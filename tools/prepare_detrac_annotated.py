# the path for detrac images
DETRAC_DATA_PATH = '/media/ytchen/hdd/dataset/Detrac'

TRAIN_FOLDER = 'Insight-MVT_Annotation_Train'

TEST_FOLDER = 'Insight-MVT_Annotation_Test'

# path for annotations, based on sequences in 'train' folder
DETRAC_ANNOTATION_PATH = '/media/ytchen/hdd/dataset/DETRAC-Train-Annotations-XML-v3'

# path for detection results, for sequences in 'test' folder
DETRAC_MOT_RESULT_PATH = ''

DEST_PATH = '../storage/results/vsim/detrac'

from xml.dom import minidom
import os

def read_xml_annotation(sequence_name):
  file_path = '{}/{}_v3.xml'.format(DETRAC_ANNOTATION_PATH, sequence_name)
  xml_doc = minidom.parse(file_path)
  frames = xml_doc.getElementsByTagName('frame')
  frame_dict = dict()

  for frame in frames:
    frame_num = int(frame.attributes['num'].value)
    target_lists = frame.getElementsByTagName('target_list') 
    # should be only one target list
    assert len(target_lists) <= 1, 'more than one target list found'
    if len(target_lists) > 0:
      object_list = list()
      frame_dict[frame_num] = object_list

      target_list = target_lists[0]
      for target in target_list.getElementsByTagName('target'):
        target_id = target.attributes['id'].value
        box_ele = target.getElementsByTagName('box')[0].attributes
        # top, left, width, height
        bboxes = ['top', 'left', 'width', 'height']
        bboxes = [box_ele[k].value for k in bboxes]
        attribute_ele = target.getElementsByTagName('attribute')[0].attributes

        vehicle_type = attribute_ele['vehicle_type'].value
        vehicle_color = attribute_ele['color'].value
        object_list.append(
          (target_id, bboxes, vehicle_type, vehicle_color)
        )
  return frame_dict

def write_results(frame_dict, file_name):
  if not os.path.isdir(DEST_PATH):
    os.makedirs(DEST_PATH)
  file_path = os.path.join(DEST_PATH, file_name)
  with open(file_path, 'w') as wf:
    for frame_id, objects in frame_dict.items():
      for target_id, bbox, vtype, vcolor in objects:
        wf.write('{},{},{},{},{},{},{},{}\n'.format(frame_id, target_id, bbox[0], bbox[1], \
          bbox[2], bbox[3], vtype, vcolor) )

def concanate_train_videos():
  meta_info = 'train_meta.txt'
  result_name = 'train_results.txt'

  frame_num_dict = dict()
  frame_start_id_dict = dict()
  last_frame = 0
  
  concate_frame_dict = dict()
  for sequence_name in os.listdir(os.path.join(DETRAC_DATA_PATH, TRAIN_FOLDER)):
    print('processing sequence', sequence_name)
    frame_dict = read_xml_annotation(sequence_name)
    frame_num = max(frame_dict.keys())
    start_frame = last_frame + 1
    for key, item in frame_dict.items():
      concate_frame_dict[key+start_frame] = item
    frame_start_id_dict[sequence_name] = start_frame
    frame_num_dict[sequence_name] = frame_num
    last_frame += frame_num

  # save.
  write_results(frame_dict, result_name)
  with open(os.path.join(DEST_PATH, meta_info), 'w') as wf:
    for key, value in frame_num_dict.items():
      wf.write('{}:{}/{}\n'.format(key, value, frame_start_id_dict[key]))

if __name__ == '__main__':
  # frame_dict = read_xml_annotation('MVI_20011')
  # write_results(frame_dict, 'test.txt')
  concanate_train_videos()