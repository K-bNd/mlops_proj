#!/usr/bin/env python3

import json
from flask import Flask, request, jsonify, send_from_directory, redirect, flash
from werkzeug.utils import secure_filename
from api_app import transcript
import os
from urllib.request import urlopen

ALLOWED_EXTENSIONS = {'mp3', 'm4a', 'mp4'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS

def create_app():
    deepl_key = open("DEEPL_KEY.txt", "rb").readline().decode().rstrip()
    openai_key = open("OPENAI_KEY.txt", "rb").readline().decode().rstrip()
    UPLOAD_FOLDER = '/upload_files'

    obj = transcript.Transcript(openai_key, deepl_key)
    app = Flask(__name__, instance_relative_config=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SECRET_KEY'] = 'dev'

    @app.route('/')
    def hello():
        return "Hi, there !"

    @app.route('/transcript', methods=['GET'])
    def get_transcript():
        params = request.get_json()
        if not "audio_file" in list(params.keys()):
            flash('No audio file given')
            return redirect(request.url)
        if not allowed_file(params["audio_file"]):
            print(request.get_json()["audio_file"])
            flash('Unallowed extension for audio file')
            return redirect(request.url)
        return "Downloading from " + params["audio_file"]

        # obj.audio_file = os.path.join(app.config['UPLOAD_FOLDER'], params["audio_file"])
        # file.save(obj.audio_file)
        # return obj.get_transcript()

    @app.route('/subtitles', methods=['GET', 'PUT'])
    def write_subtitles():
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        params = json.loads(request.data)
        audio_file = params["audio_file"]
        filename = secure_filename(params["filename"])
        obj.write_subtitles(filename, params["transcript"], params["css_options"])
        return download_file(params["filename"])
    @app.route('/uploads/<path:filename>')
    def download_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename, as_attachment=True)
    return app
