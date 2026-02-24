import streamlit as st
import preprocess
import helper
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="WhatsApp Chat Analyzer 💖",
    page_icon="💬",
    layout="wide"
)

# ==============================
# SESSION STATE INIT
# ==============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ==============================
# SIMPLE USER DATABASE
# ==============================
USER_CREDENTIALS = {
    "nivi": "1234",
    "admin": "admin123"
}

# ==============================
# LOGIN FUNCTION
# ==============================
def login():

    st.markdown("## 🔐 Login to Access Dashboard")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.success("Login Successful 💖")
            st.rerun()
        else:
            st.error("Invalid Username or Password ❌")


# ==============================
# PINK THEME
# ==============================
st.markdown("""
<style>
.stApp { background-color: #ffe6f0; }

.header {
    background: linear-gradient(90deg, #ff66a3, #ff99cc, #cc0066);
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    color: white;
    font-size: 40px;
    font-weight: bold;
}

section[data-testid="stSidebar"] {
    background-color: #ff99cc;
}

.kpi-card {
    background: rgba(255, 182, 193, 0.4);
    backdrop-filter: blur(10px);
    padding: 20px;
    border-radius: 20px;
    text-align: center;
    font-size: 18px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">💬 WhatsApp Chat Analyzer</div>', unsafe_allow_html=True)
st.markdown("---")


# ==============================
# AUTH CHECK
# ==============================
if not st.session_state.logged_in:
    login()

else:
    # ==============================
    # SIDEBAR (AFTER LOGIN)
    # ==============================
    st.sidebar.success("Logged in Successfully 💕")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.sidebar.title("📂 Upload Chat File")
    uploaded_file = st.sidebar.file_uploader("Choose your WhatsApp chat (.txt)")

    dark_mode = st.sidebar.toggle("🌙 Dark Pink Mode")

    if dark_mode:
        st.markdown("""
        <style>
        .stApp { background-color: #33001a; color: white; }
        </style>
        """, unsafe_allow_html=True)

    # ==============================
    # MAIN DASHBOARD
    # ==============================
    if uploaded_file is not None:

        bytes_data = uploaded_file.getvalue()

        try:
            data = bytes_data.decode("utf-8")
        except:
            data = bytes_data.decode("latin-1")

        with st.spinner("Analyzing your chat 💕..."):
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

            # KPI CARDS
            col1, col2, col3 = st.columns(3)

            col1.markdown(f"<div class='kpi-card'>💬 Messages<br><h2>{num_messages}</h2></div>", unsafe_allow_html=True)
            col2.markdown(f"<div class='kpi-card'>📝 Words<br><h2>{num_words}</h2></div>", unsafe_allow_html=True)
            col3.markdown(f"<div class='kpi-card'>📷 Media<br><h2>{num_media}</h2></div>", unsafe_allow_html=True)

            st.markdown("---")

            # TABS
            tab1, tab2, tab3 = st.tabs(["📊 Timeline", "😊 Emoji", "🔥 Heatmap"])

            with tab1:
                timeline = df.groupby(df['date'].dt.date).size().reset_index(name='messages')
                fig = px.line(timeline, x="date", y="messages",
                              title="📈 Daily Message Timeline",
                              color_discrete_sequence=["#cc0066"])
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                emoji_df = helper.emoji_analysis(selected_user, df)

                if not emoji_df.empty:
                    fig = px.bar(
                        emoji_df,
                        x="emoji",
                        y="count",
                        color="count",
                        color_continuous_scale="pinkyl"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write("No emojis found")

            with tab3:
                heatmap = df.pivot_table(
                    index='day_name',
                    columns=df['date'].dt.hour,
                    values='message',
                    aggfunc='count'
                ).fillna(0)

                fig, ax = plt.subplots(figsize=(10, 5))
                sns.heatmap(heatmap, cmap="RdPu", ax=ax)
                st.pyplot(fig)

            # DOWNLOAD OPTION
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Processed Data",
                data=csv,
                file_name="whatsapp_analysis.csv",
                mime="text/csv"
            )

            st.markdown("---")
            st.markdown("<center>Made with 💖 by Nivi</center>", unsafe_allow_html=True)