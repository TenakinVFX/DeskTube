import os
import re
import subprocess
import tempfile
import threading
from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = tempfile.mkdtemp()

def sanitize_filename(name):
    return re.sub(r'[^\w\s-]', '', name).strip()

@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.get_json()
    url = data.get('url', '').strip()
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    ydl_opts = {'quiet': True, 'no_warnings': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            seen = set()
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    res = f.get('height')
                    if res and res not in seen:
                        seen.add(res)
                        formats.append({
                            'format_id': f['format_id'],
                            'resolution': f'{res}p',
                            'ext': f.get('ext', 'mp4'),
                        })
            formats.sort(key=lambda x: int(x['resolution'][:-1]), reverse=True)

            # Also add audio-only
            formats.append({'format_id': 'bestaudio', 'resolution': 'Audio only (mp3)', 'ext': 'mp3'})

            return jsonify({
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'uploader': info.get('uploader'),
                'formats': formats,
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url', '').strip()
    format_id = data.get('format_id', 'best')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            if format_id == 'bestaudio':
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
                    'quiet': True,
                }
            else:
                ydl_opts = {
                    'format': f'{format_id}+bestaudio/best[height<={format_id}]/{format_id}',
                    'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                    'merge_output_format': 'mp4',
                    'quiet': True,
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = sanitize_filename(info.get('title', 'video'))

            files = os.listdir(tmpdir)
            if not files:
                return jsonify({'error': 'Download failed'}), 500

            filepath = os.path.join(tmpdir, files[0])
            ext = files[0].split('.')[-1]
            download_name = f"{title}.{ext}"

            return send_file(
                filepath,
                as_attachment=True,
                download_name=download_name,
                mimetype='video/mp4' if ext != 'mp3' else 'audio/mpeg'
            )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
