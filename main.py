"""Don't forget your docstrings!

<3 Jason
"""

import librosa
import numpy as np
import pygame


def clamp(min_value, max_value, value):

    if value < min_value:
        return min_value

    if value > max_value:
        return max_value

    return value


class LightState:

    def __init__(self, freq, color, min_brightness=10, max_brightness=100, min_decibel=-80, max_decibel=0):

        self.freq = freq

        self.color = color

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
        pass

# Enter audio file path here
filename = "music3.wav"

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

infoObject = pygame.display.Info()

frequencies = np.arange(100, 8000, 100)

light_state = LightState(freq=440, color=(255, 255, 255), min_brightness=10, max_brightness=100, min_decibel=-80, max_decibel=0)

t = pygame.time.get_ticks()
getTicksLastFrame = t

pygame.mixer.music.load(filename)
pygame.mixer.music.play(0)

# Run until the user asks to quit
running = True
while running:

    t = pygame.time.get_ticks()
    deltaTime = (t - getTicksLastFrame) / 1000.0
    getTicksLastFrame = t

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update the state of the light and push it to the Hue
    light_state.update(deltaTime, get_decibel(pygame.mixer.music.get_pos()/1000.0, light_state.freq))
    light_state.push()

# Done! Time to quit.
pygame.quit()
