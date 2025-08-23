from dotenv import load_dotenv
import os
import base64
import speech_recognition as sr
from bhashini_translator import Bhashini

load_dotenv()

def record_audio(duration=5, sample_rate=16000):
    """
    Record speech from microphone and return raw wav bytes.
    """
    r = sr.Recognizer()
    with sr.Microphone(sample_rate=sample_rate) as source:
        print("Adjusting for ambient noise. Please wait...")
        r.adjust_for_ambient_noise(source)
        print(f"Recording for {duration} seconds. Please speak now!")
        audio = r.record(source, duration=duration)
        print("Recording complete.")
        return audio.get_wav_data()

def wav_bytes_to_base64(wav_bytes):
    """
    Convert raw WAV bytes to a base64 string.
    """
    return base64.b64encode(wav_bytes).decode("utf-8")

def speech_to_speech_from_mic(source_lang, target_lang, duration=5, output_file="output_speech_to_speech.wav"):
    # Record audio from mic
    wav_bytes = record_audio(duration=duration)
    audio_b64 = wav_bytes_to_base64(wav_bytes)

    # Create translator instance
    translator = Bhashini(sourceLanguage=source_lang, targetLanguage=target_lang)
    translator.getPipeLineConfig("asr")

    # ASR -> NMT -> TTS
    translated_audio_b64 = translator.asr_nmt_tts(audio_b64)

    # Save output WAV
    with open(output_file, "wb") as f:
        f.write(base64.b64decode(translated_audio_b64))
    print(f"Translated speech-to-speech audio saved as: {output_file}")

if __name__ == "__main__":
    # Example: English -> Hindi, record for 7 seconds
    speech_to_speech_from_mic(source_lang="hi", target_lang="pa", duration=5)


