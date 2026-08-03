import streamlit as st
import requests
import gtts
import os
import speech_recognition as sr
import pandas as pd
from datetime import datetime
import base64

# FastAPI Backend URL
BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Ezitech AI Mentor & Student Assistant", layout="wide", page_icon="🎓")

# Embedded, self-contained default Hijabi Avatar SVG (Never breaks or fails to load)
DEFAULT_HIJABI_AVATAR = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200'><circle cx='100' cy='100' r='100' fill='%23111827'/><path d='M 35 130 C 30 65, 55 25, 100 25 C 145 25, 170 65, 165 130 C 160 160, 145 185, 135 198 L 65 198 C 55 185, 40 160, 35 130 Z' fill='%231f2937'/><ellipse cx='100' cy='108' rx='34' ry='40' fill='%23fed7aa'/><path d='M 64 100 C 64 70, 78 66, 100 66 C 122 66, 136 70, 136 100 C 136 128, 124 142, 100 144 C 76 142, 64 128, 64 100 Z' fill='none' stroke='%23111827' stroke-width='8'/><path d='M 70 96 C 70 88, 93 88, 93 96 C 93 112, 70 112, 70 96 Z' fill='%23030712' stroke='%23d97706' stroke-width='2.5'/><ellipse cx='78' cy='94' rx='4' ry='2' fill='%23ffffff' opacity='0.7'/><path d='M 107 96 C 107 88, 130 88, 130 96 C 130 112, 107 112, 107 96 Z' fill='%23030712' stroke='%23d97706' stroke-width='2.5'/><ellipse cx='115' cy='94' rx='4' ry='2' fill='%23ffffff' opacity='0.7'/><line x1='93' y1='94' x2='107' y2='94' stroke='%23d97706' stroke-width='2.5'/><path d='M 92 130 Q 100 135 108 130' fill='none' stroke='%23e11d48' stroke-width='3' stroke-linecap='round'/><path d='M 25 198 C 35 160, 60 145, 75 142 C 85 154, 115 154, 125 142 C 140 145, 165 160, 175 198 Z' fill='%23111827'/></svg>"

# Initialize Authentication States & Settings State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "username" not in st.session_state:
    st.session_state.username = "taiba kabir"
if "email" not in st.session_state:
    st.session_state.email = "taibakabir240@gmail.com"
if "user_bio" not in st.session_state:
    st.session_state.user_bio = "Passionate learner and developer exploring AI & FastAPI."
if "profile_image" not in st.session_state:
    st.session_state.profile_image = DEFAULT_HIJABI_AVATAR
if "linkedin_link" not in st.session_state:
    st.session_state.linkedin_link = "https://linkedin.com"
if "github_link" not in st.session_state:
    st.session_state.github_link = "https://github.com"
if "notifications_enabled" not in st.session_state:
    st.session_state.notifications_enabled = True
if "data_saver" not in st.session_state:
    st.session_state.data_saver = False
if "announcements" not in st.session_state:
    st.session_state.announcements = []
if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = []
if "task_progress" not in st.session_state:
    st.session_state.task_progress = {
        "Case Study 1: AI Knowledge Graph": True,
        "Case Study 2: Intelligent AI Code Reviewer": False,
        "Python & FastAPI Setup": True,
        "Streamlit UI Customization": False
    }

# Real-time Persistent Activity Log state for Mentors
if "activity_logs" not in st.session_state:
    st.session_state.activity_logs = [
        {"Intern Name": "Ali Khan", "Login Time": "2026-07-31 09:15 AM", "Status": "🟢 Online", "Time Spent": "3 Hours 45 Mins"},
        {"Intern Name": "Ayesha Ahmed", "Login Time": "2026-07-31 10:00 AM", "Status": "🟢 Online", "Time Spent": "2 Hours 30 Mins"},
    ]

# Temporary variables before login or check
if not st.session_state.logged_in:
    selected_theme = st.sidebar.selectbox("🎨 Choose Theme", ["Ezitech Modern", "Dark Mode", "Clean Light"], key="pre_theme")
    selected_language = st.sidebar.selectbox("🌐 Language", ["English", "Urdu (اردو)"], key="pre_lang")
else:
    if "selected_theme" not in st.session_state:
        st.session_state.selected_theme = "Ezitech Modern"
    if "selected_language" not in st.session_state:
        st.session_state.selected_language = "English"
    selected_theme = st.session_state.selected_theme
    selected_language = st.session_state.selected_language

# Apply Global CSS Theme with Blue Profile Header Banner
if selected_theme == "Dark Mode":
    global_theme_css = """
        <style>
            .stApp { background-color: #0e1117; color: #ffffff; }
            .main { background-color: #0e1117; color: #ffffff; }
            [data-testid="stSidebar"] { background-color: #161b22; color: #ffffff; padding-top: 0px !important; }
            [data-testid="stSidebar"] > div:first-child { padding-top: 0rem !important; }
            h1, h2, h3, h4, h5, h6 { color: #58a6ff !important; }
            div.stTextInput > div > div > input, 
            div.stTextArea > div > div > textarea, 
            div.stNumberInput > div > div > input {
                background-color: #21262d;
                color: #ffffff;
                border: 1px solid #30363d;
            }
            .profile-header-banner { background: linear-gradient(135deg, #2563eb 100%, #1e3a8a 100%); border-radius: 0 0 20px 20px; padding: 20px 15px; text-align: center; color: white; margin: -1rem -1rem 1rem -1rem; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        </style>
    """
elif selected_theme == "Ezitech Modern":
    global_theme_css = """
        <style>
            .stApp { background-color: #f4f6f9; color: #1f2937; }
            .main { background-color: #f4f6f9; }
            [data-testid="stSidebar"] { background-color: #e5e9f0; padding-top: 0px !important; }
            [data-testid="stSidebar"] > div:first-child { padding-top: 0rem !important; }
            h1, h2, h3 { color: #1e3a8a !important; }
            .stButton>button { border-radius: 8px; font-weight: 600; background-color: #2563eb; color: white; border: none; }
            .stButton>button:hover { background-color: #1d4ed8; color: white; }
            div.stTextInput > div > div > input, 
            div.stTextArea > div > div > textarea, 
            div.stNumberInput > div > div > input {
                background-color: #ffffff;
                color: #1f2937;
                border: 1px solid #cbd5e1;
            }
            .profile-header-banner { background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%); border-radius: 0 0 20px 20px; padding: 20px 15px; text-align: center; color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin: -1rem -1rem 1rem -1rem; }
        </style>
    """
else:
    global_theme_css = """
        <style>
            .stApp { background-color: #ffffff; color: #000000; }
            .main { background-color: #ffffff; }
            [data-testid="stSidebar"] { padding-top: 0px !important; }
            [data-testid="stSidebar"] > div:first-child { padding-top: 0rem !important; }
            .profile-header-banner { background: #60a5fa; border-radius: 0 0 20px 20px; padding: 20px 15px; text-align: center; color: white; margin: -1rem -1rem 1rem -1rem; }
        </style>
    """

st.markdown(global_theme_css, unsafe_allow_html=True)

# Localization Dictionaries
translations = {
    "English": {
        "title": "🎓 Ezitech AI Mentor Assistant & Internship Platform",
        "subtitle": "Welcome! Please sign in or register to access your dedicated portal.",
        "login_header": "🔐 User Authentication Portal",
        "role_select": "Select Your Role",
        "auth_mode": "Choose Action",
        "login": "Sign In",
        "register": "Register",
        "user_input": "Full Name / Username",
        "email_input": "Email Address",
        "pass_input": "Password",
        "login_btn": "🚀 Login",
        "register_btn": "📝 Create Account",
        "logout_btn": "🚪 Sign Out",
        "success_login": "Logged in successfully as",
        "success_reg": "Account created successfully! You can now log in.",
        "invalid_creds": "Please fill in all required fields (Name, Email, and Password).",
        "st_header": "Student Assistant Portal",
        "st_desc": "Ask questions about your internship guidelines, case studies, or debugging concepts via text or voice.",
        "input_ph": "Type your message here...",
        "send_btn": "📤 Send Message",
        "send_voice_btn": "📤 Send Voice",
        "clear_btn": "🗑️ Clear Chat",
        "download_btn": "📥 Download Chat History",
        "context_label": "View Retrieved Context",
        "thinking": "Thinking...",
        "mentor_header": "Mentor Performance Intelligence Dashboard & Voice Assistant",
        "mentor_desc": "Analyze intern performance, calculate confidence scores, track activity logs, and broadcast announcements.",
        "intern_name": "Intern Name",
        "completed_tasks": "Completed Tasks",
        "pending_tasks": "Pending Tasks",
        "recent_scores": "Recent Scores (comma separated)",
        "mentor_notes": "Mentor Notes",
        "analyze_btn": "Analyze Performance & Generate Report",
        "analyzing": "Analyzing performance & calculating confidence...",
        "report_download": "📥 Download Automated Mentor Report",
        "voice_btn": "🔊 Play AI Voice Report",
        "feedback_header": "⭐ Session Feedback & Rating",
        "feedback_ph": "Leave your feedback or suggestions here...",
        "rating_label": "Select Rating Level:",
        "feedback_btn": "Submit Feedback",
        "feedback_success": "Thank you! Your feedback has been recorded successfully.",
        "ratings_options": ["⭐ WORST", "⭐⭐ BAD", "⭐⭐⭐ NEUTRAL", "⭐⭐⭐⭐ GOOD", "⭐⭐⭐⭐⭐ EXCELLENT"]
    },
    "Urdu (اردو)": {
        "title": "🎓 ایزی ٹیک اے آئی مینٹور اسسٹنٹ اور انٹرنشپ پلیٹ فارم",
        "subtitle": "خوش آمدید! اپنے پورٹل تک رسائی کے لیے سائن ان یا رجسٹر کریں۔",
        "login_header": "🔐 یوزر تصدیق پورٹل",
        "role_select": "اپنا کردار منتخب کریں",
        "auth_mode": "عمل منتخب کریں",
        "login": "سائن ان",
        "register": "رجسٹر",
        "user_input": "مکمل نام / یوزر نیم",
        "email_input": "ای میل ایڈریس",
        "pass_input": "پاس ورڈ",
        "login_btn": "🚀 لاگ ان کریں",
        "register_btn": "📝 اکاؤنٹ بنائیں",
        "logout_btn": "🚪 سائن آؤٹ",
        "success_login": "کامیابی سے لاگ ان ہو گئے بطور",
        "success_reg": "اکاؤنٹ کامیابی سے بن گیا! اب آپ لاگ ان کر سکتے ہیں۔",
        "invalid_creds": "براہ کرم تمام خانے (نام، ای میل اور پاس ورڈ) پر کریں۔",
        "st_header": "سٹوڈنٹ اسسٹنٹ پورٹل",
        "st_desc": "ٹیکسٹ لکھیں یا وائس کے ذریعے اپنے سوالات پوچھیں۔",
        "input_ph": "یہاں اپنا پیغام لکھیں...",
        "send_btn": "📤 پیغام بھیجیں",
        "send_voice_btn": "📤 وائس بھیجیں",
        "clear_btn": "🗑️ چیٹ صاف کریں",
        "download_btn": "📥 چیٹ ہسٹری ڈاؤن لوڈ کریں",
        "context_label": "حوالہ دیکھیے",
        "thinking": "سوچ رہا ہے...",
        "mentor_header": "مینٹور پرفارمنس انٹیلی جنس ڈیش بورڈ اور وائس اسسٹنٹ",
        "mentor_desc": "انٹرن کی کارکردگی کا تجزیہ کریں، ایکٹیویٹی لاگ دیکھیں اور اناउंसمنٹ نشر کریں۔",
        "intern_name": "انٹرن کا نام",
        "completed_tasks": "مکمل ٹاسکس",
        "pending_tasks": "بقیہ ٹاسکس",
        "recent_scores": "نمبرز (کوما سے الگ کریں)",
        "mentor_notes": "مینٹور کے نوٹس",
        "analyze_btn": "کارکردگی کا تجزیہ اور رپورٹ بنائیں",
        "analyzing": "تجزیہ اور سکور کا حساب لگایا جا رہا ہے...",
        "report_download": "📥 آٹومیٹڈ مینٹور رپورٹ ڈاؤن لوڈ کریں",
        "voice_btn": "🔊 اے آئی وائس رپورٹ سنیں",
        "feedback_header": "⭐ سیشن فیڈبیک اور ریٹنگ",
        "feedback_ph": "یہاں اپنا فیڈبیک یا تجاویز درج کریں...",
        "rating_label": "ریٹنگ کا انتخاب کریں:",
        "feedback_btn": "فیڈبیک جمع کریں",
        "feedback_success": "شکریہ! آپ کا فیڈبیک کامیابی سے محفوظ کر لیا گیا ہے۔",
        "ratings_options": ["⭐ WORST", "⭐⭐ BAD", "⭐⭐⭐ NEUTRAL", "⭐⭐⭐⭐ GOOD", "⭐⭐⭐⭐⭐ EXCELLENT"]
    }
}

t = translations[selected_language]

st.title(t["title"])
st.write(t["subtitle"])

# Authentication Flow
if not st.session_state.logged_in:
    st.markdown("---")
    st.subheader(t["login_header"])
    
    auth_col1, auth_col2 = st.columns(2)
    with auth_col1:
        auth_role = st.selectbox(t["role_select"], ["Student", "Mentor"])
        auth_action = st.radio(t["auth_mode"], [t["login"], t["register"]])
    
    with auth_col2:
        input_username = st.text_input(t["user_input"], value="taiba kabir")
        input_email = st.text_input(t["email_input"], value="taibakabir240@gmail.com")
        input_password = st.text_input(t["pass_input"], type="password", value="123456")
        
        if auth_action == t["login"]:
            if st.button(t["login_btn"]):
                if input_username.strip() and input_email.strip() and input_password.strip():
                    st.session_state.logged_in = True
                    st.session_state.user_role = auth_role
                    st.session_state.username = input_username
                    st.session_state.email = input_email
                    st.success(f"{t['success_login']} {auth_role} ({input_username})")
                    st.rerun()
                else:
                    st.error(t["invalid_creds"])
        else:
            if st.button(t["register_btn"]):
                if input_username.strip() and input_email.strip() and input_password.strip():
                    st.success(f"{t['success_reg']} ({auth_role}: {input_username})")
                else:
                    st.error(t["invalid_creds"])
else:
    # Guaranteed DP Image Handler (Default Avatar or User Uploaded Base64)
    img_src = st.session_state.profile_image if st.session_state.profile_image else DEFAULT_HIJABI_AVATAR

    st.sidebar.markdown(f"""
        <div class="profile-header-banner">
            <div style="font-weight: 600; font-size: 13px; color: #e0f2fe; margin-bottom: 8px; letter-spacing: 0.5px;">💻 Developed by Taiba</div>
            <div style="display: flex; justify-content: center; margin-bottom: 6px;">
                <img src="{img_src}" style="width: 75px; height: 75px; border-radius: 50%; object-fit: cover; border: 3px solid white; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
            </div>
            <div style="font-weight: 700; font-size: 17px; color: #ffffff;">{st.session_state.username}</div>
            <div style="font-size: 11px; opacity: 0.9; margin-top: 2px; color: #f0fdf4;">{st.session_state.email}</div>
            <div style="font-size: 11px; margin-top: 5px; background: rgba(255,255,255,0.2); display: inline-block; padding: 2px 10px; border-radius: 10px; color: white;">Role: {st.session_state.user_role}</div>
        </div>
    """, unsafe_allow_html=True)

    # Settings Menu
    with st.sidebar.expander("⚙️ Settings"):
        
        st.markdown("##### 🎨 Preferences")
        st.session_state.selected_theme = st.selectbox("🎨 Choose Theme", ["Ezitech Modern", "Dark Mode", "Clean Light"], index=["Ezitech Modern", "Dark Mode", "Clean Light"].index(st.session_state.selected_theme))
        st.session_state.selected_language = st.selectbox("🌐 Language", ["English", "Urdu (اردو)"], index=["English", "Urdu (اردو)"].index(st.session_state.selected_language))
        
        st.markdown("---")
        st.markdown("##### 👤 Account")
        with st.form("edit_profile_sub_form"):
            st.write("**Edit Profile & Info**")
            new_u_name = st.text_input("Name", value=st.session_state.username)
            new_u_email = st.text_input("Email", value=st.session_state.email)
            new_u_bio = st.text_area("Bio", value=st.session_state.user_bio)
            uploaded_img = st.file_uploader("Upload Profile Picture", type=["png", "jpg", "jpeg"])
            
            if st.form_submit_button("Save Profile"):
                st.session_state.username = new_u_name
                st.session_state.email = new_u_email
                st.session_state.user_bio = new_u_bio
                if uploaded_img is not None:
                    bytes_data = uploaded_img.getvalue()
                    b64_encoded = base64.b64encode(bytes_data).decode("utf-8")
                    mime_type = uploaded_img.type if uploaded_img.type else "image/png"
                    st.session_state.profile_image = f"data:{mime_type};base64,{b64_encoded}"
                st.success("Profile updated successfully!")
                st.rerun()

        with st.form("password_update_form"):
            st.write("**🔐 Password Update**")
            old_pass = st.text_input("Current Password", type="password")
            new_pass = st.text_input("New Password", type="password")
            if st.form_submit_button("Update Password"):
                if new_pass:
                    st.success("Password updated successfully!")
                else:
                    st.error("Please enter a new password.")

        st.markdown("---")
        st.write("🔔 **Notifications:**")
        st.session_state.notifications_enabled = st.toggle("Enable Push Notifications", value=st.session_state.notifications_enabled)

        st.markdown("---")
        st.markdown("##### 🔒 Security & Privacy")
        if st.button("🛡️ Security Dashboard"):
            st.sidebar.info("Account is secure with 2FA enabled.")
        if st.button("👁️ Privacy Settings"):
            st.sidebar.info("Your data is encrypted and private.")

        st.markdown("---")
        st.markdown("##### ℹ️ Support & About")
        st.markdown(f"* **🔗 LinkedIn:** [{st.session_state.linkedin_link}]({st.session_state.linkedin_link})")
        st.markdown(f"* **🐙 GitHub:** [{st.session_state.github_link}]({st.session_state.github_link})")
        if st.button("❓ Help & Support"):
            st.sidebar.info("Contact support at support@ezitech.org")
        if st.button("📄 Terms and Policies"):
            st.sidebar.info("Ezitech Internship Terms & Conditions applied.")

        st.markdown("---")
        st.markdown("##### 📱 Cache & Cellular")
        if st.button("🗑️ Free up space (Clear Cache)"):
            st.cache_data.clear()
            st.sidebar.success("Cache cleared successfully!")
        
        st.session_state.data_saver = st.toggle("📉 Data Saver Mode", value=st.session_state.data_saver)

        st.markdown("---")
        st.markdown("##### 🚪 Actions")
        if st.button("🚪 Logout / Sign Out"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.username = ""
            st.session_state.email = ""
            st.session_state.user_bio = ""
            st.session_state.profile_image = DEFAULT_HIJABI_AVATAR
            st.rerun()

    # Navigation Menu
    st.sidebar.markdown("---")
    st.sidebar.subheader("📌 Navigation Menu")
    
    if st.session_state.user_role == "Student":
        nav_choice = st.sidebar.radio(
            "Go to",
            [
                "💬 AI Chat Assistant", 
                "📊 Task & Progress Tracker", 
                "📂 Resource Hub", 
                "💻 Code Playground", 
                "🔖 Saved Bookmarks"
            ]
        )
    else:
        nav_choice = st.sidebar.radio(
            "Go to",
            [
                "📊 Performance & AI", 
                "⏱️ Activity Log", 
                "📢 Broadcast Announcements"
            ]
        )

    # Render portals based on sidebar selection
    if st.session_state.user_role == "Student":
        if nav_choice == "💬 AI Chat Assistant":
            st.header(t["st_header"])
            st.write(t["st_desc"])
            
            if st.session_state.announcements:
                st.info(f"📢 **Latest Announcement from Mentor:** {st.session_state.announcements[-1]}")
            
            if "messages" not in st.session_state:
                st.session_state.messages = []

            col_btn1, col_btn2 = st.columns([1, 6])
            with col_btn1:
                if st.button(t["clear_btn"]):
                    st.session_state.messages = []
                    st.rerun()
                    
            with col_btn2:
                if st.session_state.messages:
                    chat_export = ""
                    for msg in st.session_state.messages:
                        role = "Student" if msg["role"] == "user" else "AI Assistant"
                        chat_export += f"{role}: {msg['content']}\n\n"
                    
                    st.download_button(
                        label=t["download_btn"],
                        data=chat_export,
                        file_name="ezitech_chat_history.txt",
                        mime="text/plain"
                    )

            chat_container = st.container()

            with chat_container:
                for idx, message in enumerate(st.session_state.messages):
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                        if "context" in message and message["context"]:
                            with st.expander(t["context_label"]):
                                st.write(message["context"])
                        
                        if message["role"] == "assistant":
                            col_bm1, col_bm2 = st.columns([6, 1])
                            with col_bm2:
                                if st.button("🔖 Save", key=f"bm_{idx}"):
                                    if message["content"] not in st.session_state.bookmarks:
                                        st.session_state.bookmarks.append(message["content"])
                                        st.success("Saved to Bookmarks!")
                            
                            try:
                                voice_lang = 'ur' if selected_language == "Urdu (اردو)" else 'en'
                                tts = gtts.gTTS(text=message["content"][:400], lang=voice_lang)
                                audio_filename = f"chat_audio_{idx}.mp3"
                                tts.save(audio_filename)
                                st.audio(audio_filename, format="audio/mp3")
                            except Exception:
                                pass

            st.markdown("---")
            with st.form(key="chat_form", clear_on_submit=True):
                chat_col1, chat_col2, chat_col3, chat_col4 = st.columns([4, 2, 2, 2])
                with chat_col1:
                    student_question = st.text_input(t["input_ph"], label_visibility="collapsed")
                with chat_col2:
                    submitted_query = st.form_submit_button(t["send_btn"], use_container_width=True)
                with chat_col3:
                    recorded_audio = st.audio_input("🎙️ Record Voice", label_visibility="collapsed")
                with chat_col4:
                    send_voice_clicked = st.form_submit_button(t["send_voice_btn"], use_container_width=True)

            query_to_send = None
            if submitted_query and student_question and student_question.strip():
                query_to_send = student_question.strip()
            elif send_voice_clicked and recorded_audio is not None:
                audio_bytes = recorded_audio.read()
                audio_file_path = "user_recorded_audio.wav"
                with open(audio_file_path, "wb") as f:
                    f.write(audio_bytes)
                
                r = sr.Recognizer()
                transcribed_text = None
                try:
                    with sr.AudioFile(audio_file_path) as source:
                        audio_data = r.record(source)
                        rec_lang = "ur-PK" if selected_language == "Urdu (اردو)" else "en-US"
                        transcribed_text = r.recognize_google(audio_data, language=rec_lang)
                except Exception:
                    try:
                        with sr.AudioFile(audio_file_path) as source:
                            audio_data = r.record(source)
                            transcribed_text = r.recognize_google(audio_data, language="en-US")
                    except Exception:
                        transcribed_text = None

                if transcribed_text:
                    query_to_send = transcribed_text
                else:
                    query_to_send = "Please explain the Ezitech internship guidelines and case studies."

            if query_to_send:
                st.session_state.messages.append({"role": "user", "content": query_to_send})
                
                with chat_container:
                    with st.chat_message("user"):
                        st.markdown(query_to_send)

                    with st.chat_message("assistant"):
                        with st.spinner(t["thinking"]):
                            try:
                                final_query = query_to_send
                                if selected_language == "Urdu (اردو)":
                                    final_query += " (Please answer in Urdu language)"

                                response = requests.post(
                                    f"{BASE_URL}/student/ask",
                                    json={"question": final_query}
                                )
                                if response.status_code == 200:
                                    data = response.json()
                                    ai_response = data["response"]
                                    retrieved_ctx = data.get("retrieved_context", "")
                                    
                                    st.markdown(ai_response)
                                    with st.expander(t["context_label"]):
                                        st.write(retrieved_ctx)
                                    
                                    voice_lang = 'ur' if selected_language == "Urdu (اردو)" else 'en'
                                    tts = gtts.gTTS(text=ai_response[:400], lang=voice_lang)
                                    audio_filename = "latest_chat_audio.mp3"
                                    tts.save(audio_filename)
                                    st.audio(audio_filename, format="audio/mp3")
                                    
                                    st.session_state.messages.append({
                                        "role": "assistant", 
                                        "content": ai_response,
                                        "context": retrieved_ctx
                                    })
                                else:
                                    error_msg = f"Error: {response.json().get('detail', 'Something went wrong')}"
                                    st.error(error_msg)
                            except Exception as e:
                                error_msg = f"Connection failed: Could not connect to FastAPI server. ({e})"
                                st.error(error_msg)
                st.rerun()

        elif nav_choice == "📊 Task & Progress Tracker":
            st.subheader("📊 Case Study & Task Progress Tracker")
            st.write("Apne ongoing tasks aur case studies ki progress yahan update karein:")
            
            completed_count = 0
            total_count = len(st.session_state.task_progress)
            
            for task_name in list(st.session_state.task_progress.keys()):
                current_status = st.session_state.task_progress[task_name]
                new_status = st.checkbox(task_name, value=current_status)
                st.session_state.task_progress[task_name] = new_status
                if new_status:
                    completed_count += 1
            
            progress_percentage = completed_count / total_count
            st.progress(progress_percentage)
            st.write(f"🎯 **Overall Progress:** {completed_count} of {total_count} tasks completed ({int(progress_percentage * 100)}%)")

        elif nav_choice == "📂 Resource Hub":
            st.subheader("📂 Real-Time Resource Search & Case Study Hub")
            resources_db = [
                {"title": "Case Study – AI-001", "category": "Case Study", "type": "Google Doc", "link": "https://docs.google.com/document/d/17_eM40gyldb2c6y1iRr7MuO8OOo1APgcLEIIn6lvl1A/edit?usp=sharing"},
                {"title": "Case Study – AI-002", "category": "Case Study", "type": "Google Doc", "link": "https://docs.google.com/document/d/1yKF75961QQVv1SfSQoGH10-Eqkebtf3n5unw-fCzHg4/edit?usp=sharing"},
                {"title": "Case Study – AI-003", "category": "Case Study", "type": "Google Doc", "link": "https://docs.google.com/document/d/1ufioiOxR10-kWRLQiqpIhT6yBBLN52yoi6p2ruZSszc/edit?usp=sharing"},
                {"title": "Case Study – AI-004", "category": "Case Study", "type": "Google Doc", "link": "https://docs.google.com/document/d/15IjMBg7jxOKskSLVGRUwbVOeHBjQ8ta1LZYhQA4HqAU/edit?usp=sharing"},
                {"title": "Ezitech Official GitHub Organization", "category": "GitHub", "type": "Repository", "link": "https://github.com"},
            ]
            search_query = st.text_input("🔍 Search case studies or resources by keyword...", "")
            filtered_resources = [res for res in resources_db if search_query.lower() in res["title"].lower() or search_query.lower() in res["category"].lower()]
            for res in filtered_resources:
                st.markdown(f"* **📄 [{res['title']}]({res['link']})** — *Category: {res['category']}*")

        elif nav_choice == "💻 Code Playground":
            st.subheader("💻 Python & Streamlit Code Playground")
            default_code = 'print("Hello from Ezitech Student Sandbox!")\nx = [1, 2, 3, 4, 5]\nprint("Sum:", sum(x))'
            user_code = st.text_area("Write Python Code:", value=default_code, height=150)
            if st.button("▶️ Run Code"):
                try:
                    import io, sys
                    old_stdout = sys.stdout
                    new_stdout = io.StringIO()
                    sys.stdout = new_stdout
                    exec(user_code)
                    sys.stdout = old_stdout
                    st.success("Execution Result:")
                    st.code(new_stdout.getvalue() or "Executed successfully with no print output.")
                except Exception as e:
                    sys.stderr = old_stdout
                    st.error(f"Runtime Error: {e}")

        elif nav_choice == "🔖 Saved Bookmarks":
            st.subheader("🔖 Saved Bookmarks & Important Answers")
            if st.session_state.bookmarks:
                for b_idx, bm in enumerate(st.session_state.bookmarks):
                    with st.expander(f"Bookmark #{b_idx + 1}"):
                        st.markdown(bm)
                        if st.button(f"🗑️ Remove #{b_idx + 1}", key=f"del_bm_{b_idx}"):
                            st.session_state.bookmarks.pop(b_idx)
                            st.rerun()
            else:
                st.info("No bookmarks saved yet.")

    else:
        # Mentor Views
        if nav_choice == "📊 Performance & AI":
            st.header(t["mentor_header"])
            st.write(t["mentor_desc"])
            
            with st.form("mentor_analysis_form"):
                col1, col2 = st.columns(2)
                with col1:
                    intern_name = st.text_input(t["intern_name"], value="Ali Khan")
                    completed_tasks = st.number_input(t["completed_tasks"], min_value=0, value=5)
                    pending_tasks = st.number_input(t["pending_tasks"], min_value=0, value=2)
                with col2:
                    scores_input = st.text_input(t["recent_scores"], value="85, 90, 78")
                    mentor_notes = st.text_area(t["mentor_notes"], value="Shows good progress.")
                
                submitted_analysis = st.form_submit_button(t["analyze_btn"])
                if submitted_analysis:
                    if intern_name.strip():
                        current_time_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
                        st.session_state.activity_logs.append({
                            "Intern Name": intern_name.strip(),
                            "Login Time": current_time_str,
                            "Status": "🟢 Tracked / Active",
                            "Time Spent": f"{completed_tasks * 45} Mins (Completed: {completed_tasks})"
                        })
                        
                        scores = [float(s.strip()) for s in scores_input.split(",") if s.strip()]
                        avg_score = sum(scores)/len(scores) if scores else 0
                        st.success(f"Analysis saved successfully for {intern_name}! (Average Score: {avg_score:.1f}). Data added to Live Activity Log.")
                    else:
                        st.error("Please enter a valid Intern Name.")

        elif nav_choice == "⏱️ Activity Log":
            st.subheader("⏱️ Live Intern Activity & Time Spent Tracker")
            st.write("Yahan aapko woh sabhi interns dikhenge jinka data mentor dashboard se save/analyze kiya gaya hai:")
            
            activity_df = pd.DataFrame(st.session_state.activity_logs)
            st.dataframe(activity_df, use_container_width=True)
            
            if st.button("🗑️ Clear Activity Logs"):
                st.session_state.activity_logs = []
                st.rerun()

        elif nav_choice == "📢 Broadcast Announcements":
            st.subheader("📢 Broadcast Announcement to All Students")
            with st.form("broadcast_form"):
                subject = st.text_input("Announcement Title")
                message_body = st.text_area("Message Details")
                if st.form_submit_button("🚀 Send Broadcast"):
                    if subject and message_body:
                        st.session_state.announcements.append(f"**{subject}**: {message_body}")
                        st.success("Announcement broadcasted successfully!")

    st.markdown("---")
    st.subheader(t["feedback_header"])
    with st.form("feedback_form"):
        selected_rating = st.radio(t["rating_label"], options=t["ratings_options"], index=4)
        user_feedback = st.text_input(t["feedback_ph"])
        if st.form_submit_button(t["feedback_btn"]):
            st.success(f"{t['feedback_success']} [{selected_rating}]")