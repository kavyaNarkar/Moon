import os
import subprocess
import webbrowser
import time
import pyautogui
import threading
from datetime import datetime
from ..config import BRAVE_PATHS
from ..utils.logger import logger

def get_brave_path():
    """
    Finds the Brave browser executable path.
    """
    for path in BRAVE_PATHS:
        if os.path.exists(path):
            return path
    return None

def send_whatsapp_message(phone, message):
    """
    Opens WhatsApp Web in Brave (or default browser), pre-fills a message, 
    and simulates 'Enter' to send it.
    """
    if not message:
        return "What message would you like to send?"

    # Sanitize phone number
    clean_phone = "".join(filter(str.isdigit, phone)) if phone else ""
    
    # Construct URL - using web.whatsapp.com/send
    encoded_message = message.replace(' ', '%20')
    if clean_phone:
        url = f"https://web.whatsapp.com/send?phone={clean_phone}&text={encoded_message}"
    else:
        url = f"https://web.whatsapp.com/send?text={encoded_message}"

    brave_path = get_brave_path()
    
    try:
        if brave_path:
            logger.info(f"Opening Brave with WhatsApp: {url}")
            subprocess.Popen([brave_path, url])
        else:
            logger.warning("Brave browser not found. Falling back to default browser.")
            webbrowser.open(url)
        
        # WhatsApp Web can take a while to load.
        logger.info("Waiting for WhatsApp Web to load and focus...")
        time.sleep(20) # Increased to 20 seconds for safety
        
        # EMPHATIC SEQUENCE: Tab to ensure focus on input, then Enter
        pyautogui.press('tab')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.press('enter') 
        logger.info("Sent focus Tab + double Enter sequence.")
        
        msg_status = f"to {phone}" if phone else "to your contact"
        return f"Message sent {msg_status}. (Ensure Brave stayed focused)"
        
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message: {e}")
        return f"An error occurred: {e}"

def schedule_whatsapp_message(phone, message, schedule_time_str):
    """
    Schedules a WhatsApp message to be sent at a specific time.
    schedule_time_str should be in 'HH:MM' or 'YYYY-MM-DD HH:MM' format.
    """
    try:
        now = datetime.now()
        try:
            # Try HH:MM first
            scheduled_time = datetime.strptime(schedule_time_str, "%H:%M")
            scheduled_time = now.replace(hour=scheduled_time.hour, minute=scheduled_time.minute, second=0, microsecond=0)
            if scheduled_time < now:
                # If time has passed today, assume it's for tomorrow
                from datetime import timedelta
                scheduled_time += timedelta(days=1)
        except ValueError:
            # Try full format
            scheduled_time = datetime.strptime(schedule_time_str, "%Y-%m-%d %H:%M")
        
        delay = (scheduled_time - now).total_seconds()
        
        if delay < 0:
            return "Scheduled time is in the past."

        # Use threading to wait in background
        def background_send():
            logger.info(f"Background scheduler: Waiting {delay} seconds to send message.")
            time.sleep(delay)
            send_whatsapp_message(phone, message)

        thread = threading.Thread(target=background_send)
        thread.daemon = True
        thread.start()
        
        return f"Message scheduled for {scheduled_time.strftime('%Y-%m-%d %H:%M')}."

    except Exception as e:
        logger.error(f"Scheduling error: {e}")
        return f"Failed to schedule message: {e}. Please use HH:MM or YYYY-MM-DD HH:MM format."

if __name__ == "__main__":
    # Test block
    print("Testing WhatsApp sender...")
    # Replace with a test number if needed, or leave blank to test contact selection
    print(send_whatsapp_message("", "Hello from Moon Assistant!"))
