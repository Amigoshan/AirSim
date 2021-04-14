import os
import setup_path 
import airsim
import time
import numpy as np
import sys

script_dir = os.path.dirname(__file__)

client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)

print("arming the drone...")
client.armDisarm(True)

def play_sound(wavfile):
    import speaker
    import wav_reader
    reader = wav_reader.WavReader()
    reader.open(wavfile, 512, speaker.Speaker())
    while True:
        buffer = reader.read()
        if buffer is None:
            break

class Numbers:
    def __init__(self):
        self.data = []

    def add(self, x):
        self.data += [x]

    def is_unstable(self, amount):
        a = np.array(self.data)
        minimum = a.min()
        maximum = a.max()
        mean = np.mean(a)
        stddev = np.std(a)
        print("min={}, max={}, mean={}, stddev={}".format(minimum, maximum, mean, stddev))
        return (maximum - minimum) > amount

while True:
    x = Numbers()
    y = Numbers()
    z = Numbers()

    while client.getMultirotorState().landed_state == airsim.LandedState.Landed:
        print("taking off...")
        client.takeoffAsync().join()
        time.sleep(1)

    # fly for a minute
    start = time.time()
    while time.time() < start + 20:
        state = client.getMultirotorState()
        x_val = state.kinematics_estimated.position.x_val
        y_val = state.kinematics_estimated.position.y_val
        z_val = state.kinematics_estimated.position.z_val
        x.add(x_val)
        y.add(y_val)
        z.add(state.gps_location.altitude)
        print("x: {}, y: {}, z: {}".format(x_val, y_val, z_val))
        time.sleep(1)

    print("landing...")
    client.landAsync().join()
    
    # more than 50 centimeter drift is unacceptable.
    a = x.is_unstable(0.5)
    b = y.is_unstable(0.5)
    c = z.is_unstable(0.5)

    if a or b or c:
        play_sound(os.path.join(script_dir, "Error.wav"))

    time.sleep(5)

    
