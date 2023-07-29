import pickle
import sys

from vsimsearch.io import _load_from_cache, _read_nodes_from_mot_result_multi_class

def read_pattern(path):
  with open(path, 'rb') as bf:
    pattern = pickle.load(bf)
  print('len:', pattern.length)
  print('nodes\n', pattern.nodes)
  print('edges\n', pattern.edges)

def read_file_with_df(path, df_func):
  path = sys.argv[1]
  with open(path, 'rb') as bf:
    index = pickle.load(bf)
  print('what')

if __name__ == '__main__':
  # read_file_with_df(path, df_func=)
  # path = sys.argv[1]
  # path = '../storage/results/vsim/pattern/traffic2-df5-1_2_3-1_10.pkl'
  # path = '../storage/results/vsim/result-pattern/traffic1-df5-14641_14642_14660-39041_39050.pkl'
  # path = '../storage/results/vsim/pattern-builder/patterns-traffic1/4-15-5/df5-1-36477_36491-13598_13626_13669_13684.pkl'
  # path = '../storage/results/vsim/pattern-builder/patterns-traffic1/4-10-5/df5-2-20543_20552-7981_7994_7995_7941.pkl'
  # path = '../storage/results/vsim-all/multi-pattern-builder2/patterns-bdd100kA/4-10-20/df6-0-44556_44565-23739_23745_23738_23742.pkl'
  # read_pattern(path)

  path = '../storage/results/vsim-all/multi-raw/bdd100kA.txt'
  pdf = _read_nodes_from_mot_result_multi_class(path)
  print(pdf)
  pass