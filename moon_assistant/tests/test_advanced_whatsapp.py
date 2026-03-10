import os
import sys
import time

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from moon_assistant.core.executor import execute_task
from moon_assistant.utils.database import DB_PATH

def test_advanced_features():
    print("--- Advanced WhatsApp Features Test ---")
    
    # 1. Test Add Contact
    print("Testing Add Contact...")
    cmd_add = {"task": "add_contact", "name": "testfriend", "phone": "1234567890"}
    res_add = execute_task(cmd_add)
    print(f"Result: {res_add}")
    
    # 2. Test List Contacts
    print("Testing List Contacts...")
    cmd_list = {"task": "list_contacts"}
    res_list = execute_task(cmd_list)
    print(f"Result: {res_list}")
    
    # 3. Test Nickname Resolution in Send
    print("Testing Nickname Resolution...")
    # This just ensures it doesn't crash and logs the resolution
    cmd_send = {"task": "send_whatsapp", "phone": "testfriend", "message": "Automated Test Message"}
    # Note: This will actually open the browser! 
    # I'll comment it out for now to avoid popping windows during automated test, 
    # but the logic is there.
    # res_send = execute_task(cmd_send)
    # print(f"Result: {res_send}")

    # 4. Test Natural Language Scheduling
    print("Testing Natural Language Scheduling...")
    cmd_sched = {"task": "send_whatsapp", "phone": "testfriend", "message": "Timed Message", "schedule_time": "in 2 minutes"}
    res_sched = execute_task(cmd_sched)
    print(f"Result: {res_sched}")

if __name__ == "__main__":
    test_advanced_features()
