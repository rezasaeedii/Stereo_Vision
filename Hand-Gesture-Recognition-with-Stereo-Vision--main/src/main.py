import numpy as np
import math
from stereohand import StereoHand
from stereovision import Stereo
from scipy.io import savemat
import pandas as pd
import sys

data_accumulator = np.empty((0, 63), dtype=float)

def update_data_accumulator(x, y, z):
    global data_accumulator
    new_data = np.array(x + y + z).reshape(1, 63)
    data_accumulator = np.append(data_accumulator, new_data, axis=0)

def save_data_to_mat():
    global data_accumulator
    print(">> Saving data to 'hand_positions.mat'...")
    savemat('hand_positions.mat', {'positions': data_accumulator})


def get_distance(x1, y1, z1, x2, y2, z2):
    return math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)


if __name__ == '__main__':
    so = Stereo(b=9.4, f=650, disparity_shift=0) 
    stereo_hand_instance = StereoHand(so)

    print(">> ROBUST YAW DETECTION (Open/Fist) STARTED.")
    print(f"{'IDX':<5} | {'STATE':<8} | {'YAW (deg)':<10} | {'DIRECTION'}")
    print("-" * 60)

    index = 0
    try:
        while True:
           
            found, pos3d = stereo_hand_instance.get_hand()
            
            if not found:
                continue 

           
            x = [p[0] for p in pos3d]
            y = [p[1] for p in pos3d]
            z = [p[2] for p in pos3d]

            update_data_accumulator(x, y, z)

            x_wrist, z_wrist = x[0], z[0]
            x_knuckle, z_knuckle = x[9], z[9]

            
            delta_x = x_knuckle - x_wrist
            delta_z = z_knuckle - z_wrist

            yaw_angle = math.degrees(math.atan2(delta_x, delta_z))

            
            dist_wrist_to_tip = get_distance(x[0], y[0], z[0], x[12], y[12], z[12])
            dist_wrist_to_knuckle = get_distance(x[0], y[0], z[0], x[9], y[9], z[9])
            
            hand_state = "OPEN "
            if dist_wrist_to_tip < (dist_wrist_to_knuckle * 1.2): 
                hand_state = "FIST "

           
            if index % 10 == 0:
                direction = "---"
                if -15 < yaw_angle < 15:
                    direction = "STRAIGHT"
                elif yaw_angle >= 15:
                    direction = "LEFT"
                elif yaw_angle <= -15:
                    direction = "RIGHT"

                print(f"{index:<5} | {hand_state:<8} | {yaw_angle:<10.1f} | {direction}")

            index += 1

    except KeyboardInterrupt:
        save_data_to_mat()
        sys.exit()