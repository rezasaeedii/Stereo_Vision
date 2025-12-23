import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from stereohand import StereoHand
from stereovision import Stereo
from collections import deque
from scipy.io import savemat
import pandas as pd
import time


data_accumulator = np.empty((0, 63), dtype=float)

def update_data_accumulator(x, y, z):
    global data_accumulator
    # Flatten x, y, z into a single array and reshape to (1, 63) for concatenation
    new_data = np.array(x + y + z).reshape(1, 63)
    # Append new data to the accumulator
    data_accumulator = np.append(data_accumulator, new_data, axis=0)

def save_data_to_mat():
    global data_accumulator
    # Save the accumulated data to a .mat file
    savemat('hand_positions.mat', {'positions': data_accumulator})

def save_positions_to_csv(x, y, z):
    # Flatten x, y, and z into a single list
    all_coords = x + y + z
    # Convert to DataFrame for easy CSV output
    df = pd.DataFrame([all_coords])  # Enclosed in a list to ensure it's treated as a single row
    df.to_csv('hand_positions.csv', index=False, mode='a', header=False)

COP1 = (658, 348) # location of the center of projection for camera 1
COP2 = (516, 237) # location of the center of projection for camera 2

so = Stereo(b=9.4, f=1080, disparity_shift=(COP1[0] - COP1[0])) # Stereo Object for Stereo hand initialization
stereo_hand_instance = StereoHand(so)

z_data = deque(maxlen=30)
x_data = deque(maxlen=30)
y_data = deque(maxlen=30)


#plt.show()
log_counter = 0
index = 0
try:
    while True:
        t0 = time.perf_counter() # time measurement
        found, pos3d = stereo_hand_instance.get_hand() # x y z in pos3d
        if not found:
            continue
        x = [e[0] for e in pos3d]
        y = [e[1] for e in pos3d]
        z = [e[2] for e in pos3d]
        if index % 10 ==0:
            print(f"index = {index}")
        index+=1
        update_data_accumulator(x, y, z)
        t1 = time.perf_counter()  # time measurement
        frame_latency = t1 - t0  # time measurement
        if index % 10 ==1:
            print(f"latency = {frame_latency:.4f} s")
        average_z = sum(z) / len(z)
        average_x = sum(x) / len(x)
        average_y = sum(y) / len(y)
        z_data.append(average_z)  # Add the new value to the deque
        x_data.append(average_x)
        y_data.append(average_y)
        '''plt.cla()  # Clear the previous plot
        plt.plot(z_data, label="Z")  # Plot the current values
        plt.plot(x_data, label="X")
        plt.plot(y_data, label="Y")
        plt.legend(loc="upper left")
        plt.ylim(min(min(y_data), min(x_data)), max(max(z_data), max(x_data), max(y_data)))  # Set axis limits based on data
        plt.draw()
        plt.pause(0.001)  # Pause briefly to avoid overwhelming the display'''
        log_counter += 1
        if log_counter == 6:
            print(f"\t{average_x}\t{average_y}\t{average_z}")
            log_counter = 0
except KeyboardInterrupt:
    # Save on exit
    save_data_to_mat()
    print("Data saved and program exited.")
    