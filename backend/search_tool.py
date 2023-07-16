"""Util that calls Google Search."""
import time

from typing import Any, Dict, Optional

import aiohttp
import requests
from dotenv import load_dotenv
from flask_socketio import emit
from pydantic.class_validators import root_validator
from pydantic.main import BaseModel

from langchain.utils import get_from_dict_or_env

from prompt import SEARCH_INSTRUCTION

load_dotenv(verbose=True)


class GoogleSerperAPIWrapper(BaseModel):
    """Wrapper around the Serper.dev Google Search API.

    You can create a free API key at https://serper.dev.

    To use, you should have the environment variable ``SERPER_API_KEY``
    set with your API key, or pass `serper_api_key` as a named parameter
    to the constructor.

    Example:
        .. code-block:: python

            from langchain import GoogleSerperAPIWrapper
            google_serper = GoogleSerperAPIWrapper()
    """

    k: int = 5
    gl: str = "us"
    hl: str = "en"
    type: str = "search"  # search, images, places, news
    tbs: Optional[str] = None
    serper_api_key: Optional[str] = None
    aiosession: Optional[aiohttp.ClientSession] = None

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key exists in environment."""
        serper_api_key = get_from_dict_or_env(
            values, "serper_api_key", "SERPER_API_KEY"
        )
        values["serper_api_key"] = serper_api_key

        return values

    def results(self, query: str, **kwargs: Any) -> Dict:
        """Run query through GoogleSearch."""
        return self._google_serper_search_results(
            query,
            gl=self.gl,
            hl=self.hl,
            num=self.k,
            tbs=self.tbs,
            search_type=self.type,
            **kwargs,
        )

    def run(self, query: str, **kwargs: Any) -> str:
        """Run query through GoogleSearch and parse result."""
        results = self._google_serper_search_results(
            query,
            gl=self.gl,
            hl=self.hl,
            num=self.k,
            tbs=self.tbs,
            search_type=self.type,
            **kwargs,
        )

        return self._parse_results(results)

    async def aresults(self, query: str, **kwargs: Any) -> Dict:
        """Run query through GoogleSearch."""
        results = await self._async_google_serper_search_results(
            query,
            gl=self.gl,
            hl=self.hl,
            num=self.k,
            search_type=self.type,
            tbs=self.tbs,
            **kwargs,
        )
        return results

    async def arun(self, query: str, **kwargs: Any) -> str:
        """Run query through GoogleSearch and parse result async."""
        results = await self._async_google_serper_search_results(
            query,
            gl=self.gl,
            hl=self.hl,
            num=self.k,
            search_type=self.type,
            tbs=self.tbs,
            **kwargs,
        )

        return self._parse_results(results)

    def _parse_results(self, results: dict) -> str:
        snippets = []

        if results.get("answerBox"):
            answer_box = results.get("answerBox", {})
            print(answer_box)
            if answer_box.get("answer"):
                if answer_box.get("link"):
                    return "content: " + answer_box.get("answer") + "\nurl: " + answer_box.get("link")
                else:
                    return "content: " + answer_box.get("answer")
            elif answer_box.get("snippet"):
                return "content: " + answer_box.get("snippet").replace("\n", " ") + "\nurl: " + answer_box.get("link")
            elif answer_box.get("snippetHighlighted"):
                return "content: " + ", ".join(answer_box.get("snippetHighlighted")) + "\nurl: " + answer_box.get(
                    "link")

        if results.get("knowledgeGraph"):
            kg = results.get("knowledgeGraph", {})
            title = kg.get("title")
            entity_type = kg.get("type")
            tmp = []
            if entity_type:
                tmp.append(f"{title}: {entity_type}.")
            description = kg.get("description")
            if description:
                tmp.append(description)
            for attribute, value in kg.get("attributes", {}).items():
                tmp.append(f"{title} {attribute}: {value}.")
            snippets.append("content: " + ", ".join(tmp) + "\nurl: \n\n")

        for result in results["organic"][: self.k]:
            tmp = []
            if "snippet" in result:
                tmp.append(result["snippet"])
            for attribute, value in result.get("attributes", {}).items():
                tmp.append(f"{attribute}: {value}.")
            snippets.append("content: " + ", ".join(tmp) + "\nurl: " + result["link"] + "\n\n")

        if len(snippets) == 0:
            return "No good Google Search Result was found"

        return "".join(snippets)

    def _google_serper_search_results(
            self, search_term: str, search_type: str = "search", **kwargs: Any
    ) -> dict:
        headers = {
            "X-API-KEY": self.serper_api_key or "",
            "Content-Type": "application/json",
        }
        params = {
            "q": search_term,
            **{key: value for key, value in kwargs.items() if value is not None},
        }
        response = requests.post(
            f"https://google.serper.dev/{search_type}", headers=headers, params=params
        )
        response.raise_for_status()
        search_results = response.json()
        return search_results

    async def _async_google_serper_search_results(
            self, search_term: str, search_type: str = "search", **kwargs: Any
    ) -> dict:
        headers = {
            "X-API-KEY": self.serper_api_key or "",
            "Content-Type": "application/json",
        }
        url = f"https://google.serper.dev/{search_type}"
        params = {
            "q": search_term,
            **{key: value for key, value in kwargs.items() if value is not None},
        }

        if not self.aiosession:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        url, params=params, headers=headers, raise_for_status=False
                ) as response:
                    search_results = await response.json()
        else:
            async with self.aiosession.post(
                    url, params=params, headers=headers, raise_for_status=True
            ) as response:
                search_results = await response.json()

        return search_results


class MultiGoogleSearchTool:
    search_engine = GoogleSerperAPIWrapper()

    def run(self, query):
        emit('status', {'status': 'Online Search'})
        query = query.split(",")
        all_ret = []
        for q in query:
            all_ret.append(self.search_engine.run(q.strip()))
        res = "".join(all_ret) + "\n\n"
        ans = SEARCH_INSTRUCTION.format(res)
        today_date = time.strftime('%b %d %Y', time.localtime(int(time.time())))
        ans += f"\n\nBe careful about the date or live event mentioned in the above searched result, as it might be outdated. You should be aware that the correct current date is {today_date}. If the current date can assist in providing a more accurate and precise answer to the user's query, please incorporate it along with the aforementioned information. However, if the current date is not relevant or necessary for addressing the query, there is no need to mention it.\n\n"
        emit('status', {'status': 'LLM'})
        return ans
