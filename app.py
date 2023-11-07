import os

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.background import BackgroundTask
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel

from app_utils import Settings, allowed_extension, download_file, flash
from transcript import Transcript

app = FastAPI()

settings = Settings()
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

app.mount("/upload_files", StaticFiles(directory="./upload_files"),
          name="upload_files")
app.mount("/static", StaticFiles(directory="./static"),
          name="static")

obj = Transcript(settings.deepl_key)

class Param(BaseModel):
    """Define param class"""
    file: str


@app.get('/')
def root() -> FileResponse:
    """Show home page."""
    return FileResponse(path="/static/index.html", media_type="text/html")

@app.get('/transcript')
def get_transcript(request: Request, param: Param):
    """Get transcript"""
    if not allowed_extension(param.file):
        print(param.file)
        err = BackgroundTask(
            flash, request, "Unallowed extension for audio file")
        return RedirectResponse(url="/", status_code=302, background=err)

    filename = os.path.join(settings.upload_folder,
                            param.file.rsplit('/', maxsplit=1)[-1])

    download_file(param.file, filename)
    res = obj.get_transcript(filename)["text"]
    os.remove(filename)
    return res


@app.get('/subtitles', response_class=FileResponse)
def write_subtitles(request: Request, param: Param):
    """Write subtitles for file"""
    if not allowed_extension(param.file):
        err = BackgroundTask(
            flash, request, "Unallowed extension for audio file")
        return RedirectResponse(url="/", status_code=302, background=err)

    filename = os.path.join(settings.upload_folder,
                            param.file.rsplit('/', maxsplit=1)[-1])
    subtitles_src = ".".join(filename.split('.')[0:-1]) + "-subtitles.vtt"

    download_file(param.file, filename)

    obj.write_subtitles(
        filename, subtitles_src)
    os.remove(filename)
    return subtitles_src