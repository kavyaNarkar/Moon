import os
import asyncio
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
        Uses Windows Biometric Framework (Windows Hello) to verify the user.
        This triggers the native Windows security prompt.
        """
        try:
            from winrt.windows.security.credentials.ui import UserConsentVerifier, UserConsentVerificationResult
            
            # request_verification_async is an awaitable object in winrt
            async def get_consent():
                result = await UserConsentVerifier.request_verification_async("Verify your identity to unlock Moon Assistant.")
                return result

            # Run the async winrt call synchronously for the Flask endpoint
            result = asyncio.run(get_consent())

            if result == UserConsentVerificationResult.VERIFIED:
                return True, "Fingerprint Recognized."
            elif result == UserConsentVerificationResult.CANCELED:
                return False, "Verification Canceled."
            else:
                return False, f"Verification failed: {result.name}"
                
        except Exception as e:
            logger.error(f"Hardware Fingerprint Error: {e}")
            # Fallback to simulated success ONLY if hardware/drivers are missing 
            # and it's a dev environment, but for the user we should report the error.
            return False, f"Biometric error: {str(e)}"

security_manager = SecurityManager()
