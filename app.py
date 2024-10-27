from flask import Flask, request, render_template, send_file, flash, redirect, url_for
from pytube import YouTube
import os
import re

app = Flask(__name__, template_folder='.') # Change this line to use current directory

def extract_video_id(url):
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^?]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^?]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

@app.route('/')
def home():
    return render_template('index.html')  # This will now look for index.html in the root directory

@app.route('/download', methods=['POST'])
def download():
    try:
        url = request.form['url']
        print(f"Received URL: {url}")
        
        video_id = extract_video_id(url)
        if not video_id:
            flash("Invalid YouTube URL format")
            return redirect(url_for('home'))
            
        standard_url = f"https://youtube.com/watch?v={video_id}"
        print(f"Standardized URL: {standard_url}")

        try:
            yt = YouTube(standard_url)
        except Exception as e:
            if "device and input code" in str(e).lower():
                flash("This video requires authentication. Please check the terminal for instructions to authenticate.")
                return redirect(url_for('home'))
            raise e

        print(f"Video title: {yt.title}")
        
        streams = yt.streams.filter(progressive=True).order_by('resolution').desc()
        if not streams:
            flash("No suitable streams found for this video")
            return redirect(url_for('home'))
            
        available_streams = {stream.resolution: stream for stream in streams}
        stream = available_streams.get('1080p') or available_streams.get('720p') or streams.first()
        
        if not stream:
            flash("No suitable stream found")
            return redirect(url_for('home'))
            
        print(f"Selected stream resolution: {stream.resolution}")
        
        if os.path.exists('downloads/video.mp4'):
            os.remove('downloads/video.mp4')
            
        stream.download(output_path='downloads', filename='video.mp4')
        return send_file('downloads/video.mp4', as_attachment=True)
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        flash(f"An error occurred: {str(e)}")
        return redirect(url_for('home'))

@app.route('/download_audio', methods=['POST'])
def download_audio():
    try:
        url = request.form['url']
        print(f"Received URL: {url}")
        
        video_id = extract_video_id(url)
        if not video_id:
            flash("Invalid YouTube URL format")
            return redirect(url_for('home'))
            
        standard_url = f"https://youtube.com/watch?v={video_id}"
        print(f"Standardized URL: {standard_url}")

        try:
            yt = YouTube(standard_url)
        except Exception as e:
            if "device and input code" in str(e).lower():
                flash("This video requires authentication. Please check the terminal for instructions to authenticate.")
                return redirect(url_for('home'))
            raise e

        print(f"Video title: {yt.title}")
        
        audio_stream = yt.streams.filter(only_audio=True).first()
        if not audio_stream:
            flash("No audio stream found")
            return redirect(url_for('home'))
            
        if os.path.exists('downloads/audio.mp4'):
            os.remove('downloads/audio.mp4')
            
        audio_stream.download(output_path='downloads', filename='audio.mp4')
        return send_file('downloads/audio.mp4', as_attachment=True)
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        flash(f"An error occurred: {str(e)}")
        return redirect(url_for('home'))

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True)