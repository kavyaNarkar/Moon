import asyncio
import sys

try:
    from winrt.windows.security.credentials.ui import UserConsentVerifier, UserConsentVerificationResult, UserConsentVerifierAvailability
    
    async def check_availability():
        print("Checking Windows Hello availability...")
        availability = await UserConsentVerifier.check_availability_async()
        print(f"Availability: {availability.name}")
        return availability

    async def test_verification():
        print("Triggering Windows Hello prompt...")
        result = await UserConsentVerifier.request_verification_async("Moon Assistant Verification Test")
        print(f"Result: {result.name}")
        return result

    async def main():
        avail = await check_availability()
        if avail == UserConsentVerifierAvailability.AVAILABLE:
            await test_verification()
        else:
            print(f"Biometrics not available on this system: {avail.name}")

    if __name__ == "__main__":
        asyncio.run(main())

except Exception as e:
    print(f"Error test script: {e}")
    sys.exit(1)
