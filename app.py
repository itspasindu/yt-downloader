from flask import Flask, request, render_template, send_file
from pytube import YouTube
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        url = request.form['url']
        print(f"Received URL: {url}")
        
        yt = YouTube(url)
        streams = yt.streams.filter(progressive=True).order_by('resolution').desc()
        stream = streams.first()
        
        if not stream:
            return "No suitable stream found", 400
            
        if os.path.exists('downloads/video.mp4'):
            os.remove('downloads/video.mp4')
            
        stream.download(output_path='downloads', filename='video.mp4')
        return send_file('downloads/video.mp4', as_attachment=True)
        
    except Exception as e:
        return f"An error occurred: {str(e)}", 400

@app.route('/download_audio', methods=['POST'])
def download_audio():
    try:
        url = request.form['url']
        print(f"Received URL: {url}")
        
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        
        if not audio_stream:
            return "No audio stream found", 400
            
        if os.path.exists('downloads/audio.mp4'):
            os.remove('downloads/audio.mp4')
            
        audio_stream.download(output_path='downloads', filename='audio.mp4')
        return send_file('downloads/audio.mp4', as_attachment=True)
        
    except Exception as e:
        return f"An error occurred: {str(e)}", 400

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True)