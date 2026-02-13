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
