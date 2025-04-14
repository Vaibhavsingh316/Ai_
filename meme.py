import streamlit as st
import requests
import json
import time
import logging
from pandas import DataFrame

# Set page config FIRST
st.set_page_config(
    page_title="🤖 Meme Generator AI",
    page_icon="😂",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS (same as app.py)
st.markdown("""
<style>
    /* Green action buttons */
    .stButton>button {
        background-color: #4CAF50 !important;
        color: #000000 !important;
        border: 1px solid #45a049 !important;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #45a049 !important;
        border-color: #398439 !important;
        transform: scale(1.02);
    }

    /* Feature card buttons */
    .bill-card h4 {
        color: #000000 !important;
        padding: 8px;
        background: #d8f5d8 !important;
        border-radius: 8px;
        display: inline-block;
    }

    /* Quick action buttons in sidebar */
    .st-emotion-cache-6qob1r .stButton>button {
        background-color: #81C784 !important;
        color: #000000 !important;
        border: 1px solid #66BB6A !important;
    }

    /* Error/warning buttons */
    .stAlert {
        background-color: #ffebee !important;
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant", 
        "content": "😂 MEME READY 😂\nTell me what you want to meme about!\nExamples:\n- 'Make a meme about procrastination'\n- 'Suggest memes for Monday mornings'\n- 'Funny cat meme ideas'\n\nLet's go viral! 🚀"
    }]

# Configure sidebar (same structure as app.py)
with st.sidebar:
    st.title("⚙️ Settings")
    with st.container():
        api_key = st.text_input("OpenRouter API Key", type="password", help="Required for AI functionality")
        st.markdown("[Get API Key](https://openrouter.ai/keys)")
        
        with st.expander("📘 Quick Start"):
            st.markdown("""
            1. Obtain API key from OpenRouter
            2. Enter key above
            3. Select AI model
            4. Start generating memes!
            """)
        
        model_name = st.selectbox(
            "🤖 AI Model",
            ("google/palm-2-chat-bison"),
            index=0
        )
        
        with st.expander("⚡ Advanced"):
            temperature = st.slider("🧠 Creativity Level", 0.0, 1.0, 0.7,
                                  help="Conservative ↔ Wild")
            max_retries = st.number_input("🔄 Max Retries", 1, 5, 2)
        
        st.markdown("### 🚀 Quick Actions")
        if st.button("🧹 Clear Chat", use_container_width=True):
            st.session_state.messages = [{
                "role": "assistant",
                "content": "Chat cleared! What's our next meme idea? 😎"
            }]

# Main interface
st.title("🤖 Meme Generator AI")
st.caption("Create hilarious memes with AI-powered humor")

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "table_data" in message and message["table_data"] is not None:
            st.table(message["table_data"])
        st.markdown(message["content"])

# System prompt for meme generation
system_message = {
    "role": "system",
    "content": """
    You are a hilarious meme generator assistant. Your tasks:
    1. Generate funny meme ideas based on user prompts
    2. Suggest perfect meme templates for situations
    3. Write hilarious captions for memes
    4. Explain why memes are funny
    
    Format responses with:
    - 😂 Emojis for maximum meme energy
    - Suggested meme template names
    - Top/bottom text suggestions
    - Funny explanations
    
    Example response:
    😂 MEME IDEA 😂
    Template: Distracted Boyfriend
    Top Text: "Me trying to focus on work"
    Bottom Text: "Me thinking about weekend plans"
    Why it's funny: Classic relatable situation of divided attention!
    
    Keep everything lighthearted and fun!
    """
}

# Chat input
if prompt := st.chat_input("What do you want to meme about?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        with st.chat_message("assistant"):
            st.error("🔑 API key required in sidebar settings")
            st.markdown("""
            <div style='background: #fff3f3; padding: 15px; border-radius: 10px; color: #000000 !important;'>
                <h4 style='color: #000000 !important;'>Get Started:</h4>
                <ol style='color: #000000 !important;'>
                    <li>Visit <a href="https://openrouter.ai/keys" style='color: #1976d2 !important;'>OpenRouter</a></li>
                    <li>Create account & get key</li>
                    <li>Enter key in sidebar</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        st.stop()

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        attempts = 0
        
        with st.spinner("Cooking up dank memes..."):
            time.sleep(0.3)
        
        while attempts < max_retries:
            try:
                # Prepare API request
                api_messages = [system_message] + st.session_state.messages[-4:]
                
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://meme-generator.streamlit.app",
                        "X-Title": "Meme Generator AI"
                    },
                    json={
                        "model": model_name,
                        "messages": api_messages,
                        "temperature": temperature,
                        "response_format": {"type": "text"}
                    },
                    timeout=15
                )

                response.raise_for_status()
                data = response.json()
                raw_response = data['choices'][0]['message']['content']
                
                # Stream response
                lines = raw_response.split('\n')
                for line in lines:
                    words = line.split()
                    for word in words:
                        full_response += word + " "
                        response_placeholder.markdown(full_response + "▌")
                        time.sleep(0.03)
                    full_response += "\n"
                    response_placeholder.markdown(full_response + "▌")
                
                # Final formatting
                response_placeholder.markdown(full_response)
                break
                
            except json.JSONDecodeError as e:
                logging.error(f"JSON Error: {str(e)}")
                attempts += 1
                if attempts == max_retries:
                    response_placeholder.error("⚠️ Processing error. Try:")
                    response_placeholder.markdown("""
                    <div style='background: #fff3f3; padding: 15px; border-radius: 10px; color: #000000 !important;'>
                        <h4 style='color: #000000 !important;'>💡 Help:</h4>
                        <ul style='color: #000000 !important;'>
                            <li>Rephrase your meme idea</li>
                            <li>Check your internet connection</li>
                            <li>Try a different template</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    time.sleep(0.5)
                
            except requests.exceptions.RequestException as e:
                response_placeholder.error(f"🌐 Network Error: {str(e)}")
                full_response = "Connection issue - please try again"
                break
                
            except Exception as e:
                logging.error(f"Error: {str(e)}")
                response_placeholder.error(f"❌ Unexpected error: {str(e)}")
                full_response = "Please try again"
                break

    st.session_state.messages.append({"role": "assistant", "content": full_response})