import streamlit as st
from BeAlive.pages.users_interact import UserDatabase
import sqlite3


# Database connection
conn = sqlite3.connect("BeAlive/data/database/BeAlive.db")
db = UserDatabase(conn)

# Initialize session state
if "username" not in st.session_state:
    st.session_state.username = None

st.set_page_config(page_title="Login", layout="wide", page_icon="🔑")

st.markdown(
    """
    <style>
    .title {
        text-align: center;
        color: #eaeaea;
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 20px; 
    }
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start; /* Align to the top instead of centering vertically */
        padding-top: 50px; 
        background-color: #1D1D2B;
        color: #EAEAEA;
        font-family: 'Poppins', sans-serif;
    }
    .login-title {
        text-align: left;
        margin-bottom: 20px;
        color: #EAEAEA;
        font-size: 28px;
        font-weight: bold;
    }
    .stTextInput>div>div {
        margin-bottom: 15px;
    }
    .stButton>button {
        background-color: #00C2FF;
        color: #EAEAEA;
        padding: 10px 20px;
        font-size: 16px;
        border-radius: 8px;
        border: none;
        font-family: 'Poppins', sans-serif;
    }
    .stButton>button:hover {
        background-color: #EAEAEA;
        color: #1D1D2B;
        transition: 0.3s;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<h1 class="title">🌟 Welcome to BeAlive! </h1>', unsafe_allow_html=True)

st.markdown('<div class="login-container">', unsafe_allow_html=True)

st.markdown('<h2 class="login-title">Login</h2>', unsafe_allow_html=True)

with st.form("login_form"):
    username = st.text_input("👤 Username", placeholder="Enter your username")
    password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
    submit = st.form_submit_button("Login")

    if submit:
        if not username or not password:
            st.error("Please fill all fields")
            st.session_state.logged_in = False

        elif not db.verify_user(username, password):
            st.error("Incorrect username or password")
            st.session_state.logged_in = False

        else:
            st.success("Login successful!")
            st.session_state.user_details = db.get_user_details(username)
            st.session_state.logged_in = True
            st.session_state.user_id = db.get_user_id(username)
            st.session_state.username = username

            st.balloons()
st.markdown('</div>', unsafe_allow_html=True)
