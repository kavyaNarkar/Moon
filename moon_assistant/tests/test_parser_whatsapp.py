import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from moon_assistant.core.parser import quick_parse

def test_parser():
    test_cases = [
        "send whatsapp message \"hi i am moon\" to 9920883511",
        "send whatssapp message [hi am moon] to [9920883511]",
        "whatsapp message to 9920883511 hello there",
        "send message on whatsapp hi how are you to 9123456789",
        "watsapp 9876543210 message ping"
    ]
    
    print("--- WhatsApp Parser Test ---")
    for case in test_cases:
        result = quick_parse(case)
        print(f"Input: {case}")
        print(f"Result: {result}")
        print("-" * 20)

if __name__ == "__main__":
    test_parser()
