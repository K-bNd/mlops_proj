#!/usr/bin/env python3

import json
from flask import Flask, request, jsonify

def create_app():
    deepl_key = open("DEEPL_KEY.txt", "rb").readline().decode().rstrip()
    openai_key = open("OPENAI_KEY.txt", "rb").readline().decode().rstrip()

    from api_app import transcript
    obj = transcript.Transcript(openai_key, deepl_key)
    app = Flask(__name__, instance_relative_config=True)
    @app.route('/')
    def hello():
        return "Hi, there !"
    @app.route('/transcript', methods=['GET'])
    def get_transcript():
        return obj.get_transcript(json.loads(request.data)["audio_file"])
    @app.route('/subtitles', methods=['GET'])
    def get_subtitles():
        params = json.loads(request.data)
        return obj.get_subtitles(params["filename"], params["transcript"], params["css_options"])
    return app
