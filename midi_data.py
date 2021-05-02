import math

def note_to_freq(note):
    return 2**((note-69)/12)*440

def freq_to_note(freq):
    return math.log((freq/440)*12+69,base=2)
