import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

data_points = list()
for i in range (10):
  data_points.append(('str'+str(i), i, (i+1)*10, (i+3)*100))
data_frame = pd.DataFrame(data=data_points, columns=['name', 'y1', 'y2', 'y3'])

offset = 60

ax = plt.gca()
sns.lineplot(data=data_frame, x='name', y='y1', color='red')
ax.yaxis.label.set_color('red')

ax2 = ax.twinx()
ax2.set_ylim(0, 110)
sns.lineplot(data=data_frame, x='name', y='y2', ax=ax2, color='blue')
ax2.yaxis.label.set_color('blue')

ax3 = ax.twinx()
ax3.set_ylim(0, 1300)
# adjust pos
ax3.spines['right'].set_position(('outward', 60))
sns.lineplot(data=data_frame, x='name', y='y3', ax=ax3, color='yellow')
ax3.yaxis.label.set_color('yellow')
plt.gcf().tight_layout()

plt.show()