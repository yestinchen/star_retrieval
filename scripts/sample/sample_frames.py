import pandas as pd
import os

def sample_frames(origin_path, new_path, sample_rate):
  #1. read result.
  df = pd.read_csv(origin_path, names=[
    'frame', 'id', 'left', 'top', 'width', 'height', 'conf', 'class', 'x', 'y', 'z'
  ], index_col=False)
  df = df[df['frame'] % sample_rate == 1]
  # update frame.
  df['frame'] = df['frame'].apply(lambda x: x // sample_rate + 1)
  if not os.path.isdir(os.path.dirname(new_path)):
    os.makedirs(os.path.dirname(new_path))
  # save back.
  df.to_csv(new_path, index=False, header=False)
  pass

def transform_meta(origin_path, new_path, sample_rate):
  sequence_list = list()
  with open(origin_path, 'r') as rf:
    for line in rf.readlines():
      name, arr = line.split(":")
      length, start_frame = tuple(map(lambda x: int(x), arr.split('/')))
      sequence_list.append((name, start_frame, length))
  assert len(sequence_list) > 0, 'oops'
  # compute mapping: sampled_frame_id -> origin_frame_id
  transformed_list = list()
  for name, start_frame, length in sequence_list:
    end_frame = start_frame + length - 1
    new_start_frame = start_frame // sample_rate + 1
    new_end_frame = end_frame // sample_rate + 1
    new_length = new_end_frame - new_start_frame + 1
    transformed_list.append((name, new_start_frame, new_length))
  # save.
  with open(new_path, 'w') as wf:
    for name, start_frame, length in transformed_list:
      wf.write('{}:{}/{}\n'.format(name, length, start_frame))

if __name__ == '__main__':

  # sequences = ['drtest', 'drtrain']
  # sample_rate = 5
  # for seq in sequences:
  #   sample_frames(
  #     '../storage/results/vsim-detrac/raw/{}.txt'.format(seq),
  #     '../storage/results/vsim-detrac-{}/raw/{}.txt'.format(sample_rate, seq),
  #     sample_rate
  #   )
  #   transform_meta(
  #     '../storage/results/vsim-detrac/raw/{}-meta.txt'.format(seq),
  #     '../storage/results/vsim-detrac-{}/raw/{}-meta.txt'.format(sample_rate, seq),
  #     sample_rate
  #   )


  sequences = ['drtest', 'drtrain', 'bdd100kA', 'bdd100kB']
  sample_rates = [5, 10]
  for seq in sequences:
    for sample_rate in sample_rates:
      sample_frames(
      '../storage/results/vsim-all/raw/{}.txt'.format(seq),
      '../storage/results/vsim-all/sample-raw/{}-{}.txt'.format(seq, sample_rate),
      sample_rate
      )
      transform_meta(
        '../storage/results/vsim-all/raw/{}-meta.txt'.format(seq),
        '../storage/results/vsim-all/sample-raw/{}-{}-meta.txt'.format(seq, sample_rate),
        sample_rate
      )