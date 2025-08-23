import streamlit as st
from audio_recorder_streamlit import audio_recorder
from dotenv import load_dotenv
import os
import base64
from bhashini_translator import Bhashini

load_dotenv()

LANGUAGES = {
    "Hindi (hi)": "hi",
    "English (en)": "en",
    "Bengali (bn)": "bn",
    "Tamil (ta)": "ta",
    "Telugu (te)": "te",
    "Gujarati (gu)": "gu",
    "Kannada (kn)": "kn",
    "Malayalam (ml)": "ml",
    "Marathi (mr)": "mr",
    "Punjabi (pa)": "pa",
    "Urdu (ur)": "ur"
    # add more as needed
}

st.title("Bhashini Speech-to-Speech Translator")

source_lang_name = st.selectbox("Select Source Language", list(LANGUAGES.keys()), index=1)
target_lang_name = st.selectbox("Select Target Language", list(LANGUAGES.keys()), index=0)
source_lang = LANGUAGES[source_lang_name]
target_lang = LANGUAGES[target_lang_name]

st.write("Press record and speak. When done, click 'Stop Recording'.")

audio_bytes = audio_recorder("Click to record", "Stop Recording")

if audio_bytes is not None and len(audio_bytes) > 0:
    st.audio(audio_bytes, format="audio/wav")
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    if st.button("Translate Speech!"):
        with st.spinner("Translating, please wait..."):
            try:
                translator = Bhashini(sourceLanguage=source_lang, targetLanguage=target_lang)
                translator.getPipeLineConfig("asr")
                result_b64 = translator.asr_nmt_tts(audio_b64)
                result_wav = base64.b64decode(result_b64)
                st.success("Your translated speech:")
                st.audio(result_wav, format="audio/wav")
                st.download_button("Download Translated Audio", data=result_wav, file_name="translated_speech.wav", mime="audio/wav")
            except Exception as e:
                st.error(f"Translation failed: {e}")

st.markdown("---")
st.info("Select or change languages and record additional speech to translate again!")
