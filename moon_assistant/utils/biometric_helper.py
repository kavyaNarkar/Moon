import asyncio
import sys
import win32gui
import win32con
import win32api
import time
import threading
from winrt.windows.security.credentials.ui import UserConsentVerifier, UserConsentVerificationResult

def force_security_prompt_to_front():
    """
    Background thread that looks for the 'Windows Security' prompt 
    and forces it to the top-most position.
    """
    timeout = 10 # Search for 10 seconds max
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        def callback(hwnd, extra):
            title = win32gui.GetWindowText(hwnd)
            # The system prompt usually has 'Windows Security' in the title
            if "Windows Security" in title:
                try:
                    # Bring the system prompt to front
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                    win32gui.SetForegroundWindow(hwnd)
                    win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
                    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                                         win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                except Exception:
                    pass
        
        win32gui.EnumWindows(callback, None)
        time.sleep(0.5)

def set_always_on_top(enable=True):
    """Sets/Unsets Moon window as always on top."""
    def window_enum_callback(hwnd, wildcard):
        title = win32gui.GetWindowText(hwnd)
        if "Moon" in title and win32gui.IsWindowVisible(hwnd):
            try:
                # 1. Bring to front
                win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                win32gui.SetForegroundWindow(hwnd)
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
                
                # 2. Set Topmost
                z_order = win32con.HWND_TOPMOST if enable else win32con.HWND_NOTOPMOST
                win32gui.SetWindowPos(hwnd, z_order, 0, 0, 0, 0, 
                                     win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            except Exception:
                pass
            
    try:
        win32gui.EnumWindows(window_enum_callback, None)
    except Exception:
        pass

# Standalone helper to avoid COM threading issues inside Flask
async def run_verifier():
    try:
        # 1. Force Moon to be front-and-center
        set_always_on_top(True)
        
        # 2. Start the "Prompt Hunter" thread to catch the OS window when it pops up
        threading.Thread(target=force_security_prompt_to_front, daemon=True).start()
        
        # 3. Trigger the Windows Hello UI
        result = await UserConsentVerifier.request_verification_async("Unlock your Moon AI Assistant")
        
        # 4. Clean up
        set_always_on_top(False)
        
        if result == UserConsentVerificationResult.VERIFIED:
            sys.exit(0)
        elif result == UserConsentVerificationResult.CANCELED:
            sys.exit(1)
        else:
            sys.exit(2)
    except Exception:
        set_always_on_top(False)
        sys.exit(3)

if __name__ == "__main__":
    try:
        asyncio.run(run_verifier())
    except Exception:
        sys.exit(3)
