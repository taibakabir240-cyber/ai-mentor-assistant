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

# Custom Elegant CSS Styling
st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# 2. Safely Fetch Groq API Key
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
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = "Student"
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your Ezitech AI Mentor & Student Assistant. How can I help you today?"}
    ]
if "nav_option" not in st.session_state:
    st.session_state.nav_option = "AI Chat Assistant"
if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "taibakabir240@gmail.com": {"password": "123", "name": "Taiba Kabir", "role": "Student"},
        "mentor@ezitech.org": {"password": "123", "name": "Sir Mentor", "role": "Mentor"}
    }

# 4. Professional Login / Sign-Up Interface
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #1e3c72;'>🎓 Ezitech Portal</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>Sign in or create an account to access your workspace.</p>", unsafe_allow_html=True)
        
        auth_tab1, auth_tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with auth_tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            login_email = st.text_input("Email Address", key="login_email_input")
            login_pass = st.text_input("Password", type="password", key="login_pass_input")
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

# 5. Sidebar Profile & Navigation (For Logged-In Users)
with st.sidebar:
    st.markdown("💻 **Ezitech Ecosystem**")
    
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
    
    st.markdown("### 🧭 Navigation")
    if st.session_state.user_role == "Student":
        nav_options = ["AI Chat Assistant", "Task & Progress Tracker", "Resource Hub", "Code Playground", "Saved Bookmarks"]
    else:
        nav_options = ["Mentor Dashboard & Analytics", "Manage Tasks", "Student Activity Logs", "Broadcast Announcements"]
        
    nav_choice = st.radio("Go to", nav_options, label_visibility="collapsed")
    st.session_state.nav_option = nav_choice
    
    st.markdown("---")
    if st.button("🚪 Logout / Sign Out", use_container_width=True, type="secondary"):
        st.session_state.logged_in = False
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your Ezitech AI Mentor & Student Assistant. How can I help you today?"}]
        st.rerun()

# 6. Main Application Pages
if st.session_state.user_role == "Student":
    if st.session_state.nav_option == "AI Chat Assistant":
        st.header("💬 AI Chat Assistant")
        st.markdown("Ask questions about your internship guidelines, case studies, or debugging concepts.")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = [{"role": "assistant", "content": "Chat history cleared. How can I help you?"}]
                st.rerun()
        with col2:
            chat_history_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages])
            st.download_button("📥 Download Chat History", chat_history_text, file_name="chat_history.txt")

        st.markdown("---")

        for message in st.session_state.messages:
            avatar = "🧕" if message["role"] == "user" else "🤖"
            with st.chat_message(message["role"], avatar=avatar):
                st.write(message["content"])

        if prompt := st.chat_input("Type your message here..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="🧕"):
                st.write(prompt)

            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Thinking..."):
                    if not client:
                        ai_reply = "Error: Groq API Key is missing or invalid. Please check your Streamlit Secrets."
                    else:
                        try:
                            formatted_messages = [
                                {"role": "system", "content": "You are a helpful, professional AI mentor and student assistant within the Ezitech ecosystem."}
                            ]
                            for m in st.session_state.messages:
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
                            ai_reply = f"An error occurred: {e}"
                    
                    st.write(ai_reply)
            
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})

    elif st.session_state.nav_option == "Task & Progress Tracker":
        st.header("📋 Task & Progress Tracker")
        df = pd.DataFrame({
            "Task": ["Setup Environment", "Parallel Computing Case Study", "YOLOv8 License Plate Detection", "AI Mentor UI Integration"],
            "Status": ["Completed", "Completed", "In Progress", "Pending"],
            "Priority": ["High", "High", "Medium", "High"]
        })
        st.dataframe(df, use_container_width=True)

    elif st.session_state.nav_option == "Resource Hub":
        st.header("📚 Resource Hub")
        st.info("Access your study materials and research documentation here.")
        st.markdown("""
        * [Ezitech Framework Documentation](https://ezitech.org)
        * [Parallel Distributed Computing Notes](https://github.com)
        """)

    elif st.session_state.nav_option == "Code Playground":
        st.header("⚡ Code Playground")
        st.text_area("Python Code Snippet", "print('Hello from Ezitech AI Mentor!')")
        if st.button("Run Code"):
            st.code("Hello from Ezitech AI Mentor!\nExecution successful.", language="text")

    elif st.session_state.nav_option == "Saved Bookmarks":
        st.header("🔖 Saved Bookmarks")
        st.write("No bookmarks saved yet.")

else:
    if st.session_state.nav_option == "Mentor Dashboard & Analytics":
        st.header("📊 Mentor Analytics & Performance Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("Active Interns", "24", "+3 this week")
        col2.metric("Completed Case Studies", "142", "+12 today")
        col3.metric("Average Score", "88.5%", "+2.1%")
        
        intern_df = pd.DataFrame({
            "Intern Name": ["Taiba Kabir", "Ali Khan", "Ayesha Ahmed"],
            "Assigned Project": ["AI Code Reviewer", "Parallel Computing", "YOLOv8 LPR"],
            "Progress": ["100%", "85%", "60%"],
            "Status": ["Active", "Active", "Pending Review"]
        })
        st.dataframe(intern_df, use_container_width=True)

    elif st.session_state.nav_option == "Manage Tasks":
        st.header("🛠️ Assign & Manage Tasks")
        st.text_input("New Task Title")
        if st.button("Publish Task"):
            st.success("Task published successfully!")

    elif st.session_state.nav_option == "Student Activity Logs":
        st.header("⏱️ Live Student Activity Logs")
        log_df = pd.DataFrame({
            "User": ["Taiba Kabir", "Ali Khan"],
            "Action": ["Ran Code Playground", "Completed Task 2"],
            "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "2026-08-04 10:15:00"]
        })
        st.dataframe(log_df, use_container_width=True)

    elif st.session_state.nav_option == "Broadcast Announcements":
        st.header("📢 Broadcast Announcements")
        announcement_text = st.text_area("Write announcement message...")
        if st.button("Broadcast Now"):
            st.success("Announcement broadcasted successfully!")
