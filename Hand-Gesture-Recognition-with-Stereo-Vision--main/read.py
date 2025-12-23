import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
from matplotlib.widgets import Slider

# Load your MAT file
mat_data = loadmat('hand_positions.mat')  # Adjust the file name
data = mat_data['positions']  # Adjust the key according to your mat file structure

# Calculate means of each segment
segment_length = 21
means = np.mean(data.reshape(-1, 3, segment_length), axis=2)

# Create a figure and a set of subplots
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25)  # Adjust subplot to make room for the slider

# Initial plot
time_point = 0
lines, = ax.plot(means[time_point, :], marker='o', linestyle='-')
ax.set_xlim(-0.5, 2.5)  # Since there are three points: X, Y, Z
ax.set_xticks([0, 1, 2])
ax.set_xticklabels(['X', 'Y', 'Z'])
ax.set_title('3D Points Mean at Time {}'.format(time_point + 1))

# Add a slider
axcolor = 'lightgoldenrodyellow'
axtime = plt.axes([0.1, 0.1, 0.8, 0.03], facecolor=axcolor)
stime = Slider(axtime, 'Time', 1, data.shape[0], valinit=1, valfmt='%d')

# Update function for the slider
def update(val):
    time_point = int(stime.val) - 1
    lines.set_ydata(means[time_point, :])
    ax.set_title('3D Points Mean at Time {}'.format(time_point + 1))
    fig.canvas.draw_idle()

# Call update function on slider value change
stime.on_changed(update)

plt.show()
# Calculate means of each segment
segment_length = 21
means = np.mean(data.reshape(-1, 3, segment_length), axis=2)

# Plotting
fig, ax = plt.subplots()
time_points = np.arange(means.shape[0])
ax.plot(time_points, means[:, 0], label='X Mean')  # Mean of first segment (X)
ax.plot(time_points, means[:, 1], label='Y Mean')  # Mean of second segment (Y)
ax.plot(time_points, means[:, 2], label='Z Mean')  # Mean of third segment (Z)

# Adding labels and title
ax.set_xlabel('Time Points')
ax.set_ylabel('Mean Values')
ax.set_title('Mean of Segments Over Time')
ax.legend()

plt.show()
