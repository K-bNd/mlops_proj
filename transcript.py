import time
import torch
from faster_whisper import WhisperModel
import logging


def measure_latency(func):
    """Wrapper to measure function call latency"""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        latency = end_time - start_time
        return result, latency

    return wrapper


class Transcript:
    """
    Init Object that creates transcript from audio files.
    """

    def __init__(self, debug=False) -> None:
        """Init function."""
        self.transcript = None

        self.spoken_lang = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        if debug:
            logging.basicConfig()
            logging.getLogger("faster-whisper").setLevel(logging.DEBUG)

    @measure_latency
    def get_transcript(self, audio_file, debug=False) -> dict:
        """Get transcript from audio file."""

        model = WhisperModel("base", device=self.device, compute_type="int8")
        segments, info = model.transcribe(audio_file, vad_filter=True)
        segments = list(segments)

        self.spoken_lang = info.language

        transcript = ""
        temperatures = []
        avg_logprobs = []

        for segment in segments:
            temperatures.append(segment.temperature)
            avg_logprobs.append(segment.avg_logprob)
            transcript += segment.text

        if debug:
            print(segments)

        self.transcript = dict(
            {
                "segments": segments,
                "text": transcript,
                "info": info,
                "temperatures": temperatures,
                "avg_logprobs": avg_logprobs,
            }
        )
        return self.transcript
