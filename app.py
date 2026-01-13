import streamlit as st
import json
import re
from src.agent_brain import EnterpriseAgent

# 1. Page Configuration
st.set_page_config(page_title="HCLTech Language Wizard", layout="wide", page_icon="🪄")

# 2. Initialize the Agent (Cache it so it doesn't reload on every click)
if "agent" not in st.session_state:
    with st.spinner("Initializing Agentic Brain..."):
        st.session_state.agent = EnterpriseAgent()
    st.session_state.messages = []

# 3. Sidebar: Domain Control & Action Monitor
with st.sidebar:
    st.title("🛡️ Enterprise Monitor")
    st.info("This panel displays real-time agent actions and JSON payloads for the 'Action Test'.")
    
    st.divider()
    st.subheader("System Status")
    st.success("BGE-M3 Embeddings: ACTIVE")
    st.success("Milvus Hybrid Store: CONNECTED")
    
    st.divider()
    st.subheader("Latest Action JSON")
    # This placeholder will update whenever a tool is called
    action_placeholder = st.empty()
    action_placeholder.code("Waiting for action...", language="json")

# 4. Main Chat Interface
st.title("🪄 HCLTech Language Wizard")
st.caption("Agentic Enterprise Assistant | Powered by RAG & Tool Calling")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. User Input Handling
if prompt := st.chat_input("Ask about the Annual Report or request an IT action..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Agent Response
    with st.chat_message("assistant"):
        with st.status("Agent is thinking...", expanded=True) as status:
            st.write("Searching Knowledge Base...")
            # Run the agent
            response = st.session_state.agent.run(prompt, st.session_state.messages)
            st.write("Synthesizing answer...")
            status.update(label="Response Generated!", state="complete", expanded=False)
        
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # 6. JSON Detection (For the Action Test)
        # We look for JSON blocks in the response to display them in the sidebar
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                action_json = json.loads(json_match.group())
                action_placeholder.json(action_json)
            except:
                pass