import os.path

import pandas as pd
import requests
from flask_socketio import emit

K = 5

key = 'S8GYPD9LEU2ONU6D'


def scrawl_news(crypto, date):
    time_from = date + 'T0000'
    time_to = date + 'T2359'
    url = 'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=CRYPTO:' + \
          crypto + \
          '&time_from=' + time_from + \
          '&time_to=' + time_to + \
          '&sort=RELEVANCE' + \
          '&limit=50' + \
          '&apikey=' + key

    r = requests.get(url)
    data = r.json()["feed"]
    _date = []
    titles = []
    urls = []
    summarys = []
    for i in data:
        _date.append(time_from[:8])
        titles.append(i['title'])
        urls.append(i['url'])
        summarys.append(i['summary'])
    df = pd.DataFrame(columns=['date', 'title', 'url', 'summary'])
    df['date'] = _date
    df['title'] = titles
    df['url'] = urls
    df['summary'] = summarys
    df.to_csv(f'news/{crypto}_' + date + '.csv')
    return df


def read_news(crypto_date):
    emit('status', {'status': 'Daily News'})
    print(crypto_date)
    crypto, date = crypto_date.split(",")
    if os.path.exists(f"news/{crypto}_{date}.csv"):
        news_data = pd.read_csv(f"news/{crypto}_{date}.csv")
    else:
        try:
            news_data = scrawl_news(crypto, date)
        except Exception:
            raise Exception("Error ", crypto, date)
    news_markdown = ""
    for i in range(K):
        news_markdown += f"{i+1}. [{news_data.iloc[i]['title']}]({news_data.iloc[i]['url']})\n"
    return news_markdown
