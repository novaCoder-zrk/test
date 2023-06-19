import os
import time

import requests
from dotenv import load_dotenv
from langchain.agents import Tool, AgentType
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferWindowMemory
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent
from urllib3.exceptions import MaxRetryError, SSLError

from price_tools import price_plot_des, show_day_price
from prompt import SYSTEM_PREFIX
from search_tool import MultiGoogleSearchTool

load_dotenv(verbose=True)


class ChatbotBackend:
    def __init__(self):
        self.search_chain = None
        self.router_chain = None
        self.default_chain = None
        self.api_key = None
        self.memory = None
        self.llm = None
        self.embeddings = None
        self.chain = None
        self.chain_type = ""
        self.gpt_cache = False
        self.authenticate(os.getenv("OPENAI_KEY"))

    def reset_llm(self):
        self.llm = None
        self.embeddings = None
        self.chain = None

    def authenticate(self, api_key):
        def is_valid_openai_key():
            # doing this without using openai.api_key, as it propagates globally to all users
            headers = {"Authorization": f"Bearer {api_key}"}
            url = "https://api.openai.com/v1/engines"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return True
            else:
                return False

        if is_valid_openai_key():
            self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
            self.api_key = api_key
            self.create_search_chatbot()
        else:
            print("Something went wrong, check your API key.")
            self.reset_llm()

    def create_search_chatbot(self, seed_memory=None):
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo-0613", temperature=0.3, openai_api_key=self.api_key)
        self.memory = seed_memory if seed_memory is not None else ConversationBufferWindowMemory(k=5,
                                                                                                 memory_key="chat_history",
                                                                                                 return_messages=True)
        search = MultiGoogleSearchTool()
        tools = [
            Tool(
                name="Search",
                func=search.run,
                description="useful for questions that ask the news about a specific event with online search. "
                            "The search engine support advanced search operators including: \n"
                            "1. '\"\"' instruct to search for the exact phrase, for example, \"Bitcoin News\" denotes the results must exactly contain the phrase \"Bitcoin News\"\n"
                            "2. 'site:' can be added into the query to limit the results from a specific website, you can use 'site: coindesk.com', 'site: cryptonews.com' or 'site: cointelegraph.com'\n"
                            "3. '*' can be used as a wildcard to replace unknown words in a search query, for example, searching for  'artificial * research' will return results related to 'artificial neural network research' or 'artificial intelligence ethics research' etc.\n"
                            "You are free to use these advanced search operators or not to rewrite and expand the original query "
                            "to a comma separated list of optimized and decomposed queries "
                            "that can better, accurately and comprehensively retrieve the desired results. "
                            "For example, `\"Ethereum upgrade roadmap\",next upgrade date of Ethereum,Ethereum upgrade details site: coindesk.com` would be the optimized queries for the original query 'Can you tell me about the next upgrade for Ethereum? When and what will happen?'.",
            ),
            Tool(
                name="Cryptocurrency Price",
                func=price_plot_des,
                description="useful for questions that query the price of cryptocurrency during a period. "
                            "This tool's input is the original query, do NOT change it."
                            "Use this more than the normal search if the question "
                            "is about querying or displaying cryptocurrency price during a period, "
                            "like 'what the BTC price of last week?', "
                            "'what is the Dogecoin price from 2022-10-01 to 2023-02-01' or "
                            "'display the BTC price from 2023.3.10 to 2023.3.12'.",
                return_direct=True
            ),
            Tool(
                name="Cryptocurrency Day Price",
                func=show_day_price,
                description="useful for questions that query the price of cryptocurrency on a specific day or hour. "
                            "This tool's input is the original query, do NOT change it."
                            "Use this more than the normal search or Cryptocurrency Price if the question "
                            "is about querying or displaying cryptocurrency price for a day rather than a period of time, "
                            "like 'what the BTC price on May 5, 2023', "
                            "'what is the Dogecoin price at 8:00 on Feb. 12, 2020' or "
                            "'display the BTC price on Jan. 2, 2021'.",
                return_direct=True
            ),
        ]

        self.search_chain = initialize_agent(tools, self.llm, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                                             verbose=True, memory=self.memory,
                                             agent_kwargs={"system_message": SYSTEM_PREFIX})

    def generate_response(self, user_input):
        today_date = time.strftime('%b %d %Y', time.localtime(int(time.time())))
        user_input = f"Today is {today_date}. " + user_input
        try:
            response = self.search_chain.run(user_input).strip()
        except (MaxRetryError, SSLError):
            response = "Network error, please retry later."
        return response


test_cases = [
        "When will CPI data be announced? What is the official Web site for the CPI data?",
        "What time does the NFP (Non-Farm Payroll) report come out?",
        "What are the dates of the next Federal Reserve meeting?",
        "What are the dates of the next Federal Open Market Committee meeting?",
        "Is the cryptocurrency SUI listed on any exchange? When and where was it first listed?",
        "Did the NFT exchange platform Opensea issue any cryptocurrency?",
        "What is the next Bitcoin halving date? What will happen after the halving?",
        "Can you tell me about the next upgrade for Ethereum? When and what will happen?",
        "What is the next cliff unlock date for the cryptocurrency ARB?"
    ]
