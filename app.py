from flask import Flask, request, render_template, send_file
from pytube import YouTube
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    print(f"Received URL for video download: {url}")  # Debugging line
    try:
        yt = YouTube(url)
        streams = yt.streams.filter(progressive=True).order_by('resolution').desc()
        available_streams = {stream.resolution: stream for stream in streams}
        stream = available_streams.get('1080p') or available_streams.get('720p') or streams.first()
        stream.download(output_path='downloads', filename='video.mp4')
        return send_file('downloads/video.mp4', as_attachment=True)
    except Exception as e:
        return f"An error occurred: {str(e)}", 400  # Return a 400 error with a message

@app.route('/download_audio', methods=['POST'])
def download_audio():
    url = request.form['url']
    print(f"Received URL for audio download: {url}")  # Debugging line
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_stream.download(output_path='downloads', filename='audio.mp4')
        return send_file('downloads/audio.mp4', as_attachment=True)
    except Exception as e:
        return f"An error occurred: {str(e)}", 400  # Return a 400 error with a message

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True)