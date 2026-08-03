import os
import streamlit as st
import pandas as pd
from datetime import datetime
import base64
from groq import Groq
from gtts import gTTS
import speech_recognition as sr
import tempfile

# 1. Page Configuration
st.set_page_config(
    page_title="Ezitech AI Mentor & Student Assistant",
    layout="wide",
    page_icon="🎓"
)

# 2. Safely Fetch Groq API Key from Streamlit Secrets or Environment
api_key = None
try:
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

if not api_key:
    api_key = os.environ.get("GROQ_API_KEY")

# Initialize Groq Client
client = None
if api_key:
    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        st.error(f"Failed to initialize Groq client: {e}")

# 3. Initialize Session States
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your Ezitech AI Mentor & Student Assistant. How can I help you with your internship guidelines, case studies, or debugging concepts today?"}
    ]
if "nav_option" not in st.session_state:
    st.session_state.nav_option = "AI Chat Assistant"

# 4. Sidebar Profile & Navigation
with st.sidebar:
    st.markdown("💻 **Developed by Taiba Kabir**")
    
    # Hijabi Avatar / Profile Card HTML
    st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 20px;">
            <div style="font-size: 50px; margin-bottom: 10px;">🧕</div>
            <h3 style="margin: 0; font-size: 20px;">taiba kabir</h3>
            <p style="margin: 5px 0 0 0; font-size: 12px; opacity: 0.8;">taibakabir240@gmail.com</p>
            <span style="background: rgba(255,255,255,0.2); padding: 2px 10px; border-radius: 10px; font-size: 11px; margin-top: 8px;">Role: Student</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🧭 Navigation Menu")
    nav_choice = st.radio(
        "Go to",
        ["AI Chat Assistant", "Task & Progress Tracker", "Resource Hub", "Code Playground", "Saved Bookmarks"],
        label_visibility="collapsed"
    )
    st.session_state.nav_option = nav_choice

# 5. Main Content Area based on Navigation
if st.session_state.nav_option == "AI Chat Assistant":
    st.markdown("Ask questions about your internship guidelines, case studies, or debugging concepts via text or voice.")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = [{"role": "assistant", "content": "Chat history cleared. How can I help you?"}]
            st.rerun()
    with col2:
        chat_history_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages])
        st.download_button("📥 Download Chat History", chat_history_text, file_name="chat_history.txt")

    st.markdown("---")

    # Display Chat History
    for message in st.session_state.messages:
        avatar = "🧕" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.write(message["content"])

    # Chat Input Box
    if prompt := st.chat_input("Type your message here..."):
        # Append user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧕"):
            st.write(prompt)

        # Generate AI Response using Direct Groq Client
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                if not client:
                    ai_reply = "Error: Groq API Key is missing or invalid. Please check your Streamlit Secrets."
                else:
                    try:
                        # Construct messages for Groq API
                        formatted_messages = [
                            {"role": "system", "content": "You are a helpful, professional AI mentor and student assistant within the Ezitech ecosystem, guiding interns with programming, debugging, and academic projects."}
                        ]
                        for m in st.session_state.messages:
                            # Map roles correctly for Groq API
                            role = "user" if m["role"] == "user" else "assistant"
                            formatted_messages.append({"role": role, "content": m["content"]})

                        completion = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=formatted_messages,
                            temperature=0.7,
                            max_tokens=1024
                        )
                        ai_reply = completion.choices[0].message.content
                    except Exception as e:
                        ai_reply = f"An error occurred while generating response: {e}"
                
                st.write(ai_reply)
        
        # Append assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})

    # Feedback Section at bottom
    st.markdown("---")
    st.markdown("### ⭐ Session Feedback & Rating")
    rating = st.radio("Select Rating Level:", ["WORST", "BAD", "NEUTRAL", "GOOD", "EXCELLENT"], horizontal=True, index=4)
    if st.button("Submit Feedback"):
        st.success("Thank you for your valuable feedback!")

elif st.session_state.nav_option == "Task & Progress Tracker":
    st.header("📋 Task & Progress Tracker")
    st.write("Track your Ezitech internship tasks and milestones here.")
    df = pd.DataFrame({
        "Task": ["Setup Environment", "Parallel Computing Case Study", "YOLOv8 License Plate Detection", "AI Mentor UI Integration"],
        "Status": ["Completed", "Completed", "In Progress", "Pending"],
        "Priority": ["High", "High", "Medium", "High"]
    })
    st.dataframe(df, use_container_width=True)

elif st.session_state.nav_option == "Resource Hub":
    st.header("📚 Resource Hub")
    st.info("Access your study materials, research proposals, and documentation here.")
    st.markdown("""
    * [Ezitech Framework Documentation](https://ezitech.org)
    * [Parallel Distributed Computing Notes](https://github.com)
    * [OpenMP & CUDA Codebases](https://github.com)
    """)

elif st.session_state.nav_option == "Code Playground":
    st.header("⚡ Code Playground")
    st.write("Test snippets or view your code workspace configuration.")
    code_input = st.text_area("Python Code Snippet", "print('Hello from Ezitech AI Mentor!')")
    if st.button("Run Code"):
        st.code("Hello from Ezitech AI Mentor!\nExecution successful.", language="text")

elif st.session_state.nav_option == "Saved Bookmarks":
    st.header("🔖 Saved Bookmarks")
    st.write("No bookmarks saved yet. Star important chats or articles to see them here.")