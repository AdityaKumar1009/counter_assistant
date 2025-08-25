import streamlit as st
from audio_recorder_streamlit import audio_recorder
from dotenv import load_dotenv
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
    "Urdu (ur)": "ur",
    "Maithili (mai)": "mai"
}

# ✅ Big Bold Title
st.markdown("<h1 style='text-align: center; font-size: 42px; font-weight: bold;'>🌐 Bhashini Speech-to-Speech Translator</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ✅ Language Selection (center aligned, large font)
col1, col2 = st.columns(2)
with col1:
    source_lang_name = st.selectbox("🎤 Source Language", list(LANGUAGES.keys()), index=1)
with col2:
    target_lang_name = st.selectbox("🔊 Target Language", list(LANGUAGES.keys()), index=0)

source_lang = LANGUAGES[source_lang_name]
target_lang = LANGUAGES[target_lang_name]

st.markdown("<p style='font-size:22px;'>🎙️ Press record and speak. When done, click <b>Stop Recording</b>.</p>", unsafe_allow_html=True)

# ✅ Recorder button
audio_bytes = audio_recorder("🎙️ Record", "⏹ Stop Recording")

if audio_bytes is not None and len(audio_bytes) > 0:
    st.audio(audio_bytes, format="audio/wav")
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    if st.button("🚀 Translate Speech!", use_container_width=True):
        with st.spinner("⏳ Translating, please wait..."):
            try:
                translator = Bhashini(sourceLanguage=source_lang, targetLanguage=target_lang)

                # ASR step - convert speech to text in source language
                translator.getPipeLineConfig("asr")
                asr_text = translator.asr(audio_b64)

                st.markdown("<h2 style='color:#004080;'>📝 Recognized Speech:</h2>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:30px; font-weight:bold; color:white;'>{asr_text}</p>", unsafe_allow_html=True)

                # NMT step - translate text from source to target
                translator.getPipeLineConfig("translation")
                nmt_text = translator.translate(asr_text)

                st.markdown("<h2 style='color:#004080;'>🌍 Translation:</h2>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:36px; font-weight:bold; color:white;'>{nmt_text}</p>", unsafe_allow_html=True)

                # TTS step - synthesize speech from translated text
                translator.getPipeLineConfig("tts")
                tts_b64 = translator.tts(nmt_text)
                tts_audio = base64.b64decode(tts_b64)

                st.markdown("<h2 style='color:#004080;'>🔊 Speech Output:</h2>", unsafe_allow_html=True)
                st.audio(tts_audio, format="audio/wav")
                st.download_button("⬇️ Download Translated Audio", data=tts_audio, file_name="translated_speech.wav", mime="audio/wav")

            except Exception as e:
                st.error(f"❌ Translation failed: {e}")

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:18px; color:gray;'>Select or change languages and record additional speech to translate again!</p>", unsafe_allow_html=True)
