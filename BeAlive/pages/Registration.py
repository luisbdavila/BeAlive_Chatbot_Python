import streamlit as st
import datetime
import sqlite3
from BeAlive.pages.users_interact import UserDatabase
import regex as re

st.set_page_config(page_title="Registration", layout="wide", page_icon=":pencil:")


def is_valid_email(email):
    """
    See if the email is valid.

    Parameters:
    -----------
    email: str
        The email address to validate.
    """
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


conn = sqlite3.connect("BeAlive/data/database/BeAlive.db")
db = UserDatabase(conn)

st.markdown(
    """
    <style>
    .header {
        text-align: center;
        color: #eaeaea;
        font-size: 40px !important;
        font-weight: bold;
        margin-bottom: 30px;
    }
    .form-container {
        background-color: #1D1D2B;
        padding: 40px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .form-submit {
        background-color: #2ecc71;
        color: white;
        font-size: 18px;
        padding: 12px 30px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
    }
    .form-submit:hover {
        background-color: #27ae60;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
        padding: 12px;
        border: 1px solid #aaa;
        font-size: 16px;
    }

    </style>
    """, unsafe_allow_html=True
)


st.markdown(
    """
    <div class="header">Registration</div>
    """,
    unsafe_allow_html=True
)

with st.form("registration_form"):
    col1, col2 = st.columns(2)

    with col1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password", help="Max 10 characters")
        name = st.text_input("Name")
        birthday = st.date_input(
            "Date of Birth",
            min_value=datetime.date(1900, 1, 1),
            max_value=datetime.date.today(),
              )

    with col2:
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        location = st.text_input("City")
        options = ["Art", "Astronomy", "Beach", "Bird Watching", "Board Games",
                   "Books", "Camping", "Cars", "Comedy", "Cooking", "Crafts",
                   "Dance", "Drawing", "Fashion", "Fishing", "Fitness", "Food",
                   "Gaming", "Gardening", "Hiking", "History", "Hunting",
                   "Indoors", "Knitting", "Martial Arts", "Meditation",
                   "Modeling", "Outdoors", "Movies", "Museums", "Music",
                   "Nature", "Painting", "Pets", "Photography", "Reading",
                   "Sewing", "Singing", "Sports", "Tech", "Theater", "Travel",
                   "Writing", "Yoga"]
        interests_lt = st.pills("Interests", options, selection_mode="multi")
        interests = ", ".join(interests_lt)
    submit = st.form_submit_button("Register")


if submit:

    if (not all([username, password, name, birthday, email, phone, location, interests])):
        st.error("Please fill all fields")

    elif not is_valid_email(email):
        st.error("Please enter a valid email")

    elif len(password) > 10:
        st.error("Password must be less than 10 characters")

    elif db.check_if_email_exists(email):
        st.error("Email already registered")

    elif len(username) > 10:
        st.error("Username must be less than 10 characters")

    elif db.check_if_username_exists(username):
        st.error("Username already exists")

    else:
        if db.add_user(username,
                       password,
                       name,
                       birthday,
                       email,
                       phone,
                       location,
                       interests,
                       3):
            st.success("Registration Successful!")
            st.text("Go to the Loging page")
            st.page_link("BeAlive/pages/Login.py", label="Login", icon="🔑")

        else:
            st.error("Registration failed. Please try again.")
