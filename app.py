import os

from fastapi import FastAPI, Request, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel

from app_utils import Settings, allowed_extension, download_file
from transcript import Transcript

app = FastAPI()

settings = Settings()
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

app.mount("/upload_files", StaticFiles(directory="/app/upload_files"), name="upload_files")
app.mount("/static", StaticFiles(directory="/app/static"), name="static")

obj = Transcript(settings.deepl_key)


class Param(BaseModel):
    """Define param class"""

    file: str


@app.get("/")
def root() -> FileResponse:
    """Show home page."""
    return FileResponse(path="/app/static/index.html", media_type="text/html")

@app.post("/test")
def test():
    return {"Hello": "World!"}

@app.post("/file_transcript")
def get_transcript(request: Request, file: UploadFile):
    """Get transcript"""
    if not allowed_extension(file.filename):
        raise HTTPException(
            status_code=422, detail="Unallowed extension for audio file"
        )

    return obj.get_transcript(file.file)["text"]


@app.post("/url_transcript")
def get_transcript(request: Request, param: Param):
    """Get transcript"""
    if not allowed_extension(param.file):
        raise HTTPException(
            status_code=422, detail="Unallowed extension for audio file"
        )
    filename = os.path.join(
        settings.upload_folder, param.file.rsplit("/", maxsplit=1)[-1]
    )

    download_file(param.file, filename)
    res = obj.get_transcript(filename)["text"]
    os.remove(filename)
    return res
