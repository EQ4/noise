import cnoise
import ctypes
import ntype
import pyaudio
import struct
import random
import math
from collections import deque

context=cnoise.NoiseContext()
context.chunk_size = 128
context.frame_rate = 48000

context.load('blocks.py')

class SchedulerBlock(cnoise.Block):
    num_inputs = 1
    num_outputs = 1
    input_names = ["t"]
    output_names = ["events_out"]

    @cnoise.Block.pull_fn
    def pull(self):
        if len(self.schedule) == 0:
            return None
        (et,e)=self.schedule[0]
        t=self.input_pull(0,ctypes.c_double)
        if t is None:
            return None
        if t.value > et:
            self.schedule.popleft()
            return e
        return None

    def __init__(self,schedule):
        self.pull_fns=[cnoise.PULL_FN_PT(self.pull)]
        self.schedule=deque(schedule)
        cnoise.Block.__init__(self)

class NOTE_T(ctypes.Structure):
    _fields_=[
        ('event',ctypes.c_int),
        ('note',ctypes.c_int),
        ('velocity',ctypes.c_double)
    ]

    def __init__(self,note,event=1,velocity=1):
        self.event=event
        self.note=note
        self.velocity=velocity

n_chunk=context.get_type('chunk')
n_double=context.get_type('double')
n_int=context.get_type('int')

dt = context.blocks["ConstantBlock"](n_double.new(0.002))
timebase = context.blocks["AccumulatorBlock"]()
timebase.set_input(0,dt,0)

timebase_splitter=context.blocks["TeeBlock"](2,n_double)
timebase_splitter.set_input(0,timebase,0)

sb=SchedulerBlock([(1,NOTE_T(69)),(2,NOTE_T(73)),(3,NOTE_T(76)),(6,NOTE_T(69,0)),(6,NOTE_T(73,0)),(6,NOTE_T(76,0))])
sb.set_input(0,timebase_splitter,1)

syn=context.blocks["SynthBlock"](.05,2,.2,.4)
syn.set_input(0,sb,0)

audio_joiner=context.blocks["WyeBlock"](2,n_chunk)
audio_joiner.set_input(0,syn,0)
audio_joiner.set_input(1,timebase_splitter,0)

cb_vol=context.blocks["ConstantBlock"](n_double.new(0.1))

mixer=context.blocks["MixerBlock"](1)
mixer.set_input(0,audio_joiner,0)
mixer.set_input(1,cb_vol,0)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32,
    channels=1,
    rate=context.frame_rate,
    frames_per_buffer=context.chunk_size,
    output=True)

while True:
    try:
        result=mixer.output_pull(0,ctypes.c_double*context.chunk_size)
        data=struct.pack('f'*context.chunk_size,*result)
        stream.write(data)

    except KeyboardInterrupt:
        break
stream.stop_stream()
stream.close()

import sys
sys.exit()

if __name__ == "__main__":
    heap=[]

    def instrument(notes,tb,tbout,wave_shape):
        # Build melody
        global heap
        melody_array = context.get_type('double[{0}]'.format(len(notes))).new(notes)

        melody_notes = context.blocks["ConstantBlock"](melody_array)
        melody_seq = context.blocks["SequencerBlock"](melody_array) # could also call this with a type
        melody_seq.set_input(0,tb,tbout)
        melody_seq.set_input(1,melody_notes,0)
        melody_freqs = context.blocks["NoteToFreqBlock"]()
        melody_freqs.set_input(0,melody_seq,0)
        melody_wave_shape = context.blocks["ConstantBlock"](n_int.new(wave_shape))
        melody_voice = context.blocks["WaveBlock"]()
        melody_voice.set_input(0,melody_freqs,0)
        melody_voice.set_input(1,melody_wave_shape,0)
        heap.append(melody_notes)
        heap.append(melody_seq)
        heap.append(melody_freqs)
        heap.append(melody_wave_shape)
        return melody_voice

    def drum(waveform,hits,tb,tbout):
        global heap
        hits_array = context.get_type('int[{0}]'.format(len(hits))).new(hits)
        hits_const = context.blocks["ConstantBlock"](hits_array)
        hits_seq = context.blocks["SequencerBlock"](hits_array)
        hits_seq.set_input(0,tb,tbout)
        hits_seq.set_input(1,hits_const,0)
        voice = context.blocks["SampleBlock"](waveform)
        voice.set_input(0,hits_seq,0)
        heap.append(hits_const)
        heap.append(hits_seq)
        return voice

    unison =         [None, None, None, 65, 75, None, 72, 67, 67, 68, None, 65, 70, 72, 70, 65, 65, None, None, 65, 75, None, 72, 67, 67, 68, 65, 72, 75, None, 72, 77]
    unison_harmony = [None, None, None, 61, 61, None, 61, 63, 63, 63, None, 63, 58, 58, 58, 65, 65, None, None, 65, 65, None, 65, 63, 63, 63, 63, 63, 68, None, 68, 61]
    unison_snare = [None, None, 1, 1]*8
    unison_kick = [1, 1, None, None]*8

    n_double=context.get_type('double')
    n_int=context.get_type('int')

    # Build a timebase
    dt = context.blocks["ConstantBlock"](n_double.new(0.01))
    timebase = context.blocks["AccumulatorBlock"]()
    timebase.set_input(0,dt,0)

    timebase_splitter=context.blocks["TeeBlock"](3,n_double)
    timebase_splitter.set_input(0,timebase,0)

    def down_octave(n):
        if n is None:
            return None
        return n-12

    tau=.0001
    snare_waveform=[random.uniform(-1,1)*math.exp(-i*tau) for i in range(50000)]
    tau1=.0001
    freq=60
    kick_waveform=[math.cos(2*math.pi*i*freq/48000)*math.exp(-i*tau1) for i in range(50000)]

    mel=instrument(unison,timebase_splitter,0,1)
    cm=instrument(map(down_octave,unison_harmony),timebase_splitter,1,2)
    snare=drum(snare_waveform,unison_snare,timebase_splitter,2)
    kick=drum(kick_waveform,unison_kick,timebase_splitter,3)

    mixer=context.blocks["MixerBlock"](4)
    mel_vol = context.blocks["ConstantBlock"](n_double.new(0.1))
    cm_vol = context.blocks["ConstantBlock"](n_double.new(0.1))
    snare_vol = context.blocks["ConstantBlock"](n_double.new(0.1))
    kick_vol = context.blocks["ConstantBlock"](n_double.new(0.8))

    mixer.set_input(0,mel,0)
    mixer.set_input(1,mel_vol,0)
    mixer.set_input(2,cm,0)
    mixer.set_input(3,cm_vol,0)
    mixer.set_input(4,snare,0)
    mixer.set_input(5,snare_vol,0)
    mixer.set_input(6,kick,0)
    mixer.set_input(7,kick_vol,0)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
        channels=1,
        rate=context.frame_rate,
        frames_per_buffer=context.chunk_size,
        output=True)
 
    while True:
        try:
            result=mixer.output_pull(0,ctypes.c_double*context.chunk_size)
            data=struct.pack('f'*context.chunk_size,*result)
            stream.write(data)

        except KeyboardInterrupt:
            break
    stream.stop_stream()
    stream.close()
