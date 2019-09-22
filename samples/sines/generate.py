#!/usr/bin/env python3

import numpy as np
from moviepy.editor import TextClip, AudioClip

length = 8  # length of each note
octaves = (0, 9)  # range of generated notes
resolution = (640, 480)  # video resolution of generated clips
fps = 30  # frame per seconds of generated clips

notes = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']  # names of the notes

wave = lambda freq: lambda t : [np.sin(freq * 2 * np.pi * t)]  # wave(freq) returns a sin(t) function

for n in range(octaves[0] * 12, octaves[1] * 12):
    freq = 55 * 2 ** (n / 12)  # A0 is 55Hz
    note_name = f'{n // 12}{notes[(n % 12)]}'
    audio = AudioClip(wave(freq),
                      duration=length).set_fps(fps)  # generate the audio for the clip
    text = TextClip(f' {note_name} ',
                    size = resolution,
                    color = 'white',
                    bg_color = 'black').\
                margin(10, color = (255, 255, 255)).\
                set_duration(length).\
                set_fps(fps)
    text.audio = audio
    text.write_videofile(f"{note_name}.mp4")
