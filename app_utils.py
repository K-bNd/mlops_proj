import os
from urllib.request import urlopen
from shutil import copyfileobj
from pydantic_settings import BaseSettings
from fastapi import Request

ALLOWED_EXTENSIONS = {'mp3', 'm4a', 'mp4'}

def allowed_extension(filename: str) -> bool:
    """Check if the extension from the uploaded file is valid."""
    return '.' in filename and \
           filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS

def download_file(url: str, filename: str) -> None:
    """Downloads a file from url into a file."""
    with urlopen(url) as in_stream, open(filename, 'wb+') as out_file:
            copyfileobj(in_stream, out_file)

class Settings(BaseSettings):
    """
    Settings for the FastAPI app. Override with environment variables or .env file.

    Override example:
    `export FASTR_SECRET_KEY=secret`
    """
    secret_key: str = "dev"
    deepl_key: str = os.environ.get("DEEPL_KEY")
    upload_folder: str = "./upload_files"

def flash(request: Request, error: str) -> None:
    """
    Recreate the flash function from Flask. Store error messages in the "flashes" key
    of the session so that all flashed messages can be displayed in a view.

    Parameters
    ----------
    request
        a fastapi request object
    error
        the error message to flash
    """
    request.session["flashes"] = request.session.get("flashes", []) + [error]