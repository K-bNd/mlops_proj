import os
from flask import Flask, request, send_from_directory, redirect, flash
from app_utils import allowed_extension, download_file
from transcript import Transcript

app = Flask(__name__, instance_relative_config=True)

DEEPL_KEY = open("DEEPL_KEY.txt", "rb").readline().decode().rstrip()
UPLOAD_FOLDER = os.path.join(app.root_path, 'upload_files')

obj = Transcript(DEEPL_KEY)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'dev'

@app.route('/')
def root():
    """Show home page."""
    return "Welcome page."

@app.route('/transcript', methods=['GET'])
def get_transcript():
    """Get transcript"""
    params = request.get_json()
    if "file" not in list(params.keys()):
        flash('No file given')
        return redirect(request.url)

    if not allowed_extension(params["file"]):
        print(request.get_json()["file"])
        flash('Unallowed extension for audio file')
        return redirect(request.url)

    url = request.get_json()["file"]
    filename = UPLOAD_FOLDER + url.rsplit('/', maxsplit=1)[-1]

    download_file(url, filename)
    res = obj.get_transcript(filename)["text"]
    os.remove(filename)
    return res

@app.route('/subtitles', methods=['GET'])
def write_subtitles():
    """Write subtitles for file"""
    params = request.get_json()
    if "file" not in list(params.keys()):
        flash('No file given')
        return redirect(request.url)

    if not allowed_extension(params["file"]):
        print(params["file"])
        flash('Unallowed extension for audio file')
        return redirect(request.url)

    url = params["file"]
    filename = os.path.join(UPLOAD_FOLDER, url.rsplit('/', maxsplit=1)[-1])
    print(filename)
    subtitles_src = ".".join(filename.split('.')[0:-1]) + "-subtitles.vtt"

    download_file(url, filename)

    obj.write_subtitles(
        filename, subtitles_src)
    os.remove(filename)
    
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                            subtitles_src.rsplit('/', maxsplit=1)[-1], as_attachment=True)

@app.route('/uploads/<path:filename>')
def expose_file(filename):
    """Make file available for users."""
    print(app.config["UPLOAD_FOLDER"])
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                                filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host ='0.0.0.0', port = 5001, debug = True)