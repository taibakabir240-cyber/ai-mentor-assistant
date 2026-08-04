import os
import io
import sys
from datetime import datetime
import streamlit as st
import pandas as pd
import gtts
import speech_recognition as sr
from groq import Groq

# Page Configuration
st.set_page_config(
    page_title="Ezitech AI Mentor Assistant & Internship Platform",
    page_icon="🎓",
    layout="wide"
)

# Initialize Session State Variables
if "user_role" not in st.session_state:
    st.session_state.user_role = "Student"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = []
if "announcements" not in st.session_state:
    st.session_state.announcements = []
if "activity_logs" not in st.session_state:
    st.session_state.activity_logs = []
if "task_progress" not in st.session_state:
    st.session_state.task_progress = {
        "Case Study AI-001 Setup": True,
        "AI Knowledge Graph Data Modeling": False,
        "Automated AI Code Review Script": False,
        "Streamlit Deployment & Testing": False
    }

# Language and Translations setup
selected_language = st.sidebar.selectbox("🌐 Choose Language / زبان", ["English", "Urdu (اردو)"], key="global_lang_select")

translations = {
    "English": {
        "title": "🎓 Ezitech AI Mentor Assistant & Internship Platform",
        "subtitle": "Welcome! Please sign in or register to access your dedicated portal.",
        "st_header": "Student Assistant Portal",
        "st_desc": "Ask questions about your internship guidelines, case studies, or debugging concepts via text or voice.",
        "mentor_header": "Mentor Performance & AI Analytics",
        "mentor_desc": "Evaluate intern progress, track task completions, and generate performance reports.",
        "clear_btn": "Clear Chat",
        "download_btn": "Download Chat History",
        "context_label": "🔍 View Retrieved AI Context & Knowledge Source",
        "thinking": "AI Mentor is thinking...",
        "input_ph": "Type your question here...",
        "send_btn": "Send Message",
        "send_voice_btn": "Send Voice",
        "intern_name": "Intern Full Name",
        "completed_tasks": "Completed Tasks Count",
        "pending_tasks": "Pending Tasks Count",
        "recent_scores": "Recent Assessment Scores (comma separated)",
        "mentor_notes": "Mentor Remarks / Feedback Notes",
        "analyze_btn": "Run AI Performance Analysis",
        "feedback_header": "Session Feedback & Rating",
        "rating_label": "Select Rating Level:",
        "ratings_options": ["⭐ WORST", "⭐⭐ BAD", "⭐⭐⭐ NEUTRAL", "⭐⭐⭐⭐ GOOD", "⭐⭐⭐⭐⭐ EXCELLENT"],
        "feedback_ph": "Leave your feedback or suggestions here...",
        "feedback_btn": "Submit Feedback",
        "feedback_success": "Thank you for your valuable feedback!"
    },
    "Urdu (اردو)": {
        "title": "🎓 ایزی ٹیک اے آئی مینٹَر اسسٹنٹ اینڈ انٹرنشپ پلیٹ فارم",
        "subtitle": "خوش آمدید! اپنے پورٹل تک رسائی کے لیے سائن ان یا رجسٹر کریں۔",
        "st_header": "اسٹوڈنٹ اسسٹنٹ پورٹل",
        "st_desc": "اپنی انٹرنشپ کی ہدایات، کیس اسٹڈیز، یا ڈی بگنگ کے بارے میں ٹیکسٹ یا آواز کے ذریعے سوال پوچھیں۔",
        "mentor_header": "مینٹَر کارکردگی اور اے آئی تجزیہ",
        "mentor_desc": "انٹرن کی کارکردگی کا جائزہ لیں، ٹاسک ٹریک کریں، اور رپورٹس تیار کریں۔",
        "clear_btn": "چیٹ صاف کریں",
        "download_btn": "چیٹ ہسٹری ڈاؤن لوڈ کریں",
        "context_label": "🔍 حاصل کردہ اے آئی کانٹیکسٹ دیکھیں",
        "thinking": "اے آئی مینٹَر سوچ رہا ہے...",
        "input_ph": "یہاں اپنا سوال لکھیں...",
        "send_btn": "پیغام بھیجیں",
        "send_voice_btn": "آواز بھیجیں",
        "intern_name": "انٹرن کا پورا نام",
        "completed_tasks": "مکمل شدہ ٹاسک کی تعداد",
        "pending_tasks": "بقیہ ٹاسک کی تعداد",
        "recent_scores": "حال ہی میں حاصل کردہ اسکورز (کاما سے الگ کریں)",
        "mentor_notes": "مینٹَر کے ریمارکس / آراء",
        "analyze_btn": "اے آئی پرفارمنس کا تجزیہ کریں",
        "feedback_header": "سیشن کی رائے اور ریٹنگ",
        "rating_label": "ریٹنگ منتخب کریں:",
        "ratings_options": ["⭐ سب سے برا", "⭐⭐ برا", "⭐⭐⭐ اوسط", "⭐⭐⭐⭐ اچھا", "⭐⭐⭐⭐⭐ بہترین"],
        "feedback_ph": "یہاں اپنی رائے یا تجاویز درج کریں...",
        "feedback_btn": "رائے جمع کروائیں",
        "feedback_success": "آپ کی قیمتی آراء کا شکریہ!"
    }
}

t = translations[selected_language]

# Sidebar Profile & Role Switcher
st.sidebar.image("https://avatars.githubusercontent.com/u/9919?s=280&v=4", width=80)
st.sidebar.markdown("### Taiba Kabeer")
st.sidebar.caption("Role: Engineering Intern")

role_toggle = st.sidebar.radio("Switch Portal View", ["Student", "Mentor"], key="role_switcher_radio")
st.session_state.user_role = role_toggle

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
        ],
        key="student_nav_radio"
    )
else:
    nav_choice = st.sidebar.radio(
        "Go to",
        [
            "📊 Performance & AI", 
            "⏱️ Activity Log", 
            "📢 Broadcast Announcements"
        ],
        key="mentor_nav_radio"
    )

# Main Header Display
st.markdown(f"# {t['title']}")
st.markdown(t["subtitle"])
st.markdown("---")

# Render portals based on sidebar selection
if st.session_state.user_role == "Student":
    if nav_choice == "💬 AI Chat Assistant":
        st.header(t["st_header"])
        st.write(t["st_desc"])
        
        if st.session_state.announcements:
            st.info(f"📢 **Latest Announcement from Mentor:** {st.session_state.announcements[-1]}")
        
        col_btn1, col_btn2 = st.columns([1, 6])
        with col_btn1:
            if st.button(t["clear_btn"], key="clear_chat_history_btn"):
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
                    mime="text/plain",
                    key="download_chat_txt_btn"
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
                student_question = st.text_input(t["input_ph"], label_visibility="collapsed", key="chat_student_input")
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

                            # Direct Groq API Integration (llama-3.1-70b-versatile)
                            groq_api_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))
                            
                            if not groq_api_key:
                                st.error("Groq API Key not found! Please add it in Streamlit Cloud Secrets.")
                            else:
                                client = Groq(api_key=groq_api_key)
                                system_prompt = "You are an AI Mentor Assistant for Ezitech internship students. Help them with guidelines, case studies, and debugging concepts."
                                
                                chat_completion = client.chat.completions.create(
                                    messages=[
                                        {"role": "system", "content": system_prompt},
                                        {"role": "user", "content": final_query}
                                    ],
                                    model="llama-3.1-70b-versatile",
                                )
                                
                                ai_response = chat_completion.choices[0].message.content
                                retrieved_ctx = "Ezitech Internship AI Knowledge Base & Guidelines"
                                
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
                        except Exception as e:
                            st.error(f"Groq API Connection Failed: {e}")
            st.rerun()

    elif nav_choice == "📊 Task & Progress Tracker":
        st.subheader("📊 Case Study & Task Progress Tracker")
        st.write("Apne ongoing tasks aur case studies ki progress yahan update karein:")
        
        completed_count = 0
        total_count = len(st.session_state.task_progress)
        
        for task_name in list(st.session_state.task_progress.keys()):
            current_status = st.session_state.task_progress[task_name]
            new_status = st.checkbox(task_name, value=current_status, key=f"task_check_{task_name}")
            st.session_state.task_progress[task_name] = new_status
            if new_status:
                completed_count += 1
        
        progress_percentage = completed_count / total_count if total_count > 0 else 0
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
        search_query = st.text_input("🔍 Search case studies or resources by keyword...", "", key="resource_search_input")
        filtered_resources = [res for res in resources_db if search_query.lower() in res["title"].lower() or search_query.lower() in res["category"].lower()]
        for res in filtered_resources:
            st.markdown(f"* **📄 [{res['title']}]({res['link']})** — *Category: {res['category']}*")

    elif nav_choice == "💻 Code Playground":
        st.subheader("💻 Python & Streamlit Code Playground")
        default_code = 'print("Hello from Ezitech Student Sandbox!")\nx = [1, 2, 3, 4, 5]\nprint("Sum:", sum(x))'
        user_code = st.text_area("Write Python Code:", value=default_code, height=150, key="playground_code_area")
        if st.button("▶️ Run Code", key="run_code_sandbox_btn"):
            try:
                old_stdout = sys.stdout
                new_stdout = io.StringIO()
                sys.stdout = new_stdout
                exec(user_code)
                sys.stdout = old_stdout
                st.success("Execution Result:")
                st.code(new_stdout.getvalue() or "Executed successfully with no print output.")
            except Exception as e:
                sys.stdout = old_stdout
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
                intern_name = st.text_input(t["intern_name"], value="Taiba Kabeer", key="mentor_intern_name")
                completed_tasks = st.number_input(t["completed_tasks"], min_value=0, value=5, key="mentor_completed_tasks")
                pending_tasks = st.number_input(t["pending_tasks"], min_value=0, value=2, key="mentor_pending_tasks")
            with col2:
                scores_input = st.text_input(t["recent_scores"], value="85, 90, 78", key="mentor_scores_input")
                mentor_notes = st.text_area(t["mentor_notes"], value="Shows good progress in AI case studies.", key="mentor_notes_area")
            
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
                    st.error("Please ensure a valid Intern Name is entered.")

    elif nav_choice == "⏱️ Activity Log":
        st.subheader("⏱️ Live Intern Activity & Time Spent Tracker")
        st.write("Yahan aapko woh sabhi interns dikhenge jinka data mentor dashboard se save/analyze kiya gaya hai:")
        
        activity_df = pd.DataFrame(st.session_state.activity_logs)
        st.dataframe(activity_df, use_container_width=True)
        
        if st.button("🗑️ Clear Activity Logs", key="clear_activity_logs_btn"):
            st.session_state.activity_logs = []
            st.rerun()

    elif nav_choice == "📢 Broadcast Announcements":
        st.subheader("📢 Broadcast Announcement to All Students")
        with st.form("broadcast_form"):
            subject = st.text_input("Announcement Title", key="broadcast_subject_input")
            message_body = st.text_area("Message Details", key="broadcast_body_input")
            if st.form_submit_button("🚀 Send Broadcast"):
                if subject and message_body:
                    st.session_state.announcements.append(f"**{subject}**: {message_body}")
                    st.success("Announcement broadcasted successfully!")

st.markdown("---")
st.subheader(t["feedback_header"])
with st.form("feedback_form"):
    selected_rating = st.radio(t["rating_label"], options=t["ratings_options"], index=4, key="feedback_rating_radio")
    user_feedback = st.text_input(t["feedback_ph"], key="feedback_text_input")
    if st.form_submit_button(t["feedback_btn"]):
        st.success(f"{t['feedback_success']} [{selected_rating}]")
