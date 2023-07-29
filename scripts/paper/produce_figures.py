from scripts.settings import file_storage_path
from scripts.plot_figures import collect_batch_query_result, filter_with_default_cond, group_by

import os
import pandas as pd
import pickle
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure, xlabel
import numpy as np

base_result_path = '{}/batch-results2'.format(file_storage_path)
figure_path = file_storage_path+'/figures/'

all_avaliable_markers = [',', '.', 'o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']
all_avaliable_bar_patterns = [ "/" , "\\" , "|" , "-" , "+" , "x", "o", "O", ".", "*" ]
all_videos_names = ['drtrain', 'drtest', 'bdd100kA', 'bdd100kB', 'base', 'prop', 'prop_s', 'GI','GI_V', 'GI_E']
all_markers = ['o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'P', 'X']
all_colors = ['#FFBE33','#6FAD51','#A24618', '#A5A5A5','#145F8F', '#426831','#D25930','#F37A3B','#3774C0', '#FFBE33','#FFBE33','#3774C0']

default_configs = dict(
  linewidth=4,
  markersize=10,
)

rename_videos = dict(
  [
    ('bdd100kA', 'bddA'),
    ('bdd100kB', 'bddB'),
  ]
)

rename_methods = dict(
  [
    ('baseline', 'base'),
    ('proposed', 'prop'),
    ('proposed_seq', 'prop_s'),
    ('baseline-1', 'GI'),
    ('baseline-3', 'GI_V'),
    ('baseline-4', 'GI_E')
  ]
)

rename_dfs = dict(
  [
    ('df5', 'df1'),
    ('df6', 'df2'),
    ('df7', 'df3'),
    ('df8', 'df4')
  ]
)

def rename_terms(pdf: pd.DataFrame):
  if 'method' in pdf.columns:
    for method, renamed_method in rename_methods.items():
      pdf.loc[pdf['method'] == method, 'method'] = renamed_method

  if 'df' in pdf.columns:
    for df, new_df in rename_dfs.items():
      pdf.loc[pdf['df'] == df, 'df'] = new_df
  return pdf

def _save_current_plot(output_name, show=False):
  if show:
    plt.show()
  else:
    if not os.path.isdir(figure_path):
      os.makedirs(figure_path)
    # plt.savefig(fig_output_folder+output_path+'.pdf')
    # plt.savefig(figure_path+output_name+'.jpg')
    plt.savefig(figure_path+output_name+'.pdf')
    plt.clf()
    plt.cla()


def plot_index_time_bar(pdframe:pd.DataFrame, output_name):
  series_names = pdframe['video'].unique().tolist()
  palette = [all_colors[all_videos_names.index(s)] for s in series_names]

  ax = plt.gca()
  sns.barplot(data=pdframe, x='video', y='time', \
     palette=palette)
  
  ax.set_ylabel('time(s)')
  # Only show ticks on the left and bottom spines
  ax.yaxis.set_ticks_position('left')
  ax.xaxis.set_ticks_position('bottom')
  _save_current_plot(output_name, True)

def plot_index_time_bar_index(pdframe:pd.DataFrame, output_name):
  series_names = pdframe['video'].unique().tolist()
  palette = [all_colors[all_videos_names.index(s)] for s in series_names]

  ax = plt.gca()
  sns.barplot(data=pdframe, x='video', y='time', hue='method', \
     palette=palette)
  
  legend = plt.legend(ncol=3, columnspacing=1)
  ax.set_ylabel('time(s)')
  ax.set_ybound((0, 1000))
  # Only show ticks on the left and bottom spines
  ax.yaxis.set_ticks_position('left')
  ax.xaxis.set_ticks_position('bottom')
  _save_current_plot(output_name, False)

def plot_index_time_per_frame(pdframe: pd.DataFrame, output_name):
  series_names = pdframe['video'].unique().tolist()
  palette = [all_colors[all_videos_names.index(s)] for s in series_names]

  # ax = plt.gca()
  ax = sns.barplot(data=pdframe, x='video', y='time', \
     palette=palette)
  # Define some hatches
  hatches = ['-', '+', 'x', '\\', '*', 'o']

  # Loop over the bars
  for i,thisbar in enumerate(ax.patches):
      # Set a different hatch for each bar
      thisbar.set_hatch(hatches[i])

  ax.set_ylabel('time(s)')
  # Only show ticks on the left and bottom spines
  ax.yaxis.set_ticks_position('left')
  ax.xaxis.set_ticks_position('bottom')

  ax2 = ax.twinx()
  sns.lineplot(data=pdframe, x= 'video', y='per_frame', legend=False, \
    ax=ax2, palette=palette, marker='X', linewidth=default_configs['linewidth'])
  ax2.set_ylabel('per frame time(ms)')
  # Only show ticks on the left and bottom spines
  ax2.yaxis.set_ticks_position('right')
  # ax2.xaxis.set_ticks_position('bottom')

  _save_current_plot(output_name)

def plot_index_time_line(pdframe:pd.DataFrame, x, output_name):
  series_names = pdframe['video'].unique().tolist()
  markers = [all_markers[all_videos_names.index(s)] for s in series_names]
  palette = [all_colors[all_videos_names.index(s)] for s in series_names]
  ax = plt.gca()
  sns.lineplot(data=pdframe, x = x, y='time', hue='video', \
    style='video', dashes=False, markers=markers, palette=palette, **default_configs)
  ax.set_yticks([0, 300, 600, 900])
  # remove name title.
  ax.legend(title='')
  ax.set_ylabel('time(s)')
  # Only show ticks on the left and bottom spines
  ax.yaxis.set_ticks_position('left')
  ax.xaxis.set_ticks_position('bottom')
  _save_current_plot(output_name)

def index_varying_percent(pdframe:pd.DataFrame, x, output_name):
  # print('pdf', pdframe)
  pdframe['p'] = pdframe['p'] * 100
  series_names = pdframe['video'].unique().tolist()
  markers = [all_markers[all_videos_names.index(s)] for s in series_names]
  palette = [all_colors[all_videos_names.index(s)] for s in series_names]
  ax = plt.gca()
  sns.lineplot(data=pdframe, x = x, y='time', hue='video', \
    style='video', dashes=False, markers=markers, palette=palette, **default_configs)
  ax.set_yticks([0, 300, 600, 900])
  ax.set_xlabel('percentage of the video (%)')
  ax.set_xticks(pdframe[x].unique().tolist())
  # remove name title.
  ax.legend(title='')
  ax.set_ylabel('time(s)')
  # Only show ticks on the left and bottom spines
  ax.yaxis.set_ticks_position('left')
  ax.xaxis.set_ticks_position('bottom')
  _save_current_plot(output_name)

def index_varying_percent_per_frame(pdframe:pd.DataFrame, x, output_name):
  # print('pdf', pdframe)
  pdframe['p'] = pdframe['p'] * 100
  series_names = pdframe['video'].unique().tolist()
  markers = [all_markers[all_videos_names.index(s)] for s in series_names]
  palette = [all_colors[all_videos_names.index(s)] for s in series_names]
  ax = plt.gca()
  sns.lineplot(data=pdframe, x = x, y='per_frame', hue='video', \
    style='video', dashes=False, markers=markers, palette=palette, **default_configs)
  # ax.set_yticks([0, 300, 600, 900])
  ax.set_xlabel('percentage of the video (%)')
  ax.set_xticks(pdframe[x].unique().tolist())
  # remove name title.
  ax.legend(title='')
  ax.set_ylabel('time(ms)')
  # Only show ticks on the left and bottom spines
  ax.yaxis.set_ticks_position('left')
  ax.xaxis.set_ticks_position('bottom')
  _save_current_plot(output_name)
def read_float_startswith(file_path, startswith):
  with open(file_path, 'r') as rf:
    for line in rf.readlines():
      if line.startswith(startswith):
        return float(line[len(startswith):])
  return None

def collect_index_build_times(videos, dfs):
  folder_path = '{}/{}'.format(file_storage_path, 'index')
  tuples = list()
  for video in videos:
    for df in dfs:
      file_path = '{}/{}-1-{}.out.txt'.format(folder_path, video, df)
      value = read_float_startswith(file_path, 'time:')
      tuples.append((video, df, value))
  data = pd.DataFrame(tuples, columns=['video', 'df', 'time'])
  return data

def collect_index_build_times_percents(videos, percents):
  folder_path = '{}/{}'.format(file_storage_path, 'index')
  tuples = list()
  for video in videos:
    for p in percents:
      file_path = '{}/percent/{}-1-{}-{}.out.txt'.format(folder_path, video, 'df6', p)
      value = read_float_startswith(file_path, 'time:')
      tuples.append((video, p, value))
  data = pd.DataFrame(tuples, columns=['video', 'p', 'time'])
  return data

def collect_index_build_times_vary_index(videos, indexes):
  folder_path = '{}/{}'.format(file_storage_path, 'index')
  tuples = list()
  names = dict(
    [(1, 'GI'), (3, 'GI_V'), (4, 'GI_E')]
  )
  for video in videos:
    for i in indexes:
      file_path = '{}/{}-{}-{}.out.txt'.format(folder_path, video, i, 'df6', )
      value = read_float_startswith(file_path, 'time:')
      tuples.append((video, names[i], value))
  data = pd.DataFrame(tuples, columns=['video', 'method', 'time'])
  return data


def plot_query_time_line(pdframe: pd.DataFrame, x, x_label, y_label, log_y, output_name):
  series_names = pdframe['method'].unique().tolist()
  markers = [all_markers[all_videos_names.index(s)] for s in series_names]
  palette = [all_colors[all_videos_names.index(s)] for s in series_names]
  x_values = pdframe[x].unique().tolist()
  ax = sns.lineplot(data=pdframe, x=x, y='time', hue='method', \
    style='method', dashes=False, markers=markers, palette=palette, **default_configs)
  ax.set_xlabel(x_label)
  ax.set_ylabel(y_label)
  ax.set_xticks(x_values)
  if log_y:
    ax.set_yscale('log')
  _save_current_plot(output_name)

def plot_query_time_bar(pdframe: pd.DataFrame, x, x_label, y_label, log_y, output_name):
  series_names = pdframe['method'].unique().tolist()
  patterns = [all_avaliable_bar_patterns[all_videos_names.index(s)] for s in series_names]
  palette = [all_colors[all_videos_names.index(s)] for s in series_names]
  ax = sns.barplot(data=pdframe, x=x, y='time', hue='method', palette=palette)
  ax.set_xlabel(x_label)
  ax.set_ylabel(y_label)
  if log_y:
    ax.set_yscale('log')
  _save_current_plot(output_name)

def plot_query_time_box(pdframe: pd.DataFrame, x, x_label, y_label, log_y, output_name):
  series_names = pdframe['method'].unique().tolist()
  markers = [all_markers[all_videos_names.index(s)] for s in series_names]
  # palette = [all_colors[all_videos_names.index(s)] for s in series_names]
  palette = sns.color_palette("colorblind")
  x_values = pdframe[x].unique().tolist()
  ax = sns.boxplot(data=pdframe, x=x, y='time', hue='method', \
    palette=palette, whis=np.inf)
  ax = sns.stripplot(x=x, y="time", hue='method', data=pdframe,color='.25', size=3, dodge=True)
  # Get the handles and labels. We only need to keep the first half (for boxplot)
  handles, labels = ax.get_legend_handles_labels()
  total_num = len(handles)//2
  legend = plt.legend(handles[:total_num], labels[:total_num], ncol=3, columnspacing=1)

  ax.set_xlabel(x_label)
  ax.set_ylabel(y_label)
  # ax.set_xticks(x_values)
  # print('x values', x_values)
  if log_y:
    ax.set_yscale('log')
  ax.yaxis.set_ticks_position('left')
  ax.xaxis.set_ticks_position('bottom')
  _save_current_plot(output_name)

def varying_k(pattern_video, pattern_num):
  result_folder = '{}/patterns-{}/4-10-{}-{}'.format(base_result_path, pattern_video, pattern_num, pattern_video)
  pdf = collect_batch_query_result(result_folder)
  # print(pdf)
  # res = group_by(pdf, dict(video=pattern_video, df='df6'))
  res = filter_with_default_cond(pdf, dict(video=pattern_video, df='df6'))
  res = rename_terms(res)
  res['k'] = res['k'] / 1000

  # print(res)
  plot_query_time_box(res, 'k', 'k (x1000)', 'time (s)', True, '{}_varying_k'.format(pattern_video))


def varying_df(pattern_video, pattern_num):
  result_folder = '{}/patterns-{}/4-10-{}-{}'.format(base_result_path, pattern_video, pattern_num, pattern_video)
  pdf = collect_batch_query_result(result_folder)
  res = filter_with_default_cond(pdf, dict(video=pattern_video, k=100))
  res = rename_terms(res)
  # res = group_by(pdf, dict(video=pattern_video, k=100))
  # print(res)
  plot_query_time_box(res, 'df', 'df', 'time (s)', True, '{}_varying_df'.format(pattern_video))

def varying_pattern_length(pattern_video, pattern_num):
  default_params = dict(
    k = 100,
    df = 'df6',
    video = pattern_video,
  )
  # pattern_template = 'patterns-{}/4-{}-5'
  pattern_template = 'patterns-{}/4-{}-{}'
  varying_lengths = [5, 10, 15]

  data_tables = list()

  for length in varying_lengths:
    batch_pattern_name = pattern_template.format(pattern_video, length, pattern_num)
    data_table = collect_batch_query_result('{}/{}-{}'\
      .format(base_result_path, batch_pattern_name, default_params['video']))
    # data_table = group_by(data_table, default_params)
    data_table = filter_with_default_cond(data_table, default_params)
    data_table = rename_terms(data_table)
    data_table['length'] = [length] * len(data_table.index)
    data_tables.append(data_table)
  
  overall_table = pd.concat(data_tables, ignore_index=True)
  plot_query_time_box(overall_table, 'length', 'length', 'time (s)', True, '{}_varying_pattern_length'.format(pattern_video))

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
    # data_table = group_by(data_table, default_params)
    data_table = filter_with_default_cond(data_table, default_params)
    data_table = rename_terms(data_table)
    data_table['num'] = [num] * len(data_table.index)
    data_tables.append(data_table)
  
  overall_table = pd.concat(data_tables, ignore_index=True)
  plot_query_time_box(overall_table, 'num', 'num', 'time (s)', True, '{}_varying_obj_num'.format(pattern_video))

def varying_videos(varying_videos, pattern_num):
  default_params = dict(k = 100, df='df6')
  pattern_template = 'patterns-{}/4-10-{}'
  data_tables = list()
  for video in varying_videos:
    batch_pattern_name = pattern_template.format(video, pattern_num)
    data_table = collect_batch_query_result('{}/{}-{}'\
      .format(base_result_path, batch_pattern_name, video))
    # data_table = group_by(data_table, default_params)
    data_table = filter_with_default_cond(data_table, default_params)
    data_table = rename_terms(data_table)
    data_table['video'] = [video] * len(data_table.index)
    data_tables.append(data_table)

  overall_table = pd.concat(data_tables, ignore_index=True)
  plot_query_time_box(overall_table, 'video', 'video', 'time (s)', True, 'query_varying_videos')

def varying_videos_multi_label(varying_videos, pattern_num):
  default_params = dict(k = 100, df='df6')
  pattern_template = 'patterns-{}/4-10-{}'
  data_tables = list()
  for video in varying_videos:
    batch_pattern_name = pattern_template.format(video, pattern_num)
    data_table = collect_batch_query_result('{}/multi-batch-results2/{}-{}'\
      .format(file_storage_path, batch_pattern_name, video))
    # data_table = group_by(data_table, default_params)
    data_table = filter_with_default_cond(data_table, default_params)
    data_table = rename_terms(data_table)
    data_table['video'] = [video] * len(data_table.index)
    data_tables.append(data_table)

  overall_table = pd.concat(data_tables, ignore_index=True)
  plot_query_time_box(overall_table, 'video', 'video', 'time (s)', True, 'multilabel_varying_videos')

def varying_index(varying_videos, pattern_num):
  default_params = dict(k = 1, df='df6')
  pattern_template = 'patterns-{}/4-10-{}'
  data_tables = list()
  for video in varying_videos:
    batch_pattern_name = pattern_template.format(video, pattern_num)
    data_table = collect_batch_query_result('{}/batch-results2-extra/{}-{}'\
      .format(file_storage_path, batch_pattern_name, video), collect_func=_collect_batch_query_result_with_index_type)
    # data_table = group_by(data_table, default_params)
    data_table = filter_with_default_cond(data_table, default_params)
    data_table = rename_terms(data_table)
    data_table['video'] = [video] * len(data_table.index)
    data_tables.append(data_table)

  overall_table = pd.concat(data_tables, ignore_index=True)
  # print('overall table', overall_table)
  plot_query_time_box(overall_table, 'video', 'video', 'time (s)', True, 'varying_index')



def varying_sample_rate(video, pattern_num):
  default_params = dict(k=100, df='df6')
  pattern_template_1 = '{}/batch-results2/patterns-{}/4-10-{}-{}'
  pattern_template_2 = '{}/sample-batch-results2/patterns-{}-{}/4-10-{}-{}-{}'
  sample_rates = [1, 5, 10]
  def get_result_path(video, sample):
    if sample == 1:
      return pattern_template_1.format(file_storage_path, video, pattern_num, video)
    else:
      return pattern_template_2.format(file_storage_path, video, \
        sample, pattern_num, video, sample)

  data_tables = list()
  rename_dict = dict([(1, 100), (5, 20), (10, 10)])
  for rate in sample_rates:
    data_table = collect_batch_query_result(get_result_path(video, rate), collect_func=_collect_batch_query_result_with_sample)
    data_table = filter_with_default_cond(data_table, default_params)
    data_table = rename_terms(data_table)
    data_table['rate'] = [rename_dict[rate]] * len(data_table.index)
    data_tables.append(data_table)
  overall_table = pd.concat(data_tables, ignore_index=True)
  plot_query_time_box(overall_table, 'rate', 'sample rate (%)', 'time (s)', True, '{}_varying_sample_rate'.format(video))
      

def _collect_batch_query_result_with_sample(result_folder_path):
  '''
  return pd.frame
  '''
  tuples = list()
  for file_name in os.listdir(result_folder_path):
    # parse queryvideo-ids-frames-df-k-method
    # print('filename', file_name)
    res = file_name.split('.')[0].split('-')
    if len(res) == 6:
      query_video, ids, frame_pair, df, k, method = res
      rate = 1
    elif len(res) == 7:
      query_video, rate, ids, frame_pair, df, k, method = res
    value = read_float_startswith(os.path.join(result_folder_path, file_name), 'time used')
    tuples.append((query_video, rate, ids, frame_pair, df, k, method, value))
  data = pd.DataFrame(tuples, columns=['video', 'rate', 'ids', 'frame_pair', 'df', 'k', 'method', 'time'])
  data = data.astype(dict(k='int32'))
  return data


def _collect_batch_query_result_with_index_type(result_folder_path):
  '''
  return pd.frame
  '''
  tuples = list()
  for file_name in os.listdir(result_folder_path):
    # parse queryvideo-ids-frames-df-k-method
    # print('filename', file_name)
    res = file_name.split('.')[0].split('-')
    if len(res) == 6:
      query_video, ids, frame_pair, df, k, method = res
      rate = 1
    elif len(res) == 7:
      query_video, ids, frame_pair, df, k, method, index_type = res
    value = read_float_startswith(os.path.join(result_folder_path, file_name), 'time used')
    method = '{}-{}'.format(method, index_type)
    tuples.append((query_video, ids, frame_pair, df, k, method, index_type, value))
  data = pd.DataFrame(tuples, columns=['video', 'ids', 'frame_pair', 'df', 'k', 'method', 'indextype', 'time'])
  data = data.astype(dict(k='int32'))
  return data

# runable entries.

# for index construnctions.

def produce_index_bar_figures():
  figure(figsize=(8, 3), dpi=80)
  videos = [ 'drtest', 'drtrain', 'bdd100kA', 'bdd100kB']
  dfs = ['df6']
  frame_nums = [56300, 83731, 138253, 138785]

  data = collect_index_build_times(videos, dfs)
  for video, frame_num in zip(videos, frame_nums):
    data.loc[data['video'] == video, 'frames'] = frame_num
  print(data)
  data['per_frame'] = data['time'] * 1000 / data['frames']
  # plot_index_time_bar(data, 'build_index_time_bar')

  plt.subplots_adjust(left=0.15, right=0.85, top=0.95, bottom=0.18)
  plot_index_time_per_frame(data, 'build_index_time_per_frame')

def produce_index_vary_df():
  figure(figsize=(8, 3), dpi=80)
  videos = ['drtest', 'drtrain', 'bdd100kA', 'bdd100kB']
  dfs = ['df5', 'df6', 'df7', 'df8']

  data = collect_index_build_times(videos, dfs)
  data = rename_terms(data)
  plot_index_time_line(data, 'df', 'build_index_line')

def produce_index_vary_frames():
  videos = ['drtest', 'drtrain', 'bdd100kA', 'bdd100kB']
  percents = [0.25, 0.5, 0.75, 1]
  data = collect_index_build_times_percents(videos, percents)
  index_varying_percent(data, 'p', 'build_index_percent')

def produce_index_vary_frames_per_frame():
  videos = ['drtest', 'drtrain', 'bdd100kA', 'bdd100kB']
  percents = [0.25, 0.5, 0.75, 1]
  data = collect_index_build_times_percents(videos, percents)
  frame_nums = [56300, 83731, 138253, 138785]
  for video, frame_num in zip(videos, frame_nums):
    data.loc[data['video'] == video, 'frames'] = frame_num
  data['per_frame'] = data['time'] * 1000 / (data['frames'] * data['p'])
  index_varying_percent_per_frame(data, 'p', 'build_index_percent_per_frame')
# for query processing.

def produce_query_time_vary_videos():
  figure(figsize=(8, 3), dpi=80)
  plt.subplots_adjust(left=0.15, right=1, top=1, bottom=0.18)
  videos = ['drtest', 'drtrain', 'bdd100kA', 'bdd100kB']
  varying_videos(videos, 20)

def produce_query_time_vary_df():
  plt.subplots_adjust(left=0.15, right=1, top=1, bottom=0.18)
  videos = ['drtest', 'drtrain', 'bdd100kA', 'bdd100kB']
  for video in videos:
    varying_df(video, 20)

def produce_query_time_vary_obj_num():
  plt.subplots_adjust(left=0.15, right=1, top=1, bottom=0.18)
  videos = ['drtest', 'drtrain', 'bdd100kA', 'bdd100kB']
  for video in videos:
    varying_num_objects(video, 20)

def produce_query_time_vary_pattern_length():
  plt.subplots_adjust(left=0.15, right=1, top=1, bottom=0.18)
  videos = ['drtest', 'drtrain', 'bdd100kA', 'bdd100kB']
  # videos = videos[:1]
  for video in videos:
    varying_pattern_length(video, 20)

def produce_query_time_vary_k():
  plt.subplots_adjust(left=0.15, right=1, top=1, bottom=0.18)
  videos = ['drtest', 'drtrain', 'bdd100kA', 'bdd100kB']
  # videos = videos[:1]
  for video in videos:
    varying_k(video, 20)

def produce_query_time_vary_sample_rate():
  plt.subplots_adjust(left=0.15, right=1, top=0.95, bottom=0.18)
  videos = ['drtest', 'drtrain', 'bdd100kA', 'bdd100kB']
  # videos = videos[:1]
  for video in videos:
    varying_sample_rate(video, 20)

def produce_query_time_multi_labels():
  figure(figsize=(8, 3), dpi=80)
  plt.subplots_adjust(left=0.15, right=1, top=1, bottom=0.18)
  videos = ['drtest', 'drtrain', 'bdd100kA', 'bdd100kB']
  varying_videos_multi_label(videos, 20)

def produce_query_time_varying_index():
  plt.subplots_adjust(left=0.15, right=1, top=1, bottom=0.18)
  videos = ['drtest', 'drtrain', 'bdd100kA', 'bdd100kB']
  # videos = ['drtrain', 'drtest', 'bdd100kA']
  varying_index(videos, 20)

def produce_index_vary_index():
  videos = ['drtest', 'drtrain', 'bdd100kA', 'bdd100kB']
  index=[1, 3, 4]

  data = collect_index_build_times_vary_index(videos, index)
  data = rename_terms(data)
  plot_index_time_bar_index(data, 'build_index_vary_index_bar')

if __name__ == '__main__':
  figure(figsize=(5, 3), dpi=80)
  sns.set_theme(font_scale=1.5, context='paper', style='white', palette='deep')

  plt.subplots_adjust(left=0.18, right=0.95, top=0.95, bottom=0.18)

  # produce_index_bar_figures()
  # produce_index_vary_df()
  # produce_index_vary_frames()
  # produce_index_vary_frames_per_frame()
  # produce_query_time_vary_k()
  # produce_query_time_vary_df()
  # produce_query_time_vary_obj_num()
  # produce_query_time_vary_pattern_length()
  # produce_query_time_vary_videos()
  produce_query_time_vary_sample_rate()
  # produce_query_time_multi_labels()
  # produce_query_time_varying_index()
  # produce_index_vary_index()