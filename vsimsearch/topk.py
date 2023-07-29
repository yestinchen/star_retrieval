import heapq

class TopkHolder:

  def __init__(self, k) -> None:
    self.k = k
    self.cache_list = list()

  def update(self, score, value):
    heapq.heappush(self.cache_list, (score, value))
    if len(self.cache_list) > self.k:
      heapq.heappop(self.cache_list)

  def last_score(self):
    if len(self.cache_list) < self.k:
      return None
    return self.cache_list[0][0]
