import os
from urllib.error import URLError

import numpy as np
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from prometheus_client import Counter, Summary, make_asgi_app

from app_utils import Settings, allowed_extension, download_file
from transcript import Transcript


# Create Prometheus metrics
REQUEST_COUNT = Counter("requests", "Total number of requests")
LATENCY = Summary("latency", "Time spent processing a request")
TEMPERATURE = Summary("temperature", "Temperature needed for the audio")
DURATION = Summary("audio_duration", "Length of the audio")
LOGPROBS = Summary("max_logprob", "Maximum avg_logprob on audio")
app = FastAPI()

metrics_app = make_asgi_app()
settings = Settings()
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.mount("/upload_files", StaticFiles(directory="./upload_files"), name="upload_files")
app.mount("/static", StaticFiles(directory="./static"), name="static")
app.mount("/metrics", metrics_app, "prometheus_metrics")

obj = Transcript()


class Param(BaseModel):
    """Define param class"""

    file: str


def remove_file(path: str) -> None:
    """Remove file from disk"""
    os.remove(path)


def log_transcript_information(transcript, latency) -> None:
    """Log transcript information to prometheus client"""
    LATENCY.observe(latency)
    DURATION.observe(transcript["info"].duration)
    logprobs = np.array(transcript["avg_logprobs"])
    temperatures = np.array(transcript["temperatures"])
    TEMPERATURE.observe(np.median(temperatures))
    LOGPROBS.observe(np.max(logprobs))
    
@app.get("/")
def root() -> FileResponse:
    """Show home page."""
    return FileResponse(path="./static/index.html", media_type="text/html")


@app.post("/url_transcript")
def get_transcript_from_url(param: Param, background_tasks: BackgroundTasks):
    """Get transcript from given url"""
    REQUEST_COUNT.inc()
    if not allowed_extension(param.file):
        raise HTTPException(
            status_code=422, detail="Unallowed extension for audio file"
        )
    filename = os.path.join(
        settings.upload_folder, param.file.rsplit("/", maxsplit=1)[-1]
    )

    try:
        path = download_file(param.file, filename)
    except (URLError, ValueError) as err:
        raise HTTPException(
            status_code=403,
            detail="Server does not have access to the content",
        ) from err
    except FileNotFoundError as err:
        raise HTTPException(
            status_code=502, detail="Server could not write file to disk"
        ) from err

    background_tasks.add_task(remove_file, path)
    transcript, latency = obj.get_transcript(path)
    log_transcript_information(transcript, latency)

    return transcript["text"]


@app.post("/file_transcript")
def get_transcript_from_file(file: UploadFile):
    """Get transcript from given file"""
    REQUEST_COUNT.inc()
    if not allowed_extension(file.filename):
        raise HTTPException(
            status_code=422, detail="Unallowed extension for audio file"
        )

    transcript, latency = obj.get_transcript(file.file)
    log_transcript_information(transcript, latency)
    return transcript["text"]
