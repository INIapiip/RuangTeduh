import os
from dotenv import load_dotenv
import streamlit as st
import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from callback_handler import GeminiCallbackHandler
import PyPDF2

# Load API Key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

# CSS Loader
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Chat ke LLM
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

# Ekstrak teks PDF
def extract_text_from_pdf(uploaded_file) -> str:
    text = ""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        return f"Terjadi kesalahan saat membaca PDF: {str(e)}"

# Main App
def main():
    st.set_page_config(page_title="CeritaTeduh", page_icon="💖", layout="centered")
    load_css()

    if "user_name" not in st.session_state or "user_city" not in st.session_state:
        st.markdown("""
        <div class='header'>
            <h1>💖 Selamat Datang di CeritaTeduh</h1>
            <p>Yuk kenalan dulu sebelum ngobrol~</p>
        </div>
        """, unsafe_allow_html=True)

        name = st.text_input("Nama Kamu 💫")
        city = st.text_input("Asal Kota 🏡")

        if st.button("Mulai Chat 💖"):
            if name.strip() and city.strip():
                st.session_state.user_name = name.strip()
                st.session_state.user_city = city.strip()
                st.rerun()
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

        # Tampilkan semua pesan
        for message in st.session_state.messages:
            avatar = "🧑‍💻" if message["role"] == "user" else "💖"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

        # Input chat utama
        if user_input := st.chat_input("Tulis sesuatu..."):
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            st.session_state.messages.append({"role": "user", "content": user_input})

            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(user_input)
                st.caption(f"🕒 {timestamp}")

            with st.chat_message("assistant", avatar="💖"):
                with st.spinner("Sedang memikirkan jawaban terbaik..."):
                    response_text = run_agent(user_input)
                    response_time = datetime.datetime.now().strftime("%H:%M:%S")
                    st.markdown(response_text)
                    st.caption(f"🕒 {response_time}")
                    st.session_state.messages.append({"role": "assistant", "content": response_text})

        # Divider & layout 2 kolom untuk tombol & upload pdf
        st.divider()
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🗑️ Hapus Riwayat Chat"):
                st.session_state.messages = []
                st.success("Riwayat chat berhasil dihapus.")

        with col2:
            uploaded_pdf = st.file_uploader("📄 Upload PDF", type=["pdf"], label_visibility="collapsed")
            st.caption("📄 Upload PDF")

        if uploaded_pdf is not None:
            pdf_text = extract_text_from_pdf(uploaded_pdf)
            if pdf_text:
                st.info("Teks dari PDF berhasil diambil. Kamu bisa tanya isi PDF di bawah ini.")
                pdf_question = st.text_input("Tanya sesuatu tentang PDF...")
                if pdf_question:
                    with st.spinner("Sedang memproses jawaban..."):
                        combined_input = f"Tolong jawab berdasarkan isi PDF ini:\n\n{pdf_text}\n\nPertanyaan saya:\n{pdf_question}"
                        response_text = run_agent(combined_input)
                        st.session_state.messages.append({"role": "user", "content": pdf_question})
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                        st.rerun()

if __name__ == "__main__":
    main()
