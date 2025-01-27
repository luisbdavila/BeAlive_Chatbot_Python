import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from BeAlive.chatbot.chains.create_activity import CreateActivityChain
from BeAlive.chatbot.chains.change_state import UpdateActivitiesChain
from BeAlive.chatbot.chains.show_reserv import ShowReservationChain
from BeAlive.chatbot.chains.show_review import ShowReviewChain
from BeAlive.chatbot.bot import MainChatbot
import time
import pymupdf


st.set_page_config(page_title="Chatbot", layout="wide", page_icon="🤖")

st.markdown(
    """
    <style>
    .stSpinner > div {
        width: 200px !important;  /* Adjust the width */
        height: 200px !important; /* Adjust the height */
        border-width: 100px !important; /* Adjust the thickness */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.spinner("Loading Chatbot..."):

    st.title("AIventure")

    def simulate_streaming(message):
        """
        Simulate a streaming response from the bot.

        Parameters:
        -----------
        message: str
            The message to be streamed.
        """
        buffer = ""
        for char in message:
            buffer += char
            if char == " " or char == "\n":
                yield buffer
                buffer = ""
                if char == "\n":  # To simulate line breaks
                    time.sleep(0.1)  # Longer pause for newlines (optional)
                else:
                    time.sleep(0.05)
        if buffer:  # Yield any remaining characters
            yield buffer


    def main(bot: MainChatbot):
        """
        Main interaction loop for the chatbot.
        """

        # Initialize session state for messages
        if "messages" not in st.session_state:
            st.session_state.messages = []

            UpdateActivitiesChain().UpdateActivities()

            ShowReservations = ShowReservationChain().ShowReservation()
            st.session_state.messages.append({"role": "bot", "content": "PENDING RESERVATIONS: \n\n" + ShowReservations})

            bot.add_messages_memory(message="Show me my pending reservations",
                                    respond=ShowReservations)

            ShowReviews = ShowReviewChain().ShowReview()
            st.session_state.messages.append({"role": "bot", "content": ShowReviews})

            bot.add_messages_memory(message="Show me my pending reviews",
                                    respond=ShowReviews)

        # Display past messages
        for message in st.session_state.messages:
            if message["role"] == "bot":
                with st.chat_message(message["role"], avatar="🤖"):
                    st.markdown(message["content"])
            elif message["role"] == "user":
                with st.chat_message(message["role"], avatar="🕺"):
                    st.markdown(message["content"])

        # User input
        user_input = st.chat_input("You:")
        if user_input:
            # Append user input to session state
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user", avatar="🕺"):
                st.markdown(user_input)

            try:
                response = bot.process_user_input({"user_input": user_input})
            except Exception as e:
                response = f"Please try again, an error has occured. Error: {str(e)}. "

            # Append response to session state
            st.session_state.messages.append({"role": "bot", "content": response})

            # Display bot response
            with st.chat_message("bot", avatar="🤖"):
                st.write_stream(simulate_streaming(response))

            bot.add_messages_memory(message=user_input,
                                    respond=response)

        # Add the download and upload buttons at the bottom of the page
        with st.container():

            with st.container():
                with open(r"BeAlive/data/pdfs/activity form/Activity_Creation_Form_PDF.pdf", "rb") as file:
                    pdf_data = file.read()

                st.download_button(
                    label="Download Activity Creation",
                    data=pdf_data,
                    file_name="activity_creation.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="download_button"
                )

            activity_upload = st.file_uploader("Upload Activity", type="pdf", key="upload_button")

            if activity_upload is not None:
                try:
                    with pymupdf.open(stream=activity_upload.read(), filetype="pdf") as pdf:
                        pdf_text = ""
                        for page_num, page in enumerate(pdf, start=1):
                            pdf_text += f"Page {page_num}:\n{page.get_text()}\n\n"

                    # Display the extracted text
                    st.text("Extracted Text from PDF:")
                    CreateActivityChain_ = CreateActivityChain()
                    result_upload = CreateActivityChain_.invoke(content=pdf_text)

                    # Append response to session state
                    st.session_state.messages.append({"role": "bot", "content": result_upload})
                    st.write(result_upload)

                    bot.add_messages_memory(message="I want to create an activity",
                                            respond=result_upload)

                except Exception as e:
                    st.error("An error occurred while processing the PDF.")
                    st.error(str(e))


    # Notify the user that the bot is starting
    with st.chat_message("bot", avatar="🤖"):
        st.markdown("Starting the bot...")

    if "bot" not in st.session_state:
        st.session_state.bot = MainChatbot()
        st.session_state.bot.user_login(user_id=f"{st.session_state.user_id}")

    with st.chat_message("bot", avatar="🤖"):
        st.markdown("Bot initialized.")

    # Run the application
    main(st.session_state.bot)

    st.markdown("""
        <style>
            /* CSS to center the chatbot */
            .chatbot-container {
                display: flex;
                justify-content: center;
                align-items: flex-start;
                height: 80vh;
                flex-direction: column;
                overflow-y: auto;
                padding-bottom: 120px;  /* Provide space for buttons */
            }

            /* CSS for the download button to be at the bottom-left */
            .download-button-container {
                position: fixed !important;
                left: 10px !important;
                bottom: 10px !important;
                z-index: 1000 !important;
                background-color: #444 !important;
                padding: 10px !important;
                border-radius: 8px !important;
            }

            /* CSS for the upload button to be at the bottom-right */
            .upload-button-container {
                position: fixed !important;
                right: 10px !important;
                bottom: 10px !important;
                z-index: 1000 !important;
                background-color: #444 !important;
                padding: 10px !important;
                border-radius: 8px !important;
            }

            /* Ensure that the chat input does not overlap with the buttons */
            .stTextInput>div>div>input {
                margin-bottom: 120px !important;  /* Add margin so it stays above the buttons */
            }
        </style>
    """, unsafe_allow_html=True)
