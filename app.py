import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import base64
import io

# 1. पेज की सेटिंग्स (प्रोफेशनल लुक के लिए)
st.set_page_config(
    page_title="My Personal AI Squad",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. Streamlit के फालतू बटन (Fork, GitHub, Footer) छिपाने के लिए CSS
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display:none;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 3. API Key सेटअप (Streamlit Secrets से)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("⚠️ कृपया Streamlit Settings -> Secrets में अपनी 'GEMINI_API_KEY' डालें।")

# 4. साइडबार: किरदारों और कहानी की मेमोरी के लिए
with st.sidebar:
    st.header("🧠 Story Memory")
    st.write("यहाँ अपनी कहानी की जानकारी लिखें ताकि AI इसे हमेशा याद रखे:")
    story_context = st.text_area(
        "कहानी और किरदार:",
        value="किरदार: सार्थक, आरव, गुरमीत, काव्या, रिया। दूसरी कहानी: प्यारे लाल (गरीब परिवार से), नंबर 1, 2, 3 और जी-1, जी-2, जी-3, जी-4।",
        height=150
    )
    voice_enabled = st.toggle("🔊 ऑटो-स्पीकर (AI बोलकर जवाब दे)", value=True)
    if st.button("🗑️ नई चैट शुरू करें"):
        st.session_state.messages = []
        st.rerun()

# 5. ऐप का मुख्य हेडर
st.title("🤖 My Personal AI Squad")
st.caption("आपका पर्सनल क्रिएटिव और स्टोरी असिस्टेंट")

# 6. बोलकर जवाब देने (Text-to-Speech) का फंक्शन
def speak_text(text):
    try:
        # हिंदी और इंग्लिश दोनों के लिए 'hi' या 'en' काम करता है
        tts = gTTS(text=text, lang='hi', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        # अपने आप चलने वाला (Autoplay) ऑडियो प्लेयर
        audio_html = f"""
            <audio autoplay="true" style="display:none;">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"ऑडियो चलाने में समस्या: {e}")

# 7. चैट हिस्ट्री सेव करना
if "messages" not in st.session_state:
    st.session_state.messages = []

# पुरानी चैट स्क्रीन पर दिखाना
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8. इनपुट बॉक्स (यहाँ आप कीबोर्ड के माइक से बोलकर भी लिख सकते हैं)
prompt = st.chat_input("बोलें या अपना सवाल यहाँ लिखें...")

if prompt:
    # यूज़र का मैसेज दिखाएं और सेव करें
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI से जवाब जनरेट करें
    with st.chat_message("assistant"):
        with st.spinner("सोच रहा हूँ..."):
            try:
                system_instruction = f"""
                तुम एक स्मार्ट, दोस्ताना और क्रिएटिव पर्सनल AI असिस्टेंट हो। 
                यूज़र से हिंदी/हिंग्लिश में बात करो। जवाब छोटे, सटीक और बोलने में आसान रखो ताकि स्पीकर पर अच्छे से सुने जा सकें।
                यूज़र की कहानियों की यह जानकारी हमेशा याद रखो: {story_context}
                """
                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",
                    system_instruction=system_instruction
                )
                
                # पिछली बातचीत का संदर्भ भेजना
                chat_history = [
                    {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
                    for m in st.session_state.messages[:-1]
                ]
                chat = model.start_chat(history=chat_history)
                response = chat.send_message(prompt)
                reply = response.text
                
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
                # अगर ऑटो-स्पीकर ऑन है, तो जवाब को तुरंत बोलकर सुनाएं
                if voice_enabled:
                    speak_text(reply)
                    
            except Exception as e:
                st.error(f"कुछ गड़बड़ हो गई: {e}")
              
