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

# ✅ Example 10 questions (generic for bank/office/hospital use cases)
QUESTIONS = [
    "What is your full name?",
    "What is your date of birth?",
    "What is your address?",
    "What is your phone number?",
    "What service are you here for?",
    "Do you have any identity proof with you?",
    "What is your account number or reference ID?",
    "Do you need help filling the form?",
    "Do you need translation assistance?",
    "Do you want to receive further communication by phone or email?"
]

# ✅ Title
st.markdown("<h1 style='text-align: center; font-size: 42px; font-weight: bold;'>🏦 Counter Assistant System</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ✅ Language Selection
col1, col2 = st.columns(2)
with col1:
    counter_lang_name = st.selectbox("💼 Counter Staff Language", list(LANGUAGES.keys()), index=1)  # default English
with col2:
    customer_lang_name = st.selectbox("👥 Customer Language", list(LANGUAGES.keys()), index=0)      # default Hindi

counter_lang = LANGUAGES[counter_lang_name]
customer_lang = LANGUAGES[customer_lang_name]

st.markdown("<h3 style='text-align:center;'>💬 Predefined Questions for the Customer</h3>", unsafe_allow_html=True)

# ✅ Display questions in customer language
translator = Bhashini(sourceLanguage=counter_lang, targetLanguage=customer_lang)
translator.getPipeLineConfig("translation")
translator.getPipeLineConfig("tts")

for idx, q in enumerate(QUESTIONS, start=1):
    try:
        q_translated = translator.translate(q)
        st.markdown(f"<p style='font-size:20px;'><b>{idx}. {q_translated}</b></p>", unsafe_allow_html=True)

        # Button to play audio of question
        if st.button(f"🔊 Play Question {idx}", key=f"tts_{idx}"):
            tts_b64 = translator.tts(q_translated)
            tts_audio = base64.b64decode(tts_b64)
            st.audio(tts_audio, format="audio/wav")

    except Exception as e:
        st.error(f"⚠️ Failed to translate question {idx}: {e}")

st.markdown("<hr>", unsafe_allow_html=True)

# ✅ Customer Response Section
st.markdown("<h3 style='text-align:center;'>🎤 If you have any further questions, you can speak in the mic</h3>", unsafe_allow_html=True)
audio_bytes = audio_recorder("🎙️ Record Answer", "⏹ Stop Recording")

if audio_bytes is not None and len(audio_bytes) > 0:
    st.audio(audio_bytes, format="audio/wav")
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    if st.button("🚀 Process Answer", use_container_width=True):
        with st.spinner("⏳ Processing..."):
            try:
                # Step 1: Speech → Text (in customer language)
                customer_translator = Bhashini(sourceLanguage=customer_lang, targetLanguage=counter_lang)
                customer_translator.getPipeLineConfig("asr")
                asr_text = customer_translator.asr(audio_b64)

                st.markdown("<h4>📝 Recognized (Customer Language):</h4>", unsafe_allow_html=True)
                st.success(asr_text)

                # Step 2: Translate → Counter staff language
                customer_translator.getPipeLineConfig("translation")
                translated_text = customer_translator.translate(asr_text)

                st.markdown("<h4>🌍 Translation (For Counter Staff):</h4>", unsafe_allow_html=True)
                st.info(translated_text)

                # Step 3: TTS for counter staff if needed
                customer_translator.getPipeLineConfig("tts")
                tts_b64 = customer_translator.tts(translated_text)
                tts_audio = base64.b64decode(tts_b64)

                st.markdown("🔊 Play Translated Answer (Counter Language):")
                st.audio(tts_audio, format="audio/wav")

            except Exception as e:
                st.error(f"❌ Processing failed: {e}")
