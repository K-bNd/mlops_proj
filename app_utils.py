from urllib.request import urlopen
from shutil import copyfileobj

ALLOWED_EXTENSIONS = {'mp3', 'm4a', 'mp4'}

def allowed_extension(filename):
    """Check if the extension from the uploaded file is valid."""
    return '.' in filename and \
           filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS

def download_file(url, filename) -> None:
    """Downloads a file from url into a file."""
    with urlopen(url) as in_stream, open(filename, 'wb+') as out_file:
            copyfileobj(in_stream, out_file)