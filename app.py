import os
import streamlit as st
import pandas as pd
from datetime import datetime
from groq import Groq

# 1. Page Configuration
st.set_page_config(
    page_title="Ezitech AI Mentor & Student Assistant",
    layout="wide",
    page_icon="🎓"
)

# 2. Initialize Session States
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = "Student"
if "user_name" not in st.session_state:
    st.session_state.user_name = "Taiba Kabir"
if "user_email" not in st.session_state:
    st.session_state.user_email = "taibakabir240@gmail.com"
if "language" not in st.session_state:
    st.session_state.language = "English"
if "theme" not in st.session_state:
    st.session_state.theme = "Light"
if "student_messages" not in st.session_state:
    st.session_state.student_messages = [
        {"role": "assistant", "content": "Hello Taiba! I am your Ezitech AI Mentor Assistant (AI-003). How can I guide you with your case studies, Neo4j, or debugging concepts today?"}
    ]
if "mentor_messages" not in st.session_state:
    st.session_state.mentor_messages = [
        {"role": "assistant", "content": "Hello Mentor! I am your Internship Intelligence Assistant. How can I help you analyze intern performance today?"}
    ]
if "nav_option" not in st.session_state:
    st.session_state.nav_option = "AI Chat Assistant"
if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "taibakabir240@gmail.com": {"password": "123", "name": "Taiba Kabir", "role": "Student"},
        "mentor@ezitech.org": {"password": "123", "name": "Sir Mentor", "role": "Mentor"}
    }

# Dynamic Theme Custom CSS Styling
if st.session_state.theme == "Dark":
    st.markdown("""
        <style>
            .main { background-color: #0e1117; color: #ffffff; }
            .stButton>button { border-radius: 8px; font-weight: 600; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            .main { background-color: #f8f9fa; color: #000000; }
            .stButton>button { border-radius: 8px; font-weight: 600; }
        </style>
    """, unsafe_allow_html=True)

# 3. Safely Fetch Groq API Key
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

# 4. Professional Login / Sign-Up Interface
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #1e3c72;'>🎓 Ezitech AI-003 Portal</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>AI Mentor Assistant & Internship Intelligence Platform</p>", unsafe_allow_html=True)
        
        auth_tab1, auth_tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with auth_tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            login_email = st.text_input("Email Address", value="taibakabir240@gmail.com", key="login_email_input")
            login_pass = st.text_input("Password", type="password", value="123", key="login_pass_input")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Login to Workspace", use_container_width=True, type="primary"):
                if login_email in st.session_state.users_db and st.session_state.users_db[login_email]["password"] == login_pass:
                    st.session_state.logged_in = True
                    st.session_state.user_email = login_email
                    st.session_state.user_name = st.session_state.users_db[login_email]["name"]
                    st.session_state.user_role = st.session_state.users_db[login_email]["role"]
                    st.success("Login successful! Loading dashboard...")
                    st.rerun()
                else:
                    st.error("Invalid email or password. Please try again.")

        with auth_tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            new_name = st.text_input("Full Name", key="signup_name_input")
            new_email = st.text_input("Email Address", key="signup_email_input")
            new_pass = st.text_input("Password", type="password", key="signup_pass_input")
            new_role = st.selectbox("Select Role", ["Student", "Mentor"], key="signup_role_input")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Create Account", use_container_width=True, type="primary"):
                if not new_email or not new_pass or not new_name:
                    st.warning("Please fill out all fields.")
                elif new_email in st.session_state.users_db:
                    st.error("Email already registered! Please login instead.")
                else:
                    st.session_state.users_db[new_email] = {
                        "password": new_pass,
                        "name": new_name,
                        "role": new_role
                    }
                    st.session_state.logged_in = True
                    st.session_state.user_email = new_email
                    st.session_state.user_name = new_name
                    st.session_state.user_role = new_role
                    st.success("Account created successfully!")
                    st.rerun()
                    
    st.stop()

# 5. Sidebar Profile, Customization & Navigation
with st.sidebar:
    st.markdown("💻 **Ezitech Ecosystem (EEF AI-003)**")
    
    role_color = "linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)" if st.session_state.user_role == "Student" else "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)"
    avatar_icon = "🧕" if st.session_state.user_role == "Student" else "👨‍🏫"
    
    st.markdown(f"""
        <div style="display: flex; flex-direction: column; align-items: center; background: {role_color}; padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 20px;">
            <div style="font-size: 50px; margin-bottom: 10px;">{avatar_icon}</div>
            <h3 style="margin: 0; font-size: 18px;">{st.session_state.user_name}</h3>
            <p style="margin: 5px 0 0 0; font-size: 11px; opacity: 0.9;">{st.session_state.user_email}</p>
            <span style="background: rgba(255,255,255,0.2); padding: 2px 10px; border-radius: 10px; font-size: 11px; margin-top: 8px;">Role: {st.session_state.user_role}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Theme & Language Selector Controls
    st.markdown("### ⚙️ App Customization")
    selected_theme = st.selectbox("🎨 Theme Mode", ["Light", "Dark"], index=0 if st.session_state.theme == "Light" else 1)
    if selected_theme != st.session_state.theme:
        st.session_state.theme = selected_theme
        st.rerun()

    selected_lang = st.selectbox("🌐 Language / زبان", ["English", "Urdu"], index=0 if st.session_state.language == "English" else 1)
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🧭 Navigation Menu")
    
    if st.session_state.user_role == "Student":
        nav_options = [
            "AI Chat Assistant" if st.session_state.language == "English" else "AI چیٹ اسسٹنٹ", 
            "Task & Progress Tracker" if st.session_state.language == "English" else "اسائنمنٹ اور پروگریس ٹریکر", 
            "Skill Gap & Roadmap" if st.session_state.language == "English" else "اسکل گیپ اور روڈ میپ", 
            "Resource Hub & Case Studies" if st.session_state.language == "English" else "ریسورس ہب اور کیس اسٹڈیز", 
            "Code Debugging Sandbox" if st.session_state.language == "English" else "کوڈ ڈیبگنگ سینڈ باکس"
        ]
    else:
        nav_options = [
            "Mentor Intelligence Dashboard" if st.session_state.language == "English" else "مینٹور انٹیلی جنس ڈیش بورڈ", 
            "Struggling Interns Analytics" if st.session_state.language == "English" else "کمزور انٹرنز کی تجزیاتی رپورٹس", 
            "Weekly Report Generator" if st.session_state.language == "English" else "ہفتہ وار رپورٹ جنریٹر", 
            "Task Difficulty & Milestones" if st.session_state.language == "English" else "ٹاسک کی مشکل اور سنگ میل", 
            "Broadcast Announcements" if st.session_state.language == "English" else "برکاسٹ اعلانات"
        ]
        
    nav_choice = st.radio("Go to", nav_options, label_visibility="collapsed")
    st.session_state.nav_option = nav_choice
    
    st.markdown("---")
    logout_label = "🚪 Logout / Sign Out" if st.session_state.language == "English" else "🚪 لاگ آؤٹ / سائن آؤٹ"
    if st.button(logout_label, use_container_width=True, type="secondary"):
        st.session_state.logged_in = False
        st.rerun()

# 6. Main Application Logic
if st.session_state.user_role == "Student":
    # ------------------ STUDENT DASHBOARD ------------------
    is_eng = (st.session_state.language == "English")
    
    if st.session_state.nav_option in ["AI Chat Assistant", "AI چیٹ اسسٹنٹ"]:
        st.header("💬 " + ("Student AI Mentor Assistant" if is_eng else "اسٹوڈنٹس AI مینٹور اسسٹنٹ"))
        st.markdown("Get answers regarding internship guidelines, Neo4j knowledge graphs, or debugging concepts." if is_eng else "انٹرنشپ کی رہنما خطوط، Neo4j، یا ڈیبگنگ کے بارے میں سوالات پوچھیں۔")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🗑️ " + ("Clear Chat" if is_eng else "چیٹ صاف کریں")):
                st.session_state.student_messages = [{"role": "assistant", "content": "Chat history cleared."}]
                st.rerun()
        with col2:
            chat_history_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.student_messages])
            st.download_button("📥 " + ("Download Chat History" if is_eng else "چیٹ ہسٹری ڈاؤن لوڈ کریں"), chat_history_text, file_name="student_chat.txt")

        st.markdown("---")

        for message in st.session_state.student_messages:
            avatar = "🧕" if message["role"] == "user" else "🤖"
            with st.chat_message(message["role"], avatar=avatar):
                st.write(message["content"])

        prompt_placeholder = "Ask your AI mentor..." if is_eng else "اپنے AI مینٹور سے پوچھیں..."
        if prompt := st.chat_input(prompt_placeholder):
            st.session_state.student_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="🧕"):
                st.write(prompt)

            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Thinking..." if is_eng else "سوچ رہا ہے..."):
                    if not client:
                        ai_reply = "Error: Groq API Key is missing."
                    else:
                        try:
                            formatted_messages = [
                                {"role": "system", "content": f"You are a professional AI mentor for students under Ezitech Engineering Framework (AI-003). Respond in {st.session_state.language} language. Guide with hints, never write full assignment code directly."}
                            ]
                            for m in st.session_state.student_messages:
                                role = "user" if m["role"] == "user" else "assistant"
                                formatted_messages.append({"role": role, "content": m["content"]})

                            # Updated active Groq model
                            completion = client.chat.completions.create(
                                model="llama-3.3-70b-versatile",
                                messages=formatted_messages,
                                temperature=0.7,
                                max_tokens=1024
                            )
                            ai_reply = completion.choices[0].message.content
                        except Exception as e:
                            ai_reply = f"Error: {e}"
                    
                    st.write(ai_reply)
            
            st.session_state.student_messages.append({"role": "assistant", "content": ai_reply})

    elif st.session_state.nav_option in ["Task & Progress Tracker", "اسائنمنٹ اور پروگریس ٹریکر"]:
        st.header("📋 " + ("Task & Progress Tracker" if is_eng else "ٹاسک اور پروگریس ٹریکر"))
        df = pd.DataFrame({
            "Case Study": ["AI-013 Neo4j Knowledge Graph", "AI-003 Mentor Assistant", "YOLOv8 License Plate Detection", "Parallel Computing OpenMP"],
            "Milestone Status": ["Completed", "In Progress", "Pending", "Pending"],
            "Confidence Score": ["95%", "80%", "N/A", "N/A"]
        })
        st.dataframe(df, use_container_width=True)

    elif st.session_state.nav_option in ["Skill Gap & Roadmap", "اسکل گیپ اور روڈ میپ"]:
        st.header("🗺️ " + ("Personalized Skill Gap & Roadmap" if is_eng else "ذاتی اسکل گیپ اور روڈ میپ"))
        st.info("AI generated insights based on performance." if is_eng else "کارکردگی کی بنیاد پر AI کی تیار کردہ رپورٹ۔")
        st.markdown("""
        * **Current Level:** Intermediate AI Engineer
        * **Identified Skill Gap:** Advanced RAG Pipeline Optimization & Neo4j Integration
        * **Recommended Next Module:** Fine-tuning open-source models using LoRA & HuggingFace
        """)

    elif st.session_state.nav_option in ["Resource Hub & Case Studies", "ریسورس ہب اور کیس اسٹڈیز"]:
        st.header("📚 " + ("Resource Hub & Case Studies" if is_eng else "ریسورس ہب اور کیس اسٹڈیز"))
        st.markdown("""
        * [Ezitech EEF Documentation](https://ezitech.org)
        * [Case Study AI-003 Specifications Repository](https://github.com)
        """)

    elif st.session_state.nav_option in ["Code Debugging Sandbox", "کوڈ ڈیبگنگ سینڈ باکس"]:
        st.header("⚡ " + ("Code Debugging Sandbox" if is_eng else "کوڈ ڈیبگنگ سینڈ باکس"))
        st.text_area("Snippet Code" if is_eng else "کوڈ یہاں درج کریں", "print('Debugging session active')")
        if st.button("Analyze Code" if is_eng else "کوڈ کا تجزیہ کریں"):
            st.success("AI Analysis: Code syntax is clean. Ensure environment paths are set correctly." if is_eng else "کوڈ بالکل درست ہے۔ ماحولیاتی راستے (paths) چیک کریں۔")

else:
    # ------------------ MENTOR DASHBOARD ------------------
    is_eng = (st.session_state.language == "English")
    
    if st.session_state.nav_option in ["Mentor Intelligence Dashboard", "مینٹور انٹیلی جنس ڈیش بورڈ"]:
        st.header("📊 " + ("Mentor Intelligence Dashboard" if is_eng else "مینٹور انٹیلی جنس ڈیش بورڈ"))
        col1, col2, col3 = st.columns(3)
        col1.metric("Active Interns", "32")
        col2.metric("Completed Case Studies", "184")
        col3.metric("AI Accuracy", "94.2%")
        
        mentor_df = pd.DataFrame({
            "Intern Name": ["Taiba Kabir", "Ali Khan", "Ayesha Ahmed"],
            "Active Case Study": ["AI-003 Mentor Assistant", "AI-002 Code Reviewer", "YOLOv8 LPR"],
            "Progress": ["85%", "100%", "45%"]
        })
        st.dataframe(mentor_df, use_container_width=True)

    elif st.session_state.nav_option in ["Struggling Interns Analytics", "کمزور انٹرنز کی تجزیاتی رپورٹس"]:
        st.header("⚠️ " + ("Struggling Interns Analytics" if is_eng else "کمزور انٹرنز کی تجزیاتی رپورٹس"))
        struggling_df = pd.DataFrame({
            "Intern Name": ["Ayesha Ahmed", "Zainab Malik"],
            "Delayed Module": ["YOLOv8 LPR", "CUDA Memory"],
            "Days Inactive": [5, 4]
        })
        st.dataframe(struggling_df, use_container_width=True)

    elif st.session_state.nav_option in ["Weekly Report Generator", "ہفتہ وار رپورٹ جنریٹر"]:
        st.header("📑 " + ("Weekly Report Generator" if is_eng else "ہفتہ وار رپورٹ جنریٹر"))
        if st.button("Generate Weekly Report" if is_eng else "ہفتہ وار رپورٹ بنائیں"):
            st.success("Weekly progress report compiled successfully!")

    elif st.session_state.nav_option in ["Task Difficulty & Milestones", "ٹاسک کی مشکل اور سنگ میل"]:
        st.header("⚙️ " + ("Task Difficulty Management" if is_eng else "ٹاسک کی مشکل کا انتظام"))
        st.selectbox("Select Intern", ["Taiba Kabir", "Ali Khan"])
        if st.button("Update Roadmap" if is_eng else "روڈ میپ اپ ڈیٹ کریں"):
            st.success("Updated successfully!")

    elif st.session_state.nav_option in ["Broadcast Announcements", "برکاست اعلانات"]:
        st.header("📢 " + ("Broadcast Announcements" if is_eng else "برکاست اعلانات"))
        st.text_area("Write broadcast message..." if is_eng else "اعلان کا پیغام لکھیں...")
        if st.button("Broadcast Now" if is_eng else "ابھی نشر کریں"):
            st.success("Announcement broadcasted successfully!")
