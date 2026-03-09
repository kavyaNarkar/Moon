import os
import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from ..config import VOSK_MODEL_PATH
from ..utils.logger import logger

audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    if status:
        logger.error(f"Audio status error: {status}")
    audio_queue.put(bytes(indata))

class VoiceInput:
    def __init__(self):
        if not os.path.exists(VOSK_MODEL_PATH):
            logger.error(f"Vosk model not found at {VOSK_MODEL_PATH}")
            self.model = None
            return
            
        try:
            self.model = Model(VOSK_MODEL_PATH)
            self.samplerate = 16000
            self.recognizer = KaldiRecognizer(self.model, self.samplerate)
        except Exception as e:
            logger.error(f"Failed to initialize Vosk: {e}")
            self.model = None

    def listen(self):
        if not self.model:
            return ""
            
        logger.info("Listening...")
        with sd.RawInputStream(samplerate=self.samplerate, blocksize=8000, dtype='int16',
                               channels=1, callback=audio_callback):
            while True:
                data = audio_queue.get()
                if self.recognizer.AcceptWaveform(data):
                    result_json = self.recognizer.Result()
                    result = json.loads(result_json)
                    text = result.get("text", "")
                    if text:
                        logger.info(f"Recognized: {text}")
                        return text

input_engine = VoiceInput()

def listen_for_command():
    return input_engine.listen()
