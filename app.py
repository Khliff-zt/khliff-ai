import streamlit as st
import os
from together import Together
import json
from datetime import datetime

# ------ CONFIGURATION AND SETUP ------

CONFIG_PATH = "khliff_config.json"

def load_config():
    """Load API key from config file"""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                return config
        except Exception as e:
            st.error(f"Error loading config: {e}")
            return {"api_key": ""}
    else:
        st.error(f"Config file not found: {CONFIG_PATH}")
        return {"api_key": ""}

# Load API key from config
config = load_config()
api_key = config.get("api_key", "")

# Set API key in environment
if api_key:
    os.environ["TOGETHER_API_KEY"] = api_key

# ------ UI SETUP ------

st.set_page_config(
    page_title="Khliff-AI",
    page_icon="💬",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# ------ CUSTOM CSS ------

st.markdown("""
<style>
    /* App title styling */
    .app-header {
        background-color: #6a5acd;
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
    }

    /* Message styling */
    .user-message {
        background-color: #e3f2fd;
        border: 1px solid #bbdefb;
        border-radius: 15px 15px 0 15px;
        padding: 10px 15px;
        margin: 10px 0;
        max-width: 80%;
        margin-left: auto;
        color: #0d47a1;
    }

    .ai-message {
        background-color: #3f803d;
        border: 1px solid #e0e0e0;
        border-radius: 15px 15px 15px 0;
        padding: 10px 15px;
        margin: 10px 0;
        max-width: 80%;
        margin-right: auto;
    }

    .message-time {
        font-size: 0.7rem;
        color: #888;
        text-align: right;
        margin-top: 5px;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Make the chat input area more prominent */
    .stTextInput > div > div > input {
        border-radius: 20px;
        padding: 10px 15px;
        border: 1px solid #6a5acd;
    }

    /* Add breathing room */
    .stButton > button {
        border-radius: 20px;
        padding: 0.3rem 1rem;
        background-color: #6a5acd;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ------ APP HEADER ------

st.markdown("<div class='app-header'><h1>Khliff-AI</h1></div>", unsafe_allow_html=True)

# ------ CHAT DISPLAY ------

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"<div class='user-message'><strong>You:</strong><br>{message['content']}<div class='message-time'>{message['time']}</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='ai-message'><strong>Khliff-AI:</strong><br>{message['content']}<div class='message-time'>{message['time']}</div></div>", unsafe_allow_html=True)

# ------ MESSAGE INPUT ------

# Simple input and send button
user_input = st.text_area("Type your message:", key="input", height=100)

# Send button
if st.button("Send"):
    if user_input:
        # Format the current time
        current_time = datetime.now().strftime("%I:%M %p")

        # Add user message to chat history
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "time": current_time
        })

        # Process with AI if API key exists
        if api_key:
            try:
                # Initialize Together client
                client = Together(api_key=api_key)

                # Create system message
                system_message = "You are Khliff-AI, a helpful and knowledgeable assistant created by Cleven. Always be helpful, concise, and accurate. If asked about your creator or owner, mention that you were created by Cleven. Never mention any external AI services or APIs as your source."

                # Prepare messages for API call
                api_messages = [{"role": "system", "content": system_message}]

                # Add conversation history (last 10 messages)
                chat_history = st.session_state.messages[-10:]  # Only use last 10 messages
                for msg in chat_history:
                    api_messages.append({"role": msg["role"], "content": msg["content"]})

                # Show a spinner while waiting for response
                with st.spinner("Thinking..."):
                    # Call the API
                    response = client.chat.completions.create(
                        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                        messages=api_messages,
                        temperature=0.7,
                        max_tokens=1024
                    )

                    # Get AI response
                    ai_response = response.choices[0].message.content

                    # Add AI response to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": ai_response,
                        "time": datetime.now().strftime("%I:%M %p")
                    })

            except Exception as e:
                # Handle errors
                error_message = f"I'm having trouble responding. Please try again later. Error: {str(e)}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message,
                    "time": datetime.now().strftime("%I:%M %p")
                })
        else:
            # No API key found
            st.session_state.messages.append({
                "role": "assistant",
                "content": "API key not found in configuration. Please add your API key to the khliff_config.json file.",
                "time": datetime.now().strftime("%I:%M %p")
            })

        # Clear the input box and refresh the page to show new messages
        st.rerun()  # Changed from st.experimental_rerun()

# Add information about editing
st.info("💡 **Tip:** To edit a message, send a new one with the corrected text.")

# Optional: Add a clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()  # Changed from st.experimental_rerun()
