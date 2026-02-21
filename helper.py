from collections import Counter
from urlextract import URLExtract
import emoji

def fetch_stats(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    num_messages = df.shape[0]

    words = []
    for msg in df['message']:
        words.extend(msg.split())

    num_words = len(words)

    num_media = df[df['message'] == '<Media omitted>'].shape[0]

    extractor = URLExtract()
    links = []
    for msg in df['message']:
        links.extend(extractor.find_urls(msg))

    return num_messages, num_words, num_media, len(links)
from collections import Counter
import emoji
import pandas as pd

def emoji_analysis(selected_user, df):

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    emojis = []

    for msg in df['message']:
        for char in msg:
            if char in emoji.EMOJI_DATA:
                emojis.append(char)

    emoji_count = Counter(emojis)

    emoji_df = pd.DataFrame(emoji_count.items(), columns=['emoji', 'count'])
    emoji_df = emoji_df.sort_values(by='count', ascending=False)

    return emoji_df.head()
def most_common_words(selected_user, df):

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    with open("stopwords.txt", "r") as f:
        stop_words = f.read().split()

    words = []

    for msg in df['message']:
        for word in msg.lower().split():
            if word not in stop_words:
                words.append(word)

    word_freq = Counter(words).most_common(10)

    common_df = pd.DataFrame(word_freq, columns=['word', 'count'])
    return common_df
def activity_heatmap(selected_user, df):

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    heatmap = df.pivot_table(
        index='day_name',
        columns='hour',
        values='message',
        aggfunc='count'
    ).fillna(0)

    return heatmap
from transformers import pipeline

# Load model only once (important!)
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

def transformer_sentiment_analysis(selected_user, df):
    
    # Filter user if not group
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    sentiments = []

    for message in df['message']:
        try:
            result = sentiment_pipeline(message[:512])[0]  # limit to 512 tokens
            sentiments.append(result['label'])
        except:
            sentiments.append("NEUTRAL")

    df['sentiment'] = sentiments

    sentiment_counts = df['sentiment'].value_counts()

    return sentiment_counts, df
def generate_chat_summary(selected_user, df, sentiment_df):
    
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    total_messages = df.shape[0]

    # Most active user (for group)
    most_active_user = None
    if selected_user == "Overall":
        most_active_user = df['user'].value_counts().idxmax()

    # Peak day
    df['only_date'] = pd.to_datetime(df['date']).dt.date
    peak_day = df['only_date'].value_counts().idxmax()

    # Peak hour
    df['hour'] = pd.to_datetime(df['date']).dt.hour
    peak_hour = df['hour'].value_counts().idxmax()

    # Sentiment score
    score_map = {"POSITIVE": 1, "NEGATIVE": -1}
    sentiment_df['score'] = sentiment_df['sentiment'].map(score_map)
    overall_score = sentiment_df['score'].mean()

    if overall_score > 0:
        mood = "predominantly positive"
    elif overall_score < 0:
        mood = "mostly negative"
    else:
        mood = "balanced"

    # Generate summary text
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


