import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from ..config import VOSK_MODEL_PATH, WAKE_WORD
from ..utils.logger import logger

wake_queue = queue.Queue()

def wake_callback(indata, frames, time, status):
    if status:
        logger.error(f"Wake status: {status}")
    wake_queue.put(bytes(indata))

class WakeWordDetector:
    def __init__(self):
        try:
            self.model = Model(VOSK_MODEL_PATH)
            self.samplerate = 16000
            self.recognizer = KaldiRecognizer(self.model, self.samplerate)
            self.wake_word = WAKE_WORD.lower()
        except Exception as e:
            logger.error(f"WakeWord init failure: {e}")
            self.model = None

    def wait_for_wake_phrase(self):
        if not self.model:
            return False
            
        logger.info(f"Waiting for wake word: {self.wake_word}")
        with sd.RawInputStream(samplerate=self.samplerate, blocksize=8000, dtype='int16',
                               channels=1, callback=wake_callback):
            while True:
                data = wake_queue.get()
                if self.recognizer.AcceptWaveform(data):
                    result_json = self.recognizer.Result()
                    result = json.loads(result_json)
                    text = result.get("text", "").lower()
                    if self.wake_word in text:
                        logger.info("Wake word detected!")
                        return True

wake_detector = WakeWordDetector()

def wait_for_moon():
    return wake_detector.wait_for_wake_phrase()
