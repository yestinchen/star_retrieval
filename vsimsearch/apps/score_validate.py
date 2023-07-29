import pickle
from vsimsearch.io import read_nodes_from_mot_result, read_nodes_from_mot_result_multi_class
from vsimsearch.apps.common import discretize_func_from_args
from vsimsearch.graph import extract_pattern_graph
import pandas as pd

def produce_score(pattern:pd.DataFrame, result:pd.DataFrame):
  # drop d column
  pattern.drop(columns=['d'], inplace=True)
  result.drop(columlns=['d'], inplace=True)

  # get candidates
  sid = pattern['sid'].unique()
  eids = pattern['eid'].unique()
  
  result_sid = result['sid'].unique()
  result_eids = result['eid'].unique()


  
  pass

def produce_score_with_mapping(pattern, result, mapping):
  sid = pattern['sid'].unique()[0]
  result_sid = result['sid'].unique()[0]
  score = 0
  for frame in pattern['frame'].unique():
    pf = pattern[(pattern['frame'] == frame)]
    rf = result[(result['frame'] == frame)]
    matched=True
    for pid, vid in mapping.items():
      p_entry = pf.loc[(pf['sid'] == sid) & (pf['eid'] == pid)].iloc[0]
      r_entry = rf.loc[(rf['sid'] == result_sid) & (rf['eid'] == vid)].iloc[0]
      if p_entry['theta'] != r_entry['theta'] or p_entry['d_ratio'] != r_entry['d_ratio']:
        matched = False
    if matched:
      score += 1
  return score

if __name__ == '__main__':
  pattern_path = '../storage/results/vsim/pattern-builder/patterns-traffic2/5-10-5/df5-2-359_368-90_34_62_98_93.pkl'
  result_path = '../storage/results/vsim/pattern/traffic2-df5-14083_14058_14065_14070_14075-51000_51009.pkl'

  with open(pattern_path, 'rb') as bf:
    pattern = pickle.load(bf)

  print(pattern.edges)

  with open(result_path, 'rb') as bf:
    result_pattern = pickle.load(bf)

  print(result_pattern.edges)

  mapping=dict([
    # (62, 14083), # x
    (34, 14058), # 0
    (98, 14075), # 2
    (93, 14070), # 3
    (90, 14065) # 3
  ])

  score = produce_score_with_mapping(pattern.edges, result_pattern.edges, mapping)
  print('score', score)