import networkx as nx
from matplotlib import pyplot as plt
from matplotlib import image as pimg

class GraphVisualizer:

  def visualize_one(self, nodes, edges, show_arrows=False):
    # assert 
    assert len(nodes['frame'].unique()) <= 1, 'can only visualize one frame'
    G = nx.Graph()
    # node, attr_dict
    node_list = []
    for _idx, row in nodes.iterrows():
      node_list.append(int(row['id']))
    G.add_nodes_from(node_list)
    pos = dict((a, (b, c)) for a,b,c in \
      zip(nodes['id'], nodes['center_x'], nodes['center_y']))
    labels = dict((a, '{}/{:.0f}'.format(a, b)) for a, b in zip(nodes['id'], nodes['class']))
    nx.draw_networkx(G, pos, labels=labels, font_color='orange')
    plt.show()

  def visualize_one_on_frame(self, img, nodes, edges):
    assert len(nodes['frame'].unique()) <= 1, 'can only visualize one frame'
    if type(img) is str:
      img = pimg.imread(img)
    plt.imshow(img)
    self.visualize_one(nodes, edges)

  def interactive_visualize(self, img_func, nodes, edges, frame_range=None):
    if frame_range is None:
      frame_range = (1, nodes['frame'].max())
    for frame in range(*frame_range):
      frame_nodes = nodes[nodes['frame'] == frame]
      frame_edges = edges[edges['frame'] == frame]
      img = img_func(frame)
      self.visualize_one_on_frame(img, frame_nodes, frame_edges)
