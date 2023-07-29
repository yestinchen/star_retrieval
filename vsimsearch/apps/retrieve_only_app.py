# only perform the retrieve part.
import argparse
import pickle
from vsimsearch.metrics import Metrics
from vsimsearch.apps.common import add_args_for_discretize_func, index_types, discretize_func_from_args
from vsimsearch.proposed_new_we import ProposedEval
from vsimsearch.baseline import BaselineWithProposedIndex
import time

def prepare_parser():
  parser = argparse.ArgumentParser(description='Retrieve app for the experiment')
  # for index
  parser.add_argument('--index_path')
  # for pattern
  parser.add_argument('--pattern_path')
  parser.add_argument('--k', type=int)
  parser.add_argument('--method', choices=['baseline', 'proposed', 'proposed_seq'])
  parser.add_argument('--index_type', type=int, choices=[1,3,4])
  return parser


def execute_retrieve(args):

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
  else:
    eval_obj = ProposedEval(metrics)

  start_time = time.process_time()
  result = None
  if args.index_type == 1:
    result = eval_obj.retrieve_data_from_proposed_index(index, pattern)
  elif args.index_type == 3:
    result = eval_obj.retrieve_data_from_vertexonly_index(index, pattern)
  elif args.index_type == 4:
    result = eval_obj.retrieve_data_from_edgeonly_index(index, pattern)
  else:
    assert False, 'unrecognized index type: '+ args.index_type
  end_time = time.process_time()
  print(result)
  print('time used', end_time - start_time)
  
  metrics.print()


if __name__ == '__main__':
  parser = prepare_parser()
  args = parser.parse_args()
  execute_retrieve(args)
