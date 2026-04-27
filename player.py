import sounddevice as sd
import numpy as np
import time

OUTPUT_DEVICE_INDEX = 4  # Speakers (BH900 PRO)

CHUNK_SIZE = 4096
current_position = 0
is_playing = False
is_paused = False
is_stopped = False
samples_global = None
samplerate_global = None


def fast_forward(seconds=10):
    """Skip forward by N seconds."""
    global current_position, samplerate_global
    if samplerate_global:
        current_position += int(seconds * samplerate_global)


def pause():
    """Pause playback."""
    global is_paused
    is_paused = True
    print("\n⏸  Paused.")


def resume():
    """Resume playback."""
    global is_paused
    is_paused = False
    print("\n▶  Resumed.")


def toggle_pause():
    """Toggle between pause and resume."""
    if is_paused:
        resume()
    else:
        pause()


def stop():
    """Stop playback and exit."""
    global is_playing, is_stopped
    is_playing = False
    is_stopped = True
    print("\n⏹  Stopped.")


def play_audiosegment(audio):
    """
    Plays a pydub AudioSegment using sounddevice.
    Supports fast forward, pause, resume, and stop.
    """
    global current_position, is_playing, is_paused, is_stopped
    global samples_global, samplerate_global

    samples = np.array(audio.get_array_of_samples(), dtype=np.float32)

    if audio.sample_width == 2:
        samples /= 32768.0
    elif audio.sample_width == 4:
        samples /= 2147483648.0

    if audio.channels == 2:
        samples = samples.reshape((-1, 2))
    else:
        samples = np.column_stack((samples, samples))

    current_position = 0
    is_playing = True
    is_paused = False
    samples_global = samples
    samplerate_global = audio.frame_rate

    with sd.OutputStream(
        device=OUTPUT_DEVICE_INDEX,
        channels=2,
        samplerate=audio.frame_rate,
        dtype="float32"
    ) as stream:
        while is_playing:
            # If paused, wait without advancing position
            if is_paused:
                time.sleep(0.1)
                continue

            start = current_position
            end = start + CHUNK_SIZE

            if start >= len(samples):
                break

            chunk = samples[start:end]
            stream.write(chunk)
            current_position += len(chunk)

    is_playing = False