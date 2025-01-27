import streamlit as st

# Set page configuration
st.set_page_config(page_title="About Us", layout="wide", page_icon=":smiley:")

# Custom CSS for consistent and modern styling
st.markdown(
    """
    <style>
    .header {
        text-align: center;
        color: #00C2F;
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
    </style>
    """, unsafe_allow_html=True
)


# Main content
st.markdown("""
<p class="header">Welcome to <strong>BeAlive</strong>, where we make boredom a thing of the past.</p>


<p class="paragraph">
    <strong>How the Idea Appeared:</strong> This idea is the product of five very bored, but adventurous friends: 
    <strong>Dinis Fernandes, Dinis Gaspar, Inês Santos, Luis Dávila, Sara Ferrer</strong>.
</p>
<p class="paragraph">
    They were seeking a new, exciting adventure, but only found impersonalized, confusing websites that lacked community building. So, they decided to take matters into their own hands, and that’s when <strong>BeAlive</strong> was born.
</p>

<p class="section-header">What is BeAlive?</p>
<p class="paragraph">
    <strong>BeAlive</strong> is a platform with an intelligent AI assistant at its core: <strong>AIventure</strong>, designed to make the search for thrilling activities effortless. You only need to tell <strong>AIventure</strong> what kind of activity you're in the mood for, and it will suggest an activity that matches your interests, lifestyle, and profile. Whether you're looking for solo or group activities, peaceful or adrenaline-pumping experiences, <strong>AIventure</strong> is your perfect guide.
</p>

<p class="paragraph">
    Since the beginning, the company has grown rapidly, now with hundreds of passionate team members making sure your experience is smooth, easy, and full of fun.
</p>

<p class="subheader">Why You Should Choose Us</p>

<p class="paragraph">
    At <strong>BeAlive</strong>, we aim to revolutionize how people spend their free time, turning every moment into an opportunity for new and exciting adventures. With <strong>AIventure</strong>, discovering new activities has never been easier or more personalized. Our mission is to help you fill your free time with fun, build connections, and spark joy.
</p>

<p class="subheader">Our Values</p>
<ul>
    <li><strong>Collaboration:</strong> We promote teamwork and open communication to deliver exceptional results.</li>
    <li><strong>Customer-Centricity:</strong> Our users are our focus, ensuring a seamless, intuitive, and personalized experience.</li>
    <li><strong>Friendship and Empathy:</strong> We foster a community-driven approach that encourages meaningful connections.</li>
    <li><strong>Innovation:</strong> We constantly innovate to stay ahead in AI technology and enhance user experience.</li>
    <li><strong>Transparency and Security:</strong> We ensure that our users' data is handled with care, clarity, and respect.</li>
</ul>

<p class="paragraph">
    Join us on this journey to transform boredom into vibrant, unforgettable experiences. With <strong>BeAlive</strong>, your next adventure is just a suggestion away!
</p>
""", unsafe_allow_html=True)

# End of the container
st.markdown('</div>', unsafe_allow_html=True)
