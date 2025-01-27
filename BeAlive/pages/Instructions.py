import streamlit as st

# Set page configuration
st.set_page_config(page_title="Instructions", layout="wide", page_icon=":scroll:")

# Custom CSS for consistent and modern styling
st.markdown(
    """
    <style>
    .header {
        text-align: center;
        color: #eaeaea;
        font-size: 40px !important;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .subheader {
        color: #82e0aa;
        font-size: 24px;
        margin-top: 20px;
    }
    .paragraph {
        font-size: 16px;
        line-height: 1.6;
        margin-bottom: 20px;
    }
    ul {
        list-style-type: none;
        padding-left: 0;
    }
    ul li {
        font-size: 16px;
        line-height: 1.6;
    }
    strong {
        color: #FFA07A;
    }
    .section-header {
        color: #82e0aa;
        font-size: 24px;
        margin-top: 20px;
    }
    .instructions-title {
        color: #2ecc71;  /* Matching the header's color */
        font-size: 40px;  /* Same as header size for consistency */
        margin-top: 40px;  /* Adding more space before this section */
        text-align: center;  /* Center-aligning the Instructions title */
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True
)



# Instructions page content
st.markdown("""
<p class="header">Welcome to the instructions page of <strong>BeAlive</strong>!</p>


<p class="paragraph">
    In here we will teach you how to get the maximum out of our chatbot, whether you're a new host just getting the hang of it or a new user looking for a new adventure.
</p>

<p class="subheader"><strong>If you are a user:</strong></p>
<p class="paragraph">
    As a user, you will be able to create your account, login and update your information.
    With the chatbot you will be able to search for activities that align with your interests, book them, and then, when it's finished, tell us your experience by writing a review.
</p>

<ul>
    <li><strong>Create your account:</strong> To create a new user account, go to the <em>Registration</em> page and fill out the required information. After completing the form, click <em>Register</em> to become the newest user of <strong>BeAlive</strong>! after it you can go to the <em>Log in</em> page</li>
</ul>


<ul>
    <li><strong>Login:</strong> Go to the <em>Login</em> page, insert your username and password, and you're all set!</li>
</ul>
            
<p class="paragraph">To perform the following actions, you will need to be logged in to our site.</p>

<p class="paragraph">The following actions will all be done in the <em>Chatbot</em> page.</p>

<ul>
    <li><strong>Search for an Activity:</strong> Ask <strong>AIventure</strong> for activity suggestions that best align with your interests and location, e.g., “I'm looking for a sports activity this weekend”</li>
    <li><strong>Reserve an Activity:</strong> Once you find the perfect activity, tell <strong>AIventure</strong> which activity you want to book. If accepted, you will receive a confirmation message; otherwise, an error will pop up, e.g., “Get me a spot in the activity X”</li>
    <li><strong>Write a Review:</strong> After completing an activity, you can leave feedback for the host by writing a review to <strong>AIventure</strong>, e.g., “Activity X was really fun. Fantastic for begginers. I would rate it a 5”</li>
</ul>

<p class="subheader"><strong>If you are a host:</strong></p>
<p class="paragraph">
    As a host, you will be able to create and remove activities, check the number of participants in your activity, and decide whether to accept or reject participants. You can also review users after an activity and check their reviews. All of this can be done through <strong>AIventure</strong>!
</p>


<ul>
    <li><strong>Create an activity:</strong> To create an activity. Just <strong>download</strong> the activity form that is in the chatbot page, <strong>fill</strong> it with the activity details and <strong>upload</strong> it.</li>
    <li><strong>Remove an activity:</strong> To delete an activity, it must not have happened yet. Just tell <strong>AIventure</strong> which activity to remove, e.g., “I want to delete the activity Y.”</li>
    <li><strong>Check Number of Participants:</strong> To check the number of participants, tell <strong>AIventure</strong>, e.g., “How many reservations does the activity Y has?.”</li>
    <li><strong>Check Participants:</strong> To view the participants who have signed up for an activity, ask <strong>AIventure</strong>, e.g., “Who has reserved the activity Y?.”</li>
    <li><strong>Accept Participant:</strong> To accept a user in your activity, tell <strong>AIventure</strong> the activity and the user you want to accept, e.g., “Accept Brian's request to participate in the activity Y.”</li>
    <li><strong>Reject Participant:</strong> To reject a user, tell <strong>AIventure</strong> the activity and the user you want to reject, e.g., “Deny Brian's request to particpate in the activity Y.”</li>
    <li><strong>Check Reviews:</strong> To view feedback on your activities, ask <strong>AIventure</strong> for the reviews of a specific activity, e.g., “Who has reviewed the activity Y?”</li>
    <li><strong>Write a Review:</strong> To give feedback to a user, tell <strong>AIventure</strong> the activity and username along with your review, e.g., Brian was extremely collaborative. I can easily give him a 5.”</li>
</ul>

<h1 style="color: #5e9ca0;"></h1>
""", unsafe_allow_html=True)
