from vsimsearch.proposed import compute_matching_score


def test_simple_matching():
  frames_dict = dict()
  # frame starts with 1
  for frame in range(1, 11):
    frames_dict[frame] = [
      [[2], [1], [3]]
    ]
  ordered_pattern_frames = list()
  for pos in range(3):
    ordered_pattern_frames.append([(i, pos) for i in range(1, 11)])
  print('frames_dict', frames_dict)
  print('ordered_pattern_frames', ordered_pattern_frames)
  score = compute_matching_score(frames_dict, ordered_pattern_frames)
  print('score', score)
  pass

if __name__ == '__main__':
  test_simple_matching()