from .utils.logger import logger
from .config import ASSISTANT_NAME

def main():
    """
    Unified entry point. Launches the Moon Desktop App (GUI) by default.
    """
    try:
        from .interfaces.gui.server import start_gui
        start_gui()
    except KeyboardInterrupt:
        print("\nMoon Assistant stopped.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"An error occurred: {e}")

def run_voice_mode():
    from .interfaces.voice_output import speak
    from .interfaces.voice_input import listen_for_command
    from .interfaces.wake_word import wait_for_moon
    from .core.brain import query_llm
    from .core.parser import parse_command, quick_parse

    logger.info("Starting Voice Mode.")
    speak(f"Hello, I am {ASSISTANT_NAME}. Listening for 'Hello Moon'...")
    
    while True:
        try:
            # 1. Wait for wake phrase
            if wait_for_moon():
                speak("Yes, I'm listening.")
                
                # 2. Recognition for command
                text_command = listen_for_command()
                
                if text_command:
                    # 3. Try Fast Track (Rule-based)
                    command_data = quick_parse(text_command)
                    
                    if not command_data:
                        # 4. Fallback to LLM
                        llm_response = query_llm(text_command)
                        command_data = parse_command(llm_response)
                    else:
                        logger.info("Fast track triggered.")
                    
                    # 5. Execute
                    from .core.executor import execute_task
                    response_text = execute_task(command_data)
                    
                    # 6. Speak response
                    speak(response_text)
                    
        except KeyboardInterrupt:
            logger.info("Voice Mode stopped by user.")
            break
        except Exception as e:
            logger.error(f"Error in Voice Mode: {e}")
            speak("I encountered an error. Please check the logs.")

if __name__ == "__main__":
    main()
