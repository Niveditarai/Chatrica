import re
import pandas as pd

def preprocess(data):

    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'date': dates, 'message': messages})

    df['date'] = pd.to_datetime(df['date'])

    users = []
    messages_clean = []

    for msg in df['message']:
        entry = re.split('([\w\W]+?):\s', msg)
        if entry[1:]:
            users.append(entry[1])
            messages_clean.append(entry[2])
        else:
            users.append("group_notification")
            messages_clean.append(entry[0])

    df['user'] = users
    df['message'] = messages_clean

    # ✅ ADD THESE INSIDE FUNCTION
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df['day_name'] = df['date'].dt.day_name()

    return df
