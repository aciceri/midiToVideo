#!/usr/bin/env python3

"""
This script is structured using classes because the initial idea was to create
a library, however I had no time to do that and at the moment this source is full
of hardcoded values specific for this particular midi.
"""

from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip, concatenate_videoclips, clips_array
import mido

notes = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']  # name of the notes


class Instrument:
    def __init__(self, folder, octaves=(1, 8)):
        self.clips = []
        self.octaves = octaves
        self._import_clips(folder)

    def _import_clips(self, folder):
        for n in range(self.octaves[0] * 12, self.octaves[1] * 12):
            note_name = f"{n // 12}{notes[(n %12)]}"
            freq = 55 * 2 ** (n / 12)
            self.clips.append({"note": note_name,
                               "freq": freq,
                               "clip": VideoFileClip(f"{folder}/{note_name}.mp4")})

    def get_clip(self, midi_note):
        return self.clips[midi_note]['clip']


class SheetMusic:
    def __init__(self, path, max_length=8):
        self.max_length = max_length
        self.channels = {}
        # if a note lasts more than this its length will be clipped
        self._import_midi(path)

    def _import_midi(self, path):
        midi = mido.MidiFile(path)
        time = 0
        for msg in midi:
            time += msg.time
            if not msg.is_meta:
                if msg.channel not in self.channels.keys():  # if the actual message is from a new channel
                    self.channels[msg.channel] = []  # create a new key in channels (empty for now)
                # Important: note_off (for every velocity) and note_on with velocity 0 are the same!
                if msg.type == 'note_on' and msg.velocity != 0:
                    self.channels[msg.channel].append({'note': msg.note,
                                                'start': time,
                                                'end': None})
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    for cn, note in enumerate(self.channels[msg.channel]):
                        if note['note'] == msg.note and note['end'] == None:
                            if time - self.channels[msg.channel][cn]['start'] > self.max_length:
                                self.channels[msg.channel][cn]['end'] = self.channels[msg.channel][i]['start'] + self.max_length
                            else:
                                self.channels[msg.channel][cn]['end'] = time
                            break

    def render(self, instrument_path, output_path):

        channel_clips = [None] * len(self.channels)
        ins = Instrument(folder=instrument_path, octaves = (1, 8))

        offset = [-1, -2, -2]  # pitch offset (multiplied by 12 semitones) for every channels
        for cn, channel in enumerate(self.channels):
            clips = []
            time = 0
            for i, note in enumerate(self.channels[channel]):
                if note['start'] > time:
                    clips.append(TextClip(" ",  # it's an empty black clip for the pause (when no note is playing)
                                          size=(640, 480),
                                          color='white',
                                          bg_color='black').\
                                 set_duration(note['start'] - time).\
                                 set_fps(30).\
                                 set_start(time))
                    time = note['start']
                clips.append(ins.get_clip(note['note'] + 12 * offset[cn]).\
                             subclip(0, note['end'] - note['start']).\
                             set_start(time))
                time = note['end']

            channel_clips[channel] = CompositeVideoClip(clips).\
                volumex(0.3).\
                resize((640, 480))

        title = " The musical offering \n Canon perpetuus super thema regium \n B.W.V 1079 - J. S. Bach "
        title_clip = TextClip(title,
                              size = (640, 480),
                              color="white",
                              bg_color="black").\
                              set_duration(max([c.duration for c in channel_clips])).\
                              set_fps(30)
        clips_array([[title_clip, channel_clips[1]],
                     [channel_clips[0], channel_clips[2]]]).\
                     write_videofile(output_path)


SheetMusic("bach.mid").render("../../samples/recorder", "bach.mp4")
