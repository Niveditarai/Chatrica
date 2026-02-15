import streamlit as st
import preprocess
import helper
import pandas as pd

st.title("WhatsApp Chat Analyzer")

uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:

    bytes_data = uploaded_file.getvalue()

    try:
        data = bytes_data.decode("utf-8")
    except:
        data = bytes_data.decode("latin-1")

    df = preprocess.preprocess(data)

    # ---- User Dropdown ----
    user_list = df['user'].unique().tolist()

    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.selectbox("Show analysis for", user_list)

    if st.button("Show Analysis"):

        # =============================
        # 📊 Basic Stats
        # =============================
        num_messages, num_words, num_media, num_links = helper.fetch_stats(selected_user, df)

        st.subheader("Top Statistics")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Messages", num_messages)
        col2.metric("Words", num_words)
        col3.metric("Media", num_media)
        col4.metric("Links", num_links)

        # =============================
        # 😊 Emoji Analysis
        # =============================
        st.subheader("Emoji Analysis")
        emoji_df = helper.emoji_analysis(selected_user, df)

        if not emoji_df.empty:
            st.dataframe(emoji_df)
            st.bar_chart(emoji_df.set_index('emoji'))
        else:
            st.write("No emojis found")

        # =============================
        # 🤖 Transformer Sentiment Analysis
        # =============================
        st.subheader("Transformer Sentiment Analysis")

        sentiment_counts, sentiment_df = helper.transformer_sentiment_analysis(selected_user, df)

        st.write("Sentiment Distribution")
        st.bar_chart(sentiment_counts)

        # ---- Timeline ----
        sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
        sentiment_df['only_date'] = sentiment_df['date'].dt.date

        daily_sentiment = sentiment_df.groupby(['only_date', 'sentiment']).size().unstack().fillna(0)

        st.line_chart(daily_sentiment)

        # ---- Score System ----
        score_map = {"POSITIVE": 1, "NEGATIVE": -1}
        sentiment_df['score'] = sentiment_df['sentiment'].map(score_map)

        overall_score = sentiment_df['score'].mean()

        st.write("Overall Sentiment Score:", round(overall_score, 3))
