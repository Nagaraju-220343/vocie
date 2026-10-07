from app.providers.voice.base import VoiceProvider
from app.providers.voice.retell import RetellVoiceProvider


def get_voice_provider() -> VoiceProvider:
    """
    Factory function to get the configured voice provider instance.
    Currently always returns the RetellVoiceProvider.
    """
    return RetellVoiceProvider()
