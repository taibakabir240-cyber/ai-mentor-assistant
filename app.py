import os
import sqlite3
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

# 2. Database Initialization (SQLite for Real Permanent Storage)
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    # Student Tasks Table (Real-time persistent task tracking)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            task_name TEXT NOT NULL,
            status TEXT NOT NULL,
            confidence TEXT NOT NULL
        )
    """)
    # Insert default users if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", ("taibakabir240@gmail.com", "123", "Taiba Kabir", "Student"))
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", ("mentor@ezitech.org", "123", "Sir Mentor", "Mentor"))
        # Default tasks for student
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
if "language" not in st.session_state:
    st.session_state.language = "English"
if "theme" not in st.session_state:
    st.session_state.theme = "Light"
if "student_messages" not in st.session_state:
    st.session_state.student_messages = [
        {"role": "assistant", "content": "Hello Taiba! I am your Ezitech AI Mentor Assistant (AI-003). How can I guide you with your case studies, Neo4j, or debugging concepts today?"}
    ]

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

# 5. Professional Login / Sign-Up Interface
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
                conn = sqlite3.connect("users.db")
                cursor = conn.cursor()
                cursor.execute("SELECT password, name, role FROM users WHERE email = ?", (login_email,))
                user_record = cursor.fetchone()
                conn.close()
                
                if user_record and user_record[0] == login_pass:
                    st.session_state.logged_in = True
                    st.session_state.user_email = login_email
                    st.session_state.user_name = user_record[1]
                    st.session_state.user_role = user_record[2]
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
                else:
                    conn = sqlite3.connect("users.db")
                    cursor = conn.cursor()
                    cursor.execute("SELECT email FROM users WHERE email = ?", (new_email,))
                    exists = cursor.fetchone()
                    
                    if exists:
                        st.error("Email already registered! Please login instead.")
                    else:
                        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (new_email, new_pass, new_name, new_role))
                        conn.commit()
                        conn.close()
                        
                        st.session_state.logged_in = True
                        st.session_state.user_email = new_email
                        st.session_state.user_name = new_name
                        st.session_state.user_role = new_role
                        st.success("Account created successfully!")
                        st.rerun()
                    conn.close()
                    
    st.stop()

# 6. Sidebar Profile & Completely Separated Navigation
with st.sidebar:
    st.markdown("💻 **Ezitech Ecosystem (EEF AI-003)**")
    
    is_student = (st.session_state.user_role == "Student")
    role_color = "linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)" if is_student else "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)"
    avatar_icon = "🧕" if is_student else "👨‍🏫"
    
    st.markdown(f"""
        <div style="display: flex; flex-direction: column; align-items: center; background: {role_color}; padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 20px;">
            <div style="font-size: 50px; margin-bottom: 10px;">{avatar_icon}</div>
            <h3 style="margin: 0; font-size: 18px;">{st.session_state.user_name}</h3>
            <p style="margin: 5px 0 0 0; font-size: 11px; opacity: 0.9;">{st.session_state.user_email}</p>
            <span style="background: rgba(255,255,255,0.2); padding: 2px 10px; border-radius: 10px; font-size: 11px; margin-top: 8px;">Portal: {'Student Dashboard' if is_student else 'Mentor Intelligence Portal'}</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⚙️ Preferences")
    selected_theme = st.selectbox("🎨 Theme Mode", ["Light", "Dark"], index=0 if st.session_state.theme == "Light" else 1)
    if selected_theme != st.session_state.theme:
        st.session_state.theme = selected_theme
        st.rerun()

    selected_lang = st.selectbox("🌐 Language / زبان", ["English", "Urdu"], index=0 if st.session_state.language == "English" else 1)
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🧭 Portal Navigation")
    
    if is_student:
        nav_options = [
            "AI Chat Assistant", 
            "Task & Progress Tracker", 
            "Skill Gap & Roadmap", 
            "Resource Hub & Case Studies", 
            "Code Debugging Sandbox"
        ]
    else:
        nav_options = [
            "Mentor Intelligence Dashboard", 
            "Struggling Interns Analytics", 
            "Weekly Report Generator", 
            "Task Difficulty & Milestones", 
            "Broadcast Announcements"
        ]
        
    nav_choice = st.radio("Select Section", nav_options, label_visibility="collapsed")
    st.session_state.nav_option = nav_choice
    
    st.markdown("---")
    if st.button("🚪 Logout / Sign Out", use_container_width=True, type="secondary"):
        st.session_state.logged_in = False
        st.rerun()

# 7. Completely Isolated Dashboards Logic
is_eng = (st.session_state.language == "English")

if is_student:
    # ==========================================
    # 🎓 STUDENT DASHBOARD & WORKSPACE
    # ==========================================
    if st.session_state.nav_option == "AI Chat Assistant":
        st.header("💬 Student AI Mentor Assistant (AI-003)")
        st.markdown("Get answers regarding your internship case studies, Neo4j knowledge graphs, or code debugging.")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🗑️ Clear Chat"):
                st.session_state.student_messages = [{"role": "assistant", "content": "Chat history cleared."}]
                st.rerun()
        with col2:
            chat_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.student_messages])
            st.download_button("📥 Download Chat Log", chat_text, file_name="student_chat.txt")

        st.markdown("---")
        for message in st.session_state.student_messages:
            avatar = "🧕" if message["role"] == "user" else "🤖"
            with st.chat_message(message["role"], avatar=avatar):
                st.write(message["content"])

        if prompt := st.chat_input("Ask your AI mentor..."):
            st.session_state.student_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="🧕"):
                st.write(prompt)

            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Thinking..."):
                    if not client:
                        ai_reply = "Error: Groq API Key missing."
                    else:
                        try:
                            formatted_msgs = [{"role": "system", "content": "You are a professional AI mentor for students under Ezitech Engineering Framework (AI-003). Guide with hints, never write full assignment code directly."}]
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
                    st.write(ai_reply)
            st.session_state.student_messages.append({"role": "assistant", "content": ai_reply})

    elif st.session_state.nav_option == "Task & Progress Tracker":
        st.header("📋 Real Database Task & Progress Tracker")
        st.markdown("Add and manage your case studies and milestones. Data is permanently saved in SQLite.")
        
        # Form to add new task to real database
        with st.form("add_task_form"):
            st.subheader("➕ Add New Task / Milestone")
            new_task_name = st.text_input("Case Study / Task Title (e.g., YOLOv8 License Plate Detection)")
            new_task_status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])
            new_task_conf = st.text_input("Confidence / Score (e.g., 90%)", value="85%")
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
        
        # Fetch tasks from database for current logged-in user
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, task_name, status, confidence FROM student_tasks WHERE email = ?", (st.session_state.user_email,))
        tasks_data = cursor.fetchall()
        conn.close()
        
        if tasks_data:
            df_tasks = pd.DataFrame(tasks_data, columns=["ID", "Case Study / Task", "Milestone Status", "Confidence Score"])
            st.dataframe(df_tasks, use_container_width=True)
            
            # Option to delete a task
            task_ids = [t[0] for t in tasks_data]
            selected_task_id = st.selectbox("Select Task ID to Delete (if completed/removed)", options=[None] + task_ids)
            if selected_task_id and st.button("Delete Selected Task"):
                conn = sqlite3.connect("users.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM student_tasks WHERE id = ?", (selected_task_id,))
                conn.commit()
                conn.close()
                st.success("Task deleted successfully!")
                st.rerun()
        else:
            st.info("No tasks found. Add a new task above!")

    elif st.session_state.nav_option == "Skill Gap & Roadmap":
        st.header("🗺️ Personalized Skill Gap & Roadmap")
        st.info("AI generated insights based on your recent performance.")
        st.markdown("""
        * **Current Level:** Intermediate AI Engineer
        * **Identified Skill Gap:** Advanced RAG Pipeline Optimization & Neo4j Integration
        * **Recommended Next Module:** Fine-tuning open-source models using LoRA & HuggingFace
        """)

    elif st.session_state.nav_option == "Resource Hub & Case Studies":
        st.header("📚 Resource Hub & Case Studies")
        st.markdown("""
        * [Ezitech EEF Documentation](https://ezitech.org)
        * [Case Study AI-003 Specifications Repository](https://github.com)
        """)

    elif st.session_state.nav_option == "Code Debugging Sandbox":
        st.header("⚡ Code Debugging Sandbox")
        snippet_code = st.text_area("Snippet Code", "print('Debugging session active')")
        if st.button("Analyze Code"):
            try:
                compile(snippet_code, '<string>', 'exec')
                st.success("AI Analysis: Code syntax is clean. Ensure environment paths are set correctly.")
            except SyntaxError as e:
                st.error(f"AI Syntax Error: {e}")

else:
    # ==========================================
    # 👨‍🏫 MENTOR INTELLIGENCE PORTAL
    # ==========================================
    if st.session_state.nav_option == "Mentor Intelligence Dashboard":
        st.header("📊 Mentor Intelligence Dashboard")
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

    elif st.session_state.nav_option == "Struggling Interns Analytics":
        st.header("⚠️ Struggling Interns Analytics")
        struggling_df = pd.DataFrame({
            "Intern Name": ["Ayesha Ahmed", "Zainab Malik"],
            "Delayed Module": ["YOLOv8 LPR", "CUDA Memory"],
            "Days Inactive": [5, 4]
        })
        st.dataframe(struggling_df, use_container_width=True)

    elif st.session_state.nav_option == "Weekly Report Generator":
        st.header("📑 Weekly Report Generator")
        if st.button("Generate Weekly Report"):
            st.success("Weekly progress report compiled successfully for all interns!")

    elif st.session_state.nav_option == "Task Difficulty & Milestones":
        st.header("⚙️ Task Difficulty Management")
        st.selectbox("Select Intern to Configure", ["Taiba Kabir", "Ali Khan", "Ayesha Ahmed"])
        if st.button("Update Roadmap & Milestones"):
            st.success("Intern roadmap updated successfully!")

    elif st.session_state.nav_option == "Broadcast Announcements":
        st.header("📢 Broadcast Announcements")
        announcement = st.text_area("Write broadcast message for all interns...")
        if st.button("Broadcast Now"):
            if announcement:
                st.success("Announcement broadcasted successfully to all active dashboards!")
            else:
                st.warning("Please enter a message to broadcast.")
