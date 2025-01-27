import streamlit as st

Login = st.Page("BeAlive/pages/Login.py", title="Login")
Registration = st.Page("BeAlive/pages/Registration.py", title="Registration")
Chatbot = st.Page("BeAlive/pages/Chatbotpage.py", title="Chatbot")
Calendar = st.Page("BeAlive/pages/Calendar.py", title="Calendar")
Instructions = st.Page("BeAlive/pages/Instructions.py", title="Instructions")
About = st.Page("BeAlive/pages/About.py", title="About us")
Account = st.Page("BeAlive/pages/Account.py", title="Account")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.logo(
    image="images/Logo.jpeg",
    size="large",
    icon_image="images/Logo.jpeg",
)

# Check if the user is logged in
if st.session_state.logged_in:
    pg = st.navigation(
        pages={
            "Pages": [
                Chatbot,
                Calendar,
                Instructions,
                Account,
                About,

            ],
        },
        expanded=True,
    )

else:
    # If the user is not logged in
    pg = st.navigation(
        pages={
            "Pages": [
                Instructions,
                About
            ],
            "Register and Login": [Registration,
                                    Login],
        },
        expanded=True,
        )

# Run Navigation
pg.run()
