import concurrent.futures
from copy import deepcopy
import deepl
import torch
from faster_whisper import WhisperModel
from faster_whisper.transcribe import Segment, Word

from .utils import WriteVTT

class Transcript:
    """
    Init Object that creates transcript and summaries from audio files.

    :param audio_file: The audio file
    :type audio_file: str
    :param api_key: The ap i key to access the OpenAI API
    :type api_key: str

    """

    def __init__(self, openai_key, deepl_key) -> None:
        """Init function.

        @param audio_file : The audio filename
        @param openai_key : OpenAI api key
        @param deepl_key : DeepL api key
        """
        self.deepl_key = deepl_key
        self.openai_key = openai_key
        self.transcript = None

        self.spoken_lang = None
        self.device = "gpu" if torch.cuda.is_available() else "cpu"

    def api_test(self):
        return "Ye ye"

    def get_transcript(self, audio_file, debug=False) -> dict:
        """Get transcript from audio file."""
        if self.transcript is not None:
            return self.transcript

        model = WhisperModel("base", device=self.device,
                             compute_type="int8")

        segments, info = model.transcribe(audio_file, vad_filter=True)
        segments = list(segments)

        self.spoken_lang = info.language

        transcript = ""

        for segment in segments:
            transcript += segment.text

        if debug:
            print(segments)
        self.transcript = dict({"segments": segments, "text": transcript, "info": info})

        return self.transcript

    def get_subtitles(self, transcript=None, given_segments=None, debug=False) -> list[dict]:
        """Get subtitles from audio in dict format.

        @param transcript : The transcript we are using (could be translated)
        @param given_segments : Translate segments instead of a transcript
        """
        if transcript is None:
            transcript = self.get_transcript()
        subtitles = []
        segments = transcript["segments"] if given_segments is None else given_segments
        for segment in segments:
            obj = {}
            obj["start"] = segment.start
            obj["end"] = segment.end
            obj["text"] = segment.text
            subtitles.append(obj)

        return subtitles

    def write_subtitles(self, filename: str, transcript=None, css_options=None) -> None:
        """Write subtitles to file in any standard format.

        @param transcript : The subtitles we are using
        @param filename : The name of the file we write to
        @param css_options: Options like max_line_width, max_line_count and
        highlight words
        """
        if transcript is None:
            transcript = self.get_transcript()

        vttWriter = WriteVTT(transcript)
        subs_file = open(filename, "w")
        default_options = {"max_line_width": 28, "max_line_count": 3, "highlight_words": False}
        options = css_options if css_options is not None else default_options
        vttWriter.write_result(transcript, subs_file, options)

    def translate_text(self, text: str, translator, out_lang: str) -> str:
        """
        Translate text to another language.

        @param text: The text to translate
        @param out_lang: The requested language
        """
        return translator.translate_text(text, target_lang=out_lang.capitalize()).text

    def translate_subtitle(self, translator, lang: str) -> dict:
        """
        Translate transcript into a single language.

        @param translator: DeepL translator object
        """
        def translate_sublist(self, sub: Segment, lang: str) -> dict:
            new_seg = Segment(
                id=sub.id,
                seek=sub.seek,
                start=sub.start,
                end=sub.end,
                text=self.translate_text(sub.text, translator, lang),
                tokens=sub.tokens,
                temperature=sub.temperature,
                avg_logprob=sub.avg_logprob,
                compression_ratio=sub.compression_ratio,
                no_speech_prob=sub.no_speech_prob,
                words=sub.words
            )
            return new_seg

        res_transcript: dict = dict({"segments": []})
        res_transcript["segments"] = list(map(lambda sub: translate_sublist(self, sub, lang), self.transcript["segments"]))
        return res_transcript

    def translate_subtitles(self, out_langs: list[str]) -> dict[dict]:
        """
        Translate the subtitles from the segment part of the transcript.

        @param out_langs: The list of languages wanted in ISO 639-1 standard
        """
        if self.transcript is None:
            self.get_transcript()

        with concurrent.futures.ProcessPoolExecutor() as executor:
            transcript_dict = {}
            translator = deepl.Translator(auth_key=self.deepl_key)
            translate_batch = {executor.submit(self.translate_subtitle, translator, lang): lang for lang in out_langs}
            for future in concurrent.futures.as_completed(translate_batch):
                lang = translate_batch[future]
                try:
                    transcript = future.result()
                except Exception as exc:
                    print('%r generated an exception: %s' % (lang, exc))
                else:
                    transcript_dict[lang] = transcript

            return transcript_dict
