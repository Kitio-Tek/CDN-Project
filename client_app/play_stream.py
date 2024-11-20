# client_app/play_stream.py
import vlc
import time

def play_stream(file_path):
    """
    Play a video file using VLC.
    """
    player = vlc.MediaPlayer(file_path)
    player.play()
    # Keep the script running while the media is playing
    while True:
        state = player.get_state()
        if state in [vlc.State.Ended, vlc.State.Error]:
            break
        time.sleep(1)
    player.stop()

if __name__ == "__main__":
    FILE_PATH = 'downloaded_content'  # Path to the downloaded content
    play_stream(FILE_PATH)
