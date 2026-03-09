import os
import asyncio
import edge_tts
import pygame
import threading
import queue
import time
from ..utils.logger import logger

class VoiceOutput:
    def __init__(self, voice="en-US-EmmaNeural"):
        self.msg_queue = queue.Queue()
        self.voice = voice
        self.temp_dir = os.path.join(os.getcwd(), "temp", "audio")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Initialize pygame mixer once
        try:
            pygame.mixer.init()
        except Exception as e:
            logger.error(f"Failed to initialize pygame mixer: {e}")

        # Start background worker
        threading.Thread(target=self._worker, daemon=True).start()

    async def _generate_and_play(self, text):
        """Generates audio with edge-tts and plays it."""
        try:
            filename = f"speech_{int(time.time() * 1000)}.mp3"
            filepath = os.path.join(self.temp_dir, filename)
            
            # 1. Generate Audio
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(filepath)
            
            # 2. Play Audio
            if os.path.exists(filepath):
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
                
                # Unload and cleanup
                pygame.mixer.music.unload()
                try:
                    os.remove(filepath)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"TTS Execution Error: {e}")

    def _worker(self):
        """Background thread loop to handle TTS requests."""
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while True:
            text = self.msg_queue.get()
            if text is None: break
            
            logger.info(f"Generating Natural Voice: {text[:50]}...")
            loop.run_until_complete(self._generate_and_play(text))
            self.msg_queue.task_done()

    def speak(self, text):
        if not text: return
        # Simple cleanup of text (remove markdown symbols)
        clean_text = text.replace("**", "").replace("__", "").replace("`", "").strip()
        self.msg_queue.put(clean_text)

# Default to a young adult, high-quality Indian neural voice
output_engine = VoiceOutput(voice="en-IN-NeerjaExpressiveNeural")

def speak(text):
    output_engine.speak(text)
