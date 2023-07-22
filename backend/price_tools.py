import os
import time
import json
import openai
import pytz
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from flask_socketio import emit
from requests import Session
from datetime import datetime, timedelta

matplotlib.use('Agg')
load_dotenv(verbose=True)


def get_names():
    names = []
    full_name, short_name = [], []
    with open("name.csv", 'r', encoding="MacRoman") as f:
        for line in f.readlines():
            line = line.strip().split(",")
            line = [l.strip() for l in line if len(l.strip()) > 0]
            names.append(line)
            full_name.append(line[0])
            short_name.append(line[1].upper())
    return names, full_name, short_name


crypto_names, full_name, short_name = get_names()


class GetPrice:
    def __init__(self, coin_symbol, st, ed):
        self.coin_symbol = coin_symbol
        self.st = st
        self.ed = ed

    def getprice(self):
        headers = {'X-CMC_PRO_API_KEY': os.getenv("COINCAP_KEY")}
        session = Session()
        session.headers.update(headers)
        xaxis = []
        yaxis = []
        url = 'https://api.coincap.io/v2/assets/' + self.coin_symbol + '/history'

        st_form = (datetime.strptime(self.st, '%Y-%m-%d')).replace(tzinfo=pytz.utc)
        ed_form = (datetime.strptime(self.ed, '%Y-%m-%d')).replace(tzinfo=pytz.utc)

        st_unix_timestamp_ms = int(st_form.timestamp() * 1000)
        ed_unix_timestamp_ms = int(ed_form.timestamp() * 1000)
        max_interval = 2505600000
        now_unix_timestamp_ms = st_unix_timestamp_ms
        while now_unix_timestamp_ms < ed_unix_timestamp_ms:
            next_unix_timestamp_ms = min(now_unix_timestamp_ms + max_interval, ed_unix_timestamp_ms)

            parameters = {
                'ids': self.coin_symbol,
                'interval': 'h1',
                'start': now_unix_timestamp_ms,
                'end': next_unix_timestamp_ms,
            }
            time.sleep(1)
            response = session.get(url, params=parameters)
            response = response.json()
            for item in response["data"]:
                xaxis.append(item['date'])
                yaxis.append(float(item['priceUsd']))
            now_unix_timestamp_ms = next_unix_timestamp_ms
        return self.coin_symbol, xaxis, yaxis


prompt = """
You are a ChatGPT model that assists users with cryptocurrency-related queries. 
Your task is to extract the cryptocurrency name, date, and time from the user's query. 
If any of these elements are missing from the query, you should replace them with None and do not need to add the content. 
Return the extracted information as a list in the format ["name", "HH:mm", "yyyy-mm-dd"] without 'answer' or 'output'.
Here are some examples of API calls:
User Query: what is the Dogecoin price at 8:00 on Feb. 12, 2020?
["dogecoin","08:00","2020-02-12"]
User Query: what is the btc price on Jan. 1, 2023?.
["bitcoin","None","2023-01-01"]
User Query: {}
"""

prompt_period = """
You are a ChatGPT model that assists users with cryptocurrency-related queries. 
Your task is to extract the cryptocurrency name, start date, and end date from the user's query. 
If any of these elements are missing from the query, you should replace them with None and do not need to add the content. 
Return the extracted information as a list in the format ["name", "yyyy-mm-dd", "yyyy-mm-dd"] without 'answer' or 'output'.
Here are some examples of API calls:
User Query: what is the Dogecoin price from Feb. 12, 2020 to May. 07, 2020?
Your Output: ["dogecoin","2020-02-12","2020-05-07"]
User Query: what is the btc price from 20/12/2022 to 01/03/2023?.
Your Output: ["btc","2022-12-20","2023-03-01"]
User Query: {}
Your Output: 
"""

openai.api_key = os.getenv("OPENAI_KEY")


def get_bot_response(question, prompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt.format(question),
        temperature=0,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return json.loads((response['choices'][0].text))


def get_day_price(question):
    answer = get_bot_response(question, prompt)

    trg_crypto = set()
    trg_crypto_acn = set()
    token = answer[0]
    for i, n in enumerate(crypto_names):
        if token.lower() in n:
            trg_crypto.add(full_name[i])
            trg_crypto_acn.add(short_name[i])
            break
    trg_crypto = list(trg_crypto)
    trg_crypto_acn = list(trg_crypto_acn)
    print(answer)
    print(trg_crypto[0])
    print(answer[1])
    print(answer[2])
    st_form = answer[2]
    ed_form = datetime.strptime(answer[2], '%Y-%m-%d') + timedelta(days=1)
    ed_form = str(ed_form.strftime("%Y-%m-%d"))
    sym, x_axis, y_axis = GetPrice(trg_crypto[0], st_form, ed_form).getprice()
    df = pd.DataFrame({"time": x_axis, sym: y_axis})
    df = df.set_index('time', drop=True)

    if answer[1] != 'None':
        result = df[df.index.str.contains(answer[2]) & df.index.str.contains(answer[1])][trg_crypto[0]]
    else:
        result = df
    if len(result) == 1:
        output = "The price of " + answer[0] + " at " + answer[1] + " on " + answer[2] + " is " + str(result[0]) + "."
    else:
        prices = result[trg_crypto[0]].values
        h, l = prices.max(), prices.min()
        output = "On " + answer[2] + ", the highest and lowest prices of " + answer[0] + " are " + str(
            h) + " and " + str(l) + ", respectively."
    return output


def get_period_price(question):
    user_input = question
    answer = get_bot_response(user_input, prompt_period)

    trg_crypto = set()
    trg_crypto_acn = set()
    token = answer[0]
    for i, n in enumerate(crypto_names):
        if token.lower() in n:
            trg_crypto.add(full_name[i])
            trg_crypto_acn.add(short_name[i])
            break
    trg_crypto = list(trg_crypto)
    trg_crypto_acn = list(trg_crypto_acn)
    print(answer)
    print(trg_crypto[0])
    print(answer[1])
    print(answer[2])
    st_form = answer[1]
    ed_form = answer[2]
    sym, x_axis, y_axis = GetPrice(trg_crypto[0], st_form, ed_form).getprice()
    # print(x_axis)
    # print(y_axis)
    new_y_axis = []
    new_x_axis = []
    for i in range(len(y_axis) // 24):
        new_y_axis.append(sum(y_axis[i * 24:(i + 1) * 24]) / 24)
        new_x_axis.append(x_axis[i * 24])
    df = pd.DataFrame({"time": new_x_axis, sym: new_y_axis})
    df = df.set_index('time', drop=True)

    df.index = pd.to_datetime(df.index.values, format='%Y-%m-%dT%H:00:00.000Z')
    formatted_s = df.index.strftime("%Y-%m-%dT%H:00:00.000Z")
    # import matplotlib.ticker as ticker
    ticker_size = int(len(formatted_s) * 0.5 * 0.5)
    plt.figure(figsize=(10, 6))
    plt.plot_date(formatted_s, df.values, linestyle='solid')
    # plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(ticker_size))
    # plt.title('Price Over Time')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.gcf().autofmt_xdate()
    fig_title = trg_crypto_acn[0] + "_" + answer[1] + "-" + answer[2]
    plt.savefig(f"./img/{fig_title}.png")

    return '#@@#' + fig_title + ".png"


def price_plot_des(query):
    try:
        emit('status', {'status': 'Crypto Price Search'})
        fig_name = get_period_price(query)
        return fig_name
    except:
        return "We cannot understand your query for now. Kindly note that our support is limited to querying cryptocurrency prices, and we do not provide stock price information. Furthermore, when specifying a date, please ensure it is in the format YYYY-mm-DD, such as '2023-05-30'."


def show_day_price(query):
    try:
        emit('status', {'status': 'Crypto Price Search'})
        output = get_day_price(query)
        return output
    except:
        return "We cannot understand your query for now."
