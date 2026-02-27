import pandas as pd
import emoji
from collections import Counter
from urlextract import URLExtract
from transformers import pipeline
import streamlit as st

# =====================================================
# CACHED MODELS (LOAD ONLY ONCE)
# =====================================================

@st.cache_resource
def load_sentiment_model():
    return pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english"
    )

@st.cache_resource
def load_toxic_model():
    return pipeline(
        "text-classification",
        model="unitary/toxic-bert"
    )

# =====================================================
# BASIC STATS
# =====================================================

def fetch_stats(selected_user, df):

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    num_messages = df.shape[0]

    words = []
    for msg in df['message']:
        words.extend(str(msg).split())

    num_words = len(words)

    num_media = df[df['message'] == '<Media omitted>'].shape[0]

    extractor = URLExtract()
    links = []
    for msg in df['message']:
        links.extend(extractor.find_urls(str(msg)))

    return num_messages, num_words, num_media, len(links)

# =====================================================
# EMOJI ANALYSIS
# =====================================================

def emoji_analysis(selected_user, df):

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    emojis = []

    for msg in df['message']:
        for char in str(msg):
            if char in emoji.EMOJI_DATA:
                emojis.append(char)

    emoji_count = Counter(emojis)

    emoji_df = pd.DataFrame(emoji_count.items(), columns=['emoji', 'count'])
    emoji_df = emoji_df.sort_values(by='count', ascending=False)

    return emoji_df.head()

# =====================================================
# MOST COMMON WORDS
# =====================================================

def most_common_words(selected_user, df):

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    with open("stopwords.txt", "r") as f:
        stop_words = f.read().split()

    words = []

    for msg in df['message']:
        for word in str(msg).lower().split():
            if word not in stop_words:
                words.append(word)

    word_freq = Counter(words).most_common(10)

    return pd.DataFrame(word_freq, columns=['word', 'count'])

# =====================================================
# HEATMAP
# =====================================================

def activity_heatmap(selected_user, df):

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    heatmap = df.pivot_table(
        index=df['date'].dt.day_name(),
        columns=df['date'].dt.hour,
        values='message',
        aggfunc='count'
    ).fillna(0)

    return heatmap

# =====================================================
# FAST SENTIMENT ANALYSIS (BATCH + LIMIT)
# =====================================================

def fast_sentiment_analysis(selected_user, df):

    model = load_sentiment_model()

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    messages = df['message'].astype(str).tolist()

    # Limit for speed
    messages = messages[:200]

    results = model(messages)

    sentiments = [r['label'] for r in results]

    df = df.head(len(sentiments)).copy()
    df['sentiment'] = sentiments

    sentiment_counts = df['sentiment'].value_counts()

    return sentiment_counts, df

# =====================================================
# FAST TOXICITY ANALYSIS (BATCH + LIMIT)
# =====================================================

def fast_toxicity_analysis(selected_user, df):

    model = load_toxic_model()

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    messages = df['message'].astype(str).tolist()
    messages = messages[:200]

    results = model(messages)

    labels = [r['label'] for r in results]

    df = df.head(len(labels)).copy()
    df['toxicity_label'] = labels

    toxic_count = labels.count("toxic")

    clean_percentage = round(
        ((len(labels) - toxic_count) / len(labels)) * 100, 2
    ) if len(labels) > 0 else 100

    return df, toxic_count, clean_percentage

# =====================================================
# ENGAGEMENT SCORE (NEWLY ADDED)
# =====================================================

def calculate_engagement_score(df, sentiment_df):

    # Message Volume Score (max 40)
    msg_score = min(len(df) / 10, 40)

    # Sentiment Positivity Score (max 30)
    if 'sentiment' in sentiment_df.columns:
        positive_ratio = sentiment_df['sentiment'].value_counts(normalize=True).get('POSITIVE', 0)
    else:
        positive_ratio = 0

    sentiment_score = positive_ratio * 30

    # Avg Message Length Score (max 30)
    avg_length = df['message'].astype(str).str.len().mean()
    length_score = min(avg_length / 10, 30)

    total_score = msg_score + sentiment_score + length_score

    return round(total_score, 2)

# =====================================================
# CHAT SUMMARY
# =====================================================

def generate_chat_summary(selected_user, df, sentiment_df):

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    total_messages = df.shape[0]

    most_active_user = None
    if selected_user == "Overall":
        most_active_user = df['user'].value_counts().idxmax()

    df['only_date'] = pd.to_datetime(df['date']).dt.date
    peak_day = df['only_date'].value_counts().idxmax()

    df['hour'] = pd.to_datetime(df['date']).dt.hour
    peak_hour = df['hour'].value_counts().idxmax()

    score_map = {"POSITIVE": 1, "NEGATIVE": -1}
    sentiment_df['score'] = sentiment_df['sentiment'].map(score_map)
    overall_score = sentiment_df['score'].mean()

    if overall_score > 0:
        mood = "predominantly positive"
    elif overall_score < 0:
        mood = "mostly negative"
    else:
        mood = "balanced"

    summary = f"""
📊 Chat Summary Report:

• Total Messages: {total_messages}
• Overall Mood: {mood}
• Peak Activity Day: {peak_day}
• Peak Activity Hour: {peak_hour}:00 hrs
"""

    if most_active_user:
        summary += f"\n• Most Active User: {most_active_user}"

    return summary