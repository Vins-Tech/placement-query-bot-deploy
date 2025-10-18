import streamlit as st
from faq import process_folder, generate_answer
from sql import sql_chain
from pathlib import Path
from router import router
from PIL import Image
import base64
from datetime import date
from query_store import get_query_count, update_query_count, get_data
from log_store import log_entry
import contextlib


import os
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 DEBUG INFO")
st.sidebar.write("BIN ID:", os.getenv("JSONBIN_BIN_ID"))
st.sidebar.write("API Key Present:", bool(os.getenv("JSONBIN_API_KEY")))
st.sidebar.write("Log BIN ID:", os.getenv("LOG_BIN_ID"))

# -------------------------------
# App setup
# -------------------------------
st.set_page_config(
    page_title="BNMIT Placement Bot",
    page_icon="🎓",
)

MAX_QUERIES = 25  # shared daily limit

# -------------------------------
# Cached initialization
# -------------------------------
def init_vector_store():
    BASE_DIR = Path(__file__).parent
    folder = BASE_DIR / "resources/placement_texts"
    with contextlib.redirect_stdout(None):
        _ = list(process_folder(folder, reset=False))
    return True

if "initialized" not in st.session_state:
    with st.spinner("Setting up resources..."):
        st.session_state["initialized"] = init_vector_store()

# -------------------------------
# Cached logo loading
# -------------------------------
def load_logo_base64():
    logo_path = Path(__file__).parent / "resources/bnmit_logo.png"
    logo = Image.open(logo_path)
    from io import BytesIO
    buffered = BytesIO()
    logo.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

logo_base64 = load_logo_base64()

# -------------------------------
# Load query count once per session
# -------------------------------
data = get_data()
today = str(date.today())

if "last_reset" not in st.session_state or st.session_state.get("last_reset") != today:
    st.session_state["query_count"] = get_query_count()
    st.session_state["last_reset"] = today

# -------------------------------
# Ask function (synchronous)
# -------------------------------
def ask(query):
    count = st.session_state["query_count"]
    if count >= MAX_QUERIES:
        return "⚠️ Sorry, the total query limit for today has been reached. Please try again tomorrow."

    # Increment and persist count (synchronously)
    new_count = count + 1
    update_query_count(new_count)
    st.session_state["query_count"] = new_count

    # Route the query
    route_obj = router(query)
    route_name = route_obj.name
    route_score = route_obj.score
    print(route_name, route_score)

    if route_name == 'faq':
        answer, context_s = generate_answer(query)
        response_text = answer
    elif route_name == 'sql':
        response_text = sql_chain(query)
    else:
        response_text = (
            "I'm designed to answer queries about placements and related details. "
            "Please try asking about training, vision & mission, faculty, or hiring statistics."
        )

    # Log the query and response synchronously
    try:
        log_entry(
            query=query,
            response=response_text,
            route=route_name,
            score=route_score,
        )
    except Exception as e:
        print("Logging failed:", e)

    return response_text

# -------------------------------
# Header and Branding
# -------------------------------
st.markdown("<h1 style='text-align: center;'>Welcome to BNMIT Placement Department Bot</h1>", unsafe_allow_html=True)
st.markdown(
    """
    <p style='text-align: center; font-size: 14px; color: gray;'>
    💡 This chatbot is a student project developed for learning purposes. It is <b>not an official BNMIT bot</b>.
    </p>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    """
    <p style='text-align: center; font-size: 14px; color: gray;'>
    <b>(Queries are limited. Expand the left panel from top arrows for details.)</b>
    </p>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f'<div style="text-align: center;"><img src="data:image/png;base64,{logo_base64}" width="200"></div>',
    unsafe_allow_html=True,
)

# -------------------------------
# Sidebar info
# -------------------------------
count = st.session_state.get("query_count", 0)
st.sidebar.markdown("### USAGE INFO:")
st.sidebar.info(
    f"💬 **Queries used today (shared across all users):** {count} / {MAX_QUERIES}\n\n"
    f"⏰ **Auto-reset daily at midnight**"
)
st.sidebar.progress(min(count / MAX_QUERIES, 1.0))

st.sidebar.markdown("---")
st.sidebar.markdown("### PROJECT INFO:")
st.sidebar.markdown(f"""
This chatbot is a student project created for learning purposes.  
It is not an official BNMIT bot, and some information may be outdated or inaccurate.

- **Each query is independent** (chat history not saved)
- Using free APIs, daily limit = {MAX_QUERIES} (shared)
""")
st.sidebar.markdown("---")
st.sidebar.markdown("""
👨‍💻 **Contact:** Vinay S  
📧 [vins.techn@gmail.com](mailto:vins.techn@gmail.com)
""")

# -------------------------------
# Chat Interface
# -------------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if len(st.session_state["messages"]) == 0:
    welcome_msg = """
            👋 **Hello! I’m the BNMIT Placement Department Bot.**  
            I'm here to help you with information about placements, recruiters, faculty, and more.  

            💡 You can ask me questions like:
            - What is the average package for CSE in 2025?  
            - Who is the placement officer for BNMIT?  
            - Highest package offering company in 2025?  
            """
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

query = st.chat_input("Ask anything about placements...")

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if query:
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})

    with st.spinner("🤖 Thinking..."):
        response = ask(query)

    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
