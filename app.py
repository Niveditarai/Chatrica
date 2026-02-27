import streamlit as st
import preprocess
import helper
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import os
import zipfile

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Chatrica 🤖", layout="wide")

# ================= THEME TOGGLE =================
theme = st.sidebar.toggle("🌙 Dark Mode", value=True)

# ================= COLOR PALETTE (BASED ON YOUR IMAGE) =================
primary_color = "#4cc9f0"     # neon blue
secondary_color = "#b5179e"   # purple accent
text_color = "white" if theme else "black"
glass_bg = "rgba(10,10,20,0.85)" if theme else "rgba(255,255,255,0.85)"

# ================= CUSTOM CSS =================
st.markdown(f"""
<style>

/* Background using your image */
.stApp {{
    background-image: url("background.png");
    background-size: cover;
    background-attachment: fixed;
    background-position: center;
    color: {text_color};
}}

/* Glass container */
.block-container {{
    background: {glass_bg};
    padding: 2rem;
    border-radius: 20px;
}}

/* Title Styling */
.title {{
    font-size: 60px;
    text-align: center;
    font-weight: 800;
    background: linear-gradient(90deg, {primary_color}, {secondary_color});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 3px;
}}

/* Subtitle */
.subtitle {{
    text-align: center;
    font-size: 18px;
    color: {primary_color};
    margin-bottom: 20px;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: rgba(0,0,20,0.95);
}}

/* KPI Cards */
.kpi-card {{
    background: rgba(76,201,240,0.08);
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    border: 1px solid {primary_color};
    backdrop-filter: blur(12px);
    transition: 0.3s ease;
}}

.kpi-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 8px 20px {primary_color};
}}

/* Buttons */
.stButton>button {{
    background: linear-gradient(90deg,{primary_color},{secondary_color});
    color: white;
    font-weight: bold;
    border-radius: 10px;
    border: none;
    height: 3em;
}}

.stButton>button:hover {{
    transform: scale(1.05);
}}

</style>
""", unsafe_allow_html=True)

# ================= TITLE =================
st.markdown('<div class="title">🤖 Chatrica</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI Powered Conversation Intelligence</div>', unsafe_allow_html=True)
st.markdown("---")

# ================= SESSION =================
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "run_toxicity" not in st.session_state:
    st.session_state.run_toxicity = False

# ================= FILE UPLOAD =================
uploaded_file = st.sidebar.file_uploader(
    "Upload Chat (.txt or .zip with media)",
    type=["txt","zip"]
)

if uploaded_file:

    if uploaded_file.name.endswith(".zip"):
        with zipfile.ZipFile(uploaded_file) as z:
            txt_file = [f for f in z.namelist() if f.endswith(".txt")][0]
            with z.open(txt_file) as f:
                data = f.read().decode("utf-8", errors="ignore")

            media_files = [
                f for f in z.namelist()
                if f.lower().endswith((".jpg",".png",".mp4",".mp3",".opus"))
            ]
            total_media_files = len(media_files)
    else:
        data = uploaded_file.getvalue().decode("utf-8", errors="ignore")
        total_media_files = 0

    df = preprocess.preprocess(data)

    selected_user = st.selectbox(
        "Analyze for",
        ["Overall"] + df['user'].unique().tolist()
    )

    if st.button("Analyze Conversations"):
        st.session_state.analysis_done = True

    if st.session_state.analysis_done:

        msgs, words, media, _ = helper.fetch_stats(selected_user, df)

        col1,col2,col3,col4 = st.columns(4)

        col1.markdown(f"<div class='kpi-card'><h3>💬 Messages</h3><h2>{msgs}</h2></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='kpi-card'><h3>📝 Words</h3><h2>{words}</h2></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='kpi-card'><h3>📷 Media Mentions</h3><h2>{media}</h2></div>", unsafe_allow_html=True)
        col4.markdown(f"<div class='kpi-card'><h3>📦 Media Files</h3><h2>{total_media_files}</h2></div>", unsafe_allow_html=True)

        st.markdown("## 📊 Analytics")
        st.markdown("---")

        tab1,tab2,tab3,tab4 = st.tabs(
            ["Timeline","Emoji","Sentiment","🛡 Toxicity"]
        )

        with tab1:
            timeline = df.groupby(df['date'].dt.date).size().reset_index(name="messages")
            fig = px.line(timeline,x="date",y="messages",
                          color_discrete_sequence=[primary_color])
            st.plotly_chart(fig,use_container_width=True)

        with tab2:
            emoji_df = helper.emoji_analysis(selected_user, df)
            if not emoji_df.empty:
                fig = px.bar(emoji_df,x="emoji",y="count",
                             color="count",
                             color_continuous_scale="blues")
                st.plotly_chart(fig,use_container_width=True)

        with tab3:
            sentiment_counts, sentiment_df = helper.fast_sentiment_analysis(selected_user, df)
            st.bar_chart(sentiment_counts)

        with tab4:
            if st.button("Run Toxicity Scan"):
                toxic_df, toxic_count, clean_percentage = helper.fast_toxicity_analysis(selected_user, df)
                st.metric("Toxic Messages", toxic_count)
                st.metric("Clean Chat %", f"{clean_percentage}%")

        st.download_button("Download CSV", df.to_csv(index=False), "chatrica_analysis.csv")