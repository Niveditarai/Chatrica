import streamlit as st
import preprocess
import helper
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import os

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="WhatsApp Chat Analyzer 💚",
    page_icon="💬",
    layout="wide"
)

# ==============================
# SESSION INIT
# ==============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ==============================
# USER FILE SETUP
# ==============================
USER_FILE = "users.csv"

if not os.path.exists(USER_FILE):
    pd.DataFrame(columns=["username", "password"]).to_csv(USER_FILE, index=False)

# ==============================
# AUTH FUNCTIONS
# ==============================
def signup():
    st.subheader("📝 Sign Up")

    new_user = st.text_input("Create Username")
    new_pass = st.text_input("Create Password", type="password")

    if st.button("Sign Up"):

        if new_user.strip() == "" or new_pass.strip() == "":
            st.warning("Fields cannot be empty ⚠")
            return

        users = pd.read_csv(USER_FILE)

        if new_user.strip() in users["username"].astype(str).values:
            st.warning("Username already exists ⚠")
        else:
            new_data = pd.DataFrame(
                [[new_user.strip(), new_pass.strip()]],
                columns=["username", "password"]
            )
            new_data.to_csv(USER_FILE, mode='a', header=False, index=False)
            st.success("Account Created Successfully 🎉 Please Login.")


def login():
    st.subheader("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        users = pd.read_csv(USER_FILE)

        users["username"] = users["username"].astype(str).str.strip()
        users["password"] = users["password"].astype(str).str.strip()

        username = username.strip()
        password = password.strip()

        if ((users["username"] == username) & 
            (users["password"] == password)).any():

            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login Successful 💚")
            st.rerun()
        else:
            st.error("Invalid Username or Password ❌")


# ==============================
# WHATSAPP GREEN THEME
# ==============================
st.markdown("""
<style>
.stApp { background-color: #f0fdf4; }

.header {
    background: linear-gradient(90deg, #25D366, #128C7E);
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    color: white;
    font-size: 36px;
    font-weight: bold;
}

section[data-testid="stSidebar"] {
    background-color: #128C7E;
    color: white;
}

.stButton>button {
    background-color: #25D366;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    font-size: 16px;
    border: none;
}

.stButton>button:hover {
    background-color: #128C7E;
}

.kpi-card {
    background: rgba(37, 211, 102, 0.15);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">💬 WhatsApp Chat Analyzer</div>', unsafe_allow_html=True)
st.markdown("---")

# ==============================
# AUTH SCREEN
# ==============================
if not st.session_state.logged_in:

    choice = st.radio("Choose Option", ["Login", "Sign Up"])

    if choice == "Login":
        login()
    else:
        signup()

# ==============================
# DASHBOARD
# ==============================
else:

    st.sidebar.success(f"Welcome {st.session_state.username} 💚")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.sidebar.title("📂 Upload Chat File")
    uploaded_file = st.sidebar.file_uploader("Choose your WhatsApp chat (.txt)")

    if uploaded_file is not None:

        bytes_data = uploaded_file.getvalue()

        try:
            data = bytes_data.decode("utf-8")
        except:
            data = bytes_data.decode("latin-1")

        df = preprocess.preprocess(data)

        st.success("File Uploaded Successfully 🎉")

        user_list = df['user'].unique().tolist()
        if 'group_notification' in user_list:
            user_list.remove('group_notification')

        user_list.sort()
        user_list.insert(0, "Overall")

        selected_user = st.selectbox("Show analysis for", user_list)

        if st.button("Show Analysis"):

            num_messages, num_words, num_media, _ = helper.fetch_stats(selected_user, df)

            col1, col2, col3 = st.columns(3)

            col1.markdown(f"<div class='kpi-card'>💬 Messages<br><h2>{num_messages}</h2></div>", unsafe_allow_html=True)
            col2.markdown(f"<div class='kpi-card'>📝 Words<br><h2>{num_words}</h2></div>", unsafe_allow_html=True)
            col3.markdown(f"<div class='kpi-card'>📷 Media<br><h2>{num_media}</h2></div>", unsafe_allow_html=True)

            st.markdown("---")

            tab1, tab2 = st.tabs(["📊 Timeline", "😊 Emoji"])

            with tab1:
                timeline = df.groupby(df['date'].dt.date).size().reset_index(name='messages')
                fig = px.line(timeline, x="date", y="messages",
                              color_discrete_sequence=["#128C7E"])
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                emoji_df = helper.emoji_analysis(selected_user, df)

                if not emoji_df.empty:
                    fig = px.bar(
                        emoji_df,
                        x="emoji",
                        y="count",
                        color="count",
                        color_continuous_scale="greens"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write("No emojis found")

            st.markdown("---")
            st.markdown("<center>Made with 💚 by Nivi</center>", unsafe_allow_html=True)