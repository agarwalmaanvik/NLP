import streamlit as st
import json
import os
from src.agent_brain import EnterpriseAgent
from datetime import datetime

st.set_page_config(page_title="HCLTech | NexaSupport", layout="wide")

st.markdown("""
    <style>
    /* 1. Global Reset */
    .stApp { background-color: #ffffff; }

    /* 2. SIDEBAR TEXT COLOR UPDATES */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
        border-right: 1px solid #e0e0e0;
    }

    /* Target "Logged in as", "Navigation", and Radio options specifically */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #FFFAFA !important; /* Snow color for most text */
    }

    /* EXCEPTION: Keep "Reset Chat" and "Sign Out" button text Blue */
    div.stButton > button p {
        color: #0056b3 !important;
        font-weight: 600;
    }
    
    /* 3. METRIC BOX UPDATES */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 20px !important;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    /* Label text (Employee ID, etc.) to be White on Blue background */
    [data-testid="stMetricLabel"] p {
        color: #ffffff !important; 
        background-color: #0056b3; 
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 500;
    }
    /* Value text (EMP_6785, etc.) to be Black and visible */
    [data-testid="stMetricValue"] div {
        color: #000000 !important;
        font-size: 24px !important;
        white-space: normal !important;
        overflow: visible !important;
    }

    /* 4. CHAT ASSISTANT HEADER */
    .chat-header {
        color: #0056b3 !important; /* Blue color */
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0px;
    }

    /* 5. BUTTON STYLING (Off-White) */
    div.stButton > button {
        background-color: #F5F5F5 !important; /* Off-white background */
        border: 1px solid #E0E0E0 !important;
        border-radius: 8px;
    }

    /* --- SIDEBAR TEXT COLOR FIX --- */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
        border-right: 1px solid #e0e0e0;
    }

    /* Set "Logged in as", "Navigation", and all menu labels to HCL Blue */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] .stMarkdown strong {
        color: #0056b3 !important; /* Uniform HCL Blue */
        font-weight: 500 !important;
    }

    /* Target the active radio selection to ensure it stands out */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
        color: #0056b3 !important;
    }

    /* 1. Force Assistant Response Text to Black */
    .stChatMessage p, .stMarkdown p {
        color: #000000 !important;
        font-weight: 400;
    }

    /* 2. Fix Action Logs Visibility (Sidebar/Right Column) */
    /* Ensure labels and JSON keys in logs are not white */
    [data-testid="stVerticalBlock"] p, 
    [data-testid="stVerticalBlock"] span {
        color: #000000 !important;
    }

    /* 3. Style the Status Indicator "Ready!" Text */
    .stStatus [data-testid="stMarkdownContainer"] p {
        color: #0056b3 !important; /* HCL Blue for the status text */
        font-weight: 600;
    }

    /* 4. Ensure JSON payload text in logs is visible */
    /* --- ACTION LOG JSON TEXT FIX --- */
    /* Targets the text inside the JSON component specifically */
    .stJson div, .stJson span {
        color: #FFFFFF !important; /* Forces text inside JSON blocks to be White */
    }

    .stJson span, .stJson div, .stJson p, .stJson label {
        color: #FFFFFF !important;
    }

    /* Target JSON keys specifically to make them pop in HCL Blue */
    [data-testid="stJsonKey"] {
        color: #0056b3 !important;
        font-weight: bold !important;
    }

    /* Professional dark background for the logs */
    .stJson {
        background-color: #1e1e1e !important;
        border-radius: 8px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

def authenticate(emp_id, password):
    path = os.path.join("data", "hr_docs", "hr_policy.json")
    if not os.path.exists(path): return None
    with open(path, "r") as f:
        data = json.load(f)
    user = data.get(emp_id.upper())
    if user and user.get("password") == password:
        return user
    return None

if "auth_status" not in st.session_state:
    st.session_state.auth_status = False

if not st.session_state.auth_status:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://www.financialexpress.com/wp-content/uploads/2022/09/hcl1.jpg", width=180)
        st.markdown('<div class="dashboard-header">Employee Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="proprietary-text">NexaSupport | HCLTech proprietary software</div>', unsafe_allow_html=True)
        with st.form("login"):
            id_input = st.text_input("Employee ID")
            pw_input = st.text_input("Password", type="password")
            if st.form_submit_button("Authenticate"):
                user = authenticate(id_input, pw_input)
                if user:
                    st.session_state.auth_status = True
                    st.session_state.user = user
                    st.session_state.emp_id = id_input.upper()
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    st.stop()

user = st.session_state.user
with st.sidebar:
    st.image("https://www.financialexpress.com/wp-content/uploads/2022/09/hcl1.jpg", width=140)
    st.markdown(f"**Logged in as:**\n{user['name']}")
    st.divider()
    
    view = st.radio("Navigation", 
        ["Chat Assistant", "Knowledge Base", "Agent Workflow"])
    
    st.divider()
    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.rerun()
    if st.button("Sign Out"):
        st.session_state.auth_status = False
        st.rerun()

if view == "Chat Assistant":
    st.markdown('<div class="chat-header">Chat Assistant</div>', unsafe_allow_html=True)
    st.caption(f"Session Active for {user['name']} | RAG + Function Calling")
    
    # Corrected Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Employee ID", st.session_state.emp_id)
    m2.metric("Earned Leave", f"{user['earned_leave_balance']} Days")
    m3.metric("Sick Leave", f"{user['sick_leave_balance']} Days")
    m4.metric("Insurance Plan", user['insurance_plan'])
    
    st.divider()
    
    chat_col, log_col = st.columns([2, 1])

    with log_col:
        st.subheader("Action Logs")
        log_container = st.container()

    with chat_col:
        if "agent" not in st.session_state:
            st.session_state.agent = EnterpriseAgent()
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("How can I help you today?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.status("Thinking...") as status:
                    res = st.session_state.agent.run(prompt, st.session_state.messages[:-1], st.session_state.emp_id)
                    
                    with log_container:
                        for i, step in enumerate(res.get("intermediate_steps", [])):
                            st.write(f"**Step {i+1}:** {step[0].tool}")
                            st.json(step[1])
                    
                    status.update(label="Ready!", state="complete")
                
                st.markdown(res["output"])
                st.session_state.messages.append({"role": "assistant", "content": res["output"]})