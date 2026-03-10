import edge_tts
import asyncio
import os
from ..utils.logger import logger

# Voice Selection: en-IN-NeerjaNeural (Premium Indian Voice) or en-US-GuyNeural
DEFAULT_VOICE = "en-IN-NeerjaNeural"

async def generate_speech(text, output_path, voice=DEFAULT_VOICE):
    """
    Generates an MP3 file from text using edge-tts.
    """
    logger.info(f"VOICE: Generating speech for: {text[:50]}...")
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        logger.info(f"VOICE: Speech saved to {output_path}")
        return True
    except Exception as e:
        logger.error(f"VOICE: Failed to generate speech: {e}")
        return False

def speak_text_sync(text, output_path, voice=DEFAULT_VOICE):
    """Sync wrapper for the async generate_speech function."""
    try:
        asyncio.run(generate_speech(text, output_path, voice))
        return True
    except Exception as e:
        logger.error(f"VOICE: Sync speech generation failed: {e}")
        return False
