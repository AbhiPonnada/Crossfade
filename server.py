import os
import threading
from flask import Flask, request, jsonify, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ["PATH"] += os.pathsep + os.path.join(BASE_DIR, "ffmpeg")

from player import play_audiosegment, fast_forward, toggle_pause, stop
from crossfade import equal_power_crossfade
from recommender import pick_next_song

app = Flask(__name__, static_folder='static')

SONGS_DIR = "songs"
ALLOWED = {'.mp3', '.wav', '.flac', '.ogg', '.aac', '.m4a'}
os.makedirs(SONGS_DIR, exist_ok=True)

playback_thread = None
is_running = False
current_song_name = ""
next_song_name = ""

def get_songs():
    return [f for f in os.listdir(SONGS_DIR) if os.path.splitext(f)[1].lower() in ALLOWED]

def playback_loop():
    global is_running, current_song_name, next_song_name
    import player
    songs = [os.path.join(SONGS_DIR, f) for f in get_songs()]
    if len(songs) < 2:
        is_running = False
        return
    current = songs[0]
    is_running = True
    while is_running:
        if player.is_stopped:
            is_running = False
            break
        nxt = pick_next_song(current, songs)
        if not nxt:
            break
        current_song_name = os.path.basename(current)
        next_song_name = os.path.basename(nxt)
        try:
            mix = equal_power_crossfade(current, nxt, 7000)
            play_audiosegment(mix)
        except Exception as e:
            print(f"Playback error: {e}")
            break
        current = nxt
    is_running = False

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/songs')
def list_songs():
    return jsonify({'songs': get_songs()})

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('songs')
    saved = []
    for f in files:
        ext = os.path.splitext(f.filename)[1].lower()
        if ext not in ALLOWED:
            continue
        f.save(os.path.join(SONGS_DIR, f.filename))
        saved.append(f.filename)
    if not saved:
        return jsonify({'error': 'No valid audio files'}), 400
    return jsonify({'saved': saved})

@app.route('/bpm/<filename>')
def get_bpm(filename):
    try:
        import librosa
        path = os.path.join(SONGS_DIR, filename)
        if not os.path.exists(path):
            return jsonify({'error': 'File not found'}), 404
        y, sr = librosa.load(path, duration=60)  # analyse first 60s only for speed
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        return jsonify({'bpm': round(float(tempo), 1)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/control/play', methods=['POST'])
def play():
    global playback_thread, is_running
    import player
    player.is_stopped = False
    if not is_running:
        playback_thread = threading.Thread(target=playback_loop, daemon=True)
        playback_thread.start()
        return jsonify({'status': 'playing'})
    else:
        toggle_pause()
        return jsonify({'status': 'toggled'})

@app.route('/control/pause', methods=['POST'])
def pause():
    toggle_pause()
    return jsonify({'status': 'paused'})

@app.route('/control/stop', methods=['POST'])
def stop_route():
    global is_running
    stop()
    is_running = False
    return jsonify({'status': 'stopped'})

@app.route('/control/skip', methods=['POST'])
def skip():
    fast_forward(10)
    return jsonify({'status': 'skipped'})

@app.route('/control/next', methods=['POST'])
def next_song():
    import player
    player.is_stopped = True
    return jsonify({'status': 'next'})

@app.route('/status')
def status():
    return jsonify({
        'is_playing': is_running,
        'current': current_song_name,
        'next': next_song_name,
    })

if __name__ == '__main__':
    print("Server running at http://localhost:5000")
    app.run(debug=False, port=5000)