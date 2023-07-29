from scripts.plot_figures import collect_batch_query_result, filter_with_default_cond, _save_current_plot
from scripts.settings import file_storage_path
import pickle
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scripts.detrac.gather_selectivity import compute_num_candidates, compute_unique_pattern_per_frame, read_index, read_pattern
import math

# base_result_path = '../storage/results/vsim-detrac/batch-results2/'
# figure_path = '../storage/results/vsim-detrac/figures2/'
# base_result_path = '../storage/results/vsim-detrac-10/batch-results2/'
# figure_path = '../storage/results/vsim-detrac-10/figures2/'
# base_result_path = '../storage/results/vsim-detrac-5/batch-results2/'
# figure_path = '../storage/results/vsim-detrac-5/figures2/'
base_result_path = '../storage/results/vsim-all/batch-results2/'
figure_path = '../storage/results/vsim-all/figures2/'

index_cache = None

def plot_details(pattern_video, pattern_num, logy=False, other_axis='candidates'):
  assert other_axis in ['candidates', 'unique_edges', 'unique_edges_per_frame']
  result_folder = '{}/patterns-{}/4-10-{}-{}'.format(base_result_path, pattern_video, pattern_num, pattern_video)
  pdf = collect_batch_query_result(result_folder)
  pdf = filter_with_default_cond(pdf, dict(video=pattern_video, df='df6',k=100))
  # 
  pdf['sort_key'] = pdf['frame_pair'].str.split('_').apply(lambda x : int(x[0]))
  pdf = pdf.sort_values(by=['sort_key', 'method'])
  print(pdf)
  total_len = len(pdf.index)
  parts = total_len // 30
  if (total_len / 30) > (total_len // 30):
    parts += 1

  pattern_config = [pattern_video, 'df6', 4, 10, pattern_num]
  query_config = [pattern_video, 100]
  global index_cache
  if index_cache is None:
    index_cache = read_index('drtrain', 'df6')
  frame_pair_dict = read_pattern(pattern_config, query_config)
  for part_id in range(parts):
    pdf_part = pdf.iloc[part_id*30: min((part_id+1)*30, total_len)]
    # plt.figure(figsize=(20,8))
    plt.figure(figsize=(6.4*2,4.8))
    sns.barplot(data=pdf_part, x='frame_pair', y='time', hue='method')

    new_list = list()
    for frame_str in pdf_part['frame_pair'].unique():
      if other_axis == 'unique_edges':
        new_list.append((frame_str, -len(frame_pair_dict[frame_str])))
      elif other_axis == 'unique_edges_per_frame':
        new_list.append((frame_str, -compute_unique_pattern_num(frame_pair_dict[frame_str])))
      elif other_axis == 'candidates':
        new_list.append((frame_str, compute_num_candidates(index_cache, frame_pair_dict[frame_str])))
    
    if logy:
      plt.yscale('log')
    ax = plt.gca()
    ax2 = ax.twinx()
    # statics_data = pd.DataFrame(new_list, columns=['frame_pair', 'unique'])
    statics_data = pd.DataFrame(new_list, columns=['frame_pair', other_axis])
    sns.lineplot(data=statics_data, x='frame_pair', y=other_axis, ax=ax2)

    # ax3 = ax.twinx()
    # if other_axis == 'unique_edges':
    #   new_list = list()
    #   for frame_str in pdf_part['frame_pair'].unique():
    #     new_list.append((frame_str, -compute_unique_pattern_num(frame_pair_dict[frame_str])))
    #   statics_data = pd.DataFrame(new_list, columns=['frame_pair', 'unique_edges_per_frame'])
    #   sns.lineplot(data=statics_data, x='frame_pair', y='unique_edges_per_frame', ax=ax2)
    #   plt.legend()

    # print(pd)
    _save_current_plot('{}_default_detailscomp_{}_{}{}'.format(pattern_video, other_axis, \
      part_id, '_log' if logy else ''))
    # reset
    plt.figure(figsize=(6.4,4.8))
  pass

def compute_unique_pattern_num(edge_frames_dict):
  frame_unique_edge_dict = compute_unique_pattern_per_frame(edge_frames_dict)
  frame_count_dict = dict([(k, len(v)) for k,v in frame_unique_edge_dict.items()])
  return sum(frame_count_dict.values()) / len(frame_count_dict)



def plot_all_details(pattern_video, pattern_num, logy=False):
  pattern_config = [pattern_video, 'df6', 4, 10, pattern_num]
  query_config = [pattern_video, 100]
  result_folder = '{}/patterns-{}/4-10-{}-{}'.format(base_result_path, pattern_video, pattern_num, pattern_video)
  pdf = collect_batch_query_result(result_folder)
  pdf = filter_with_default_cond(pdf, dict(video=pattern_video, df='df6',k=100))
  # 
  pdf['sort_key'] = pdf['frame_pair'].str.split('_').apply(lambda x : int(x[0]))
  pdf = pdf.sort_values(by=['sort_key', 'method'])
  # print(pdf)
  total_len = len(pdf.index)
  parts = total_len // 30
  if (total_len / 30) > (total_len // 30):
    parts += 1

  # global index_cache
  # if index_cache is None:
  #   index_cache = read_index('drtrain', 'df6')
  # # frame_pair_dict = read_pattern(pattern_config, query_config)
  for part_id in range(parts):
    pdf_part = pdf.iloc[part_id*30: min((part_id+1)*30, total_len)]
    # plt.figure(figsize=(20,8))
    plt.figure(figsize=(6.4*2,4.8))
    sns.barplot(data=pdf_part, x='frame_pair', y='time', hue='method')

    pattern_info = pdf_part[['frame_pair', 'ids']].drop_duplicates()
    print(pattern_info)
    new_list = list()
    for index, row in pattern_info.iterrows():
      frame_pair = row['frame_pair'].split('_')
      ids = row['ids'].split('_')
      candidates = read_value_from_baseline_output(pattern_config, query_config, ids, frame_pair, 'edge_retrieve_count:')
      windows = read_value_from_baseline_output(pattern_config, query_config, ids, frame_pair, 'window_collected:')
      steps_checked_count = read_value_from_baseline_output(pattern_config, query_config, ids, frame_pair, 'steps_checked_count:')
      computed_candidates = read_value_from_baseline_output(pattern_config, query_config, ids, frame_pair, 'computed_candidates:')
      new_list.append((row['frame_pair'], candidates, windows, steps_checked_count, computed_candidates))
      # new_list.append((row['frame_pair'], candidates, windows, steps_checked_count))
      
    
    if logy:
      plt.yscale('log')
    ax = plt.gca()
    ax2 = ax.twinx()
    # statics_data = pd.DataFrame(new_list, columns=['frame_pair', 'unique'])
    # statics_data = pd.DataFrame(new_list, columns=['frame_pair', 'candidates', 'windows', 'steps'])
    statics_data = pd.DataFrame(new_list, columns=['frame_pair', 'candidates', 'windows', 'steps', 'c_candidates'])
    sns.lineplot(data=statics_data, x='frame_pair', y='candidates', ax=ax2, color='blue')
    ax2.yaxis.label.set_color('blue')
    ax3 = ax.twinx()
    ax3.spines['right'].set_position(('outward', 40))
    sns.lineplot(data=statics_data, x='frame_pair', y='windows', ax=ax3, color='green')
    ax3.yaxis.label.set_color('green')
    ax4 = ax.twinx()
    ax4.spines['right'].set_position(('outward', 80))
    sns.lineplot(data=statics_data, x='frame_pair', y='steps', ax=ax4, color='red')
    ax4.yaxis.label.set_color('red')
    ax5 = ax.twinx()
    ax5.spines['right'].set_position(('outward', 120))
    sns.lineplot(data=statics_data, x='frame_pair', y='c_candidates', ax=ax5, color='black')
    ax5.yaxis.label.set_color('black')

    plt.gcf().tight_layout()

    # print(pd)
    _save_current_plot('{}_{}_default_detailsall_{}{}'.format(pattern_video, pattern_num, part_id, '_log' if logy else ''))
    # reset
    
    plt.figure(figsize=(6.4,4.8))


def read_value_from_baseline_output(pattern_params, query_params, ids, frame_pair, line_starts):
  video_name, df_name, obj_num, pattern_length, pattern_num = pattern_params
  query_video, query_k = query_params
  result_folder_path = '{}/batch-results2/patterns-{}/{}-{}-{}-{}'.format(file_storage_path, 
      video_name, obj_num, pattern_length, pattern_num, query_video)
  output_path = '{}/{}-{}-{}-{}-{}-{}.txt'.format(result_folder_path, video_name, \
    '_'.join(ids), '_'.join(frame_pair), df_name, query_k, 'baseline')
  with open(output_path, 'r') as rf:
    for line in rf.readlines():
      if line.startswith(line_starts):
        value = int(line.replace(line_starts, '').strip())
        return value

if __name__ == '__main__':
  pattern_videos =[
    ('drtest', 20),
    ('drtrain', 20)
    # ('drtest', 40),
    # ('drtrain', 60)
    # ('bdd100kA', 20),
    # ('bdd100kB', 20)
  ]
  for pv, pattern_num in pattern_videos:
    # plot_details(pv, pattern_num, logy=True, other_axis='unique_edges')
    # plot_details(pv, pattern_num, logy=True, other_axis='unique_edges_per_frame')
    # plot_details(pv, pattern_num, logy=True, other_axis='candidates')
    plot_all_details(pv, pattern_num, logy=True)