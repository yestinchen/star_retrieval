# serves as the main entry 
import argparse
import pickle
from vsimsearch.metrics import Metrics
from vsimsearch.apps.common import add_args_for_discretize_func, index_types, discretize_func_from_args
from vsimsearch.proposed_new_we import ProposedEval
from vsimsearch.baseline import BaselineWithProposedIndex
import time

from vsimsearch.proposed_no_imd import ProposedEvalNoIMD

def prepare_parser():
  parser = argparse.ArgumentParser(description='Main app for the experiment')
  # for index
  parser.add_argument('--index_path')
  # for pattern
  parser.add_argument('--pattern_path')
  parser.add_argument('--k', type=int)
  parser.add_argument('--method', choices=['baseline', 'proposed', 'proposed_seq', 'noimd'])
  parser.add_argument('--index_type', type=int, choices=[1,2])
  return parser

def execute_query(args):
  # read
  index, pattern = None, None
  with open(args.index_path, 'rb') as index_f:
    index = pickle.load(index_f)
  with open(args.pattern_path, 'rb') as pattern_f:
    pattern = pickle.load(pattern_f)
  
  # print(pattern.nodes)
  # print(pattern.edges)
  # perform.

  eval_obj = None
  metrics = Metrics()
  if args.method == 'baseline':
    eval_obj = BaselineWithProposedIndex(metrics)
  elif args.method == 'noimd':
    eval_obj = ProposedEvalNoIMD(metrics)
  else:
    eval_obj = ProposedEval(metrics)

  start_time = time.process_time()
  result = None
  if args.index_type == 1:
    if args.method == 'proposed_seq':
      result = eval_obj.query(index, pattern, args.k, sequential=True)
    else:
      result = eval_obj.query(index, pattern, args.k)
  elif args.index_type == 2:
    if args.method == 'proposed_seq':
      result = eval_obj.query_with_index_per_frame(index, pattern, args.k, sequential=True)
    else:
      result = eval_obj.query_with_index_per_frame(index, pattern, args.k)
  else:
    assert False, 'unrecognized index type: '+ args.index_type
  end_time = time.process_time()
  # print(result)
  print(sorted(result, reverse=True))
  print('time used', end_time - start_time)
  
  metrics.print()

if __name__ == '__main__':
  parser = prepare_parser()  
  args = parser.parse_args()
  execute_query(args)
  
