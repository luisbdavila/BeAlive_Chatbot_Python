import sqlite3
import streamlit as st
from BeAlive.pages.users_interact import UserDatabase
from BeAlive.pages.Registration import is_valid_email


# Set page configuration
st.set_page_config(page_title="Account",layout="wide", page_icon=":bust_in_silhouette:")

# Connect to the database
conn = sqlite3.connect("BeAlive/data/database/BeAlive.db")
db = UserDatabase(conn)

# Fetch the current user details
username, password, name, birthday, email, phone_number, location, interests, cumulative_rating = db.get_user_details(st.session_state.username)

# Add custom CSS to style the page
st.markdown(
    """
    <style>
    .header {
        text-align: center;
        color: #EAEAEA;
        font-size: 40px !important;
        font-weight: bold;
        margin-bottom: 30px;
    }
    .section-title {
        font-size: 20px;
        color: #82e0aa !important;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .input-container {
        background-color: #8d948d;  
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True
)

# Page Title
st.markdown("<h1 class='header'>User Profile</h1>", unsafe_allow_html=True)

# Log Out Button
if st.button("Log Out"):
    st.session_state.clear()

# Profile Editing Section
st.subheader("Edit Your Profile")

# Display user profile information with edit options
st.markdown("<h4 class='section-title'>Username</h4>", unsafe_allow_html=True)
st.markdown(f"<div class='input-container'>{username}</div>", unsafe_allow_html=True)

# Password input
st.markdown("<h4 class='section-title'>Password</h4>", unsafe_allow_html=True)
new_password = st.text_input("New Password", value=password, type="password", key="new_password")

# Name input
st.markdown("<h4 class='section-title'>Name</h4>", unsafe_allow_html=True)
st.markdown(f"<div class='input-container'>{name}</div>", unsafe_allow_html=True)

# Birthday input
st.markdown("<h4 class='section-title'>Birthday</h4>", unsafe_allow_html=True)
st.markdown(f"<div class='input-container'>{birthday}</div>", unsafe_allow_html=True)

# Email input
st.markdown("<h4 class='section-title'>Email</h4>", unsafe_allow_html=True)
new_email = st.text_input("New Email", value=email)

# Phone number input
st.markdown("<h4 class='section-title'>Phone Number</h4>", unsafe_allow_html=True)
new_phone_number = st.text_input("New Phone Number", value=phone_number)

# Location input
st.markdown("<h4 class='section-title'>Location</h4>", unsafe_allow_html=True)
new_location = st.text_input("New Location", value=location)

# Interests input
st.markdown("<h4 class='section-title'>Interests</h4>", unsafe_allow_html=True)
options = [
    "Art", "Beach", "Books", "Cars", "Comics", "Crafts", "Dance", "Fashion", 
    "Fitness", "Food", "Gaming", "Gardening", "Indoor", "Mountains", "Movies", 
    "Music", "Nature", "Outdoor", "Pets", "Photography", "Sports", "Tech", "Writing", "Yoga"
]
new_interests_lt = st.pills("Interests", options, selection_mode="multi")
new_interests = ", ".join(new_interests_lt)

# Rating Section (Display only, not editable)
st.markdown("<h4 class='section-title'>Rating</h4>", unsafe_allow_html=True)
st.markdown(f"<div class='input-container'>{cumulative_rating}</div>", unsafe_allow_html=True)

# Update Button
updates = {
    "password": new_password,
    "email": new_email,
    "phone_number": new_phone_number,
    "location": new_location,
    "interests": new_interests
}

if st.button("Save Changes"):
    if not is_valid_email(new_email):
        st.error("Please enter a valid email")

    elif len(new_password) > 10:
        st.error("Password must be less than 10 characters")

    elif new_email != email and db.check_if_email_exists(new_email):
        st.error("Email already registered")

    else:
        success = db.update_user(username, **updates)
        if success:
            st.success("Profile updated successfully!")
        else:
            st.error("Failed to update profile. Please try again.")

# Account Deletion Section
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False

if st.button("Delete Account"):
    st.session_state.confirm_delete = True

if st.session_state.confirm_delete:
    st.warning("Are you sure you want to delete your account?")
    quest = st.selectbox("Confirm deletion:", ["-", "Yes", "No"])

    if quest == "Yes":
        delete = db.delete_user(st.session_state.user_id)
        if delete:
            st.success("Account deleted successfully!")
            st.session_state.logged_in = False
        else:
            st.error("Failed to delete account. Please try again.")
    elif quest == "No":
        st.info("Account deletion canceled.")
