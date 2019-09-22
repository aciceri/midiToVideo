#!/usr/bin/env python3

import numpy as np
from moviepy.editor import TextClip, AudioClip, VideoFileClip
from moviepy.audio.AudioClip import AudioArrayClip
from librosa.effects import pitch_shift

input_file = 'input.mp4'  # path of the input file
starting_times = (9, 25, 40, 52, 65, 77, 89, 121, 137, 157, 170, 184)
# times in seconds when each note starts in the input video
length = 8  # length of the generated clips
octaves = (0, 9)  # range of octaves
resolution = (600, 800)  # video resolution of the outputs

notes = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']  # name of the notes

src_clips = [VideoFileClip(input_file).\
             subclip(start, start + length).\
             volumex(0.6)
             for start in starting_times]
# this list contains the clips for each note in the input video

for n in range(octaves[0] * 12, octaves[1] * 12):
    note_name = f"{n // 12}{notes[(n % 12)]}"
    clip = src_clips[(n - 3) % 12].copy()
    # the '-3' is because notes starts with 'C' but during the generation they starts from 'A'
    trans = (((n - 3) // 12) - 5) * 12  # transposition offset
    clip.audio = AudioArrayClip(
        np.transpose(
            np.stack(
                [pitch_shift(  # this function does the trick
                    np.transpose(clip.audio.to_soundarray())[channel],
                    48000,  # it's the sampling of the source video
                    n_steps = trans) for channel in (0, 1)])),  # (0, 1) because the source is stereo
        fps = 48000)
    clip.write_videofile(f"{note_name}.mp4")

