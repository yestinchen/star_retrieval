from vsimsearch.utils import init_bitset
from vsimsearch.proposed2 import ProposedEval

frame_set = set(list(range(3,10)))
print('frames', frame_set)
mask = init_bitset(3)
mask[0]=1
mask[1]=1

eval = ProposedEval()
value = eval.compute_frame_score_dict(frame_set, mask, 3)
print(value)