"""The verified anthem melody (as transcribed from the score), shared by the check scripts.
Source key: E minor (cantorion 3849 score and the MIDI). Pitches as MIDI numbers, durations in quarter beats.
Structure: pickup + a (bars 1-10) + b (bars 11-20); the stanza is a b b."""
E = {'B3': 59, 'E4': 64, 'F#4': 66, 'G4': 67, 'A4': 69, 'B4': 71, 'C5': 72, 'D5': 74, 'E5': 76}

A_BARS = [
    [('E4', 1.5), ('F#4', .5), ('G4', 1), ('A4', 1)],
    [('B4', 2), ('E4', 1), ('E4', 1)],
    [('C5', 1.5), ('B4', .5), ('A4', 1), ('A4', 1)],
    [('D5', 1.5), ('C5', .5), ('B4', 1), ('B4', 1)],
    [('E5', 1.5), ('D5', .5), ('C5', .5), ('B4', .5), ('A4', 1)],
    [('B4', 1), ('G4', 2), ('A4', 1)],
    [('B4', 1.5), ('A4', .5), ('G4', 1), ('F#4', 1)],
    [('E4', 1.5), ('F#4', .5), ('G4', 1), ('A4', 1)],
    [('B4', 1), ('A4', .5), ('G4', .5), ('F#4', 1), ('G4', 1)],
    [('E4', 2), (None, 1), ('E4', 1)],          # last quarter = upbeat "A-" into b
]
B_BARS = [
    [('E4', 1.5), ('E5', .5), ('E5', 1), ('E5', 1)],
    [('E5', 2), ('D5', 1), ('D5', 1)],
    [('E5', 1.5), ('D5', .5), ('C5', .5), ('B4', .5), ('A4', 1)],
    [('D5', 1.5), ('C5', .5), ('B4', 1), ('B4', 1)],
    [('E5', 1.5), ('D5', .5), ('C5', .5), ('B4', .5), ('A4', 1)],
    [('B4', 1), ('G4', 2), ('A4', 1)],
    [('B4', 1.5), ('A4', .5), ('G4', 1), ('F#4', 1)],
    [('E4', 1.5), ('F#4', .5), ('G4', 1), ('A4', 1)],
    [('B4', 1), ('A4', .5), ('G4', .5), ('F#4', 1), ('G4', 1)],
    [('E4', 3), ('E4', 1)],                     # 1st ending: upbeat "A-" again; 2nd ending: E4 3 + rest
]
B_LAST = [('E4', 3), (None, 1)]


def stanza(transpose=0):
    """List of (midi or None, beats) for pickup + a + b + b (2nd ending)."""
    seq = [(E['B3'] + transpose, 1)]
    bars = A_BARS + B_BARS + B_BARS[:-1] + [B_LAST]
    for bar in bars:
        for n, d in bar:
            seq.append((None if n is None else E[n] + transpose, d))
    return seq


def notes_only(transpose=0):
    return [p for p, d in stanza(transpose) if p is not None]
