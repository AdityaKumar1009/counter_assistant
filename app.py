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

# ✅ Questions for Railway Enquiry
RAILWAY_QUESTIONS = [
    "What is your full name?",
    "What is your phone number?",
    "What is your PNR number?",
    "What is your train number or train name?",
    "What is your boarding station?",
    "What is your destination station?",
    "What is your date of journey?",
    "Do you need to check seat availability?",
    "Do you want to enquire about train timings?",
    "Do you want to enquire about train delay status?",
    "Do you want to know about platform information?",
    "Do you need help with ticket cancellation or refund?"
]

# ✅ Questions for Airport Enquiry
AIRPORT_QUESTIONS = [
    "What is your full name?",
    "What is your phone number?",
    "Do you have any identity proof with you?",
    "What is your flight number?",
    "What is your departure city?",
    "What is your destination city?",
    "What is your travel date?",
    "Do you need to check flight status?",
    "Do you want to enquire about check-in counters?",
    "Do you want to enquire about boarding gates?",
    "Do you want to know baggage allowance?",
    "Do you need information about delays or cancellations?",
    "Do you need help with ticket rescheduling?"
]

# ✅ Title
st.markdown("<h1 style='text-align: center; font-size: 42px; font-weight: bold;'>🛠️ Counter Assistant System</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ✅ Service Selection
service_type = st.radio(
    "Select Service Type:",
    ("🚆 Railway Enquiry", "✈️ Airport Enquiry"),
    horizontal=True
)

if service_type == "🚆 Railway Enquiry":
    QUESTIONS = RAILWAY_QUESTIONS
else:
    QUESTIONS = AIRPORT_QUESTIONS

# ✅ Language Selection
col1, col2 = st.columns(2)
with col1:
    counter_lang_name = st.selectbox("💼 Counter Staff Language", list(LANGUAGES.keys()), index=1)  # default English
with col2:
    customer_lang_name = st.selectbox("👥 Customer Language", list(LANGUAGES.keys()), index=0)      # default Hindi

counter_lang = LANGUAGES[counter_lang_name]
customer_lang = LANGUAGES[customer_lang_name]

# ✅ Translator object
translator = Bhashini(sourceLanguage=counter_lang, targetLanguage=customer_lang)
translator.getPipeLineConfig("translation")
translator.getPipeLineConfig("tts")

# ✅ Translate heading
if service_type == "🚆 Railway Enquiry":
    heading_text = "Railway Enquiry Questions for the Customer"
else:
    heading_text = "Airport Enquiry Questions for the Customer"

translator.getPipeLineConfig("translation")
heading_translated = translator.translate(heading_text)
st.markdown(f"<h3 style='text-align:center;'>💬 {heading_translated}</h3>", unsafe_allow_html=True)

# ✅ Loop through questions
for idx, q in enumerate(QUESTIONS, start=1):
    try:
        # Translate question
        q_translated = translator.translate(q)
        st.markdown(f"<p style='font-size:20px;'><b>{idx}. {q_translated}</b></p>", unsafe_allow_html=True)

        # Button to play question in audio
        if st.button(f"🔊 Play Question {idx}", key=f"tts_{idx}"):
            tts_b64 = translator.tts(q_translated)
            tts_audio = base64.b64decode(tts_b64)
            st.audio(tts_audio, format="audio/wav")

        # --- ✅ Customer Audio Answer ---
        st.markdown(f"<p style='font-size:16px;'>🎤 Answer for Question {idx}:</p>", unsafe_allow_html=True)
        audio_bytes = audio_recorder(f"🎙️ Record Answer {idx}", f"⏹ Stop Recording {idx}", key=f"rec_{idx}")

        if audio_bytes is not None and len(audio_bytes) > 0:
            st.audio(audio_bytes, format="audio/wav")
            audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

            # Process Answer Button
            if st.button(f"🚀 Process Answer {idx}", key=f"process_{idx}"):
                with st.spinner("⏳ Processing answer..."):
                    try:
                        # Step 1: ASR - Convert speech → text (customer language)
                        customer_translator = Bhashini(sourceLanguage=customer_lang, targetLanguage=counter_lang)
                        customer_translator.getPipeLineConfig("asr")
                        asr_text = customer_translator.asr(audio_b64)

                        st.markdown("<h5>📝 Recognized (Customer Language):</h5>", unsafe_allow_html=True)
                        st.success(asr_text)

                        # Step 2: Translate to counter staff language
                        customer_translator.getPipeLineConfig("translation")
                        translated_text = customer_translator.translate(asr_text)

                        st.markdown("<h5>🌍 Translation (For Counter Staff):</h5>", unsafe_allow_html=True)
                        st.info(translated_text)

                        # Step 3: Optional TTS for staff answer
                        customer_translator.getPipeLineConfig("tts")
                        tts_b64 = customer_translator.tts(translated_text)
                        tts_audio = base64.b64decode(tts_b64)
                        st.markdown("🔊 Play Translated Answer (Counter Language):")
                        st.audio(tts_audio, format="audio/wav")

                    except Exception as e:
                        st.error(f"❌ Processing failed: {e}")

        st.markdown("<hr>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ Failed to translate question {idx}: {e}")

# ✅ Customer Response Section 
final_text = "🎤 If you have any further questions, you can speak in the mic" 
translator.getPipeLineConfig("translation") 
final_translated = translator.translate(final_text) 
st.markdown(f"<h3 style='text-align:center;'>💬 {final_translated}</h3>", unsafe_allow_html=True) 
audio_bytes = audio_recorder("🎙️ Record Answer", "⏹ Stop Recording")
