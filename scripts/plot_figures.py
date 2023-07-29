import os
import pandas as pd
import pickle
import seaborn as sns
import matplotlib.pyplot as plt

# base_result_path = '../storage/results/vsim/batch-results2/'
# figure_path = '../storage/results/vsim/figures2/'
# base_result_path = '../storage/results/vsim-detrac/batch-results2/'
# figure_path = '../storage/results/vsim-detrac/figures2/'
# base_result_path = '../storage/results/vsim-detrac-10/batch-results2/'
# figure_path = '../storage/results/vsim-detrac-10/figures2/'
# base_result_path = '../storage/results/vsim-detrac-5-fixed/batch-results2/'
# figure_path = '../storage/results/vsim-detrac-5-fixed/figures2/'
base_result_path = '../storage/results/vsim-all/batch-results2/'
figure_path = '../storage/results/vsim-all/figures2/'
LINE_PLOT=1
BAR_PLOT=2

def _save_current_plot(output_name, show=False):
  if show:
    plt.show()
  else:
    if not os.path.isdir(figure_path):
      os.makedirs(figure_path)
    # plt.savefig(fig_output_folder+output_path+'.pdf')
    plt.savefig(figure_path+output_name+'.jpg')
    # plt.savefig(figure_path+output_name+'.pdf')
    plt.clf()
    plt.cla()

def plot_query_time(pdframe:pd.DataFrame, output_name, x, plot_type=LINE_PLOT):
  '''
  y: time
  three series: baseline, proposed, proposed_seq
  x: video, df, k
  type: lineplot (for k), bar (for video)
  '''
  if plot_type == LINE_PLOT:
    sns.lineplot(data=pdframe, x=x, y='time', hue='method') 
  elif plot_type == BAR_PLOT:
    sns.barplot(data=pdframe, x=x, y='time', hue='method')
  else:
    assert False, 'Illegal plot type'
  # _save_current_plot(output_name, True)
  _save_current_plot(output_name)
  pass

def varying_query_video(pattern_video, pattern_num):
  batch_pattern_name = 'patterns-{}/4-10-{}'.format(pattern_video, pattern_num)
  videos = ['traffic1', 'traffic2']

  default_params = dict(
     k=100,
     df='df6'
  )

  data_tables = list()
  for video in videos:
    data_table = collect_batch_query_result('{}/{}-{}'\
      .format(base_result_path, batch_pattern_name, video))
    # print('data\n', data_table)
    data_table = group_by(data_table, default_params)
    data_tables.append(data_table)
  
  overall_table = pd.concat(data_tables, ignore_index=True)
  
  plot_query_time(overall_table, '{}_varying_query_videos'.format(pattern_video), 'video', BAR_PLOT)

def varying_pattern_length(pattern_video, pattern_num):
  default_params = dict(
    k = 100,
    df = 'df6',
    video = pattern_video
  )
  # pattern_template = 'patterns-{}/4-{}-5'
  pattern_template = 'patterns-{}/4-{}-{}'
  varying_lengths = [5, 10, 15]

  data_tables = list()

  for length in varying_lengths:
    batch_pattern_name = pattern_template.format(pattern_video, length, pattern_num)
    data_table = collect_batch_query_result('{}/{}-{}'\
      .format(base_result_path, batch_pattern_name, default_params['video']))
    data_table = group_by(data_table, default_params)
    data_table['length'] = [length] * len(data_table.index)
    data_tables.append(data_table)
  
  overall_table = pd.concat(data_tables, ignore_index=True)
  plot_query_time(overall_table, '{}_varying_pattern_length'.format(pattern_video), 'length')

def varying_num_objects(pattern_video, pattern_num):
  default_params = dict(
    k = 100,
    df = 'df6',
    video = pattern_video
  )
  # pattern_template = 'patterns-{}/{}-10-5'
  pattern_template = 'patterns-{}/{}-10-{}'
  varying_num = [3, 4, 5]

  data_tables = list()

  for num in varying_num:
    batch_pattern_name = pattern_template.format(pattern_video, num, pattern_num)
    data_table = collect_batch_query_result('{}/{}-{}'\
      .format(base_result_path, batch_pattern_name, default_params['video']))
    data_table = group_by(data_table, default_params)
    data_table['num'] = [num] * len(data_table.index)
    data_tables.append(data_table)
  
  overall_table = pd.concat(data_tables, ignore_index=True)
  plot_query_time(overall_table, '{}_varying_obj_num'.format(pattern_video), 'num')

def varying_df_functions(pattern_video, pattern_num):
  # result_folder = '{}/patterns-{}/4-10-5-{}'.format(base_result_path, pattern_video, pattern_video)
  result_folder = '{}/patterns-{}/4-10-{}-{}'.format(base_result_path, pattern_video, pattern_num, pattern_video)
  pdf = collect_batch_query_result(result_folder)
  res = group_by(pdf, dict(video=pattern_video, k=100))
  # print(res)
  plot_query_time(res, '{}_varying_df'.format(pattern_video), 'df', BAR_PLOT)

def varying_k(pattern_video, pattern_num):
  # result_folder = '{}/patterns-{}/4-10-5-{}'.format(base_result_path, pattern_video, pattern_video)
  result_folder = '{}/patterns-{}/4-10-{}-{}'.format(base_result_path, pattern_video, pattern_num, pattern_video)
  pdf = collect_batch_query_result(result_folder)
  # print(pdf)
  res = group_by(pdf, dict(video=pattern_video, df='df6'))
  # print(res)
  plot_query_time(res, '{}_varying_k'.format(pattern_video), 'k')

def plot_details(pattern_video, pattern_num, logy=False):
  result_folder = '{}/patterns-{}/4-10-{}-{}'.format(base_result_path, pattern_video, pattern_num, pattern_video)
  pdf = collect_batch_query_result(result_folder)
  pdf = filter_with_default_cond(pdf, dict(video=pattern_video, df='df6',k=100))
  # 
  total_len = len(pdf.index)
  parts = total_len // 30
  if (total_len / 30) > (total_len // 30):
    parts += 1
  for part_id in range(parts):
    pd = pdf.iloc[part_id*30: min((part_id+1)*30, total_len)]
    # plt.figure(figsize=(20,8))
    plt.figure(figsize=(6.4*2,4.8))
    sns.barplot(data=pd, x='frame_pair', y='time', hue='method')
    if logy:
      plt.yscale('log')
    # print(pd)
    _save_current_plot('{}_default_details_{}{}'.format(pattern_video, part_id, '_log' if logy else ''))
    # reset
    plt.figure(figsize=(6.4,4.8))
  pass

def read_float_startswith(file_path, startswith):
  with open(file_path, 'r') as rf:
    for line in rf.readlines():
      if line.startswith(startswith):
        return float(line[len(startswith):])
  return None

def _collect_batch_query_result(result_folder_path):
  '''
  return pd.frame
  '''
  tuples = list()
  for file_name in os.listdir(result_folder_path):
    # parse queryvideo-ids-frames-df-k-method
    query_video, ids, frame_pair, df, k, method = file_name.split('.')[0].split('-')
    value = read_float_startswith(os.path.join(result_folder_path, file_name), 'time used')
    tuples.append((query_video, ids, frame_pair, df, k, method, value))
  data = pd.DataFrame(tuples, columns=['video', 'ids', 'frame_pair', 'df', 'k', 'method', 'time'])
  data = data.astype(dict(k='int32'))
  return data

def collect_batch_query_result(result_folder_path, force_rebuild=True, collect_func=None):
  cache_file = os.path.join(result_folder_path, 'cache.pkl')
  if force_rebuild:
    if os.path.isfile(cache_file):
      os.remove(cache_file)
  if not os.path.isfile(cache_file):
    if collect_func is None:
      pdf = _collect_batch_query_result(result_folder_path)
    else:
      pdf = collect_func(result_folder_path)
    with open(cache_file, 'wb') as wf:
      pickle.dump(pdf, wf)
  with open(cache_file, 'rb') as rf:
    res = pickle.load(rf)
    # sort
    return res.sort_values(by=['video', 'ids', 'frame_pair', 'df', 'k', 'method'])
    

def group_by(pdframe:pd.DataFrame, default_params:dict):
  result = pdframe.groupby(['video','df', 'k', 'method']).mean()
  # for each 
  result.reset_index(inplace=True)
  return filter_with_default_cond(result, default_params)

def filter_with_default_cond(pdframe: pd.DataFrame, default_params:dict):
  mask_cond = [True] * len(pdframe.index)
  for k, v in default_params.items():
    mask_cond &= (pdframe[k] == v)
  result = pdframe[mask_cond]
  result.drop(columns=list(default_params.keys()), inplace=True)
  return result

if __name__ == '__main__':
  # file_path = result_folder + '/traffic1-16668_16747_16750-44726_44735-df5-100-proposed_seq.txt'
  # print(read_float_startswith(file_path, 'time used'))
  # pattern_videos = [
  #   'traffic1', 
  #   'traffic2',
  # ]
  pattern_videos =[
    # ('drtest', 40),
    # ('drtrain', 60)
    # ('bdd100kA', 70),
    # ('bdd100kB', 70)
    ('bdd100kA', 20),
    # ('bdd100kB', 20),
  ]
  for pv, pattern_num in pattern_videos:
    # plot_details(pv, pattern_num, logy=False)
    # varying_k(pv, pattern_num)
    # # varying_query_video(pv)
    varying_df_functions(pv, pattern_num)
    varying_num_objects(pv, pattern_num)
    varying_pattern_length(pv, pattern_num)
    # varying_num_objects(pv)

  # result_folder = '../storage/results/vsim/batch-results/patterns-traffic1/4-15-5-traffic1'
  # result_folder = '../storage/results/vsim/batch-results/patterns-traffic2/4-15-5-traffic2'
  # result_folder = '../storage/results/vsim/batch-results/patterns-traffic1/5-10-5-traffic1'
  # result_folder = '../storage/results/vsim/batch-results/patterns-traffic2/5-10-5-traffic2'
  # result_folder = '../storage/results/vsim/batch-results/patterns-traffic2/4-10-5-traffic1'
  # print(result_folder)
  # res = collect_batch_query_result(result_folder)
  # res = res[
  #   (res['k']==100) & (res['df']=='df5')
  # ]
  # print(res)