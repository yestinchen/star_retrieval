import time
import pandas

class Metrics:
  OVERRIDE = 0
  ACCUMULATE = 1

  def __init__(self):
    self.time_dict = dict()
    self.running_timers = dict()
    self.counter_dict = dict()
    self.txt_dict = dict()
    self.table_data_dict = dict()
    self.table_info_dict = dict()
  
  def start_timer(self, name, timer_type=OVERRIDE):
    assert name not in self.running_timers, \
      'timer aleady exists with name: {}'.format(name)
    t = Timer()
    t.start()
    self.running_timers[name] = (t, timer_type)

  def end_timer(self, name):
    timer, timer_type = self.running_timers.pop(name)
    time_ellapsed = timer.end()
    if timer_type == Metrics.OVERRIDE:
      self.time_dict[name] = time_ellapsed
    elif timer_type == Metrics.ACCUMULATE:
      if name not in self.time_dict:
        self.time_dict[name] = 0
      self.time_dict[name] += time_ellapsed
    else:
      assert False, 'unexpected type: {}'.format(timer_type)

  def inc_counter(self, name, value=1):
    if name not in self.counter_dict:
      self.counter_dict[name] = 0
    self.counter_dict[name] += value
  
  def record_txt(self, key, value):
    self.txt_dict[key] = value

  def add_entry(self, table_name, **item_dict):
    table_info = self.table_info_dict.get(table_name)
    # make sure the items matches the meta-info
    if table_info is None:
      table_info = list(item_dict.keys())
      self.table_info_dict[table_name] = table_info
      self.table_data_dict[table_name] = []
    
    assert len(set(table_info).intersection(\
      set(item_dict.keys()))) == len(table_info), \
        'the keys for table [{}] does not match!'.format(table_name)
    table_data = self.table_data_dict[table_name]
    table_data.append([item_dict[x] for x in table_info])

  def print(self):
    print('timers dict============')
    for k, v in self.time_dict.items():
      print('{}: {}'.format(k, v))
    print('counter_dict=========')
    for k, v in self.counter_dict.items():
      print('{}: {}'.format(k, v))
    print('txt dict =========')
    for k, v in self.txt_dict.items():
      print('{}: {}'.format(k, v))
    print('table summaries ===========')
    # print tables
    # step 1. init table
    for table, info in self.table_info_dict.items():
      pandas_table = pandas.DataFrame(self.table_data_dict[table], columns=info)
      print('------- table: {}'.format(table))
      print(pandas_table.mean())
    # save figures

class Timer:
  def __init__(self):
    self.reset()

  def start(self):
    self.start_time = time.process_time()
  
  def end(self):
    self.end_time = time.process_time()
    return self.end_time - self.start_time

  def reset(self):
    self.start_time = None
    self.end_time = None