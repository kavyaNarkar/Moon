import os
import subprocess
import webbrowser
import time
import pyautogui
import threading
from datetime import datetime
from ..config import BRAVE_PATHS, DEFAULT_COUNTRY_CODE
from ..utils.logger import logger
from ..utils.database import save_scheduled_message, get_pending_messages, mark_message_done, get_contact

def get_brave_path():
    """Finds the Brave browser executable path."""
    for path in BRAVE_PATHS:
        if os.path.exists(path):
            return path
    return None

def simulate_whatsapp_send():
    """
    Performs the robust keyboard sequence to bypass WhatsApp Web overlays
    and send the pre-filled message.
    """
    logger.info("MESSENGER: Executing expanded robust Esc -> Enter -> Enter sequence...")
    # 1. Escape multiple times to clear any notification popups or overlays
    for _ in range(2):
        pyautogui.press('esc')
        time.sleep(1)
    
    # 2. Enter to trigger "Continue to Chat" or bypass selection
    pyautogui.press('enter')
    time.sleep(4) # Wait even longer for loading
    
    # 3. Try to Tab once to ensure focus is in the message box if it wasn't
    pyautogui.press('tab')
    time.sleep(1)
    
    # 4. Final sequence of Enters to trigger the send button
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.press('enter')
    logger.info("MESSENGER: WhatsApp combined send sequence completed.")

def send_whatsapp_message(phone, message):
    """
    Opens WhatsApp Web in Brave browser (or default) with a pre-filled message
    and simulates keyboard actions to send it.
    """
    try:
        logger.info(f"MESSENGER: Request - Phone: '{phone}', Message Snippet: '{message[:30]}...'")
    
        # 1. Resolve Contact Name
        if phone and not any(char.isdigit() for char in str(phone)):
            logger.info(f"MESSENGER: Resolving contact name: '{phone}'")
            resolved_phone = get_contact(phone.strip())
            if resolved_phone:
                logger.info(f"MESSENGER: Resolved '{phone}' to '{resolved_phone}'")
                phone = str(resolved_phone).strip()
            else:
                logger.error(f"MESSENGER: Could not find contact '{phone}'")
                return f"Contact '{phone}' not found. Please add them in the Contacts menu."

        # 2. Sanitize and Format Number
        import re
        clean_phone = re.sub(r'\D', '', str(phone)) if phone else ""
        
        # Prepend country code if 10 digits
        if len(clean_phone) == 10 and DEFAULT_COUNTRY_CODE:
            logger.info(f"MESSENGER: Prepending {DEFAULT_COUNTRY_CODE}")
            clean_phone = str(DEFAULT_COUNTRY_CODE) + clean_phone
        
        if not clean_phone:
            logger.warning("MESSENGER: No phone number. Opening contact search.")
        
        # 3. Construct URL
        # Using api.whatsapp.com is the "Final Approach" recommendation for stability
        encoded_message = message.replace(' ', '%20') if message else ""
        if clean_phone:
            url = f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_message}"
        else:
            url = f"https://web.whatsapp.com/send?text={encoded_message}"
        
        brave_path = get_brave_path()
        logger.info(f"MESSENGER: Final URL - {url}")
        
        # 4. Launch Browser
        if brave_path:
            # Force focus with --new-window
            subprocess.Popen([brave_path, "--new-window", url])
        else:
            webbrowser.open(url)
        
        # 5. Wait for Heavy UI
        logger.info("MESSENGER: Waiting 30s for WhatsApp Web UI...")
        time.sleep(30) 
        
        # 6. Execute Send Sequence
        simulate_whatsapp_send()
        
        return f"Message sent to {phone}."
        
    except Exception as e:
        logger.error(f"MESSENGER: Fatal error occurred: {e}")
        return f"Failed to send: {e}"

def schedule_whatsapp_message(phone, message, schedule_time_str):
    """Schedules a message persistency via SQLite."""
    try:
        import dateparser
        now = datetime.now()
        scheduled_time = dateparser.parse(schedule_time_str, settings={'PREFER_DATES_FROM': 'future'})
        
        if not scheduled_time:
            return "Could not parse the provided time format."
            
        if scheduled_time < now:
            return f"Scheduled time ({scheduled_time}) is in the past."

        time_str = scheduled_time.strftime("%Y-%m-%d %H:%M:%S")
        if save_scheduled_message(phone, message, time_str):
            return f"Message scheduled for {time_str}."
        return "Failed to save scheduled message to database."

    except Exception as e:
        logger.error(f"Scheduling error: {e}")
        return f"Failed to schedule message: {e}"

def broadcast_whatsapp(recipients, message):
    """Sends the same message to multiple recipients."""
    results = []
    for r in recipients:
        res = send_whatsapp_message(r.strip(), message)
        results.append(f"{r}: {res}")
        time.sleep(5) # Delay between broadcasts to prevent spam blocking
    return "\n".join(results)

def start_scheduler_service():
    """Background service to check for pending messages."""
    def check_loop():
        logger.info("Starting background WhatsApp scheduler service.")
        while True:
            try:
                now = datetime.now()
                pending = get_pending_messages()
                for msg_id, phone, msg, sched_time_str in pending:
                    sched_time = datetime.strptime(sched_time_str, "%Y-%m-%d %H:%M:%S")
                    if now >= sched_time:
                        logger.info(f"Triggering scheduled message {msg_id}")
                        send_whatsapp_message(phone, msg)
                        mark_message_done(msg_id)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
            time.sleep(30) # Check every 30 seconds

    thread = threading.Thread(target=check_loop)
    thread.daemon = True
    thread.start()

# Start the service
start_scheduler_service()
