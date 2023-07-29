import argparse
import pickle
from vsimsearch.metrics import Metrics
from vsimsearch.baseline import BaselineWithProposedIndex
import time

def prepare_parser():
  parser = argparse.ArgumentParser(description='Main app for the experiment')
  # for index
  parser.add_argument('--index_path')
  # for pattern
  parser.add_argument('--pattern_path')
  parser.add_argument('--k', type=int)
  parser.add_argument('--index_type', type=int, choices=[1,2])
  return parser

def get_window_scores(args):
  # read
  index, pattern = None, None
  with open(args.index_path, 'rb') as index_f:
    index = pickle.load(index_f)
  with open(args.pattern_path, 'rb') as pattern_f:
    pattern = pickle.load(pattern_f)

  metrics = Metrics()
  eval_obj = BaselineWithProposedIndex(metrics, True)

  start_time = time.process_time()
  result = None
  if args.index_type == 1:
    result = eval_obj.query(index, pattern, args.k)
  elif args.index_type == 2:
    result = eval_obj.query_with_index_per_frame(index, pattern, args.k)
  else:
    assert False, 'unrecognized index type: '+ args.index_type
  end_time = time.process_time()
  print(result)
  print('time used', end_time - start_time)

  metrics.print()

  window_score_dict = eval_obj.all_window_scores_dict
  # get k-th result
  k_score, window_id = result[-1]

  # 1. get # of windows >= k_score
  satisfied_window_count = 0
  for window, score in window_score_dict.items():
    if score >= k_score:
      satisfied_window_count += 1
  total_window_count = len(window_score_dict)
  print('k: {}, selectivity: {}/{}, ratio: {}'.format(args.k , satisfied_window_count, \
     total_window_count, satisfied_window_count/total_window_count))
  
  score_dict = eval_obj.computed_score_count_dict
  count = score_dict[k_score]
  print('topk score object set count: {}, #obj/window ratio: {}'.format(count, count/satisfied_window_count))


if __name__ == '__main__':
  parser = prepare_parser()
  args = parser.parse_args()
  get_window_scores(args)