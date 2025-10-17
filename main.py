import streamlit as st
from faq import process_folder, generate_answer, vector_store
from sql import sql_chain
from pathlib import Path
from router import router
from PIL import Image
import base64
from datetime import date, datetime
from query_store import get_query_count, update_query_count
from log_store import log_entry


# Force sidebar to open by default
st.set_page_config(
    page_title="BNMIT Placement Bot",
    page_icon="🎓",
    #layout="wide",
    #initial_sidebar_state="expanded"  # 👈 this line ensures sidebar is open
)


MAX_QUERIES = 25  # shared daily limit

# -------------------------------
# Initialize placement data
# -------------------------------
if "initialized" not in st.session_state:
    BASE_DIR = Path(__file__).parent
    folder = BASE_DIR / "resources/placement_texts"
    for msg in process_folder(folder, reset=False):
        print(msg)
    st.session_state["initialized"] = True

# -------------------------------
# Load query count once per session
# -------------------------------
from datetime import date
from query_store import get_data, get_query_count

# Always ensure count is fresh per calendar day
data = get_data()
today = str(date.today())

if "last_reset" not in st.session_state or st.session_state.get("last_reset") != today:
    st.session_state["query_count"] = get_query_count()
    st.session_state["last_reset"] = today

# -------------------------------
# Ask function
# -------------------------------
def ask(query):
    """
    Handles a single user query:
      - checks & increments shared daily counter
      - routes to faq/sql
      - logs (timestamp, route, query, response)
    """
    count = st.session_state["query_count"]

    if count >= MAX_QUERIES:
        return "⚠️ Sorry, the total query limit for today has been reached. Please try again tomorrow."

    # increment and persist (shared bin)
    new_count = count + 1
    update_query_count(new_count)
    st.session_state["query_count"] = new_count  # immediately reflect in UI

    # route the query
    route_obj = router(query)
    route_name=route_obj.name
    route_score=route_obj.score
    print(route_name,route_score)

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

    # log the query + response + route + timestamp (best-effort, non-blocking)
    try:
        log_entry(
            query=query,
            response=response_text,
            route=route_name,
            score=route_score,  # ✅ add similarity score
        )
    except Exception as e:
        print("Logging failed:", e)

    return response_text

# -------------------------------
# Header and Branding
# -------------------------------
st.markdown("<h1 style='text-align: center;'>Welcome to BNMIT Placement department Bot</h1>", unsafe_allow_html=True)
st.markdown(
    """
    <p style='text-align: center; font-size: 14px; color: gray;'>
    💡 This chatbot is a student project developed for learning purposes. It is <b>not an official BNMIT bot</b>.
    </p>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <p style='text-align: center; font-size: 14px; color: gray;'>
    <b>(queries are limited.expand the left panel from top arrows for details)</b>.
    </p>
    """,
    unsafe_allow_html=True
)
# College logo
logo_path = Path(__file__).parent / "resources/bnmit_logo.png"
logo = Image.open(logo_path)

def image_to_base64(img):
    from io import BytesIO
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

logo_base64 = image_to_base64(logo)
st.markdown(
    f'<div style="text-align: center;"><img src="data:image/png;base64,{logo_base64}" width="200"></div>',
    unsafe_allow_html=True
)

# -------------------------------
# Sidebar info + project note
# -------------------------------
# Use session state value so it matches immediately after ask()
count = st.session_state.get("query_count", 0)

st.sidebar.markdown("###  USAGE INFO:")
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

- **Each query is independent** and chat history is not saved (no context from previous prompts/responses/chats)
- Using free APIs, so the daily query limit is {MAX_QUERIES} (shared across users)
""")

import datetime
st.sidebar.markdown("---")
st.sidebar.write("🕒 Server time:", datetime.datetime.now())
st.sidebar.markdown("---")

st.sidebar.markdown("""
👨‍💻 **Contact:** Vinay S  
📧 [vins.techn@gmail.com](mailto:vins.techn@gmail.com)
""")

# -------------------------------
# Chat Interface
# -------------------------------
query = st.chat_input("Ask anything about placements...")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if query:
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})

    response = ask(query)

    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
