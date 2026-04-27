import random

def pick_next_song(current_song, songs):
    candidates = [s for s in songs if s != current_song]
    if not candidates:
        return None
    return random.choice(candidates)