
# the general procedure of baseline:
# 1. prune 

from collections import defaultdict
from vsimsearch.graph import extract_pattern_graph
from vsimsearch.topk import TopkHolder
from vsimsearch.utils import compute_if_absent, get_from_multi_level_dict
from vsimsearch.indexing import ProposedIndexPerFrame


def extract_pattern_graphs(temporal_pattern):
  '''
  Returns (node_label_dict, unique_patterns, mapping_dict)

  node_label_dict:
    node_id -> node_type

  unique_patterns: list of 
    (sid, eid) -> (theta, d)

  mapping_dict:
    frame id -> unique_pattern_id
  '''
  nodes, edges = temporal_pattern.nodes, temporal_pattern.edges
  # get obj type
  id_sub_table = nodes.groupby('id').first()
  node_label_dict = dict()
  for _id, row in id_sub_table.iterrows():
    obj_id = int(_id)
    node_label_dict[obj_id] = int(row['class'])
  
  # edge label dict: (u, v) -> (theta, d)
  edge_label_dicts = defaultdict(dict)
  # list of patterns, len(edge_label_dicts) = len(edges['frames'].unique())
  for _, edge in edges.iterrows():
    sid, eid, theta, d, frame = int(edge['sid']), int(edge['eid']), \
      edge['theta'], edge['d_ratio'], int(edge['frame'])
    edge_label_dicts[frame][(sid, eid)] = (theta, d)
  
  unique_patterns, mapping_dict = _compute_unique_pattern_graphs(edge_label_dicts)
  # unique_patterns, mapping_dict = _compute_unique_pattern_graphs_dummy(edge_label_dicts)

  return node_label_dict, unique_patterns, mapping_dict

def _compute_unique_pattern_graphs_dummy(all_pattern_graphs):
  unique_patterns = list()
  mapping_dict = dict()
  for frame, unique_pattern in all_pattern_graphs.items():
    mapping_dict[frame] = len(unique_patterns)
    unique_patterns.append(unique_pattern)
  return unique_patterns, mapping_dict


def _compute_unique_pattern_graphs(all_pattern_graphs):
  '''
  Returns: (unique_patterns, mapping_dict)

  unique_patterns: list of 
    (sid, eid) -> (theta, d)

  mapping_dict:
    frame id -> unique_pattern_id
  '''

  def is_the_same_pattern_graph(graph1, graph2):
    # graph: (sid, eid) -> (theta, d)
    len_euqal = len(graph1) == len(graph2)
    if not len_euqal:
      return False
    for edge, condition in graph1.items():
      if not condition == graph2.get(edge):
        return False
    return True

  # compact:
  unique_pattern_graphs = list()

  last_pattern_id = None
  pattern_unique_id_dict = dict()
  for frame, current_pattern in all_pattern_graphs.items():
    matched_pattern_id = None
    if last_pattern_id is not None:
      # check if still equals
      if is_the_same_pattern_graph(unique_pattern_graphs[last_pattern_id], current_pattern):
        matched_pattern_id = last_pattern_id
    if matched_pattern_id is None:
      # find a pattern equal to this
      for pattern_id, unique_pattern_graph in enumerate(unique_pattern_graphs):
        if is_the_same_pattern_graph(unique_pattern_graph, current_pattern):
          # record this
          matched_pattern_id = pattern_id
    if matched_pattern_id is None:
      # append
      matched_pattern_id = len(unique_pattern_graphs)
      unique_pattern_graphs.append(current_pattern)
    pattern_unique_id_dict[frame] = matched_pattern_id
    last_pattern_id = matched_pattern_id
  return unique_pattern_graphs, pattern_unique_id_dict
  
class BaselineWithProposedIndex():

  def __init__(self, metrics=None, keep_all_windows=False):
    self.metrics = metrics
    self.all_window_scores_dict = dict() if keep_all_windows else None
    self.computed_score_count_dict = defaultdict(lambda:0) if keep_all_windows else None

  def restruct_patterns(self, node_label_dict, unique_patterns):
    converted_patterns = list()
    for unique_pattern in unique_patterns:
      # for each
      # 1. 
      converted_pattern = defaultdict(list)
      for (sid, eid), (theta, d) in unique_pattern.items():
        stype, etype = node_label_dict[sid], node_label_dict[eid]
        converted_pattern[(stype, etype, theta, d)].append((sid, eid))
      converted_patterns.append(converted_pattern)
    return converted_patterns

  def query_with_index_per_frame(self, index, pattern, topk):
    # index on edges.
    # extract edges
    node_label_dict, unique_patterns, mapping_dict = extract_pattern_graphs(pattern)
    # print('node dict', node_label_dict)
    # print('unique patterns', len(unique_patterns), unique_patterns)
    # print('mapping dict', mapping_dict)

    # node_label_dict: node -> label
    # unique_pattern: (sid, eid) -> (theta, d)
    converted_patterns = self.restruct_patterns(node_label_dict, unique_patterns)
    # convert to:
    # list of (stype, etype, theta, d) -> [(sid, eid), ...]
    
    # 
    # print('converted patterns', converted_patterns)
    # collect matching for each frame.
    matching_result_dict = dict()
    for frame, current_frame_index in index.items():
      # print('processing frame', frame, current_frame_index)
      pattern_matching_result_dict = dict()
      for pattern_id, unique_pattern in enumerate(converted_patterns):
        matching_results = self.test_match(current_frame_index, unique_pattern)
        if len(matching_results) > 0:
          pattern_matching_result_dict[pattern_id]= matching_results
      # only keep frames with at least one matched pattern.
      # search
      # print('matching for frame', frame, matching_result)
      if len(pattern_matching_result_dict) > 0:
        matching_result_dict[frame] = pattern_matching_result_dict

    return self.eval_window_scores(matching_result_dict, mapping_dict, pattern.length, topk)
    # index: stype -> etype -> theta, d -> sid, eid, -> frame_list
    # for each frame.
    # print('matching result ', matching_result_dict)

  def retrieve_data_from_proposed_index(self, index, pattern):
    node_label_dict, unique_patterns, mapping_dict = extract_pattern_graphs(pattern)
    converted_patterns = self.restruct_patterns(node_label_dict, unique_patterns)
    index_per_frame = dict()
    for pattern_id, converted_pattern in enumerate(converted_patterns):
      for pattern_edge in converted_pattern:
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
    node_label_dict, unique_patterns, mapping_dict = extract_pattern_graphs(pattern)
    converted_patterns = self.restruct_patterns(node_label_dict, unique_patterns)
    index_per_frame = dict()
    for pattern_id, converted_pattern in enumerate(converted_patterns):
      for pattern_edge in converted_pattern:
        stype, etype, theta, d = pattern_edge
        # retrieve
        tuple_frame_dict = get_from_multi_level_dict(index, [(theta,d)])
        # clear tuple.
        if tuple_frame_dict is None:
          continue
        edge_frames_dict = dict()
        for (sid, eid, sid_type, eid_type), frames in tuple_frame_dict.items():
          # clear.
          if sid_type == stype and eid_type == eid_type:
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

  def retrieve_data_from_vertexonly_index(self, index, pattern):
    node_label_dict, unique_patterns, mapping_dict = extract_pattern_graphs(pattern)
    converted_patterns = self.restruct_patterns(node_label_dict, unique_patterns)
    index_per_frame = dict()
    for pattern_id, converted_pattern in enumerate(converted_patterns):
      for pattern_edge in converted_pattern:
        stype, etype, theta, d = pattern_edge
        # retrieve
        tuple_frame_dict = get_from_multi_level_dict(index, [(stype,etype)])
        # clear tuple.
        if tuple_frame_dict is None:
          continue
        edge_frames_dict = dict()
        for (sid, eid, i_theta, i_d), frames in tuple_frame_dict.items():
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

  def query(self, index, pattern, topk):


    if self.metrics is not None:
      self.metrics.start_timer('pattern_transform')
    # index on edges.
    # extract edges
    node_label_dict, unique_patterns, mapping_dict = extract_pattern_graphs(pattern)
    # print('node dict', node_label_dict)
    # print('unique patterns', len(unique_patterns), unique_patterns)
    # print('mapping dict', mapping_dict)

    # node_label_dict: node -> label
    # unique_pattern: (sid, eid) -> (theta, d)
    converted_patterns = self.restruct_patterns(node_label_dict, unique_patterns)
    if self.metrics is not None:
      self.metrics.end_timer('pattern_transform')
    # convert to:
    # list of (stype, etype, theta, d) -> [(sid, eid), ...]
    
    if self.metrics is not None:
      self.metrics.start_timer('pattern_matching/edge_retrieval')
    # retrieve from index
    index_per_frame = dict()
    for pattern_id, converted_pattern in enumerate(converted_patterns):
      for pattern_edge in converted_pattern:
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
    # 
    # print('converted patterns', converted_patterns)
    # collect matching for each frame.
    matching_result_dict = dict()
    for frame, current_frame_index in index_per_frame.items():
      # if frame == 51000:
      #   print('current index', current_frame_index)
      # print('processing frame', frame, current_frame_index)
      pattern_matching_result_dict = dict()
      for pattern_id, unique_pattern in enumerate(converted_patterns):
        matching_results = self.test_match(frame, current_frame_index, unique_pattern)
        # if frame == 51000:
        #   print('matching result', matching_results, pattern_id)
        if len(matching_results) > 0:
          pattern_matching_result_dict[pattern_id]= matching_results
      # only keep frames with at least one matched pattern.
      # search
      # print('matching for frame', frame, matching_result)
      if len(pattern_matching_result_dict) > 0:
        matching_result_dict[frame] = pattern_matching_result_dict
    
    if self.metrics is not None:
      self.metrics.end_timer('pattern_matching/frame_matching')


    if self.metrics is not None:
      self.metrics.start_timer('temporal_matching')    
    # print('pattern', pattern)
    res = self.eval_window_scores(matching_result_dict, mapping_dict, pattern.length, topk)
    if self.metrics is not None:
      self.metrics.end_timer('temporal_matching')    
    return res
    # index: stype -> etype -> theta, d -> sid, eid, -> frame_list
    # for each frame.
    # print('matching result ', matching_result_dict)
  
  def eval_window_scores(self, matching_result_dict, pattern_mapping_dict, pattern_length, topk):
    if len(matching_result_dict) == 0:
      return []
    all_frames = matching_result_dict.keys()
    start_frame = max(1, min(all_frames))
    end_frame = max(all_frames) - pattern_length + 1
    topk_holder = TopkHolder(topk)
    if self.metrics is not None:
      self.metrics.record_txt('eval_range', (start_frame, end_frame))
    # print('eval range', start_frame, end_frame)
    for window_start in range(start_frame, end_frame + 1):
      # if window_start != 51000:
      #   continue
      # collect matched patterns:
      matched_pattern_list = list()
      # estimate_score = 0
      base_score = 0
      # print('pattern length', pattern_length)
      for frame_i in range(pattern_length):
        graph_frame = window_start + frame_i
        # pattern frame starts with 1
        pattern_frame = 1 + frame_i
        expected_pattern_id = pattern_mapping_dict.get(pattern_frame)

        # compute score for each possible combinations
        
        if expected_pattern_id is None:
          # inc 1 if the pattern is empty, means that it can be matched to anything.
          # FIXME: what if the blank is intentional? i.e., we don't want any matched object to appear in the frame?
          base_score += 1
        else:
          matched_patterns = matching_result_dict.get(graph_frame)
          if matched_patterns is not None and expected_pattern_id in matched_patterns:
            # TODO: further check the mapping dict.
            # FIXME: only inc score if the mapping is ok.
            matched_pattern_list.append(matched_patterns[expected_pattern_id])
            # estimate_score += 1
          # else:
          #   print('else?', graph_frame, matched_patterns, expected_pattern_id)
      # print('matched', matched_pattern_list)
      # compute score
      # score = estimate_score + base_score
      score = base_score
      # 1. collect dict: pattern_node -> matched_node -> set[matched_idx]
      pattern_node_count_dict = dict()
      for idx, pattern_dict_list in enumerate(matched_pattern_list):
        # print('what', pattern_dict_list)
        for pattern_dict in pattern_dict_list:
          for pattern_node, matched_node in pattern_dict.items():
            match_for_patter_node = compute_if_absent(pattern_node_count_dict, pattern_node, dict)
            pattern_set = compute_if_absent(match_for_patter_node, matched_node, set)
            pattern_set.add(idx)
      # loop all combinations to collect scores
      if len(pattern_node_count_dict) == 0:
        # no need to continue
        if self.metrics is not None:
          self.metrics.inc_counter('window_skipped')
        continue
      if self.metrics is not None:
        self.metrics.inc_counter('window_collected')
      max_score = [0]
      collected_pattern_nodes = set()
      matched_pattern_idx_set = set()
      self.enumerate_combinations(list(pattern_node_count_dict.items()), collected_pattern_nodes, \
        matched_pattern_idx_set, max_score, window_start)
      # if window_start == 137138:
      #   print('final max score', max_score[0])

      score += max_score[0]
      # update score.
      if score > 0:
        topk_holder.update(score, window_start)
      if self.all_window_scores_dict is not None:
        self.all_window_scores_dict[window_start] = score
    return topk_holder.cache_list

  def enumerate_combinations(self, pattern_node_count_dict_items, collected_pattern_nodes, \
    matched_pattern_idx_set:set, max_score, window_start, depth=0):
    if self.metrics is not None:
      self.metrics.inc_counter('steps_checked_count')
    # print('step >>>')
    # get the current node
    # print('depth', depth, 'len', len(pattern_node_count_dict_items))
    current_pattern_node, current_matched_dict = pattern_node_count_dict_items[depth]
    collected_pattern_nodes.add(current_pattern_node)

      # empty set, no need to continue.
    if depth > 0 and len(matched_pattern_idx_set) <= 1:
      if self.metrics is not None:
        self.metrics.inc_counter('early_pruned_candidates')
      return
    for matched_node, matched_idx_set in current_matched_dict.items():
      # new instance, otherwise the result could be incorrect.
      new_matched_pattern_idx_set = set(matched_pattern_idx_set)
      if depth == 0:
        new_matched_pattern_idx_set.update(matched_idx_set)
      else:
        new_matched_pattern_idx_set.intersection_update(matched_idx_set)
      
      if window_start == 4187:
        print('depth:', depth, len(pattern_node_count_dict_items))
        print('matched', new_matched_pattern_idx_set, collected_pattern_nodes)
        print('current', matched_node, matched_idx_set)
      # print('current', collected_pattern_nodes, matched_idx_set, len(new_matched_pattern_idx_set), depth)
      if depth + 1 == len(pattern_node_count_dict_items):
        if self.metrics is not None:
          self.metrics.inc_counter('computed_candidates')
        # update max score
        current_score = len(new_matched_pattern_idx_set)
        if self.computed_score_count_dict is not None:
          self.computed_score_count_dict[current_score] += 1
        max_score[0] = max(max_score[0], current_score)
      else:
        self.enumerate_combinations(pattern_node_count_dict_items, collected_pattern_nodes, \
          new_matched_pattern_idx_set, max_score, window_start, depth + 1)
    collected_pattern_nodes.remove(current_pattern_node)

  def test_match(self, frame, current_frame_index, unique_pattern):
    '''
    unique_pattern: 
      (stype, etype, theta, d) -> [(sid, eid), ...]
    '''
    # get pattern.
    # 1. collect all mappings from pattern edge -> current edge

    pattern_edge_eid_dict = dict()
    for edge, pairs in unique_pattern.items():
      stype, etype, theta, d = edge
      # get from index
      sid_eid_list = get_from_multi_level_dict(current_frame_index, [stype, etype, (theta, d)])
      # fors each (sid, eid), try to map it to the (sid, eid) in pairs
      if sid_eid_list is not None:
        for pattern_pair in pairs:
          pattern_edge_eid_dict[pattern_pair] = set(sid_eid_list)

    # if frame == 51000:
    #   print('edge', pattern_edge_eid_dict)
    # missing edges    
    if len(pattern_edge_eid_dict) < len(unique_pattern):
      # empty list
      return []

    # 2. consider matchings.
    matching_dict = dict()
    # all pattern_pairs have to be satisfied with the same mapping.
    # we pick the first pattern pair as the starting point.
    # for each pattern node, keep the # of edges picked.
    ref_count_dict = defaultdict(lambda: 0)
    # collect results.
    matching_results = list()
    self.__edge_matches(frame, list(pattern_edge_eid_dict.items()), matching_dict, ref_count_dict, matching_results)
    return matching_results
    
  def __edge_matches(self, frame, pattern_edge_eid_dict_items, matching_dict, ref_count_dict, matching_results, depth=0):
    # pattern_edge_eid_dict_items: (pattern_pair -> graph_pairs)
    # if frame == 51000:
    #   print('depth', depth, 'items', len(pattern_edge_eid_dict_items))
    #   print(matching_dict)
    # print('depth', depth)
    pattern_pair, graph_pairs = pattern_edge_eid_dict_items[depth]
    pattern_sid, pattern_eid = pattern_pair


    matched_sid, matched_eid = matching_dict.get(pattern_sid), matching_dict.get(pattern_eid)

    for sid, eid in graph_pairs:
      # skip not mtaching pairs.
      if matched_sid is not None and sid != matched_sid:
        continue 
      if matched_eid is not None and eid != matched_eid:
        continue
      # if matching_dict.get(62)==14083 and matching_dict.get(98) == 14075 and \
      #   matching_dict.get(34) == 14058:
      #   print('gotya')

      # add current pattern_node counts
      ref_count_dict[pattern_sid] += 1 
      ref_count_dict[pattern_eid] += 1

      if matched_sid is None:
        matching_dict[pattern_sid] = sid
      if matched_eid is None:
        matching_dict[pattern_eid] = eid
      # 
      # if reached to the last pattern_edge
      if len(pattern_edge_eid_dict_items) == depth + 1:
        # if frame == 51000:
        #   print('what', matching_dict)
        if len(set(matching_dict.keys())) == len(set(matching_dict.values())):
          # keep the current result.
          matching_results.append(dict(matching_dict))
        #   if frame == 51000:
        #     print('added')
        # else:
        #   if frame == 51000:
        #     print('dropped')
      else:
        # continue to next level.
        self.__edge_matches(frame, pattern_edge_eid_dict_items, matching_dict, ref_count_dict, \
          matching_results, depth+1)

      ref_count_dict[pattern_sid] -= 1
      ref_count_dict[pattern_eid] -= 1
      # otherwise, remove current mapping.
      if ref_count_dict[pattern_sid] == 0:
        # remove sid
        del matching_dict[pattern_sid]
        del ref_count_dict[pattern_sid]
      if ref_count_dict[pattern_eid] == 0:
        del matching_dict[pattern_eid]
        del ref_count_dict[pattern_eid]
  