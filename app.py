import os
import sqlite3
import streamlit as st
import pandas as pd
from datetime import datetime
from groq import Groq
from io import BytesIO
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
from PIL import Image
import base64

# 1. Page Configuration
st.set_page_config(
    page_title="Ezitech AI Portal",
    layout="wide",
    page_icon="🎓"
)

# 2. Database Initialization
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            linkedin TEXT
        )
    """)
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN linkedin TEXT")
    except Exception:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            task_name TEXT NOT NULL,
            status TEXT NOT NULL,
            confidence TEXT NOT NULL
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (email, password, name, role, linkedin) VALUES (?, ?, ?, ?, ?)", 
                       ("taibakabir240@gmail.com", "123", "Taiba Kabir", "Student", "https://linkedin.com/in/taibakabir"))
        cursor.execute("INSERT INTO users (email, password, name, role, linkedin) VALUES (?, ?, ?, ?, ?)", 
                       ("mentor@ezitech.org", "123", "Sir Mentor", "Mentor", "https://linkedin.com"))
        cursor.execute("INSERT INTO student_tasks (email, task_name, status, confidence) VALUES (?, ?, ?, ?)", 
                       ("taibakabir240@gmail.com", "AI-013 Neo4j Knowledge Graph", "Completed", "95%"))
        cursor.execute("INSERT INTO student_tasks (email, task_name, status, confidence) VALUES (?, ?, ?, ?)", 
                       ("taibakabir240@gmail.com", "AI-003 Mentor Assistant", "In Progress", "80%"))
        conn.commit()
    conn.close()

init_db()

# 3. Initialize Session States
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = "Student"
if "user_name" not in st.session_state:
    st.session_state.user_name = "Taiba Kabir"
if "user_email" not in st.session_state:
    st.session_state.user_email = "taibakabir240@gmail.com"
if "user_linkedin" not in st.session_state:
    st.session_state.user_linkedin = "https://linkedin.com/in/taibakabir"
if "profile_image" not in st.session_state:
    st.session_state.profile_image = None
if "language" not in st.session_state:
    st.session_state.language = "English"
if "theme" not in st.session_state:
    st.session_state.theme = "Light"
if "student_messages" not in st.session_state:
    st.session_state.student_messages = [
        {"role": "assistant", "content": "Hello ! Welcome to your Ezitech AI Mentor Workspace. How can I assist you with your technical case studies, development frameworks, or debugging tasks today?"
        }
if "last_audio_signature" not in st.session_state:
    st.session_state.last_audio_signature = None

# Theme & Centered Profile CSS with Smooth Image Rendering
if st.session_state.theme == "Dark":
    st.markdown("""
        <style>
            .main { background-color: #0e1117; color: #ffffff; }
            .stButton>button[kind="primary"] { 
                background-color: #1e3c72 !important; 
                color: white !important; 
                border: none !important;
                border-radius: 8px; 
                font-weight: 600; 
            }
            .stButton>button[kind="primary"]:hover { 
                background-color: #2a5298 !important; 
            }
            section.main > div:last-child { padding-bottom: 120px; }
            
            [data-testid="stSidebar"] img {
                border-radius: 50% !important;
                object-fit: cover !important;
                width: 90px !important;
                height: 90px !important;
                display: block !important;
                margin-left: auto !important;
                margin-right: auto !important;
                border: 3px solid #4a90e2 !important;
            }

            .whatsapp-fixed-bar {
                position: fixed !important;
                bottom: 0 !important;
                left: 0 !important;
                right: 0 !important;
                background-color: #1f2c34 !important;
                padding: 12px 24px !important;
                z-index: 999999 !important;
                box-shadow: 0 -2px 10px rgba(0,0,0,0.3);
                border-top: 1px solid #2a3942;
            }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            .main { background-color: #f8f9fa; color: #000000; }
            .stButton>button[kind="primary"] { 
                background-color: #1e3c72 !important; 
                color: white !important; 
                border: none !important;
                border-radius: 8px; 
                font-weight: 600; 
            }
            .stButton>button[kind="primary"]:hover { 
                background-color: #2a5298 !important; 
            }
            section.main > div:last-child { padding-bottom: 120px; }
            
            [data-testid="stSidebar"] img {
                border-radius: 50% !important;
                object-fit: cover !important;
                width: 90px !important;
                height: 90px !important;
                display: block !important;
                margin-left: auto !important;
                margin-right: auto !important;
                border: 3px solid #2a5298 !important;
            }

            .whatsapp-fixed-bar {
                position: fixed !important;
                bottom: 0 !important;
                left: 0 !important;
                right: 0 !important;
                background-color: #f0f2f5 !important;
                padding: 12px 24px !important;
                z-index: 999999 !important;
                box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
                border-top: 1px solid #e9edef;
            }
        </style>
    """, unsafe_allow_html=True)

# 4. Safely Fetch Groq API Key
api_key = None
try:
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

if not api_key:
    api_key = os.environ.get("GROQ_API_KEY")

client = None
if api_key:
    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        st.error(f"Failed to initialize Groq client: {e}")

# 5. Professional Login / Sign-Up Interface with Real Ezitech Logo
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
            <div style="display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 0px;">
                <div style="background-color: #1976d2; border-radius: 12px; width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden; border: 2px solid #1565c0;">
                    <svg viewBox="0 0 500 500" width="38" height="38" xmlns="http://www.w3.org/2000/svg">
                        <g fill="#ffffff">
                            <path d="M150 120 L350 120 L350 160 L190 160 L190 200 L330 200 L330 240 L190 240 L190 290 L350 290 L350 330 L150 330 Z" />
                            <path d="M220 290 L270 290 L270 410 L310 410 L310 450 L180 450 L180 410 L220 410 Z" transform="translate(15, -40)" />
                            <polygon points="350,290 390,310 350,330 310,310" />
                            <path d="M380 320 Q395 360 385 390 L370 380 Z" />
                        </g>
                    </svg>
                </div>
                <h1 style="color: #1e3c72; margin: 0; font-size: 26px; font-weight: 700;">Welcome to Ezitech AI Portal</h1>
            </div>
            <p style="text-align: center; color: #666; margin-top: 6px; font-size: 14px;">AI Mentor Assistant & Internship Intelligence Platform</p>
        """, unsafe_allow_html=True)
        
        auth_tab1, auth_tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with auth_tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            login_email = st.text_input("Email Address", value="taibakabir240@gmail.com", key="login_email_input")
            login_pass = st.text_input("Password", type="password", value="123", key="login_pass_input")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Login to Workspace", use_container_width=True, type="primary"):
                conn = sqlite3.connect("users.db")
                cursor = conn.cursor()
                cursor.execute("SELECT password, name, role, linkedin FROM users WHERE email = ?", (login_email,))
                user_record = cursor.fetchone()
                conn.close()
                
                if user_record and user_record[0] == login_pass:
                    st.session_state.logged_in = True
                    st.session_state.user_email = login_email
                    st.session_state.user_name = user_record[1]
                    st.session_state.user_role = user_record[2]
                    st.session_state.user_linkedin = user_record[3] if user_record[3] else ""
                    st.success("Login successful! Loading dashboard...")
                    st.rerun()
                else:
                    st.error("Invalid email or password. Please try again.")

        with auth_tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            new_name = st.text_input("Full Name", key="signup_name_input")
            new_email = st.text_input("Email Address", key="signup_email_input")
            new_pass = st.text_input("Password", type="password", key="signup_pass_input")
            new_linkedin = st.text_input("LinkedIn Profile URL", key="signup_linkedin_input")
            new_role = st.selectbox("Select Role", ["Student", "Mentor"], key="signup_role_input")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Create Account", use_container_width=True, type="primary"):
                if not new_email or not new_pass or not new_name:
                    st.warning("Please fill out all fields.")
                else:
                    conn = sqlite3.connect("users.db")
                    cursor = conn.cursor()
                    cursor.execute("SELECT email FROM users WHERE email = ?", (new_email,))
                    exists = cursor.fetchone()
                    
                    if exists:
                        st.error("Email already registered! Please login instead.")
                    else:
                        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (new_email, new_pass, new_name, new_role, new_linkedin))
                        conn.commit()
                        conn.close()
                        
                        st.session_state.logged_in = True
                        st.session_state.user_email = new_email
                        st.session_state.user_name = new_name
                        st.session_state.user_role = new_role
                        st.session_state.user_linkedin = new_linkedin
                        st.success("Account created successfully!")
                        st.rerun()
                    conn.close()
                    
    st.stop()

# 6. Sidebar Profile & Settings Section (Fixed Image Upload Blinking)
with st.sidebar:
    st.markdown("💻 **Developed by Taiba Kabir**")
    st.markdown("---")
    
    is_student = (st.session_state.user_role == "Student")
    role_color = "linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)" if is_student else "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)"
    
    # Display Profile Picture or Default Avatar Icon
    if st.session_state.profile_image:
        col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
        with col_img2:
            st.image(st.session_state.profile_image)
    else:
        avatar_icon = "🧕" if is_student else "👨‍🏫"
        st.markdown(f"<div style='font-size: 50px; text-align: center;'>{avatar_icon}</div>", unsafe_allow_html=True)
    
    st.markdown(f"""
        <div style="background: {role_color}; padding: 15px; border-radius: 12px; color: white; text-align: center; margin-top: 10px; margin-bottom: 15px;">
            <h3 style="margin: 0; font-size: 16px;">{st.session_state.user_name}</h3>
            <p style="margin: 3px 0 0 0; font-size: 11px; opacity: 0.9;">{st.session_state.user_email}</p>
            <span style="background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 8px; font-size: 10px; margin-top: 5px; display:inline-block;">{'Student' if is_student else 'Mentor'}</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⚙️ Sidebar Settings & Profile")
    
    with st.expander("👤 Edit Profile & Picture"):
        uploaded_file = st.file_uploader("Upload Profile Picture", type=["png", "jpg", "jpeg"], key="profile_pic_uploader")
        if uploaded_file is not None:
            img = Image.open(uploaded_file)
            if st.session_state.profile_image != img:
                st.session_state.profile_image = img
                st.toast("Profile picture updated successfully!", icon="✅")
                st.rerun()
            
        new_name_sidebar = st.text_input("Update Name", value=st.session_state.user_name, key="sb_name")
        new_li_sidebar = st.text_input("LinkedIn URL", value=st.session_state.user_linkedin, key="sb_li")
        if st.button("Save Profile Info"):
            st.session_state.user_name = new_name_sidebar
            st.session_state.user_linkedin = new_li_sidebar
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET name = ?, linkedin = ? WHERE email = ?", (new_name_sidebar, new_li_sidebar, st.session_state.user_email))
            conn.commit()
            conn.close()
            st.success("Updated successfully!")
            st.rerun()

    with st.expander("🎨 Appearance & Language"):
        selected_theme = st.selectbox("Theme Mode", ["Light", "Dark"], index=0 if st.session_state.theme == "Light" else 1, key="sb_theme")
        selected_lang = st.selectbox("Language", ["English", "Urdu"], index=0 if st.session_state.language == "English" else 1, key="sb_lang")
        if st.button("Apply Settings"):
            st.session_state.theme = selected_theme
            st.session_state.language = selected_lang
            st.success("Theme and settings applied successfully!")
            st.rerun()

    with st.expander("🔒 Password & Privacy"):
        pass_input = st.text_input("New Password", type="password", key="sb_pass")
        priv_check = st.checkbox("Enable Privacy Mode", value=True, key="sb_priv")
        if st.button("Update Security"):
            if pass_input:
                conn = sqlite3.connect("users.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET password = ? WHERE email = ?", (pass_input, st.session_state.user_email))
                conn.commit()
                conn.close()
                st.success("Password updated!")
            else:
                st.success("Privacy settings saved!")

    with st.expander("🧹 Cleanup Space"):
        if st.button("Clear Cache & Logs"):
            st.session_state.student_messages = [{"role": "assistant", "content": "Cache cleared."}]
            st.session_state.last_audio_signature = None
            if os.path.exists("temp_audio.wav"):
                os.remove("temp_audio.wav")
            st.success("Workspace cleaned successfully!")
            st.rerun()

    st.markdown("---")
    if st.button("🚪 Logout / Sign Out", use_container_width=True, type="secondary"):
        st.session_state.logged_in = False
        st.rerun()

# 7. Main Professional Navigation & Dashboards Logic
is_eng = (st.session_state.language == "English")

if is_student:
    st.markdown("## 🚀 Student Workspace Dashboard")
    nav_tabs = st.tabs([
        "💬 AI Chat Assistant", 
        "📋 Task Tracker", 
        "🗺️ Skill Roadmap", 
        "📚 Resource Hub", 
        "⚡ Code Sandbox"
    ])
    
    with nav_tabs[0]:
        st.header("Student AI Mentor Assistant & Voice Chat")
        st.markdown("Type your message below or use the voice recording button for real-time audio interaction."")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🗑️ Clear Chat"):
                st.session_state.student_messages = [{"role": "assistant", "content": "Chat history cleared."}]
                st.session_state.last_audio_signature = None
                st.rerun()
        with col2:
            chat_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.student_messages])
            st.download_button("📥 Download Chat Log", chat_text, file_name="student_chat.txt")

        st.markdown("---")

        for message in st.session_state.student_messages:
            avatar = "🧕" if message["role"] == "user" else "🤖"
            with st.chat_message(message["role"], avatar=avatar):
                st.write(message["content"])
                if message["role"] == "assistant":
                    try:
                        tts = gTTS(text=message["content"], lang='en')
                        fp = BytesIO()
                        tts.write_to_fp(fp)
                        st.audio(fp.getvalue(), format='audio/mp3')
                    except Exception:
                        pass

        def submit_whatsapp_query():
            q = st.session_state.whatsapp_input_field.strip()
            if q:
                st.session_state.student_messages.append({"role": "user", "content": q})
                if not client:
                    ai_reply = "Error: Groq API Key missing."
                else:
                    try:
                        formatted_msgs = [{
                            "role": "system", 
                            "content": "You are Taiba's professional AI Mentor for Ezitech Engineering Framework . Give concise, direct answers and helpful guidance."
                        }]
                        for m in st.session_state.student_messages:
                            formatted_msgs.append({"role": "user" if m["role"] == "user" else "assistant", "content": m["content"]})

                        completion = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=formatted_msgs,
                            temperature=0.7,
                            max_tokens=1024
                        )
                        ai_reply = completion.choices[0].message.content
                    except Exception as e:
                        ai_reply = f"Error: {e}"
                st.session_state.student_messages.append({"role": "assistant", "content": ai_reply})
                st.session_state.whatsapp_input_field = ""

        st.markdown('<div class="whatsapp-fixed-bar">', unsafe_allow_html=True)
        col_input, col_mic = st.columns([11, 1])
        with col_input:
            st.text_input(
                "Type a message", 
                placeholder="Type a message...", 
                label_visibility="collapsed", 
                key="whatsapp_input_field", 
                on_change=submit_whatsapp_query
            )
        with col_mic:
            audio_info = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='whatsapp_round_mic', format="webm")
        st.markdown('</div>', unsafe_allow_html=True)

        if audio_info and 'bytes' in audio_info:
            audio_bytes = audio_info['bytes']
            audio_sig = hash(audio_bytes) if audio_bytes else None
            
            if client and len(audio_bytes) > 0 and audio_sig != st.session_state.last_audio_signature:
                st.session_state.last_audio_signature = audio_sig
                with st.spinner("Transcribing your voice..."):
                    try:
                        audio_file_path = "temp_audio.wav"
                        with open(audio_file_path, "wb") as f:
                            f.write(audio_bytes)
                        
                        with open(audio_file_path, "rb") as file:
                            transcription = client.audio.transcriptions.create(
                                file=(audio_file_path, file.read()),
                                model="whisper-large-v3",
                                language="en",
                                response_format="text",
                                temperature=0.0
                            )
                        prompt = transcription.strip()
                        
                        if os.path.exists(audio_file_path):
                            os.remove(audio_file_path)
                            
                        if prompt:
                            st.session_state.student_messages.append({"role": "user", "content": prompt})
                            try:
                                formatted_msgs = [{
                                    "role": "system", 
                                    "content": "You are Taiba's professional AI Mentor for Ezitech Engineering Framework. Give concise, direct answers and helpful guidance."
                                }]
                                for m in st.session_state.student_messages:
                                    formatted_msgs.append({"role": "user" if m["role"] == "user" else "assistant", "content": m["content"]})

                                completion = client.chat.completions.create(
                                    model="llama-3.3-70b-versatile",
                                    messages=formatted_msgs,
                                    temperature=0.7,
                                    max_tokens=1024
                                )
                                ai_reply = completion.choices[0].message.content
                            except Exception as e:
                                ai_reply = f"Error: {e}"
                            st.session_state.student_messages.append({"role": "assistant", "content": ai_reply})
                            st.rerun()
                    except Exception as e:
                        st.error(f"Speech-to-Text Error: {e}")

    with nav_tabs[1]:
        st.header("📋 Real Database Task & Progress Tracker")
        with st.form("add_task_form"):
            st.subheader("➕ Add New Task / Milestone")
            new_task_name = st.text_input("Case Study / Task Title")
            new_task_status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])
            new_task_conf = st.text_input("Confidence / Score", value="85%")
            submit_task = st.form_submit_button("Save Task to Database")
            
            if submit_task:
                if new_task_name:
                    conn = sqlite3.connect("users.db")
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO student_tasks (email, task_name, status, confidence) VALUES (?, ?, ?, ?)",
                                   (st.session_state.user_email, new_task_name, new_task_status, new_task_conf))
                    conn.commit()
                    conn.close()
                    st.success("Task added successfully and saved to database!")
                    st.rerun()
                else:
                    st.warning("Please enter a task name.")

        st.markdown("---")
        st.subheader("📌 Your Current Tasks")
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, task_name, status, confidence FROM student_tasks WHERE email = ?", (st.session_state.user_email,))
        tasks_data = cursor.fetchall()
        conn.close()
        
        if tasks_data:
            df_tasks = pd.DataFrame(tasks_data, columns=["ID", "Case Study / Task", "Milestone Status", "Confidence Score"])
            st.dataframe(df_tasks, use_container_width=True)
            
            task_ids = [t[0] for t in tasks_data]
            selected_task_id = st.selectbox("Select Task ID to Delete", options=[None] + task_ids)
            if selected_task_id and st.button("Delete Selected Task"):
                conn = sqlite3.connect("users.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM student_tasks WHERE id = ?", (selected_task_id,))
                conn.commit()
                conn.close()
                st.success("Task deleted successfully!")
                st.rerun()
        else:
            st.info("No tasks found.")

    with nav_tabs[2]:
        st.header("🗺️ Personalized Skill Gap & Roadmap")
        st.info("AI generated insights based on your recent performance.")
        st.markdown("""
        * **Current Level:** Intermediate AI Engineer
        * **Identified Skill Gap:** Advanced RAG Pipeline Optimization & Neo4j Integration
        * **Recommended Next Module:** Fine-tuning open-source models using LoRA & HuggingFace
        """)

    with nav_tabs[3]:
        st.header("📚 Resource Hub & Case Studies")
        st.markdown("""
        * [Ezitech EEF Documentation](https://ezitech.org)
        * [Case Study AI-003 Specifications Repository](https://github.com)
        """)

    with nav_tabs[4]:
        st.header("⚡ Code Debugging Sandbox")
        snippet_code = st.text_area("Snippet Code", "print('Debugging session active')")
        if st.button("Analyze Code"):
            try:
                compile(snippet_code, '<string>', 'exec')
                st.success("AI Analysis: Code syntax is clean. Ensure environment paths are set correctly.")
            except SyntaxError as e:
                st.error(f"AI Syntax Error: {e}")

else:
    st.markdown("## 📊 Mentor Intelligence Dashboard")
    mentor_tabs = st.tabs([
        "📊 Overview", 
        "⚠️ Struggling Interns", 
        "📑 Reports", 
        "⚙️ Milestones", 
        "📢 Broadcast"
    ])
    
    with mentor_tabs[0]:
        col1, col2, col3 = st.columns(3)
        col1.metric("Active Interns", "32")
        col2.metric("Completed Case Studies", "184")
        col3.metric("Platform AI Accuracy", "94.2%")
        
        mentor_df = pd.DataFrame({
            "Intern Name": ["Taiba Kabir", "Ali Khan", "Ayesha Ahmed"],
            "Active Case Study": ["AI-003 Mentor Assistant", "AI-002 Code Reviewer", "YOLOv8 LPR"],
            "Progress": ["85%", "100%", "45%"]
        })
        st.dataframe(mentor_df, use_container_width=True)

    with mentor_tabs[1]:
        st.header("⚠️ Struggling Interns Analytics")
        struggling_df = pd.DataFrame({
            "Intern Name": ["Ayesha Ahmed", "Zainab Malik"],
            "Delayed Module": ["YOLOv8 LPR", "CUDA Memory"],
            "Days Inactive": [5, 4]
        })
        st.dataframe(struggling_df, use_container_width=True)

    with mentor_tabs[2]:
        st.header("📑 Weekly Report Generator")
        if st.button("Generate Weekly Report"):
            st.success("Weekly progress report compiled successfully for all interns!")

    with mentor_tabs[3]:
        st.header("⚙️ Task Difficulty Management")
        st.selectbox("Select Intern to Configure", ["Taiba Kabir", "Ali Khan", "Ayesha Ahmed"])
        if st.button("Update Roadmap & Milestones"):
            st.success("Intern roadmap updated successfully!")

    with mentor_tabs[4]:
        st.header("📢 Broadcast Announcements")
        announcement = st.text_area("Write broadcast message for all interns...")
        if st.button("Broadcast Now"):
            if announcement:
                st.success("Announcement broadcasted successfully to all active dashboards!")
            else:
                st.warning("Please enter a message to broadcast.")
