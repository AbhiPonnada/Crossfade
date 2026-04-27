import os
import warnings
import threading
import sys

# ✅ Add ffmpeg folder to PATH — must be before any pydub imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ["PATH"] += os.pathsep + os.path.join(BASE_DIR, "ffmpeg")

# ✅ Suppress pydub warnings
warnings.filterwarnings("ignore", message="Couldn't find ffmpeg or avconv")
warnings.filterwarnings("ignore", message="Couldn't find ffprobe or avprobe")

from pydub import AudioSegment
from crossfade import equal_power_crossfade
from player import play_audiosegment, fast_forward, toggle_pause, stop, is_stopped
from recommender import pick_next_song
import keyboard  # pip install keyboard

# -------------------------------------------------------------------
# ✅ Configuration
# -------------------------------------------------------------------
SONGS_DIR = "songs"
FADE_DURATION_MS = 7000

# -------------------------------------------------------------------
# ✅ Key listener
# -------------------------------------------------------------------
def start_key_listener():
    print("Controls:")
    print("  → Right arrow : Fast forward 10 seconds")
    print("  Space         : Pause / Resume")
    print("  Escape        : Stop and exit\n")

    keyboard.add_hotkey("right", lambda: fast_forward(10) or print("\n⏩ Fast forwarding 10 seconds..."))
    keyboard.add_hotkey("space", toggle_pause)
    keyboard.add_hotkey("escape", stop)
    keyboard.wait()  # keeps listener alive

listener_thread = threading.Thread(target=start_key_listener, daemon=True)
listener_thread.start()

# -------------------------------------------------------------------
# ✅ Load songs
# -------------------------------------------------------------------
songs = [
    os.path.join(SONGS_DIR, f)
    for f in os.listdir(SONGS_DIR)
    if f.lower().endswith((".mp3", ".wav", ".flac"))
]

if len(songs) < 2:
    raise RuntimeError("Please add at least two audio files to the songs folder.")

# -------------------------------------------------------------------
# ✅ Playback loop
# -------------------------------------------------------------------
current_song = songs[0]

while True:
    # Check if stopped before starting next song
    from player import is_stopped
    if is_stopped:
        print("Exiting.")
        sys.exit(0)

    next_song = pick_next_song(current_song, songs)

    if next_song is None:
        print("No more songs to play.")
        break

    print(f"Crossfading:\n  {current_song} → {next_song}")

    final_mix = equal_power_crossfade(
        current_song,
        next_song,
        FADE_DURATION_MS
    )

    print(f"Duration: {len(final_mix)}ms")

    play_audiosegment(final_mix)

    # Exit cleanly if stopped during playback
    from player import is_stopped
    if is_stopped:
        print("Exiting.")
        sys.exit(0)

    current_song = next_song