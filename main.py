import os
from dotenv import load_dotenv
import streamlit as st
import datetime
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from callback_handler import GeminiCallbackHandler
from googlesearch import search
from tools.date_tools import show_current_date
from tools.cooping_tools import get_coping_tips
from tools.pscyologist_tools import get_professional_help
from tools.translate_tools import TranslationService
from streamlit.runtime.scriptrunner import RerunException
from streamlit.runtime.scriptrunner import get_script_run_ctx

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def run_agent(user_input: str) -> str:
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.2,
            callbacks=[GeminiCallbackHandler()],
            convert_system_message_to_human=True
        )

        response = llm.invoke(user_input)
        return str(response.content)
    except Exception as e:
        return f"Terjadi kesalahan: {str(e)}"

def main():
    st.set_page_config(page_title="Chatbot AI Kesehatan Mental", page_icon="🧠", layout="centered")
    load_css()

    if "user_name" not in st.session_state or "user_city" not in st.session_state:
        st.markdown("""
        <div class='header'>
            <h1>💖 Selamat Datang di Chatbot Kesehatan Mental</h1>
            <p>Sebelum kita ngobrol, kenalan dulu yuk~</p>
        </div>
        """, unsafe_allow_html=True)

        st.write("Isi data berikut:")
        name = st.text_input("Nama Kamu:")
        city = st.text_input("Asal Kota:")

        if st.button("Mulai Chat", type="primary"):
            if name.strip() and city.strip():
                st.session_state.user_name = name.strip()
                st.session_state.user_city = city.strip()
                raise RerunException(get_script_run_ctx())
            else:
                st.warning("Nama dan Kota wajib diisi dulu ya!")

    else:
        st.markdown(f"""
        <div class='header'>
            <h1>💖 Hai {st.session_state.user_name}!</h1>
            <p>Senang bisa ngobrol bareng kamu dari {st.session_state.user_city} ✨</p>
        </div>
        """, unsafe_allow_html=True)

        if "messages" not in st.session_state:
            st.session_state.messages = [{
                "role": "assistant",
                "content": f"Halo {st.session_state.user_name}! Aku senang bisa menemani kamu. Cerita apa hari ini?"
            }]

        for message in st.session_state.messages:
            avatar = "🧑‍💻" if message["role"] == "user" else "🧠"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

        if user_input := st.chat_input("Tulis sesuatu..."):
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            st.session_state.messages.append({"role": "user", "content": user_input})

            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(user_input)
                st.caption(f"🕒 {timestamp}")

            with st.chat_message("assistant", avatar="🧠"):
                with st.spinner("Sedang memikirkan jawaban terbaik..."):
                    response_text = run_agent(user_input)
                    response_time = datetime.datetime.now().strftime("%H:%M:%S")
                    st.markdown(response_text)
                    st.caption(f"🕒 {response_time}")
                    st.session_state.messages.append({"role": "assistant", "content": response_text})

if __name__ == "__main__":
    main()