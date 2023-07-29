from collections import defaultdict
from vsimsearch.topk import TopkHolder
from vsimsearch.utils import compute_if_absent, get_from_multi_level_dict, init_bitset
from vsimsearch.baseline import extract_pattern_graphs
import heapq
import itertools
  

class PartialEntry:
  def __init__(self, id_set, frame_dict):
    self.id_set = id_set
    self.frame_dict = frame_dict
    self.score = len(self.frame_dict)

  def __lt__(self, other):
    # since we are using min-heap, and we would like the highest score on the top
    return -self.score < -other.score

def extract_id_and_frames_dict(frame_pos_list, frames_dict):
  # generate all candidates
  # merge.
  prefix_list_dict = defaultdict(dict)
  for pattern_frame, available_id_lists in frames_dict.items():
    id_pos = frame_pos_list.get(pattern_frame)
    # no matched pattern
    # FIXME: do we need to fix this?
    if id_pos is None:
      continue
    # skip empty frames.
    if available_id_lists is None:
      continue
    for start_id, available_lists in available_id_lists.items():
      # print('frame dict', frames_dict)
      # print('id list', available_id_lists)
      # print('availabel', available_list, id_pos)
      if id_pos == 0:
        # means sid, only one element is guaranteed.
        # filter out.
        prefix_list_dict[start_id][pattern_frame] = available_lists
      else:
        available_id_dict = dict()
        for _l in available_lists:
          _id = _l[id_pos]
          if _id in available_id_dict:
            available_id_dict[_id].append(_l)
          else:
            available_id_dict[_id] = [_l]
        for _id, _list in available_id_dict.items():
          # id_frame_dict
          if pattern_frame in prefix_list_dict[_id]:
            prefix_list_dict[_id][pattern_frame].extend(_list)
          else:
            prefix_list_dict[_id][pattern_frame] = _list
  return prefix_list_dict

def extract_id_and_frames_dict_2(frame_pos_list, frames_dict):
  prefix_list_dict = defaultdict(dict)
  # print('avaiable', frames_dict)
  # import sys
  # sys.exit(0)
  for pattern_frame, available_id_lists in frames_dict.items():
    id_pos = frame_pos_list.get(pattern_frame)
    # not matched pattern
    # FIXME: do we need to fix this?
    if id_pos is None:
      continue
      # skip empty frames.
    if available_id_lists is None:
      continue
    
    # print('list', available_id_lists)
    available_ids = dict()
    for _l in available_id_lists:
      # if len(_l) <= id_pos:
      #   print('l', _l, id_pos,  pattern_frame)
      _ids = _l[id_pos]
      for _id in _ids:
        # print('_id', _id)
        if _id in available_ids:
          available_ids[_id].append(_l)
        else:
          available_ids[_id] = [_l]

    # available_ids = available_id_lists[id_pos]
    for _id, _list in available_ids.items():
      # frame -> matched list?
      prefix_list_dict[_id][pattern_frame] = _list
  return prefix_list_dict


class WorkingWindow:
  def __init__(self, frames_dict, ordered_pattern_frames, metrics, window_id) -> None:
    self.frames_dict = frames_dict
    self.ordered_pattern_frames = ordered_pattern_frames
    self.metrics = metrics
    self.window_id = window_id

    self.ordered_pattern_frames = [dict([(y, z) for y,z in x.items() if y in frames_dict]) \
      for x in ordered_pattern_frames]
    for i in range(len(self.ordered_pattern_frames)-1, -1, -1):
      if len(self.ordered_pattern_frames[i]) == 0:
        del self.ordered_pattern_frames[i]
    # if window_id == 22049:
    #   print('frames', frames_dict)
    # init
    current_matching_objects = ordered_pattern_frames[0]
    # construct the first pattern id.
    prefix_frame_list_dicts = extract_id_and_frames_dict(current_matching_objects, frames_dict)

    self.partial_result_heap = list()
    for start_id, frame_list_dict in prefix_frame_list_dicts.items():
      if len(frame_list_dict) >=1:
        self.partial_result_heap.append(PartialEntry(set([start_id]), frame_list_dict))
    heapq.heapify(self.partial_result_heap)

    self.score = None
  
  def _step(self, score_limit=0):
    '''
    one more step forward
    '''
    # now, always proceed with the highest score.
    entry = heapq.heappop(self.partial_result_heap)
    id_set, frames_dict = entry.id_set, entry.frame_dict
    origin_len = len(id_set)
    # continue with the set
    matching_objects = self.ordered_pattern_frames[origin_len]
    # print('matching',len(id_set), matching_objects, self.ordered_pattern_frames)

    # print('frame dict', frames_dict)
    # import sys
    # sys.exit(-1)

    new_id_dict = extract_id_and_frames_dict_2(matching_objects, frames_dict)
    new_tuples = list()
    # print('step >>>')
    for new_id, frames_dict in new_id_dict.items():
      # frame dict: frame -> matched ordered list
      if new_id not in id_set:
        # create new tuples
        new_set = set(id_set)
        new_set.add(new_id)
        # if self.window_id == 22049:
        #   print('score', len(self.ordered_pattern_frames), new_set, new_id, frames_dict)
        # print('current', new_set, len(frames_dict))
        if len(new_set) == len(self.ordered_pattern_frames):
          # if self.window_id == 22049:
          #   print('score', new_set, len(frames_dict))
          if self.score is None or self.score < len(frames_dict):
            self.score = len(frames_dict)
            # if self.window_id == 39041:
            #   print('score', self.score, frames_dict.keys())
            #   for key, value in frames_dict.items():
            #     print('{}:{}'.format(key, value))
        elif len(frames_dict) > 1 if self.score is None else self.score:
          # print('len', len(frames_dict))
          if len(frames_dict) > score_limit:
            # push back.
            new_tuples.append(PartialEntry(new_set, frames_dict))
    # push all new tuples back.
    for t in new_tuples:
      heapq.heappush(self.partial_result_heap, t)
    # if self.window_id == 22049:
    #   print('heap', self.partial_result_heap[0].score)

  def _current_highest_score(self):
    return self.partial_result_heap[0].score if len(self.partial_result_heap) > 0 else 0

  def compute_score(self, score_limit = 0):
    _metrics_starting_score = self._current_highest_score()
    while len(self.partial_result_heap) > 0 and \
      (self.score is None or self.score < self.partial_result_heap[0].score):
      if self.metrics is not None:
        self.metrics.inc_counter('steps_checked_count')
      self._step(score_limit)
    # stop score
    # _metrics_stop_score = self._current_highest_score()
    # while len(self.partial_result_heap) > 0:
    #   if self.metrics is not None:
    #     self.metrics.inc_counter('steps_pruned_count')
    #   self._step()
    # _metrics_final_stop_score = self._current_highest_score()

    # if self.metrics is not None:
    #   self.metrics.add_entry('score_table', start=_metrics_starting_score,\
    #     stop=_metrics_stop_score, total=_metrics_final_stop_score)

  def compute_score_to(self, stop_score):
    while len(self.partial_result_heap) > 0 and \
      (self.score is None or self.score < self.partial_result_heap[0].score) and \
        self.partial_result_heap[0].score > stop_score:
      if self.metrics is not None:
        self.mertics.inc_counter('steps_checked_count')
      self._step()
  
  def is_terminated(self):
    return self.score >= self.partial_result_heap[0]

class WorkingWindowWithEstimation(WorkingWindow):
  def __init__(self, frames_dict, ordered_pattern_frames, metrics, window_id) -> None:
    super().__init__(frames_dict, ordered_pattern_frames, metrics, window_id)
    self.estimated_score = self._estimate_score()
    # if window_id == 39041:
    #   print('estimated score',self.estimated_score)

  def _estimate_score(self):
    return 0 if len(self.partial_result_heap) == 0 else self.partial_result_heap[0].score
  
  # def process(self, stop):
  #   pass

  def __lt__(self, other):
    return self.estimated_score > other.estimated_score

# ======= proposed matching method ends

class ProposedEvalNoIMD:

  def __init__(self, metrics = None) -> None:
    self.metrics = metrics

  def compute_global_ordered_patterns(self, node_type_dict, unique_patterns, pattern_mapping_dict):
    '''
    Returns:

    ordered_patterns:
      e.g., [[3, 1, 2]], where 3, 1, 2 are object ids in the frame pattern.
    
    condition_pos_mapping:
      e.g., (sid, eid, theta, d) -> [(pattern_idx, pattern_id_pos)], 
     
    global_order_frames_with_pos:
      e.g., [[(1,0),(2,0)], [(1,1),(2,1)]]
        innter list: (pattern_idx, pattern_id_pos);
        outer list: one unique object;
    
    unique_pattern_count:
      e.g., [[1, 2]]. Assume the ordered pattern is [[3,1,2]], and both edges (3,1) and (3,2) share the 
      same theta and d values, thus, there is only one unique edge. To satisfy the whole graph condition, 
      we need at least one object matches 3, and at least two objects match 1 and 2 individually.
    
    unique_patterns:
      e.g., [[(sid, eid, theta, d), ...], ...]. 
    '''
    # print('unique patterns', unique_patterns)
    # print('pattern_mapping_dict', pattern_mapping_dict)
    # global ordered nodes
    id_temporal_dict = defaultdict(list)
    ordered_patterns = list()
    ordered_edge_idxs = list()
    ordered_edge_idx_counts = list()
    condition_pos_mapping = defaultdict(list)
    for pattern_id, unique_pattern in enumerate(unique_patterns):
      # create an ordered list
      ordered_list = list()
      pos_to_unique_edge_mapping = list()
      unique_edge_keeper = dict()
      count_list = list()
      # pos -> unique pos
      # print('unique pattern', unique_pattern)
      for edge, condition in unique_pattern.items():
        sid, eid = edge
        theta, d = condition
        if len(ordered_list) == 0:
          ordered_list.append(sid)
          pos_to_unique_edge_mapping.append(0) # sid does not need any mapping.
          count_list.append(1)
        stype, etype = node_type_dict[sid], node_type_dict[eid]
        generalized_edge = (stype, etype, theta, d)
        if generalized_edge not in unique_edge_keeper:
          new_unique_edge_idx = len(unique_edge_keeper) + 1
          unique_edge_keeper[generalized_edge] = new_unique_edge_idx
          condition_pos_mapping[generalized_edge].append((pattern_id, new_unique_edge_idx))
        unique_pos = unique_edge_keeper[generalized_edge]
        if unique_pos < len(count_list):
          count_list[unique_pos] += 1
        else:
          count_list.append(1)
        # mapping starts from 1, meaning the 1st edge.
        pos_to_unique_edge_mapping.append(unique_pos)
        ordered_list.append(eid)
      ordered_patterns.append(ordered_list)
      ordered_edge_idxs.append(pos_to_unique_edge_mapping)
      ordered_edge_idx_counts.append(count_list)

      # count
      for oid in ordered_list:
        id_temporal_dict[oid].append(pattern_id)


    # aggregate cond_pos_mapping
    squeezed_condition_pos_mapping = dict()
    for edge_info, pattern_pos_list in condition_pos_mapping.items():
      pattern_to_pos_dict = defaultdict(list)
      for pattern_idx, pos_idx in pattern_pos_list:
        pattern_to_pos_dict[pattern_idx].append(pos_idx)
      squeezed_condition_pos_mapping[edge_info] = pattern_to_pos_dict
    
    # print('ordered_patterns', ordered_patterns)
    # print('ordered_edge', ordered_edge_idxs)
    # print('count list', ordered_edge_idx_counts)

    # print('id_temporal_dict', id_temporal_dict)
    # print('condition_pos_mapping', condition_pos_mapping)
    # print('condition_pos_mapping', squeezed_condition_pos_mapping)

    # step 3. compute a global ordering.
    global_order_id_patterns = sorted(id_temporal_dict.items(), key=lambda x: len(x[1]), reverse=True)
    # get dict.
    pattern_id_pos_dict = dict()
    for pid, ordered_pattern in enumerate(ordered_patterns):
      # skip empty frames
      if ordered_pattern is None:
        continue
      id_pos_dict = dict()
      for pos, id in enumerate(ordered_pattern):
        id_pos_dict[id] = pos
      pattern_id_pos_dict[pid] = id_pos_dict

    # print('global order', global_order_id_patterns)
    # print('pattern_id_pos', pattern_id_pos_dict)
    # 
    # print('cond_pos_mapping', condition_pos_mapping)
    # print('squeezed', squeezed_condition_pos_mapping)

    pattern_id_frame_mapping = defaultdict(list)
    for pattern_frame, pattern_id in pattern_mapping_dict.items():
      pattern_id_frame_mapping[pattern_id].append(pattern_frame)

    # print('pid mapping', pattern_id_frame_mapping)

    global_order_frames_with_pos = list()
    for _id, pattern_ids in global_order_id_patterns:
      # global_order_frames_with_pos.append([(frame, frame_id_pos_dict[pid][_id]) for pid in pattern_ids])
      # replace pattern id
      frame_pos_list = list()
      for pid in pattern_ids:
        for frame in pattern_id_frame_mapping[pid]:
          origin_pos = pattern_id_pos_dict[pid][_id]
          unique_pos = ordered_edge_idxs[pid][origin_pos]
          frame_pos_list.append((frame, unique_pos))
      global_order_frames_with_pos.append(frame_pos_list)
    
    # transform to [dict(frame_id -> pos)]
    global_order_frames_with_pos = [dict(x) for x in global_order_frames_with_pos]

    # print('global ordere frames', global_order_frames_with_pos)
    # print('condition_pos_mapping', condition_pos_mapping)

    unique_patterns = dict()
    for edge, pattern_pos_list in condition_pos_mapping.items():
      for pattern_idx, pos in pattern_pos_list:
        up = compute_if_absent(unique_patterns, pattern_idx, dict)
        up[pos] = edge
    # print('unique patterns', unique_patterns)

    # print('p', unique_patterns, global_order_id_patterns)
    # print('global ordered frames', global_order_frames_with_pos)
    # import sys
    # sys.exit(0)

    # frame_edge_num_count_list = defaultdict(dict)
    # for _dict in global_order_frames_with_pos:
    #   for _pattern_id, _pos in _dict.items():
    #     if _pos in frame_edge_num_count_list[_pattern_id]:
    #       frame_edge_num_count_list[_pattern_id][_pos] += 1
    #     else:
    #       frame_edge_num_count_list[_pattern_id][_pos] = 1
    # print('frame_edge', frame_edge_num_count_list)

    frame_edge_num_count_list = defaultdict(dict)
    for _id, pattern_ids in global_order_id_patterns:
      for pid in pattern_ids:
        origin_pos = pattern_id_pos_dict[pid][_id]
        unique_pos = ordered_edge_idxs[pid][origin_pos]
        if unique_pos in frame_edge_num_count_list[pid]:
          frame_edge_num_count_list[pid][unique_pos] += 1
        else:
          frame_edge_num_count_list[pid][unique_pos] = 1
    # print('fr', frame_edge_num_count_list)

    # import sys
    # sys.exit(0)
    return ordered_patterns, condition_pos_mapping, global_order_frames_with_pos,\
       ordered_edge_idx_counts, unique_patterns, frame_edge_num_count_list

  def collect_match_results_from_index(self, index, generalized_edges_with_pos_dict,\
     ordered_patterns, unique_count_lists, unique_patterns, edge_count_dict):

    if self.metrics is not None:
      self.metrics.start_timer('pattern_matching/edge_retrieval')
    # retrieve from index
    index_per_frame = dict()
    for pattern_edge in generalized_edges_with_pos_dict.keys():
      stype, etype, theta, d = pattern_edge
      # retrieve
      edge_frames_dict = get_from_multi_level_dict(index, [stype, etype, (theta,d)])
      if edge_frames_dict is None:
        continue
      for edge, frames in edge_frames_dict.items():
        for frame in frames:
          if self.metrics is not None:
            self.metrics.inc_counter('edge_retrieve_count')
          index_for_this_frame = compute_if_absent(index_per_frame, frame, dict)
          sid_type_index = compute_if_absent(index_for_this_frame, stype, dict)
          eid_type_index = compute_if_absent(sid_type_index, etype, dict)
          sid_eid_list = compute_if_absent(eid_type_index, (theta, d), list)
          sid_eid_list.append(edge)
    if self.metrics is not None:
      self.metrics.end_timer('pattern_matching/edge_retrieval')

    if self.metrics is not None:
      self.metrics.start_timer('pattern_matching/frame_matching')
    frame_matched_arr_dict = dict()
    # compute frame matching.
    pattern_id_count = dict()
    for idx, count_list in enumerate(unique_count_lists):
      pattern_id_count[idx] = len(count_list)

    # print('edge count', edge_count_dict)
    # print('unique patterns', unique_patterns)
    for frame, current_frame_index in index_per_frame.items():
      # print('current frame idx', current_frame_index)
      pattern_matching_result_dict = dict()
      # enumerate patterns
      for pattern_idx, unique_pattern in unique_patterns.items():
        num_count_dict = edge_count_dict[pattern_idx]
        # print('num dict', num_count_dict, pattern_idx+1, edge_count_dict)
        dict_per_unique_pattern = dict()
        for pos, pattern_edge in unique_pattern.items():
          # retrieve.
          stype, etype, theta, d = pattern_edge
          sid_eid_list = get_from_multi_level_dict(current_frame_index, [stype, etype, (theta, d)])
          if sid_eid_list is None:
            continue
          # put.
          for sid, eid in sid_eid_list:
            matched_result_with_same_sid = compute_if_absent(dict_per_unique_pattern, sid, dict)

            matched_result_at_pos = compute_if_absent(matched_result_with_same_sid, pos, list)
            matched_result_at_pos.append(eid)
        # prune
        for sid in list(dict_per_unique_pattern.keys()):
          if len(dict_per_unique_pattern[sid]) < len(unique_pattern):
            # missing matched edges.
            del dict_per_unique_pattern[sid]
          else:
            # append sid to first pos
            dict_per_unique_pattern[sid][0] = [sid]
        if len(dict_per_unique_pattern) > 0:
          # generate all patterns.
          transformed_dict = dict()
          # all_lists = []
          for sid, sub_dict in dict_per_unique_pattern.items():
            pattern_lists = []
            # init.
            for comb in itertools.combinations(sub_dict[0], num_count_dict[0]):
              pattern_lists.append([comb])
            for k in sorted(sub_dict.keys()):
              if k == 0:
                continue
              # print('k', k, num_count_dict)
              new_lists = []
              for comb in itertools.combinations(sub_dict[k], num_count_dict[k]):
                for _l in pattern_lists:
                  new_lists.append([*_l, comb])
              pattern_lists = new_lists
            # add this result.
            transformed_dict[sid] = pattern_lists
            # all_lists.append(pattern_lists)
          pattern_matching_result_dict[pattern_idx] = transformed_dict
          # pattern_matching_result_dict[pattern_idx] = all_lists
      if len(pattern_matching_result_dict) > 0:
        frame_matched_arr_dict[frame] = pattern_matching_result_dict
    if self.metrics is not None:
      self.metrics.end_timer('pattern_matching/frame_matching')
    
    return frame_matched_arr_dict

  def retrieve_data_from_proposed_index(self, index, pattern):
    pattern_node_type_dict, unique_patterns, pattern_mapping_dict = extract_pattern_graphs(pattern)
    
    if self.metrics is not None:
      self.metrics.start_timer('pattern_transform')
    # 0. get ordered patterns.
    ordered_patterns, condition_pos_mapping, global_ordered_frames, unique_count_lists, unique_patterns = \
      self.compute_global_ordered_patterns(pattern_node_type_dict, unique_patterns, pattern_mapping_dict)

    # retrieve from index
    index_per_frame = dict()
    for pattern_edge in condition_pos_mapping.keys():
      stype, etype, theta, d = pattern_edge
      # retrieve
      edge_frames_dict = get_from_multi_level_dict(index, [stype, etype, (theta,d)])
      if edge_frames_dict is None:
        continue
      for edge, frames in edge_frames_dict.items():
        for frame in frames:
          if self.metrics is not None:
            self.metrics.inc_counter('edge_retrieve_count')
          index_for_this_frame = compute_if_absent(index_per_frame, frame, dict)
          sid_type_index = compute_if_absent(index_for_this_frame, stype, dict)
          eid_type_index = compute_if_absent(sid_type_index, etype, dict)
          sid_eid_list = compute_if_absent(eid_type_index, (theta, d), list)
          sid_eid_list.append(edge)

  def retrieve_data_from_edgeonly_index(self, index, pattern):
    pattern_node_type_dict, unique_patterns, pattern_mapping_dict = extract_pattern_graphs(pattern)
    
    if self.metrics is not None:
      self.metrics.start_timer('pattern_transform')
    # 0. get ordered patterns.
    ordered_patterns, condition_pos_mapping, global_ordered_frames, unique_count_lists, unique_patterns = \
      self.compute_global_ordered_patterns(pattern_node_type_dict, unique_patterns, pattern_mapping_dict)

    # retrieve from index
    index_per_frame = dict()
    for pattern_edge in condition_pos_mapping.keys():
      stype, etype, theta, d = pattern_edge
      # retrieve
      index_dict = get_from_multi_level_dict(index, [(theta,d)])
      if index_dict is None:
        continue
      edge_frames_dict = dict()
      for (sid, eid, i_stype, i_etype), frames in index_dict.items():
        if i_stype == stype and i_etype == etype:
          edge_frames_dict[(sid, eid)] = frame
      for edge, frames in edge_frames_dict.items():
        for frame in frames:
          if self.metrics is not None:
            self.metrics.inc_counter('edge_retrieve_count')
          index_for_this_frame = compute_if_absent(index_per_frame, frame, dict)
          sid_type_index = compute_if_absent(index_for_this_frame, stype, dict)
          eid_type_index = compute_if_absent(sid_type_index, etype, dict)
          sid_eid_list = compute_if_absent(eid_type_index, (theta, d), list)
          sid_eid_list.append(edge)
  
  def retrieve_data_from_vertexonly_index(self, index, pattern):
    pattern_node_type_dict, unique_patterns, pattern_mapping_dict = extract_pattern_graphs(pattern)
    
    if self.metrics is not None:
      self.metrics.start_timer('pattern_transform')
    # 0. get ordered patterns.
    ordered_patterns, condition_pos_mapping, global_ordered_frames, unique_count_lists, unique_patterns = \
      self.compute_global_ordered_patterns(pattern_node_type_dict, unique_patterns, pattern_mapping_dict)

    # retrieve from index
    index_per_frame = dict()
    for pattern_edge in condition_pos_mapping.keys():
      stype, etype, theta, d = pattern_edge
      # retrieve
      index_dict = get_from_multi_level_dict(index, [(theta,d)])
      if index_dict is None:
        continue
      edge_frames_dict = dict()
      for (sid, eid, i_theta, i_d), frames in index_dict.items():
        # clear.
        if i_theta == theta and i_d == d:
          # collect
          edge_frames_dict[(sid, eid)] = frames
      for edge, frames in edge_frames_dict.items():
        for frame in frames:
          if self.metrics is not None:
            self.metrics.inc_counter('edge_retrieve_count')
          index_for_this_frame = compute_if_absent(index_per_frame, frame, dict)
          sid_type_index = compute_if_absent(index_for_this_frame, stype, dict)
          eid_type_index = compute_if_absent(sid_type_index, etype, dict)
          sid_eid_list = compute_if_absent(eid_type_index, (theta, d), list)
          sid_eid_list.append(edge)

  def query(self, index, temporal_pattern, topk, sequential=False):
    pattern_node_type_dict, unique_patterns, pattern_mapping_dict = extract_pattern_graphs(temporal_pattern)
    
    if self.metrics is not None:
      self.metrics.start_timer('pattern_transform')
    # 0. get ordered patterns.
    ordered_patterns, condition_pos_mapping, global_ordered_frames, unique_count_lists, unique_patterns, edge_count_dict = \
      self.compute_global_ordered_patterns(pattern_node_type_dict, unique_patterns, pattern_mapping_dict)

    if self.metrics is not None:
      self.metrics.end_timer('pattern_transform')


    if self.metrics is not None:
      self.metrics.start_timer('pattern_matching')
    # 1. retrieve edges + for each frame, obtain a list of matched objects.
    frame_match_array_dict = self.collect_match_results_from_index(index, \
        condition_pos_mapping, ordered_patterns, unique_count_lists, unique_patterns, edge_count_dict)
    if self.metrics is not None:
      self.metrics.end_timer('pattern_matching')
    # 3. prune + rank frames according to estimated scores.
    # for k, v in frame_match_array_dict.items():
    #   print('k', k, v)
    #   import sys
    #   sys.exit(0)
    # 4.

    # let's do it
    if self.metrics is not None:
      self.metrics.start_timer('temporal_matching')
    if sequential:
      res = self.sequential_evaluate(temporal_pattern, \
        frame_match_array_dict, global_ordered_frames, ordered_patterns, pattern_mapping_dict, topk)
    else:
      res = self.estimated_evaluate(frame_match_array_dict, global_ordered_frames, \
          ordered_patterns, pattern_mapping_dict, temporal_pattern.length, topk)
    if self.metrics is not None:
      self.metrics.end_timer('temporal_matching')
    return res

  def sequential_evaluate(self, temporal_pattern, \
      frame_match_array_dict, global_order_frames, ordered_patterns, pattern_mapping_dict, topk):
    if len(frame_match_array_dict) == 0:
      return []
    all_frames = frame_match_array_dict.keys()
    window_size = temporal_pattern.length
    start_frame = max(1, min(all_frames))
    end_frame = max(all_frames) - window_size + 1 # include the start frame.
    topk_holder = TopkHolder(topk)
    
    working_windows = dict()
    if self.metrics is not None:
      self.metrics.start_timer('temporal_matching/window_prepare')
    # init windows.
    for window_start in range(start_frame, end_frame + 1):
      # if window_start != 51000:
      #   continue
      # construct the frame id.
      matched_result_per_frame = self.collect_matched_result_per_frame(window_start,\
         window_size, frame_match_array_dict, ordered_patterns, pattern_mapping_dict)
      if len(matched_result_per_frame) == 0:
        if self.metrics is not None:
          self.metrics.inc_counter('window_skipped')
      else:
        if self.metrics is not None:
          self.metrics.inc_counter('window_collected')
        ww = WorkingWindow(matched_result_per_frame, global_order_frames, self.metrics, window_start)
        working_windows[window_start] = ww
    if self.metrics is not None:
      self.metrics.end_timer('temporal_matching/window_prepare')

    if self.metrics is not None:
      self.metrics.start_timer('temporal_matching/score-computation')
    for window_start, ww in working_windows.items():
      # print(matched_result_per_frame)
      # perform matching.
      # TODO: compute matching score based on mapping_dict
      # FIXME: 
      last_score = topk_holder.last_score()
      ww.compute_score(0 if last_score is None else 0)
      score = ww.score
      # print('score for ', window_start, score)
      if score is not None:
        topk_holder.update(score, window_start)
    if self.metrics is not None:
      self.metrics.end_timer('temporal_matching/score-computation')
    return topk_holder.cache_list

  def estimated_evaluate(self, frame_match_array_dict, global_order_frames,\
      ordered_patterns, pattern_mapping_dict, pattern_length, topk):
    if len(frame_match_array_dict) == 0:
      return []
    all_frames = frame_match_array_dict.keys()
    window_size = pattern_length
    start_frame = max(1, min(all_frames))
    end_frame = max(all_frames) - window_size + 1 # include the start frame.
    topk_holder = TopkHolder(topk)

    working_windows = list()
    if self.metrics is not None:
      self.metrics.start_timer('temporal_matching/window_prepare')
    # init windows.
    for window_start in range(start_frame, end_frame + 1):
      matched_result_per_frame = self.collect_matched_result_per_frame(window_start,\
        window_size, frame_match_array_dict, ordered_patterns, pattern_mapping_dict)
      # construct the frame id.
      if len(matched_result_per_frame) == 0:
        if self.metrics is not None:
          self.metrics.inc_counter('window_skipped')
      else:
        if self.metrics is not None:
          self.metrics.inc_counter('window_collected')
        wwe = WorkingWindowWithEstimation(matched_result_per_frame, global_order_frames, \
          self.metrics, window_start)
        working_windows.append(wwe)
    
    if len(working_windows) == 0:
      return []

    # heapify
    heapq.heapify(working_windows)
    if self.metrics is not None:
      self.metrics.end_timer('temporal_matching/window_prepare')

    if self.metrics is not None:
      self.metrics.inc_counter('window_total', len(working_windows))
      # first score
      self.metrics.record_txt('window score range', \
        (working_windows[0].estimated_score, working_windows[-1].estimated_score))
    if self.metrics is not None:
      self.metrics.start_timer('temporal_matching/score-computation')
    # scheduling.
    while len(working_windows) > 0 and \
      (topk_holder.last_score() is None or \
      topk_holder.last_score() < working_windows[0].estimated_score):
      if self.metrics is not None:
        self.metrics.inc_counter('window_processed')

      wwe = heapq.heappop(working_windows)

      if self.metrics is not None:
        # record stop pos
        self.metrics.record_txt('last_estiamted_window_score', wwe.estimated_score)

      last_score = topk_holder.last_score()
      wwe.compute_score(0 if last_score is None else last_score)
      score = wwe.score
      if score is not None:
        topk_holder.update(score, wwe.window_id)

    if self.metrics is not None:
      self.metrics.end_timer('temporal_matching/score-computation')

    return topk_holder.cache_list


  def collect_matches_per_frame(self, frame_edge_dict):
    frame_match_array_dict = dict()
    for frame, edge_list in frame_edge_dict.items():
      # edge list: 
      # format: start_id -> end ids
      edge_se_dict = dict()
      for sid, eid, pattern_frame_pos_list in edge_list:
        for pattern_frame, pos in pattern_frame_pos_list:
          # here we need to retrieve the position.
          pattern_frame_dict = compute_if_absent(edge_se_dict, pattern_frame, dict)
          # we may have multiple sids
          sid_dict = compute_if_absent(pattern_frame_dict, sid, dict)
          pos_dict = compute_if_absent(sid_dict, pos, list)
          pos_dict.append(eid)
      frame_match_array_dict[frame] = edge_se_dict
    return frame_match_array_dict

  def collect_matched_result_per_frame(self, start_frame, window_size,\
     frame_match_array_dict, ordered_patterns, pattern_mapping_dict):
    matched_result_per_frame = dict()
    for frame_i_in_window in range(window_size):
      to_match_frame = start_frame + frame_i_in_window
      pattern_frame = frame_i_in_window + 1
      current_ordered_pattern_id = pattern_mapping_dict.get(pattern_frame)
      if current_ordered_pattern_id is None:
        continue

      # [frame_i_in_window]
      
      # test if there is any matching for the frame
      matchings_for_the_frame = frame_match_array_dict.get(to_match_frame)
      if matchings_for_the_frame is None:
        continue
      if matchings_for_the_frame.get(current_ordered_pattern_id) is None:
        continue
      processing_edge_dict = matchings_for_the_frame.get(current_ordered_pattern_id)
      # skip empty pattern groups
      if processing_edge_dict is None:
        continue
     
      matched_result_per_frame[pattern_frame] = processing_edge_dict
    return matched_result_per_frame