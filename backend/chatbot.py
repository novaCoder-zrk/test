import os
import time
from langchain.output_parsers import RetryWithErrorOutputParser
from loguru import logger
import langchain
import requests
from dotenv import load_dotenv
from flask_socketio import emit
from langchain import PromptTemplate, OpenAI
from langchain.agents import Tool, AgentType, ConversationalChatAgent
from langchain.cache import SQLiteCache
from langchain.callbacks import get_openai_callback, FileCallbackHandler
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferWindowMemory
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent
from urllib3.exceptions import MaxRetryError, SSLError

from daily_news import read_news
from log_handler import LogCallbackHandler
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
            langchain.llm_cache = SQLiteCache(database_path=".langchain.db")
        else:
            print("Something went wrong, check your API key.")
            self.reset_llm()

    def create_search_chatbot(self, seed_memory=None):
        logfile = f"log/{time.strftime('%Y-%m-%d', time.localtime(int(time.time())))}.log"
        logger.add(logfile, colorize=True, enqueue=True)
        handler = LogCallbackHandler(logfile)
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0.1, openai_api_key=self.api_key)
        self.memory = seed_memory if seed_memory is not None else ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True)
        search = MultiGoogleSearchTool()
        tools = [
            Tool(
                name="Search",
                func=search.run,
                # description="useful for questions that ask the news about a specific event with online search. "
                #             "The search engine support advanced search operators including: \n"
                #             "1. '\"\"' instruct to search for the exact phrase, for example, \"Bitcoin News\" denotes the results must exactly contain the phrase \"Bitcoin News\"\n"
                #             "2. 'site:' can be added into the query to limit the results from a specific website, you can use 'site: coindesk.com', 'site: cryptonews.com' or 'site: cointelegraph.com'\n"
                #             "3. '*' can be used as a wildcard to replace unknown words in a search query, for example, searching for  'artificial * research' will return results related to 'artificial neural network research' or 'artificial intelligence ethics research' etc.\n"
                #             "You are free to use these advanced search operators or not to rewrite and expand the original query "
                #             "to a comma separated list of optimized and decomposed queries "
                #             "that can better, accurately and comprehensively retrieve the desired results. "
                #             "Here are example responses that are properly optimized and rewrote with advanced search operators: "
                #             "Original query: Can you tell me about the next upgrade for Ethereum? When and what will happen?\n"
                #             "Optimized query: `\"Ethereum upgrade roadmap\",next upgrade date of Ethereum,Ethereum upgrade details site: coindesk.com`\n\n"
                #             "Original query: Recent news related to BTC and ETH\n"
                #             "Optimized query: `\"BTC OR ETH\",BTC site: coindesk.com,BTC site: cointelegraph.com,ETH site: coindesk.com,ETH site: cointelegraph.com`\n\n"
                #             "Now, please give the optimized query given user's input."
                description="useful for questions that ask the news about a specific event with online search. "
                            "You need to rewrite and expand the original query "
                            "to a comma separated list of optimized and decomposed queries "
                            "that can better, accurately and comprehensively retrieve the desired results. "
                            "Here are example responses that are properly optimized and rewrote: "
                            "Original query: Can you tell me about the next upgrade for Ethereum? When and what will happen?\n"
                            "Optimized query: `Ethereum upgrade roadmap,next upgrade date of Ethereum,Ethereum upgrade details`\n\n"
                            "Original query: When will CPI data be announced? What is the official Web site for the CPI data?\n"
                            "Optimized query: `CPI announce time,CPI official website`\n\n"
                            "Now, please give the optimized query given user's input."
            ),
            Tool(
                name="Cryptocurrency Price",
                func=price_plot_des,
                description="useful for questions that query the price of cryptocurrency during a period, NOT for stock querying. "
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
            Tool(
                name="Daily News",
                func=read_news,
                description="useful for querying cryptocurrency-related news on a specific day. "
                            "This original query should be transformed into a comma separated format of 'cryptocurrency name,date'."
                            "For example: "
                            "original query: 'what happened to BTC on May 23, 2020?'"
                            "transformed query: 'BTC,20200523'"
                            "original query: 'news related to ETH on April 19 2023?'"
                            "transformed query: 'ETH,20230419'",
                return_direct=True
            )
        ]

        self.search_chain = initialize_agent(tools, self.llm, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                                             verbose=True, memory=self.memory, max_iterations=4,
                                             handle_parsing_errors=False, callbacks=[handler],
                                             early_stopping_method="generate",
                                             agent_kwargs={"system_message": SYSTEM_PREFIX})

    def _get_datetime(self):
        return time.strftime('%b %d %Y', time.localtime(int(time.time())))

    def _get_suffix(self, inp):
        if len(inp) > 50:
            return "Please answer the query as comprehensively as possible."
        else:
            return ""

    def generate_response(self, user_input):
        emit('status', {'status': 'LLM'})
        prompt = PromptTemplate(
            template="Today is {date}. {query} {suffix}",
            input_variables=["query"],
            partial_variables={"date": self._get_datetime, "suffix": self._get_suffix(user_input)}
        )
        user_input = prompt.format(query=user_input)
        try:
            with get_openai_callback() as cb:
                try:
                    response = self.search_chain.run(user_input)
                except ValueError as e:
                    response = str(e)
                    if not response.startswith("Could not parse LLM output: "):
                        raise e
                    response = response.removeprefix("Could not parse LLM output: ")
                    head_str = '{'
                    print('response:', response)
                    if response.startswith(head_str):
                        response = response[53:]
                    if response[:-1] == '}':
                        response = response[:-2]
                print(f"\n{'#' * 20}\nTotal Tokens: {cb.total_tokens}")
                print(f"Prompt Tokens: {cb.prompt_tokens}")
                print(f"Completion Tokens: {cb.completion_tokens}")
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
    "What is the next cliff unlock date for the cryptocurrency ARB?",
    "Why did Nvidia's stock price almost double in the first half of 2023?",
    "How did the Coinbase stock perform in the past few days? Any reason behind that?",
    "I want to build a cryptocurrency portfolio. You will send a series of recommendations based on my growth goals and criteria. I want the portfolio to contain 50% low to medium risk coins. This 50% will be within the top 75 in current cryptocurrency market cap, must have an all time high that is close to 10x of the current market price, and be an established and trusted project. Next, I'd like the next 30% of the portfolio to contain medium-cap coins. These should be less than 1 billion current market cap, but greater than 100 million. I want these to achieve a realistic 20-30x in the next bull market (ie: grow from 100m to 2 billion). These should be trusted projects that are reasonably well established, but have more room to grow than some of the larger projects. Finally, I want to allocate the remaining 20% of the portfolio into speculative, low market cap projects. These should NOT be shitcoins, but they should be small with potential to 50x or even 100x in the next bull market. These must have real world utility and the potential to have an impact long term, NOT be a random pump and dump memecoin. Within each of these sectors, I want to dollar cost average into 5-10 projects at most every week. Thus, please send in detail which projects are the best fit for each of these sectors, and WHY they should be included in my portfolio. It's very important that this portfolio achieves 15x or more total growth by the end of the next bull market cycle."
]
