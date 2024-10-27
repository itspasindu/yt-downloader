from flask import Flask, request, render_template, send_file
from pytube import YouTube
import os
import re

app = Flask(__name__)

def extract_video_id(url):
    # Patterns for different YouTube URL formats
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)',  # Standard YouTube URL
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^?]+)',              # Shortened youtu.be URL
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^?]+)',    # Embedded YouTube URL
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        url = request.form['url']
        print(f"Received URL: {url}")
        
        # Extract video ID and construct standard YouTube URL
        video_id = extract_video_id(url)
        if not video_id:
            return "Invalid YouTube URL format", 400
            
        standard_url = f"https://youtube.com/watch?v={video_id}"
        print(f"Standardized URL: {standard_url}")

        # Create YouTube object
        yt = YouTube(
            standard_url,
            use_oauth=True,
            allow_oauth_cache=True
        )
        
        print(f"Video title: {yt.title}")
        
        # Get the highest quality progressive stream
        streams = yt.streams.filter(progressive=True).order_by('resolution').desc()
        if not streams:
            return "No suitable streams found for this video", 400
            
        available_streams = {stream.resolution: stream for stream in streams}
        stream = available_streams.get('1080p') or available_streams.get('720p') or streams.first()
        
        if not stream:
            return "No suitable stream found", 400
            
        print(f"Selected stream resolution: {stream.resolution}")
        
        # Clear existing file if it exists
        if os.path.exists('downloads/video.mp4'):
            os.remove('downloads/video.mp4')
            
        # Download the video
        stream.download(output_path='downloads', filename='video.mp4')
        return send_file('downloads/video.mp4', as_attachment=True)
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return f"An error occurred: {str(e)}", 400

@app.route('/download_audio', methods=['POST'])
def download_audio():
    try:
        url = request.form['url']
        print(f"Received URL: {url}")
        
        # Extract video ID and construct standard YouTube URL
        video_id = extract_video_id(url)
        if not video_id:
            return "Invalid YouTube URL format", 400
            
        standard_url = f"https://youtube.com/watch?v={video_id}"
        print(f"Standardized URL: {standard_url}")

        # Create YouTube object
        yt = YouTube(
            standard_url,
            use_oauth=True,
            allow_oauth_cache=True
        )
        
        print(f"Video title: {yt.title}")
        
        # Get the highest quality audio stream
        audio_stream = yt.streams.filter(only_audio=True).first()
        if not audio_stream:
            return "No audio stream found", 400
            
        # Clear existing file if it exists
        if os.path.exists('downloads/audio.mp4'):
            os.remove('downloads/audio.mp4')
            
        # Download the audio
        audio_stream.download(output_path='downloads', filename='audio.mp4')
        return send_file('downloads/audio.mp4', as_attachment=True)
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return f"An error occurred: {str(e)}", 400

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True)