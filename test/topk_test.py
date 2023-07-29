from vsimsearch.topk import TopkHolder

if __name__ == '__main__':
  holder = TopkHolder(2)
  holder.update(10, 10)
  holder.update(11, 11)
  print(holder.cache_list)
  print(holder.last_score())
  holder.update(12, 12)
  print(holder.cache_list)
  print(holder.last_score())