from pydub import AudioSegment

def equal_power_crossfade(song_a_path, song_b_path, fade_duration_ms):
    """
    Smooth equal-power crossfade between two audio files.

    Parameters:
        song_a_path (str): Path to current song
        song_b_path (str): Path to next song
        fade_duration_ms (int): Crossfade duration in milliseconds

    Returns:
        AudioSegment: Combined crossfaded audio
    """

    # Load audio files
    song_a = AudioSegment.from_file(song_a_path)
    song_b = AudioSegment.from_file(song_b_path)

    # Ensure fade duration is safe
    fade_duration_ms = min(
        fade_duration_ms,
        len(song_a) - 1000,
        len(song_b) - 1000
    )

    if fade_duration_ms <= 0:
        raise ValueError("Fade duration too long for one of the tracks.")

    # Split Song A
    a_main = song_a[:-fade_duration_ms]
    a_fade = song_a[-fade_duration_ms:]

    # Split Song B
    b_fade = song_b[:fade_duration_ms]
    b_main = song_b[fade_duration_ms:]

    # Apply fades
    a_fade = a_fade.fade_out(fade_duration_ms)
    b_fade = b_fade.fade_in(fade_duration_ms)

    # Overlay fade segments
    crossfaded = a_fade.overlay(b_fade)

    # Combine final track
    final_mix = a_main + crossfaded + b_main

    return final_mix