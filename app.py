import streamlit as st
import preprocess
import helper

st.title("WhatsApp Chat Analyzer")

uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:

    data = uploaded_file.getvalue().decode("utf-8", errors="ignore")

    df = preprocess.preprocess(data)

    st.write("Data Loaded Successfully ✅")
    st.dataframe(df.head())

    # Extract unique users (MOVE INSIDE THIS BLOCK)
    user_list = df['user'].unique().tolist()

    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.selectbox("Show analysis for", user_list)

    if st.button("Show Analysis"):

        num_messages, num_words, num_media, num_links = helper.fetch_stats(selected_user, df)

        st.subheader("Top Statistics")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Messages", num_messages)
        col2.metric("Words", num_words)
        col3.metric("Media", num_media)
        col4.metric("Links", num_links)
