import os
import asyncio
from winrt.windows.security.credentials.ui import UserConsentVerifier, UserConsentVerificationResult
from ..utils.logger import logger

class SecurityManager:
    def __init__(self):
        self.users = {
            "yash bhadva ahe": "Yash",
            "sneha@2712": "Sneha",
            "supriya@0406": "Supriya",
            "RAM@3511": "Kavya" # Original password assigned to Kavya
        }

    def verify_password(self, password):
        """Checks if the entered password matches any known user password."""
        if password in self.users:
            return True, self.users[password]
        return False, "Incorrect Password."

    def verify_fingerprint(self):
        """
        Uses a separate process helper to bypass COM/event-loop conflicts 
        between Flask threads and WinRT UI calls.
        """
        import subprocess
        import sys
        
        logger.info("SECURITY: verify_fingerprint triggering separate process...")
        try:
            # Get path to helper script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            helper_path = os.path.join(os.path.dirname(current_dir), "utils", "biometric_helper.py")
            
            # Use current python executable to run helper
            # This is significantly more robust than calling winrt inside a flask thread
            process = subprocess.run([sys.executable, helper_path], capture_output=False, timeout=60)
            
            logger.info(f"SECURITY: Helper process exited with code: {process.returncode}")
            
            if process.returncode == 0:
                logger.info("SECURITY: Biometric Verification SUCCESS.")
                return True, "Verified"
            elif process.returncode == 1:
                logger.warning("SECURITY: Biometric Verification CANCELED.")
                return False, "Canceled"
            else:
                logger.error(f"SECURITY: Biometric Verification FAILED (Code {process.returncode}).")
                return False, "Failed"
                
        except subprocess.TimeoutExpired:
            logger.error("SECURITY: Biometric verification timed out.")
            return False, "Timed Out"
        except Exception as e:
            logger.error(f"SECURITY: Subprocess error - {e}")
            return False, "Scanner Error"

security_manager = SecurityManager()
