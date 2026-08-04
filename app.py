import os
import streamlit as st
import pandas as pd
from datetime import datetime
import base64
from groq import Groq
from gtts import gTTS
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

# 3. Initialize Session States for Authentication & App
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = "Student"
if "user_name" not in st.session_state:
    st.session_state.user_name = "Taiba Kabir"
if "user_email" not in st.session_state:
    st.session_state.user_email = "taibakabir240@gmail.com"
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your Ezitech AI Mentor & Student Assistant. How can I help you with your internship guidelines, case studies, or debugging concepts today?"}
    ]
if "nav_option" not in st.session_state:
    st.session_state.nav_option = "AI Chat Assistant"
if "users_db" not in st.session_state:
    # Dummy database for handling signup/login locally
    st.session_state.users_db = {
        "taibakabir240@gmail.com": {"password": "123", "name": "Taiba Kabir", "role": "Student"},
        "mentor@ezitech.org": {"password": "123", "name": "Sir Mentor", "role": "Mentor"}
    }

# 4. Authentication Flow (Login / Sign Up)
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🎓 Ezitech Portal Login & Registration</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Please sign in or register to access your portal.</p>", unsafe_allow_html=True)
    
    auth_tab1, auth_tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with auth_tab1:
        st.subheader("Login to your account")
        login_email = st.text_input("Email Address", key="login_email")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login Now", use_container_width=True):
            if login_email in st.session_state.users_db and st.session_state.users_db[login_email]["password"] == login_pass:
                st.session_state.logged_in = True
                st.session_state.user_email = login_email
                st.session_state.user_name = st.session_state.users_db[login_email]["name"]
                st.session_state.user_role = st.session_state.users_db[login_email]["role"]
                st.success("Login successful! Redirecting...")
                st.rerun()
            else:
                st.error("Invalid email or password. Please try again.")

    with auth_tab2:
        st.subheader("Create a new account")
        new_name = st.text_input("Full Name", key="signup_name")
        new_email = st.text_input("Email Address", key="signup_email")
        new_pass = st.text_input("Password", type="password", key="signup_pass")
        new_role = st.selectbox("Select Role", ["Student", "Mentor"], key="signup_role")
        
        if st.button("Register & Login", use_container_width=True):
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
                
    st.stop() # Stop further execution until logged in

# 5. Sidebar Profile & Navigation (For Authenticated Users)
with st.sidebar:
    st.markdown("💻 **Ezitech Ecosystem Platform**")
    
    # Dynamic Profile Card based on Role
    role_color = "linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)" if st.session_state.user_role == "Student" else "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)"
    avatar_icon = "🧕" if st.session_state.user_role == "Student" else "👨‍🏫"
    
    st.markdown(f"""
        <div style="display: flex; flex-direction: column; align-items: center; background: {role_color}; padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 20px;">
            <div style="font-size: 50px; margin-bottom: 10px;">{avatar_icon}</div>
            <h3 style="margin: 0; font-size: 20px;">{st.session_state.user_name}</h3>
            <p style="margin: 5px 0 0 0; font-size: 12px; opacity: 0.8;">{st.session_state.user_email}</p>
            <span style="background: rgba(255,255,255,0.2); padding: 2px 10px; border-radius: 10px; font-size: 11px; margin-top: 8px;">Role: {st.session_state.user_role}</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🧭 Navigation Menu")
    
    if st.session_state.user_role == "Student":
        nav_options = ["AI Chat Assistant", "Task & Progress Tracker", "Resource Hub", "Code Playground", "Saved Bookmarks"]
    else:
        nav_options = ["Mentor Dashboard & Analytics", "Manage Tasks", "Student Activity Logs", "Broadcast Announcements"]
        
    nav_choice = st.radio("Go to", nav_options, label_visibility="collapsed")
    st.session_state.nav_option = nav_choice
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# 6. Main Content Area based on User Role & Navigation
if st.session_state.user_role == "Student":
    if st.session_state.nav_option == "AI Chat Assistant":
        st.header("💬 AI Chat Assistant")
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
                            formatted_messages = [
                                {"role": "system", "content": "You are a helpful, professional AI mentor and student assistant within the Ezitech ecosystem, guiding interns with programming, debugging, and academic projects."}
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
                            ai_reply = f"An error occurred while generating response: {e}"
                    
                    st.write(ai_reply)
            
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

else:
    # Mentor Portal Views
    if st.session_state.nav_option == "Mentor Dashboard & Analytics":
        st.header("📊 Mentor Analytics & Performance Overview")
        st.success("Welcome back, Mentor! Here is the overall performance overview of active interns.")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Active Interns", "24", "+3 this week")
        col2.metric("Completed Case Studies", "142", "+12 today")
        col3.metric("Average Score", "88.5%", "+2.1%")
        
        st.markdown("### 📈 Recent Intern Progress Submissions")
        intern_df = pd.DataFrame({
            "Intern Name": ["Taiba Kabir", "Ali Khan", "Ayesha Ahmed", "Hamza Ali"],
            "Assigned Project": ["AI Code Reviewer", "Parallel Computing", "YOLOv8 LPR", "Knowledge Graph"],
            "Progress": ["100%", "85%", "60%", "90%"],
            "Status": ["Active", "Active", "Pending Review", "Completed"]
        })
        st.dataframe(intern_df, use_container_width=True)

    elif st.session_state.nav_option == "Manage Tasks":
        st.header("🛠️ Assign & Manage Tasks")
        st.text_input("New Task Title")
        st.selectbox("Assign To", ["All Students", "Taiba Kabir", "Specific Batch"])
        if st.button("Publish Task"):
            st.success("Task published successfully to student portals!")

    elif st.session_state.nav_option == "Student Activity Logs":
        st.header("⏱️ Live Student Activity Logs")
        st.write("Monitor real-time login and interaction records.")
        log_df = pd.DataFrame({
            "User": ["Taiba Kabir", "Ali Khan", "Ayesha Ahmed"],
            "Action": ["Ran Code Playground", "Completed Task 2", "Asked AI Assistant"],
            "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "2026-08-04 10:15:00", "2026-08-04 09:30:00"]
        })
        st.dataframe(log_df, use_container_width=True)

    elif st.session_state.nav_option == "Broadcast Announcements":
        st.header("📢 Broadcast Announcements")
        announcement_text = st.text_area("Write announcement message for all students...")
        if st.button("Broadcast Now"):
            if announcement_text:
                st.success("Announcement broadcasted to all active student portals!")
            else:
                st.warning("Please write a message before broadcasting.")
