"""Don't forget your docstrings!

<3 Jason
"""
from time import sleep
import librosa
import numpy as np
import pygame
from hue_api import HueApi

BRIDGE_IP_ADDRESS = '192.168.0.20'
USERNAME = 'H5xJW-0SeSydktptmIUmTkfiXWdIBvVEyzlbwAzR'


def clamp(min_value, max_value, value):

    if value < min_value:
        return min_value

    if value > max_value:
        return max_value

    return value


class LightState:

    def __init__(self, light, min_brightness=0, max_brightness=255, min_decibel=-80, max_decibel=0):

        self.light = light

        self.min_brightness, self.max_brightness = min_brightness, max_brightness

        self.brightness = min_brightness

        self.min_decibel, self.max_decibel = min_decibel, max_decibel

        self.__decibel_brightness_ratio = (self.max_brightness - self.min_brightness)/(self.max_decibel - self.min_decibel)

    def update(self, dt, decibel):
        """Updates the light state based on the decibel value."""

        desired_brightness = decibel * self.__decibel_brightness_ratio + self.max_brightness

        speed = (desired_brightness - self.brightness)/0.1

        self.brightness += speed * dt

        self.brightness = clamp(self.min_brightness, self.max_brightness, self.brightness)

    def push(self):
        """Pushes the light state to the Hue bulb."""
        self.light.set_brightness(self.brightness)
        print(self.brightness)

# Enter audio file path here
filename = "test.wav"

time_series, sample_rate = librosa.load(filename)  # getting information from the file

# getting a matrix which contains amplitude values according to frequency and time indexes
stft = np.abs(librosa.stft(time_series, hop_length=512, n_fft=2048*4))

spectrogram = librosa.amplitude_to_db(stft, ref=np.max)  # converting the matrix to decibel matrix

frequencies = librosa.core.fft_frequencies(n_fft=2048*4)  # getting an array of frequencies

# getting an array of time periodic
times = librosa.core.frames_to_time(np.arange(spectrogram.shape[1]), sr=sample_rate, hop_length=512, n_fft=2048*4)

time_index_ratio = len(times)/times[len(times) - 1]

frequencies_index_ratio = len(frequencies)/frequencies[len(frequencies)-1]

def get_decibel(target_time, freq):
    return spectrogram[int(freq * frequencies_index_ratio)][int(target_time * time_index_ratio)]


pygame.init()
print("Playing audio...")

# Initialize Hue API
api = HueApi()
api.user_name = USERNAME
api.bridge_ip_address = BRIDGE_IP_ADDRESS
api.base_url = f'http://{BRIDGE_IP_ADDRESS}/api/{USERNAME}'

lights = api.fetch_lights()
light = lights[0]

# Create a lightstate
light_state = LightState(light, min_decibel=-80, max_decibel=0)

t = pygame.time.get_ticks()
getTicksLastFrame = t

pygame.mixer.music.load(filename)
pygame.mixer.music.play(0)

brightness = 0
color = 0
# Run until the user asks to quit
running = True
while running:

    t = pygame.time.get_ticks()
    deltaTime = (t - getTicksLastFrame) / 1000.0
    getTicksLastFrame = t

    # Update the state of the light and push it to the Hue
    # light_state.update(deltaTime, get_decibel(pygame.mixer.music.get_pos()/1000.0, 440))
    # light_state.push()

    brightness = (brightness + 10) % 130
    color = (color + 200) % 70000
    light_state.light.set_brightness(brightness)
    light_state.light.set_color(color, 125)
    print(brightness, color)

    sleep(0.1)

# Done! Time to quit.
pygame.quit()
