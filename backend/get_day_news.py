import os

import requests
import time
from datetime import datetime, date, timedelta
import openai
from dotenv import load_dotenv

load_dotenv(verbose=True)
# prompt = """As a news aggregator. Given a set of headlines and summaries of news articles,
# provide a summary of the content of each article in a concise and informative manner.
# Your summary should give me a good idea of what this news list is about without requiring
# me to read it article by article. Please ensure that your abstract is accurate, unbiased
# and relevant to the title and abstract of the article. Also, please try to group related
# articles together and highlight any overarching themes or trends in the news listings.
# Please note that your answer should not exceed 2,000 words.
# News list: {}
# """

prompt = """
Act as a news summarizer. Please summarize the following news list:

{}

Please ensure that each news item is marked with the markdown format citation [number](url) after summarization, where 'number' is the order of the news item and 'url is its url link'. 
The summary should be under 3000 words."""

openai.api_key = os.getenv("OPENAI_KEY")


def get_bot_response(news_list):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt.format(news_list),
        temperature=0.8,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # 返回机器人的回复
    return response['choices'][0].text


def get_day_news(keywards, date):
    time_to = datetime.strptime(date, '%Y-%m-%d')
    time_to = time_to.strftime('%Y%m%d')
    time_from = datetime.strptime(time_to, '%Y%m%d') - timedelta(days=1)
    time_from = time_from.strftime('%Y%m%d')
    time_to, time_from = time_to + 'T2300', time_from + 'T0000'
    print(keywards, time_from, time_to)
    url = 'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=CRYPTO:' + \
          keywards + \
          '&time_from=' + time_from + \
          '&time_to=' + time_to + \
          '&sort=RELEVANCE' + \
          '&apikey=' + os.getenv("alphavantage_key")
    r = requests.get(url)
    data = r.json()["feed"]
    content = ""
    for i in data[:5]:
        content += i['url'] + '\n' + \
                   i['summary'] + '\n\n'
    summary = get_bot_response(content)

    return summary
