import os
import sys

# Add the project root to sys.path to allow relative imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from moon_assistant.tools.messenger import send_whatsapp_message

def test_whatsapp_logic():
    print("--- WhatsApp Tool Test ---")
    
    # Test case 1: Immediate send
    # print("Test 1: Immediate send...")
    # result = send_whatsapp_message("", "Hello! Immediate test.")
    # print(f"Result: {result}")

    # Test case 2: Scheduled send (in 1 minute)
    from datetime import datetime, timedelta
    future_time = (datetime.now() + timedelta(minutes=1)).strftime("%H:%M")
    print(f"Test 2: Scheduling message for {future_time}...")
    result = schedule_whatsapp_message("", "Hello! This was scheduled.", future_time)
    print(f"Result: {result}")
    
    # Keep the script running to see the background thread execute
    print("Waiting for scheduled message to trigger...")
    time.sleep(70) 

if __name__ == "__main__":
    test_whatsapp_logic()
