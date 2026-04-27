import librosa
import numpy as np

def analyze_track(path):
    y, sr = librosa.load(path, mono=True)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    rms = np.mean(librosa.feature.rms(y=y))
    duration = librosa.get_duration(y=y, sr=sr)

    return {
        "tempo": tempo,
        "loudness": rms,
        "beats": beats,
        "duration": duration
    }