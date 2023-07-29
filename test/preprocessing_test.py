import pandas as pd
from vsimsearch.preprocessing import discretize_attributes

if __name__ == '__main__':
  df = pd.DataFrame([(1.11, 1.35, 1.25)], columns=['a', 'b', 'c'])
  print(df) 
  discretize_attributes(df, [
    ('a', round),
    ('b', lambda x: round(x, 1)),
    ('c', lambda x: x**2)
  ])
  print(df) 