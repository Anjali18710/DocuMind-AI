"""
voice.py
--------
Speech-to-text for spoken questions, using Whisper on Groq.
Works for English, Hindi and mixed Hinglish speech.
"""

from config.settings import GROQ_API_KEY, WHISPER_MODEL


def voice_available() -> bool:
    return bool(GROQ_API_KEY)


def transcribe(audio_bytes: bytes, filename: str = "question.wav") -> str:
    from groq import Groq

    client = Groq(api_key=GROQ_API_KEY)
    result = client.audio.transcriptions.create(
        file=(filename, audio_bytes),
        model=WHISPER_MODEL,
        # A short hint improves recognition of plant vocabulary.
        prompt="Steel plant SOP question. Terms: PPE, SCBA, blast furnace, coke oven, LD gas, BFG, COG, ppm, permit to work.",
        temperature=0.0,
    )
    return (result.text or "").strip()
